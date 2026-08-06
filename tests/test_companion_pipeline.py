"""Companion 唤起与协作契约。

防三类漂移：
1. 唤不起：description / 触发语缺失，Agent 扫不到 companion
2. 交错位：思考/呈现落盘路径与园丁接线断掉
3. 角色塌缩：companion 代园丁吸附或代专家写领域定论 / 呈现物进 20_领域

风格对齐 tests/test_short_video_pipeline.py：锁 SKILL.md 与接线文档中的可扫描契约。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

sys.path.insert(0, str(ROOT / "scripts"))
import validate_skills as vs  # noqa: E402

THINKING = (
    "grill-me",
    "topic-resonate",
    "content-diagnose",
    "script-flow",
    "content-decomposer",
)
PRESENTING = (
    "frontend-slides",
    "ian-xiaohei-illustrations",
    "gbro-cover-design",
)
ALL_COMPANIONS = THINKING + PRESENTING

# description 里须能匹配的用户口语 / 关键词（技能发现依赖 description）
INVOKE_PHRASES: dict[str, tuple[str, ...]] = {
    "grill-me": ("grill", "想法很糊", "观点梳清楚", "grill me"),
    "topic-resonate": ("打中人", "共鸣"),
    "content-diagnose": ("内容怎么做", "内容诊断"),
    "script-flow": ("逻辑延续", "划走"),
    "content-decomposer": ("拆解", "对标"),
    "frontend-slides": ("presentation", "slides", "演示"),
    "ian-xiaohei-illustrations": ("配图", "小黑"),
    "gbro-cover-design": ("封面", "封面设计"),
}


def _fm_and_body(name: str) -> tuple[dict[str, str], str]:
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    return vs.parse_frontmatter(text)


def _desc(name: str) -> str:
    meta, _ = _fm_and_body(name)
    return meta.get("description", "")


def test_all_companions_discoverable():
    """npx skills / validate 能扫到全部 companion（与核心同级）。"""
    names = {p.name for p in vs.discover_skill_dirs(ROOT)}
    missing = set(ALL_COMPANIONS) - names
    assert not missing, f"undiscoverable: {sorted(missing)}"
    for name in ALL_COMPANIONS:
        assert (SKILLS / name / "SKILL.md").is_file(), name


def test_companion_frontmatter_name_matches_dir():
    for name in ALL_COMPANIONS:
        meta, _ = _fm_and_body(name)
        assert meta.get("name") == name
        desc = meta.get("description", "").strip()
        assert desc and desc != "|", name
        assert len(desc) <= 1024, name


def test_description_contains_invoke_phrases():
    """唤起前提：description 含用户可能说出的触发语。"""
    for name, phrases in INVOKE_PHRASES.items():
        desc = _desc(name)
        for phrase in phrases:
            assert phrase in desc, f"{name} description missing invoke phrase: {phrase!r}"


def test_thinking_skills_expose_when_to_trigger_section():
    """中文思考包正文须有可路由的触发说明（何时触发 / 触发）。"""
    for name in THINKING:
        _, body = _fm_and_body(name)
        assert (
            "何时触发" in body
            or "触发方式" in body
            or "触发：" in body
            or "触发条件" in body
        ), name


def test_setup_lists_companions_and_evoke_handoffs():
    """setup 探测表点名 companion；糊想法可交接 grill；勿编造未安装；支持选装。"""
    setup = (SKILLS / "setup-knowledge-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    for name in ALL_COMPANIONS:
        assert name in setup, f"setup missing companion listing: {name}"
    assert "帮我 grill" in setup or "grill-me" in setup
    assert "90_export" in setup
    assert "勿编造" in setup or "不编造" in setup
    assert "选装" in setup
    assert "--skill grill-me" in setup
    assert "这个选题能不能打中人" in setup
    assert "按我的标准拆解这条对标" in setup
    assert ".agents/skills" in setup
    assert "更新提示" in setup
    assert "刷新技能包说明" in setup or "update" in setup.lower()

    pack = (
        SKILLS / "setup-knowledge-skills" / "assets" / "技能包说明.md"
    ).read_text(encoding="utf-8")
    for name in THINKING:
        assert name in pack, name
    assert "90_export" in pack
    assert "{{STATUS_grill-me}}" in pack
    assert "未装" in pack
    assert "--skill grill-me" in pack or "选装" in pack
    assert "## 更新提示" in pack
    assert "## 选题创作怎么用" in pack
    assert "帮我 grill 一下" in pack
    assert "刷新一下技能包说明" in pack


def test_gardener_routes_sparse_idea_and_benchmark_to_companions():
    """园丁：糊想法→grill；对标→decomposer；导出物非吸附。"""
    gardener = (SKILLS / "wiki-gardener" / "SKILL.md").read_text(encoding="utf-8")
    assert "交接：零散思路" in gardener
    assert "grill-me" in gardener
    assert "domain-expert" in gardener
    assert "帮我 grill 一下" in gardener
    assert "交接：对标材料" in gardener or "content-decomposer" in gardener
    assert "content-decomposer" in gardener
    assert "90_export" in gardener
    assert "不是吸附对象" in gardener or "勿挂进" in gardener


def test_expert_writing_dedupes_grill_and_offers_export():
    """专家执笔：已有 grill 提纲少重复追问；定稿可导向呈现导出。"""
    writing = (
        SKILLS / "domain-expert" / "references" / "writing-mode.md"
    ).read_text(encoding="utf-8")
    assert "grill-me" in writing
    assert "跳过重复追问" in writing or "少重复追问" in writing
    assert "帮我 grill 一下" in writing
    assert "90_export" in writing
    assert "frontend-slides" in writing or "呈现 companion" in writing


def test_thinking_handoff_chain():
    """思考链：resonate→diagnose；grill/decomposer→expert；落 inbox。"""
    resonate = (SKILLS / "topic-resonate" / "SKILL.md").read_text(encoding="utf-8")
    assert "content-diagnose" in resonate
    assert "domain-expert" in resonate
    assert "grill-me" in resonate
    assert "帮我 grill 一下" in resonate

    diagnose = (SKILLS / "content-diagnose" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "topic-resonate" in diagnose or "grill-me" in diagnose
    assert "domain-expert" in diagnose
    assert "script-flow" in diagnose
    assert "帮我 grill 一下" in diagnose

    grill = (SKILLS / "grill-me" / "SKILL.md").read_text(encoding="utf-8")
    assert "不成文" in grill or "不写正文" in grill
    assert "domain-expert" in grill
    assert "共识提纲" in grill
    assert "一次只问一个问题" in grill or "一次一问" in grill
    assert "推荐答案" in grill
    assert "20_领域" in grill
    assert "10_inbox" in grill

    decomp = (SKILLS / "content-decomposer" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    for key in ("为何有效", "可参考", "不可照搬", "下一步"):
        assert key in decomp, key
    assert "判断标准" in decomp
    assert "10_inbox" in decomp
    assert "domain-expert" in decomp


def test_script_flow_does_not_bypass_existence_gate():
    """脚本逻辑检查不能冒充运营放行。"""
    script = (SKILLS / "script-flow" / "SKILL.md").read_text(encoding="utf-8")
    assert "存在性先于形态性" in script or "运营审核" in script
    assert "不替代" in script or "不能替代" in script or "不等于运营" in script
    assert "10_inbox" in script
    assert "20_领域" in script


def test_presenting_forbid_domain_tree_require_export():
    for name in PRESENTING:
        text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        assert "90_export" in text, name
        assert "20_领域" in text, name
        # 硬边界表述
        assert (
            "禁止" in text
            or "Do **not**" in text
            or "do **not**" in text
            or "Do not" in text
        ), name


def test_image_companions_soft_wire_mcp_with_fallback():
    """配图/封面可选用本机 mcp-image，但须可降级且不硬绑密钥。"""
    ian = (SKILLS / "ian-xiaohei-illustrations" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "mcp-image" in ian
    assert "generate_image" in ian
    assert "16:9" in ian
    assert "不假装" in ian or "降级" in ian
    assert "MCP-图像能力" in ian

    gbro = (SKILLS / "gbro-cover-design" / "SKILL.md").read_text(encoding="utf-8")
    assert "mcp-image" in gbro
    assert "3:4" in gbro
    assert "提示词" in gbro
    assert "可选" in gbro
    assert "MCP-图像能力" in gbro

    setup = (SKILLS / "setup-knowledge-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "mcp-image" in setup
    assert "MCP-图像能力" in setup

    mcp_doc = ROOT / "docs" / "MCP-图像能力.md"
    assert mcp_doc.is_file()
    mcp_text = mcp_doc.read_text(encoding="utf-8")
    assert "ian-xiaohei" in mcp_text
    assert "gbro-cover" in mcp_text
    assert "密钥" in mcp_text


def test_thinking_forbid_domain_require_inbox():
    for name in THINKING:
        text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        assert "10_inbox" in text, name
        assert "20_领域" in text, name
        assert "不直写" in text or "禁止" in text, name


def test_eval_and_flow_doc_cover_companion_evoke():
    """行为评测与流程说明锁定唤起场景。"""
    eval_md = (ROOT / "tests" / "EVAL.md").read_text(encoding="utf-8")
    assert "C3. Companion 协作" in eval_md
    assert "grill" in eval_md.lower()
    assert "content-decomposer" in eval_md or "decomposer" in eval_md
    assert "90_export" in eval_md

    flow = ROOT / "docs" / "companion协作流程.md"
    assert flow.is_file(), "missing docs/companion协作流程.md"
    flow_text = flow.read_text(encoding="utf-8")
    for name in ALL_COMPANIONS:
        assert name in flow_text, name
    assert "唤起" in flow_text or "触发" in flow_text
    assert "10_inbox" in flow_text
    assert "90_export" in flow_text
    assert "存在性先于形态性" in flow_text
    assert "更新说明" in flow_text

    update_doc = ROOT / "docs" / "更新说明.md"
    assert update_doc.is_file()
    update_text = update_doc.read_text(encoding="utf-8")
    assert "npx skills@latest update" in update_text
    assert "setup-knowledge-skills" in update_text
    assert "帮我 grill 一下" in update_text


def test_no_emoji_in_companion_skill_md():
    """companion 主 SKILL.md 无人话 emoji（与仓库禁令一致）。"""
    from check_no_emoji import EMOJI_RE, BANNED_CHARS

    for name in ALL_COMPANIONS:
        text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        assert not EMOJI_RE.search(text), name
        for ch in BANNED_CHARS:
            assert ch not in text, f"{name} contains banned {ch!r}"


def test_install_glob_will_include_companions():
    """安装脚本默认 --skill '*'，companion 与核心一并装上后才可被唤起。"""
    script = (ROOT / "scripts" / "install_skills.sh").read_text(encoding="utf-8")
    assert "--skill '*'" in script or '--skill "*"' in script
    # 目录层：companion 确实在 skills/ 下，会被 * 扫到
    discovered = {p.name for p in vs.discover_skill_dirs(ROOT)}
    assert set(ALL_COMPANIONS) <= discovered
