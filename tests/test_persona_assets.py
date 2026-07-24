"""Persona / domain-seed 资产契约：schema、交叉引用、setup-wizard 第零轮对齐。

与 tests/fixtures/interview-personas/（访谈风格指纹）严格分离：
本文件只锁 wiki-gardener/assets/personas 与 assets/domain-seeds。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WG = ROOT / "wiki-gardener"
PERSONAS_DIR = WG / "assets" / "personas"
SEEDS_DIR = WG / "assets" / "domain-seeds"
WIZARD = WG / "references" / "setup-wizard.md"
INTERVIEW_README = ROOT / "tests" / "fixtures" / "interview-personas" / "README.md"

sys.path.insert(0, str(ROOT / "scripts"))
import validate_skills as vs  # noqa: E402
import score_constitution as sc  # noqa: E402


def persona_files() -> list[Path]:
    return sorted(PERSONAS_DIR.glob("*.md"))


def seed_files() -> list[Path]:
    return sorted(SEEDS_DIR.glob("*.md"))


def test_at_least_one_persona_and_seeds():
    assert PERSONAS_DIR.is_dir()
    assert SEEDS_DIR.is_dir()
    assert persona_files(), "assets/personas/ 至少需要 1 个 persona"
    assert seed_files(), "assets/domain-seeds/ 至少需要 1 个域种子"


@pytest.mark.parametrize("path", persona_files(), ids=lambda p: p.name)
def test_persona_required_sections(path: Path):
    errs = vs.check_persona_file(path, SEEDS_DIR)
    assert not errs, errs


@pytest.mark.parametrize("path", seed_files(), ids=lambda p: p.name)
def test_domain_seed_required_sections(path: Path):
    errs = vs.check_domain_seed_file(path)
    assert not errs, errs


def test_persona_and_domain_seeds_via_validate():
    errs = vs.check_persona_and_domain_seeds(WG)
    assert not errs, errs


def test_persona_seed_cross_refs():
    """独立老师推荐域对应的三种子均存在。"""
    teacher = PERSONAS_DIR / "独立老师.md"
    assert teacher.is_file()
    text = teacher.read_text(encoding="utf-8")
    for name in ("课程设计.md", "招生.md", "抖音运营.md"):
        assert f"domain-seeds/{name}" in text
        assert (SEEDS_DIR / name).is_file(), name


def test_default_vs_on_demand_markers():
    for path in persona_files():
        text = path.read_text(encoding="utf-8")
        body = vs.section_body(text, "推荐初始域")
        assert body is not None, path.name
        assert "默认加载" in body, f"{path.name}: 须有默认加载域"
        assert "按需" in body, f"{path.name}: 须有按需加载域"


def test_interview_variants_reference_wizard_qs():
    wizard = WIZARD.read_text(encoding="utf-8")
    # 第 2 节问题清单应能定位到 Q 编号对应的默认问题
    for path in persona_files():
        text = path.read_text(encoding="utf-8")
        body = vs.section_body(text, "访谈变体")
        assert body is not None, path.name
        qs = set(re.findall(r"\bQ([4-8])\b", body))
        assert qs, f"{path.name}: 访谈变体须引用至少一个 Q"
        for q in qs:
            # setup-wizard 用「4. …」列出问题；访谈变体用 Q4
            assert re.search(rf"^{q}\.\s", wizard, re.MULTILINE), (
                f"{path.name}: Q{q} 在 setup-wizard 第 2 节无对应题号"
            )


def test_setup_wizard_has_round_zero():
    wizard = WIZARD.read_text(encoding="utf-8")
    assert "第零轮" in wizard
    assert "assets/personas/" in wizard
    assert "都不像" in wizard
    assert "种子不是笼子" in wizard or "亲口确认" in wizard
    assert "用户确认" in wizard or "亲口确认" in wizard


def test_naming_collision_docs():
    """interview-personas ≠ assets/personas；scorer 不得指向资产包。"""
    assert "assets/personas" not in str(sc.PERSONAS_DIR)
    readme = INTERVIEW_README.read_text(encoding="utf-8")
    assert "assets/personas" in readme
    assert "interview-personas" in readme or "风格" in readme
