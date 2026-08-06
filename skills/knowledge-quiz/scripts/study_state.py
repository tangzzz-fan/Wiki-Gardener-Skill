#!/usr/bin/env python3
"""Deterministic Markdown study-state management for knowledge-quiz."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

STATE_VERSION = 1
LEARNING_RELATIVE = Path("00_系统") / "学习记录"
INDEX_NAME = "掌握索引.md"
SESSIONS_DIR = "测验记录"
DATA_START = "<!-- knowledge-quiz:data:start -->"
DATA_END = "<!-- knowledge-quiz:data:end -->"
VALID_STATES = {"unseen", "learning", "mastered", "review_due"}
VALID_ACTIONS = {"recall", "explain", "application", "relation"}
QUALIFYING_ACTIONS = {"application", "relation"}


class StudyStateError(ValueError):
    """Raised for invalid inputs or unsafe study-state operations."""


def _normalized_text(value: str, field: str) -> str:
    text = " ".join(unicodedata.normalize("NFKC", value).strip().split())
    if not text:
        raise StudyStateError(f"{field} 不能为空")
    return text


def normalize_source_path(source_path: str) -> str:
    """Return a safe, normalized vault-relative POSIX path."""
    raw = unicodedata.normalize("NFKC", source_path.strip()).replace("\\", "/")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or ".." in path.parts:
        raise StudyStateError("source_path 必须是 vault 内不含 '..' 的相对路径")
    normalized = path.as_posix()
    if normalized in {"", "."}:
        raise StudyStateError("source_path 不能指向 vault 根目录")
    return normalized


def normalize_heading_anchor(heading_anchor: str) -> str:
    """Normalize a Markdown heading or heading anchor."""
    value = unicodedata.normalize("NFKC", heading_anchor).strip()
    value = re.sub(r"^#+\s*", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        raise StudyStateError("heading_anchor 不能为空")
    return value


def _stable_hash(prefix: str, parts: Iterable[str]) -> str:
    payload = json.dumps(list(parts), ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}_{digest}"


def stable_concept_id(
    source_path: str, heading_anchor: str, concept_key: str
) -> str:
    """Build a stable concept ID from source, heading, and concept key."""
    return _stable_hash(
        "c",
        (
            normalize_source_path(source_path),
            normalize_heading_anchor(heading_anchor),
            _normalized_text(concept_key, "concept_key"),
        ),
    )


def question_signature(
    concept_id: str, cognitive_action: str, tested_relation: str
) -> str:
    """Build a stable question signature independent of wording."""
    concept = _normalized_text(concept_id, "concept_id")
    action = _normalized_text(cognitive_action, "cognitive_action").lower()
    if action not in VALID_ACTIONS:
        choices = ", ".join(sorted(VALID_ACTIONS))
        raise StudyStateError(f"cognitive_action 必须是: {choices}")
    relation = _normalized_text(tested_relation, "tested_relation")
    return _stable_hash("q", (concept, action, relation))


def source_fingerprint(path: Path | str) -> str:
    """Return the SHA-256 fingerprint of a source file's raw bytes."""
    source = Path(path)
    if not source.is_file():
        raise StudyStateError(f"来源文件不存在或不是文件: {source}")
    try:
        return hashlib.sha256(source.read_bytes()).hexdigest()
    except OSError as exc:
        raise StudyStateError(f"无法读取来源文件 {source}: {exc}") from exc


def detect_source_change(
    recorded_fingerprint: str | None, current_fingerprint: str
) -> bool:
    """Return whether a previously fingerprinted source has changed."""
    return bool(
        recorded_fingerprint
        and current_fingerprint
        and recorded_fingerprint != current_fingerprint
    )


def _vault_source(vault: Path | str, source_path: str) -> Path:
    vault_root = Path(vault).expanduser().resolve()
    source = (vault_root / normalize_source_path(source_path)).resolve()
    try:
        source.relative_to(vault_root)
    except ValueError as exc:
        raise StudyStateError("来源路径解析后位于 vault 之外") from exc
    if not source.is_file():
        raise StudyStateError(f"vault 内找不到来源文件: {source_path}")
    return source


def _learning_root(vault: Path | str, create: bool = False) -> Path:
    vault_root = Path(vault).expanduser().resolve()
    if not vault_root.is_dir():
        raise StudyStateError(f"vault 不存在或不是目录: {vault_root}")
    root = (vault_root / LEARNING_RELATIVE).resolve()
    try:
        root.relative_to(vault_root)
    except ValueError as exc:
        raise StudyStateError("学习记录目录解析后位于 vault 之外") from exc
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_managed_path(root: Path, relative: Path | str) -> Path:
    target = (root / relative).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise StudyStateError("写入目标必须位于 00_系统/学习记录 内") from exc
    return target


def _empty_state() -> dict[str, Any]:
    return {"version": STATE_VERSION, "concepts": []}


def _validate_state(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise StudyStateError("掌握索引数据必须是 JSON 对象")
    if data.get("version") != STATE_VERSION:
        raise StudyStateError(
            f"不支持的掌握索引版本: {data.get('version')!r}"
        )
    concepts = data.get("concepts")
    if not isinstance(concepts, list):
        raise StudyStateError("掌握索引 concepts 必须是数组")
    seen: set[str] = set()
    for position, item in enumerate(concepts, start=1):
        if not isinstance(item, dict):
            raise StudyStateError(f"concepts 第 {position} 项必须是对象")
        concept_id = item.get("concept_id")
        if not isinstance(concept_id, str) or not concept_id:
            raise StudyStateError(f"concepts 第 {position} 项缺少 concept_id")
        if concept_id in seen:
            raise StudyStateError(f"掌握索引存在重复 concept_id: {concept_id}")
        seen.add(concept_id)
        if item.get("status") not in VALID_STATES:
            raise StudyStateError(
                f"{concept_id} 的 status 无效: {item.get('status')!r}"
            )
    return data


def load_index(vault: Path | str) -> dict[str, Any]:
    """Load and validate the Markdown mastery index, or return empty state."""
    root = _learning_root(vault)
    index_path = _safe_managed_path(root, INDEX_NAME)
    if not index_path.exists():
        return _empty_state()
    try:
        text = index_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StudyStateError(f"无法读取掌握索引: {exc}") from exc
    if text.count(DATA_START) != 1 or text.count(DATA_END) != 1:
        raise StudyStateError("掌握索引必须各含一个受控数据起止标记")
    start = text.index(DATA_START) + len(DATA_START)
    end = text.index(DATA_END, start)
    controlled = text[start:end].strip()
    match = re.fullmatch(r"```json\s*\n(.*)\n```", controlled, re.DOTALL)
    if not match:
        raise StudyStateError("掌握索引受控数据块必须是单个 json 围栏")
    try:
        return _validate_state(json.loads(match.group(1)))
    except json.JSONDecodeError as exc:
        raise StudyStateError(
            f"掌握索引 JSON 无法解析（第 {exc.lineno} 行）: {exc.msg}"
        ) from exc


def _wikilink(item: Mapping[str, Any]) -> str:
    source = str(item.get("source_path", "")).replace("|", r"\|")
    heading = str(item.get("heading_anchor", "")).replace("|", r"\|")
    return f"[[{source}#{heading}]]"


def _canonical_state(data: Mapping[str, Any]) -> dict[str, Any]:
    concepts: list[dict[str, Any]] = []
    for raw in data.get("concepts", []):
        item = dict(raw)
        for field in (
            "asked_question_signatures",
            "correct_question_signatures_current",
            "correct_sessions_current",
            "qualifying_actions_current",
        ):
            item[field] = sorted(set(item.get(field, [])))
        concepts.append(item)
    concepts.sort(key=lambda item: item["concept_id"])
    return {"version": STATE_VERSION, "concepts": concepts}


def render_index(data: Mapping[str, Any]) -> str:
    """Render deterministic, human-readable Markdown index content."""
    canonical = _canonical_state(data)
    lines = [
        "# 掌握索引",
        "",
        "此文件由 knowledge-quiz 管理。表格供人阅读，JSON 数据块是确定性真源。",
        "",
        "| concept_id | 状态 | 来源 | 当前版正确会话 |",
        "|---|---|---|---:|",
    ]
    for item in canonical["concepts"]:
        lines.append(
            f"| {item['concept_id']} | {item['status']} | "
            f"{_wikilink(item)} | "
            f"{len(item.get('correct_sessions_current', []))} |"
        )
    if not canonical["concepts"]:
        lines.append("| - | unseen | - | 0 |")
    payload = json.dumps(
        canonical, ensure_ascii=False, indent=2, sort_keys=True
    )
    lines.extend(
        ["", DATA_START, "```json", payload, "```", DATA_END, ""]
    )
    return "\n".join(lines)


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except (OSError, UnboundLocalError):
            pass
        raise StudyStateError(f"无法安全写入 {path}: {exc}") from exc


def save_index(vault: Path | str, data: Mapping[str, Any]) -> Path:
    """Validate and atomically save the mastery index."""
    root = _learning_root(vault, create=True)
    canonical = _canonical_state(data)
    _validate_state(canonical)
    index_path = _safe_managed_path(root, INDEX_NAME)
    _atomic_write(index_path, render_index(canonical))
    return index_path


def filter_candidates(
    index_data: Mapping[str, Any],
    candidates: Iterable[Mapping[str, Any]],
    include_mastered: bool = False,
    include_asked: bool = False,
) -> list[dict[str, Any]]:
    """Filter mastered concepts and previously asked question signatures."""
    entries = {
        item["concept_id"]: item for item in index_data.get("concepts", [])
    }
    result: list[dict[str, Any]] = []
    for raw in candidates:
        candidate = dict(raw)
        concept_id = candidate.get("concept_id")
        if not isinstance(concept_id, str) or not concept_id:
            raise StudyStateError("每个候选都必须含非空 concept_id")
        entry = entries.get(concept_id)
        status = "unseen" if entry is None else entry["status"]
        current = candidate.get("source_fingerprint")
        if (
            entry is not None
            and isinstance(current, str)
            and detect_source_change(entry.get("source_fingerprint"), current)
        ):
            status = "review_due"
        candidate["status"] = status
        signature = candidate.get("question_signature")
        already_asked = bool(
            entry is not None
            and isinstance(signature, str)
            and signature in entry.get("asked_question_signatures", [])
        )
        candidate["already_asked"] = already_asked
        if already_asked and not include_asked:
            continue
        if include_mastered or status != "mastered":
            result.append(candidate)
    priority = {"review_due": 0, "learning": 1, "unseen": 2, "mastered": 3}
    return sorted(
        result,
        key=lambda item: (priority[item["status"]], item["concept_id"]),
    )


def refresh_source_changes(vault: Path | str) -> list[str]:
    """Persist review_due for indexed concepts whose sources changed."""
    data = load_index(vault)
    changed: list[str] = []
    for item in data["concepts"]:
        current = source_fingerprint(
            _vault_source(vault, item["source_path"])
        )
        if detect_source_change(item.get("source_fingerprint"), current):
            item["status"] = "review_due"
            item["source_fingerprint"] = current
            item["correct_question_signatures_current"] = []
            item["correct_sessions_current"] = []
            item["qualifying_actions_current"] = []
            changed.append(item["concept_id"])
    if changed:
        save_index(vault, data)
    return sorted(changed)


def _safe_topic(topic: str) -> str:
    value = _normalized_text(topic, "topic")
    value = re.sub(r"[^\w\u3400-\u9fff-]+", "-", value, flags=re.UNICODE)
    value = value.strip("-_")[:60]
    if not value:
        raise StudyStateError("topic 清理后为空，请使用含文字或数字的主题")
    return value


def _session_relative_path(
    topic: str, session_file: str | None, now: datetime
) -> Path:
    if session_file:
        supplied = Path(session_file)
        if supplied.is_absolute() or ".." in supplied.parts:
            raise StudyStateError("session_file 必须是测验记录目录内的相对路径")
        if supplied.suffix.lower() != ".md":
            raise StudyStateError("session_file 必须以 .md 结尾")
        if len(supplied.parts) != 1:
            raise StudyStateError("session_file 只能是文件名，不能包含子目录")
        filename = supplied.name
    else:
        timestamp = now.astimezone().strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}-{_safe_topic(topic)}.md"
    return Path(SESSIONS_DIR) / filename


def append_session_record(
    vault: Path | str,
    *,
    session_id: str,
    topic: str,
    record: Mapping[str, Any],
    session_file: str | None = None,
    now: datetime | None = None,
) -> Path:
    """Append one answer to a deterministic Markdown session record."""
    instant = now or datetime.now(timezone.utc)
    root = _learning_root(vault, create=True)
    relative = _session_relative_path(topic, session_file, instant)
    target = _safe_managed_path(root, relative)
    if target.exists():
        text = target.read_text(encoding="utf-8")
        header_id = re.search(r"^- session_id: `([^`]+)`$", text, re.MULTILINE)
        if not header_id or header_id.group(1) != session_id:
            raise StudyStateError(
                f"会话文件已存在但 session_id 不匹配: {target.name}"
            )
        number = len(re.findall(r"^## 题目 \d+$", text, re.MULTILINE)) + 1
        prefix = text.rstrip() + "\n\n"
    else:
        number = 1
        prefix = (
            f"# 测验记录：{topic}\n\n"
            f"- session_id: `{session_id}`\n"
            f"- started_at: {instant.isoformat()}\n\n"
        )
    weak_point = record.get("weak_point") or "本题未发现"
    audit = json.dumps(dict(record), ensure_ascii=False, sort_keys=True)
    block = "\n".join(
        [
            f"## 题目 {number}",
            "",
            f"- 时间：{record['answered_at']}",
            f"- concept_id：`{record['concept_id']}`",
            f"- question_signature：`{record['question_signature']}`",
            f"- 认知动作：`{record['cognitive_action']}`",
            f"- 题目：{record['question']}",
            f"- 回答：{record['answer']}",
            f"- 判定：{record['judgment']}",
            f"- 来源：{record['source_citation']}",
            f"- 解析：{record['explanation']}",
            f"- 薄弱点：{weak_point}",
            f"- 状态：`{record['previous_status']}` -> `{record['new_status']}`",
            f"<!-- knowledge-quiz:answer {audit} -->",
            "",
        ]
    )
    _atomic_write(target, prefix + block)
    return target


def record_answer(
    vault: Path | str,
    *,
    source_path: str,
    heading_anchor: str,
    concept_key: str,
    cognitive_action: str,
    tested_relation: str,
    session_id: str,
    topic: str,
    question: str,
    answer: str,
    correct: bool,
    judgment: str,
    source_citation: str,
    explanation: str,
    weak_point: str = "",
    session_file: str | None = None,
    answered_at: str | None = None,
) -> dict[str, Any]:
    """Record one answer, update the index, and append the session log."""
    concept = stable_concept_id(source_path, heading_anchor, concept_key)
    action = _normalized_text(cognitive_action, "cognitive_action").lower()
    signature = question_signature(concept, action, tested_relation)
    session = _normalized_text(session_id, "session_id")
    normalized_source = normalize_source_path(source_path)
    source_file = _vault_source(vault, normalized_source)
    fingerprint = source_fingerprint(source_file)
    instant = answered_at or datetime.now(timezone.utc).isoformat()
    data = load_index(vault)
    previous_data = json.loads(json.dumps(data, ensure_ascii=False))
    existing_index_path = _safe_managed_path(
        _learning_root(vault), INDEX_NAME
    )
    index_preexisted = existing_index_path.is_file()
    entries = {item["concept_id"]: item for item in data["concepts"]}
    item = entries.get(concept)
    previous_status = "unseen" if item is None else item["status"]
    if item is None:
        item = {
            "concept_id": concept,
            "source_path": normalized_source,
            "heading_anchor": normalize_heading_anchor(heading_anchor),
            "concept_key": _normalized_text(concept_key, "concept_key"),
            "source_fingerprint": fingerprint,
            "status": "unseen",
            "asked_question_signatures": [],
            "correct_question_signatures_current": [],
            "correct_sessions_current": [],
            "qualifying_actions_current": [],
            "attempt_count": 0,
            "correct_count": 0,
            "last_seen_at": "",
            "last_question_signature": "",
        }
        data["concepts"].append(item)
    elif (
        item.get("source_path") != normalized_source
        or item.get("heading_anchor") != normalize_heading_anchor(heading_anchor)
        or item.get("concept_key") != _normalized_text(concept_key, "concept_key")
    ):
        raise StudyStateError(
            "concept_id 与索引中的来源、标题或概念键不一致"
        )
    if detect_source_change(item.get("source_fingerprint"), fingerprint):
        previous_status = "review_due"
        item["correct_question_signatures_current"] = []
        item["correct_sessions_current"] = []
        item["qualifying_actions_current"] = []
    item["source_fingerprint"] = fingerprint
    item["attempt_count"] = int(item.get("attempt_count", 0)) + 1
    item["last_seen_at"] = instant
    item["last_question_signature"] = signature
    asked_signatures = set(item.get("asked_question_signatures", []))
    asked_signatures.add(signature)
    correct_signatures = set(
        item.get("correct_question_signatures_current", [])
    )
    sessions = set(item.get("correct_sessions_current", []))
    actions = set(item.get("qualifying_actions_current", []))
    if correct:
        item["correct_count"] = int(item.get("correct_count", 0)) + 1
        correct_signatures.add(signature)
        sessions.add(session)
        if action in QUALIFYING_ACTIONS:
            actions.add(action)
        item["status"] = (
            "mastered"
            if len(sessions) >= 2
            and len(correct_signatures) >= 2
            and bool(actions)
            else "learning"
        )
    else:
        item["correct_count"] = int(item.get("correct_count", 0))
        item["status"] = "learning"
    item["asked_question_signatures"] = sorted(asked_signatures)
    item["correct_question_signatures_current"] = sorted(correct_signatures)
    item["correct_sessions_current"] = sorted(sessions)
    item["qualifying_actions_current"] = sorted(actions)
    record = {
        "answered_at": instant,
        "answer": _normalized_text(answer, "answer"),
        "cognitive_action": action,
        "concept_id": concept,
        "correct": bool(correct),
        "explanation": _normalized_text(explanation, "explanation"),
        "judgment": _normalized_text(judgment, "judgment"),
        "new_status": item["status"],
        "previous_status": previous_status,
        "question": _normalized_text(question, "question"),
        "question_signature": signature,
        "source_citation": _normalized_text(
            source_citation, "source_citation"
        ),
        "source_fingerprint": fingerprint,
        "tested_relation": _normalized_text(
            tested_relation, "tested_relation"
        ),
        "weak_point": " ".join(
            unicodedata.normalize("NFKC", weak_point).strip().split()
        ),
    }
    index_path = save_index(vault, data)
    try:
        session_path = append_session_record(
            vault,
            session_id=session,
            topic=_normalized_text(topic, "topic"),
            record=record,
            session_file=session_file,
        )
    except Exception as exc:
        try:
            if index_preexisted:
                save_index(vault, previous_data)
            else:
                index_path.unlink(missing_ok=True)
        except (OSError, StudyStateError) as rollback_exc:
            raise StudyStateError(
                "会话记录追加失败，且掌握索引回滚失败；"
                f"请人工核对 {index_path}。追加错误: {exc}；"
                f"回滚错误: {rollback_exc}"
            ) from exc
        raise StudyStateError(
            f"会话记录追加失败，掌握索引已回滚: {exc}"
        ) from exc
    return {
        "concept_id": concept,
        "question_signature": signature,
        "previous_status": previous_status,
        "new_status": item["status"],
        "index_path": str(index_path),
        "session_path": str(session_path),
    }


def _read_candidates(path: str) -> list[dict[str, Any]]:
    try:
        text = sys.stdin.read() if path == "-" else Path(path).read_text("utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise StudyStateError(f"无法读取候选 JSON: {exc}") from exc
    if not isinstance(data, list) or not all(
        isinstance(item, dict) for item in data
    ):
        raise StudyStateError("候选 JSON 必须是对象数组")
    return data


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "管理 knowledge-quiz 的 Markdown 学习状态。"
            "所有写操作仅限 vault/00_系统/学习记录。"
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    concept = sub.add_parser("concept-id", help="生成稳定 concept_id")
    concept.add_argument("--source", required=True, help="vault 相对来源路径")
    concept.add_argument("--heading", required=True, help="来源标题或锚点")
    concept.add_argument("--key", required=True, help="稳定概念键")

    signature = sub.add_parser(
        "question-signature", help="生成稳定 question_signature"
    )
    signature.add_argument("--concept-id", required=True)
    signature.add_argument(
        "--action", required=True, choices=sorted(VALID_ACTIONS)
    )
    signature.add_argument("--relation", required=True, help="被测关系")

    fingerprint = sub.add_parser("fingerprint", help="计算来源 SHA-256")
    fingerprint.add_argument("path", help="要读取的来源文件")

    filtered = sub.add_parser(
        "filter", help="按掌握状态和来源 fingerprint 过滤候选 JSON"
    )
    filtered.add_argument("--vault", required=True)
    filtered.add_argument(
        "--candidates", required=True, help="JSON 文件路径；- 表示 stdin"
    )
    filtered.add_argument("--include-mastered", action="store_true")
    filtered.add_argument(
        "--include-asked",
        action="store_true",
        help="显式允许重复历史上相同 question_signature 的题",
    )

    refresh = sub.add_parser(
        "refresh", help="检测来源变化并持久化 review_due"
    )
    refresh.add_argument("--vault", required=True)

    record = sub.add_parser(
        "record", help="记录一次答题并更新索引和会话 Markdown"
    )
    record.add_argument("--vault", required=True)
    record.add_argument("--source", required=True, help="vault 相对来源路径")
    record.add_argument("--heading", required=True)
    record.add_argument("--key", required=True, help="稳定概念键")
    record.add_argument(
        "--action", required=True, choices=sorted(VALID_ACTIONS)
    )
    record.add_argument("--relation", required=True, help="被测关系")
    record.add_argument("--session-id", required=True)
    record.add_argument("--session-file", help="测验记录目录内的 .md 文件名")
    record.add_argument("--topic", required=True)
    record.add_argument("--question", required=True)
    record.add_argument("--answer", required=True)
    correctness = record.add_mutually_exclusive_group(required=True)
    correctness.add_argument("--correct", action="store_true")
    correctness.add_argument("--incorrect", action="store_true")
    record.add_argument("--judgment", required=True)
    record.add_argument("--source-citation", required=True)
    record.add_argument("--explanation", required=True)
    record.add_argument("--weak-point", default="")
    record.add_argument("--answered-at", help="可选 ISO 8601 时间")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "concept-id":
            print(stable_concept_id(args.source, args.heading, args.key))
        elif args.command == "question-signature":
            print(
                question_signature(
                    args.concept_id, args.action, args.relation
                )
            )
        elif args.command == "fingerprint":
            print(source_fingerprint(args.path))
        elif args.command == "filter":
            candidates = _read_candidates(args.candidates)
            for candidate in candidates:
                if (
                    "source_fingerprint" not in candidate
                    and "source_path" in candidate
                ):
                    candidate["source_fingerprint"] = source_fingerprint(
                        _vault_source(args.vault, candidate["source_path"])
                    )
            result = filter_candidates(
                load_index(args.vault),
                candidates,
                include_mastered=args.include_mastered,
                include_asked=args.include_asked,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "refresh":
            changed = refresh_source_changes(args.vault)
            print(json.dumps({"review_due": changed}, ensure_ascii=False))
        elif args.command == "record":
            result = record_answer(
                args.vault,
                source_path=args.source,
                heading_anchor=args.heading,
                concept_key=args.key,
                cognitive_action=args.action,
                tested_relation=args.relation,
                session_id=args.session_id,
                session_file=args.session_file,
                topic=args.topic,
                question=args.question,
                answer=args.answer,
                correct=args.correct,
                judgment=args.judgment,
                source_citation=args.source_citation,
                explanation=args.explanation,
                weak_point=args.weak_point,
                answered_at=args.answered_at,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except StudyStateError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
