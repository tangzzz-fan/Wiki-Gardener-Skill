"""knowledge-quiz 学习状态脚本契约。"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "knowledge-quiz" / "scripts" / "study_state.py"


def _load_module():
    assert SCRIPT.is_file(), f"missing study-state script: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("study_state", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def study_state():
    return _load_module()


@pytest.fixture
def vault_source(tmp_path: Path) -> tuple[Path, Path]:
    vault = tmp_path / "vault"
    path = vault / "20_领域" / "示例" / "BLE 配网.md"
    path.parent.mkdir(parents=True)
    path.write_text("# 配网边界\n\n连接成功不等于配网完成。\n", encoding="utf-8")
    return vault, path


def _record(study_state, vault: Path, *, session_id: str, action: str):
    return study_state.record_answer(
        vault,
        source_path="20_领域/示例/BLE 配网.md",
        heading_anchor="配网边界",
        concept_key="连接与配网的区别",
        cognitive_action=action,
        tested_relation="连接与配网的边界",
        session_id=session_id,
        session_file=f"{session_id}.md",
        topic="BLE 配网",
        question="连接成功是否等于配网完成？",
        answer="不等于，还需要设备确认。",
        correct=True,
        judgment="正确",
        source_citation="[[20_领域/示例/BLE 配网.md#配网边界]]",
        explanation="连接只完成通信链路。",
        answered_at="2026-08-06T10:00:00+00:00",
    )


def test_concept_id_is_stable_and_input_sensitive(study_state):
    first = study_state.stable_concept_id(
        "20_领域/示例/BLE 配网.md", "配网边界", "连接与配网的区别"
    )
    assert first == study_state.stable_concept_id(
        "20_领域/示例/./BLE 配网.md", " 配网边界 ", "连接与配网的区别"
    )
    assert first != study_state.stable_concept_id(
        "20_领域/示例/BLE 配网.md", "配网边界", "扫描与连接的区别"
    )


def test_question_signature_ignores_wording_but_tracks_cognitive_action(study_state):
    concept_id = study_state.stable_concept_id(
        "20_领域/示例/BLE 配网.md", "配网边界", "连接与配网的区别"
    )
    recall = study_state.question_signature(concept_id, "recall", "连接与配网的边界")
    reworded = study_state.question_signature(
        concept_id, "recall", " 连接与配网的边界 "
    )
    application = study_state.question_signature(
        concept_id, "application", "连接与配网的边界"
    )
    assert recall == reworded
    assert recall != application


def test_filter_mastered_excludes_mastered_by_default(study_state):
    index = {
        "version": 1,
        "concepts": [
            {"concept_id": "c_learning", "status": "learning"},
            {"concept_id": "c_mastered", "status": "mastered"},
            {"concept_id": "c_due", "status": "review_due"},
        ],
    }
    candidates = [
        {"concept_id": "c_learning"},
        {"concept_id": "c_mastered"},
        {"concept_id": "c_due"},
    ]
    filtered = study_state.filter_candidates(index, candidates)
    assert [item["concept_id"] for item in filtered] == ["c_due", "c_learning"]
    assert len(
        study_state.filter_candidates(index, candidates, include_mastered=True)
    ) == 3


def test_filter_candidates_excludes_asked_signature_by_default(study_state):
    index = {
        "version": 1,
        "concepts": [
            {
                "concept_id": "c_learning",
                "status": "learning",
                "asked_question_signatures": ["q_seen"],
            }
        ],
    }
    candidates = [
        {"concept_id": "c_learning", "question_signature": "q_seen"},
        {"concept_id": "c_learning", "question_signature": "q_new"},
    ]

    filtered = study_state.filter_candidates(index, candidates)
    assert [item["question_signature"] for item in filtered] == ["q_new"]
    assert len(
        study_state.filter_candidates(index, candidates, include_asked=True)
    ) == 2


def test_cross_session_evidence_upgrades_to_mastered(
    study_state, vault_source: tuple[Path, Path]
):
    vault, _ = vault_source
    first = _record(study_state, vault, session_id="session-1", action="recall")
    assert first["new_status"] == "learning"

    second = _record(
        study_state, vault, session_id="session-2", action="application"
    )
    assert second["new_status"] == "mastered"
    assert study_state.load_index(vault)["concepts"][0]["status"] == "mastered"


def test_repeated_signature_across_sessions_does_not_master(
    study_state, vault_source: tuple[Path, Path]
):
    vault, _ = vault_source
    first = _record(
        study_state, vault, session_id="session-1", action="application"
    )
    second = _record(
        study_state, vault, session_id="session-2", action="application"
    )

    assert first["question_signature"] == second["question_signature"]
    assert second["new_status"] == "learning"
    concept = study_state.load_index(vault)["concepts"][0]
    assert len(concept["correct_sessions_current"]) == 2
    assert len(concept["correct_question_signatures_current"]) == 1


def test_source_fingerprint_change_marks_review_due(
    study_state, vault_source: tuple[Path, Path]
):
    vault, source = vault_source
    _record(study_state, vault, session_id="session-1", action="recall")
    mastered = _record(
        study_state, vault, session_id="session-2", action="application"
    )
    source.write_text("# 配网边界\n\n配网完成还需要设备确认。\n", encoding="utf-8")

    assert study_state.refresh_source_changes(vault) == [mastered["concept_id"]]
    concept = study_state.load_index(vault)["concepts"][0]
    assert concept["status"] == "review_due"
    assert concept["correct_sessions_current"] == []
    assert concept["qualifying_actions_current"] == []


def test_history_is_appended_not_overwritten(
    study_state, vault_source: tuple[Path, Path]
):
    vault, _ = vault_source
    first = _record(study_state, vault, session_id="session-1", action="recall")
    history = Path(first["session_path"])
    before = history.read_text(encoding="utf-8")
    _record(study_state, vault, session_id="session-1", action="application")
    after = history.read_text(encoding="utf-8")

    assert before in after
    assert after.count("## 题目") == 2
    assert after.count("knowledge-quiz:answer") == 2


def test_learning_state_path_rejects_escape(
    study_state, vault_source: tuple[Path, Path], tmp_path: Path
):
    vault, _ = vault_source
    with pytest.raises(study_state.StudyStateError):
        study_state.stable_concept_id(
            "../20_领域/越界.md", "标题", "越界概念"
        )

    record = {
        "answered_at": "2026-08-06T10:00:00+00:00",
        "concept_id": "c_example",
        "question_signature": "q_example",
        "cognitive_action": "recall",
        "question": "题目",
        "answer": "回答",
        "judgment": "正确",
        "source_citation": "[[来源]]",
        "explanation": "解析",
        "previous_status": "unseen",
        "new_status": "learning",
    }
    with pytest.raises(study_state.StudyStateError):
        study_state.append_session_record(
            vault,
            session_id="session-1",
            topic="越界",
            record=record,
            session_file="../20_领域/越界.md",
        )
    with pytest.raises(study_state.StudyStateError):
        study_state.append_session_record(
            vault,
            session_id="session-1",
            topic="越界",
            record=record,
            session_file=str(tmp_path / "outside.md"),
        )


def test_record_failure_rolls_back_new_index(
    study_state, vault_source: tuple[Path, Path]
):
    vault, _ = vault_source

    with pytest.raises(study_state.StudyStateError, match="已回滚"):
        study_state.record_answer(
            vault,
            source_path="20_领域/示例/BLE 配网.md",
            heading_anchor="配网边界",
            concept_key="连接与配网的区别",
            cognitive_action="recall",
            tested_relation="连接与配网的边界",
            session_id="session-1",
            session_file="../越界.md",
            topic="BLE 配网",
            question="连接成功是否等于配网完成？",
            answer="不等于。",
            correct=True,
            judgment="正确",
            source_citation="[[20_领域/示例/BLE 配网.md#配网边界]]",
            explanation="还需设备确认。",
        )

    index_path = vault / "00_系统" / "学习记录" / "掌握索引.md"
    assert not index_path.exists()
    assert study_state.load_index(vault) == {"version": 1, "concepts": []}
