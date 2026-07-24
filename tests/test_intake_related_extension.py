"""吸附关系判定契约：相关补缺 ≠ 近似重复合并。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "skills" / "wiki-gardener" / "references" / "intake.md"
SKILL = ROOT / "skills" / "wiki-gardener" / "SKILL.md"
FIXTURE_DRAFT = (
    ROOT / "tests" / "fixtures" / "sample-vault" / "10_inbox" / "BLE自定义协议草稿.md"
)
EVAL = ROOT / "tests" / "EVAL.md"

sys.path.insert(0, str(ROOT / "scripts"))
import validate_skills as vs  # noqa: E402


def test_intake_defines_related_extension_and_truth_gate():
    text = INTAKE.read_text(encoding="utf-8")
    assert "真实性关卡" in text or "真实性先于结构性" in text
    body = vs.section_body(text, "关系判定") or text
    assert "相关补缺" in body
    assert "新建" in body and "互链" in body
    assert "禁止" in body or "不要" in body or "而非" in body
    # 示例场景锚点
    assert "自定义协议" in text or "配网" in text


def test_intake_decision_matrix_orders_truth_before_structure():
    text = INTAKE.read_text(encoding="utf-8")
    # 章节标题可能是「## 4. 决策矩阵」
    matrix = vs.section_body(text, "决策矩阵") or vs.section_body(text, "4. 决策矩阵")
    assert matrix is not None
    assert "真实性关卡" in matrix or "相关补缺" in matrix
    assert "相关补缺" in matrix


def test_skill_mentions_related_extension():
    text = SKILL.read_text(encoding="utf-8")
    assert "相关补缺" in text


def test_fixture_custom_protocol_draft_exists_with_flaws():
    assert FIXTURE_DRAFT.is_file()
    text = FIXTURE_DRAFT.read_text(encoding="utf-8")
    assert "status: draft" in text
    assert "自定义协议" in text
    assert "主线程" in text or "sleep" in text or "同步" in text


def test_eval_has_a2b_scenario():
    text = EVAL.read_text(encoding="utf-8")
    assert "A2b" in text
    assert "相关补缺" in text
    assert "BLE自定义协议" in text or "自定义协议" in text
