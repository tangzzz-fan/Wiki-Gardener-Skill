#!/usr/bin/env python3
"""
score_constitution.py — 按访谈人设评分宪章风格

用于：
  1. CI：校验各人设的 宪章.golden.md 自身满足指纹
  2. L2 EVAL：Agent 访谈落盘后，对真实 vault 评分

用法：
  python3 scripts/score_constitution.py --persona engineering-craft
  python3 scripts/score_constitution.py --persona engineering-craft \\
      --constitution /tmp/wiki-eval-empty/00_系统/宪章.md \\
      --vault /tmp/wiki-eval-empty
  python3 scripts/score_constitution.py --all-goldens
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSONAS_DIR = ROOT / "tests" / "fixtures" / "interview-personas"

# setup-wizard.md Q2 → 度量重点 的显性映射（供单测与文档对齐）
Q2_METRIC_MAP = {
    "找不到东西": ["孤儿", "挂载", "MOC", "检索", "找不到"],
    "重复堆叠": ["冗余", "重复"],
    "信息过时": ["腐烂", "过时", "时效"],
    "越记越乱": ["孤儿", "乱", "结构", "挂载"],
}

Q6_STYLE_MAP = {
    "原文摘录为主": ["摘录"],
    "自己理解重写为主": ["重写"],
    "混合": ["混合"],
}


def load_persona(persona_id: str) -> dict:
    path = PERSONAS_DIR / persona_id / "persona.json"
    if not path.is_file():
        raise FileNotFoundError(f"persona not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_personas() -> list[str]:
    return sorted(
        p.name
        for p in PERSONAS_DIR.iterdir()
        if p.is_dir() and (p / "persona.json").is_file()
    )


def section_body(text: str, heading: str) -> str:
    """Extract markdown section body under ## heading until next ##."""
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    start = text.find("\n", start)
    if start < 0:
        return ""
    rest = text[start + 1 :]
    nxt = rest.find("\n## ")
    return rest if nxt < 0 else rest[:nxt]


def any_hit(text: str, keywords: list[str]) -> list[str]:
    return [k for k in keywords if k in text]


def score_constitution(
    constitution: str,
    persona: dict,
    vault: Path | None = None,
) -> tuple[bool, list[str]]:
    """Return (ok, failure_messages)."""
    expect = persona["expect"]
    fails: list[str] = []

    for sec in expect.get("must_sections", []):
        if f"## {sec}" not in constitution:
            fails.append(f"missing section: {sec}")

    checks = [
        ("北极星", "north_star_any"),
        ("收录标准", "include_any"),
        ("排斥标准", "exclude_any"),
        ("好笔记的定义", "writing_style_any"),
        ("度量重点", "metrics_any"),
    ]
    for heading, key in checks:
        body = section_body(constitution, heading)
        kws = expect.get(key, [])
        if kws and not any_hit(body, kws):
            fails.append(
                f"section「{heading}」missing style fingerprints {kws} "
                f"(got excerpt: {body.strip()[:80]!r})"
            )

    # 写法偏好应落在「好笔记的定义」
    style_body = section_body(constitution, "好笔记的定义")
    for k in expect.get("writing_style_any", []):
        if k not in style_body:
            # already covered by writing_style_any check; keep explicit
            pass

    if vault is not None:
        domain_root = vault / "20_领域"
        if expect.get("forbid_domain_dirs_under_20") and domain_root.is_dir():
            subdirs = [p for p in domain_root.iterdir() if p.is_dir()]
            if subdirs:
                fails.append(
                    f"should not pre-create domain folders under 20_领域/: "
                    f"{[p.name for p in subdirs]}"
                )
        packs = vault / "00_系统" / "domains"
        if expect.get("forbid_prebuilt_domain_packs") and packs.is_dir():
            md_packs = [
                p
                for p in packs.glob("*.md")
                if p.name != "README.md" and "模板" not in p.name and "说明" not in p.name
            ]
            # 允许空目录或仅说明文件；初始化时不应按 Q8 建好各域档案
            # 若存在与主题同名的域档案则失败
            themes = expect.get("mentioned_themes_as_text_only", [])
            for p in md_packs:
                name_l = p.stem.lower()
                for t in themes:
                    if t.lower() in name_l or name_l in t.lower():
                        fails.append(
                            f"should not pre-build domain pack for theme "
                            f"{t!r}: {p.relative_to(vault)}"
                        )

    return (len(fails) == 0, fails)


def score_answer_mapping(persona: dict) -> tuple[bool, list[str]]:
    """Check persona answers align with Q2/Q6 mapping tables."""
    fails: list[str] = []
    answers = persona["answers"]
    expect = persona["expect"]
    q2 = answers["Q2"]
    q6 = answers["Q6"]

    if q2 not in Q2_METRIC_MAP:
        fails.append(f"Q2={q2!r} not in Q2_METRIC_MAP")
    else:
        mapped = Q2_METRIC_MAP[q2]
        if not set(mapped) & set(expect.get("metrics_any", [])):
            fails.append(
                f"Q2={q2!r} maps to {mapped}, but expect.metrics_any="
                f"{expect.get('metrics_any')}"
            )

    # normalize q6 key
    q6_key = q6 if q6 in Q6_STYLE_MAP else None
    if q6_key is None:
        for k in Q6_STYLE_MAP:
            if k in q6:
                q6_key = k
                break
    if q6_key is None:
        fails.append(f"Q6={q6!r} not in Q6_STYLE_MAP")
    else:
        mapped = Q6_STYLE_MAP[q6_key]
        if not set(mapped) & set(expect.get("writing_style_any", [])):
            fails.append(
                f"Q6={q6!r} maps to {mapped}, but expect.writing_style_any="
                f"{expect.get('writing_style_any')}"
            )
    return (len(fails) == 0, fails)


def main() -> int:
    ap = argparse.ArgumentParser(description="Score constitution style vs persona")
    ap.add_argument("--persona", help="persona id")
    ap.add_argument(
        "--constitution",
        type=Path,
        help="path to 宪章.md (default: persona golden)",
    )
    ap.add_argument(
        "--vault",
        type=Path,
        help="optional vault root to check no prebuilt domains",
    )
    ap.add_argument(
        "--all-goldens",
        action="store_true",
        help="score every persona golden",
    )
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    results = []
    targets: list[tuple[str, Path, Path | None]] = []

    if args.all_goldens:
        for pid in list_personas():
            golden = PERSONAS_DIR / pid / "宪章.golden.md"
            targets.append((pid, golden, None))
    else:
        if not args.persona:
            ap.error("need --persona or --all-goldens")
        persona = load_persona(args.persona)
        const_path = args.constitution or (
            PERSONAS_DIR / args.persona / "宪章.golden.md"
        )
        targets.append((args.persona, const_path, args.vault))

    all_ok = True
    for pid, const_path, vault in targets:
        persona = load_persona(pid)
        map_ok, map_fails = score_answer_mapping(persona)
        if not const_path.is_file():
            results.append(
                {
                    "persona": pid,
                    "ok": False,
                    "fails": [f"missing file: {const_path}"],
                }
            )
            all_ok = False
            continue
        text = const_path.read_text(encoding="utf-8")
        ok, fails = score_constitution(text, persona, vault)
        fails = list(map_fails) + list(fails)
        ok = map_ok and ok
        results.append({"persona": pid, "ok": ok, "fails": fails, "file": str(const_path)})
        all_ok = all_ok and ok

    if args.json:
        print(json.dumps({"ok": all_ok, "results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = "PASS" if r["ok"] else "FAIL"
            print(f"[{status}] {r['persona']}  ({r.get('file', '')})")
            for f in r["fails"]:
                print(f"  - {f}")
        print("OK" if all_ok else "FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
