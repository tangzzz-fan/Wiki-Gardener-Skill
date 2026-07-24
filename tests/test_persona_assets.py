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
    """每个 persona 引用的 domain-seeds 均存在（独立老师作显式样例）。"""
    teacher = PERSONAS_DIR / "独立老师.md"
    assert teacher.is_file()
    text = teacher.read_text(encoding="utf-8")
    for name in ("课程设计.md", "招生.md", "抖音运营.md"):
        assert f"domain-seeds/{name}" in text
        assert (SEEDS_DIR / name).is_file(), name

    for path in persona_files():
        errs = vs.check_persona_file(path, SEEDS_DIR)
        assert not errs, errs


ENGINEER_PERSONA_NAMES = (
    "全栈工程师.md",
    "iOS原生与跨平台工程师.md",
)
ENGINEERING_SEED_NAMES = (
    "架构设计.md",
    "后端开发.md",
    "前端开发.md",
    "iOS开发.md",
    "跨平台开发.md",
)
FIRST_PRINCIPLES_MARKERS = ("第一性原理", "深入本质")


def engineer_persona_files() -> list[Path]:
    return [PERSONAS_DIR / name for name in ENGINEER_PERSONA_NAMES]


@pytest.mark.parametrize("path", engineer_persona_files(), ids=lambda p: p.name)
def test_engineer_personas_require_first_principles(path: Path):
    """软件工程师 persona 必须写入深入本质 + 第一性原理要求。"""
    assert path.is_file(), path.name
    text = path.read_text(encoding="utf-8")
    for marker in FIRST_PRINCIPLES_MARKERS:
        assert marker in text, f"{path.name}: 缺少「{marker}」"
    include = vs.section_body(text, "收录标准种子")
    assert include is not None
    assert "第一性原理" in include
    assert "深入本质" in include or "本质" in include


@pytest.mark.parametrize("name", ENGINEERING_SEED_NAMES)
def test_engineering_domain_seeds_require_first_principles(name: str):
    """工程域种子把第一性原理写进专家立场/写作立场，供执笔与审查读取。"""
    path = SEEDS_DIR / name
    assert path.is_file(), name
    text = path.read_text(encoding="utf-8")
    assert "第一性原理" in text, f"{name}: 缺少「第一性原理」"
    stance = vs.section_body(text, "专家立场")
    assert stance is not None
    assert "第一性原理" in stance or "深入本质" in stance


def test_default_vs_on_demand_markers():
    for path in persona_files():
        text = path.read_text(encoding="utf-8")
        body = vs.section_body(text, "推荐初始域")
        assert body is not None, path.name
        assert "默认加载" in body, f"{path.name}: 须有默认加载域"
        assert "按需" in body, f"{path.name}: 须有按需加载域"


def test_personas_have_atlas_partitions_not_folders():
    """分类靠总 MOC 分区，禁止把分区建成 20_领域 子目录。"""
    for path in persona_files():
        text = path.read_text(encoding="utf-8")
        body = vs.section_body(text, "推荐 Atlas 分区")
        assert body is not None, f"{path.name}: 缺少推荐 Atlas 分区"
        assert "20_领域" in body or "总 MOC" in body or "MOC" in body, path.name
        # 须明确否定实体目录；允许「勿建 / 不要建成 01-xxx」迁移说明
        assert any(m in body for m in ("不是文件夹", "勿建", "不要", "禁止")), path.name
        assert "平铺" in body or "总 MOC" in body or "MOC" in body


def test_teacher_persona_maps_legacy_folders_to_moc():
    """独立老师：旧编号目录心智映射到 MOC，且明确勿建文件夹。"""
    text = (PERSONAS_DIR / "独立老师.md").read_text(encoding="utf-8")
    atlas = vs.section_body(text, "推荐 Atlas 分区")
    assert atlas is not None
    assert "勿建" in atlas or "不是文件夹" in atlas
    for section in ("课程体系", "教案与课堂", "题库与练习", "学情档案", "家长沟通"):
        assert section in atlas, section
    assert "保分" in text or "包过" in text
    assert "协作边界" in text


def test_douyin_ops_hands_off_to_director():
    """算法运营审完应交接短视频编导，不代替写拍摄清单。"""
    ops = (SEEDS_DIR / "抖音运营.md").read_text(encoding="utf-8")
    craft = (SEEDS_DIR / "短视频编导.md").read_text(encoding="utf-8")
    assert "短视频编导" in ops
    assert "存在性先于形态性" in ops or "存在性先于形态性" in craft
    assert "资深短视频编导" in craft or "短视频编导" in craft
    assert "制作指导卡" in craft
    assert "图文" in craft and "口播" in craft and "出镜" in craft
    teacher = (PERSONAS_DIR / "独立老师.md").read_text(encoding="utf-8")
    creator = (PERSONAS_DIR / "自媒体工作者.md").read_text(encoding="utf-8")
    assert "短视频编导.md" in teacher and "短视频编导" in teacher
    assert "短视频编导.md" in creator and "短视频编导" in creator
    assert "存在性先于形态性" in teacher
    assert "存在性先于形态性" in creator


def test_setup_wizard_applies_atlas_partitions():
    wizard = WIZARD.read_text(encoding="utf-8")
    assert "推荐 Atlas 分区" in wizard
    assert "协作边界" in wizard
    assert "20_领域/" in wizard


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
