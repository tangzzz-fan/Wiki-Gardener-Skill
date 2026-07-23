"""访谈风格人设：黄金宪章指纹 + Q2/Q6 映射契约。"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "tests" / "fixtures" / "interview-personas"
SCORE = ROOT / "scripts" / "score_constitution.py"

# 保证可导入同仓脚本
sys.path.insert(0, str(ROOT / "scripts"))
import score_constitution as sc  # noqa: E402


def persona_ids() -> list[str]:
    return sc.list_personas()


@pytest.mark.parametrize("persona_id", persona_ids())
def test_persona_json_schema(persona_id: str):
    data = sc.load_persona(persona_id)
    assert data["id"] == persona_id
    for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"):
        assert q in data["answers"], q
    assert "expect" in data
    for key in (
        "north_star_any",
        "include_any",
        "exclude_any",
        "writing_style_any",
        "metrics_any",
        "must_sections",
    ):
        assert data["expect"].get(key), f"missing expect.{key}"


@pytest.mark.parametrize("persona_id", persona_ids())
def test_golden_constitution_matches_persona(persona_id: str):
    persona = sc.load_persona(persona_id)
    golden = PERSONAS / persona_id / "宪章.golden.md"
    text = golden.read_text(encoding="utf-8")
    map_ok, map_fails = sc.score_answer_mapping(persona)
    ok, fails = sc.score_constitution(text, persona, vault=None)
    assert map_ok, map_fails
    assert ok, fails


def test_all_goldens_cli():
    result = subprocess.run(
        [sys.executable, str(SCORE), "--all-goldens"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_q2_metric_map_covers_wizard_options():
    """与 setup-wizard 第二题选项对齐。"""
    wizard = (ROOT / "wiki-gardener" / "references" / "setup-wizard.md").read_text(
        encoding="utf-8"
    )
    for option in sc.Q2_METRIC_MAP:
        assert option in wizard, option


def test_styles_are_distinguishable():
    """四个方向的度量/写法指纹不应坍缩成同一套。"""
    metrics = []
    styles = []
    for pid in persona_ids():
        exp = sc.load_persona(pid)["expect"]
        metrics.append(tuple(sorted(exp["metrics_any"])))
        styles.append(tuple(sorted(exp["writing_style_any"])))
    assert len(set(metrics)) >= 3, metrics
    assert len(set(styles)) >= 2, styles


def test_score_rejects_wrong_style_pairing():
    """工程黄金宪章不应通过研究人设的指纹。"""
    eng_text = (PERSONAS / "engineering-craft" / "宪章.golden.md").read_text(
        encoding="utf-8"
    )
    research = sc.load_persona("research-notes")
    ok, fails = sc.score_constitution(eng_text, research)
    assert not ok
    assert fails


def test_forbid_prebuilt_domain_dirs(tmp_path: Path):
    persona = sc.load_persona("life-ops")
    const = (PERSONAS / "life-ops" / "宪章.golden.md").read_text(encoding="utf-8")
    vault = tmp_path / "vault"
    (vault / "20_领域" / "健康").mkdir(parents=True)
    (vault / "00_系统" / "domains").mkdir(parents=True)
    (vault / "00_系统" / "domains" / "健康.md").write_text("# 域档案：健康\n", encoding="utf-8")
    ok, fails = sc.score_constitution(const, persona, vault=vault)
    assert not ok
    assert any("domain" in f.lower() or "域" in f for f in fails)
