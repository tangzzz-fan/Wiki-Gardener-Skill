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


def test_install_script_defaults_to_all_skills_and_setup():
    script = (ROOT / "scripts" / "install_skills.sh").read_text(encoding="utf-8")
    assert "--skill '*'" in script or '--skill "*"' in script
    assert "setup-knowledge-skills" in script
    assert "--no-setup" in script
