"""skills/ 包布局与 setup-knowledge-skills 契约。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

sys.path.insert(0, str(ROOT / "scripts"))
import validate_skills as vs  # noqa: E402


def test_skills_container_has_required_packages():
    assert SKILLS.is_dir()
    for name in vs.REQUIRED_SKILLS:
        assert (SKILLS / name / "SKILL.md").is_file(), name


def test_discover_skill_dirs_finds_all():
    dirs = vs.discover_skill_dirs(ROOT)
    names = {p.name for p in dirs}
    assert names >= set(vs.REQUIRED_SKILLS)


def test_setup_skill_is_bootstrap_not_gardener():
    text = (SKILLS / "setup-knowledge-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "name: setup-knowledge-skills" in text
    assert "vault" in text.lower() or "笔记库" in text
    assert "wiki-gardener" in text
    assert "domain-expert" in text
    # 交接初始化，不自己定北极星
    assert "北极星" in text
    assert "帮我初始化一个知识库" in text
    assert (SKILLS / "setup-knowledge-skills" / "assets" / "技能包说明.md").is_file()
    # companion 可选：探测 + 选装，不强迫
    assert "选装" in text
    assert "不编造" in text or "勿编造" in text


def test_install_script_defaults_to_all_skills_and_setup():
    script = (ROOT / "scripts" / "install_skills.sh").read_text(encoding="utf-8")
    assert "--skill '*'" in script or '--skill "*"' in script
    assert "setup-knowledge-skills" in script
    assert "--no-setup" in script


def test_existing_vault_onboarding_docs_and_wizard():
    guide = ROOT / "docs" / "已有知识库接入.md"
    assert guide.is_file()
    guide_text = guide.read_text(encoding="utf-8")
    assert "分批漏斗" in guide_text
    assert "就地登记" in guide_text
    assert "10_inbox" in guide_text

    wizard = (
        SKILLS / "wiki-gardener" / "references" / "setup-wizard.md"
    ).read_text(encoding="utf-8")
    assert "1.1 已有乱库接入" in wizard
    assert "禁止" in wizard and "静默删除" in wizard

    setup = (SKILLS / "setup-knowledge-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "已有知识库接入" in setup
    assert "保留旧文件" in setup


def test_gardener_hands_off_sparse_ideas_to_writer():
    gardener = (SKILLS / "wiki-gardener" / "SKILL.md").read_text(encoding="utf-8")
    assert "零散思路" in gardener
    assert "domain-expert" in gardener
    assert "不执笔成文" in gardener or "不是作者" in gardener
    assert "grill-me" in gardener
    assert "content-decomposer" in gardener
    assert "90_export" in gardener

    expert = (SKILLS / "domain-expert" / "SKILL.md").read_text(encoding="utf-8")
    assert "零散思路" in expert
    assert "10_inbox" in expert

    eval_md = (ROOT / "tests" / "EVAL.md").read_text(encoding="utf-8")
    assert "B3-E" in eval_md
    assert "零散思路全链路" in eval_md
    assert "C3. Companion 协作" in eval_md


def test_companion_packages_present_with_vault_contract():
    """思考/呈现 companion 已落 skills/，并带 inbox / 90_export 边界。"""
    thinking = (
        "grill-me",
        "topic-resonate",
        "content-diagnose",
        "script-flow",
        "content-decomposer",
    )
    presenting = (
        "frontend-slides",
        "ian-xiaohei-illustrations",
        "gbro-cover-design",
    )
    for name in thinking + presenting:
        skill = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        assert f"name: {name}" in skill, name
        assert "20_领域" in skill or "20_领域/" in skill, name

    for name in thinking:
        skill = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        assert "10_inbox" in skill, name

    for name in presenting:
        skill = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        assert "90_export" in skill, name

    setup = (SKILLS / "setup-knowledge-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "grill-me" in setup
    assert "90_export" in setup
    assert "不编造未安装" in setup or "勿编造" in setup
    assert "选装" in setup or "--skill grill-me" in setup
    assert "已装" in setup and "未装" in setup
    assert "~/.agents/skills" in setup or ".agents/skills" in setup
    assert "topic-resonate" in setup
    assert "content-decomposer" in setup
    assert "这个选题能不能打中人" in setup or "内容诊断" in setup
