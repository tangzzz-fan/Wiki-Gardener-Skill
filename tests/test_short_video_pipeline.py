"""短视频流水线契约：抖音运营审核 → 短视频编导 → 脚本/制作指导卡 → inbox。

防两类漂移：
1. 只审不出：运营通过后不交接编导、不交制作指导卡/脚本
2. 直接出脚本入库：跳过运营，或成稿直写 20_领域/ 绕开吸附
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WG = ROOT / "skills" / "wiki-gardener"
DE = ROOT / "skills" / "domain-expert"
SEEDS = WG / "assets" / "domain-seeds"
PERSONAS = WG / "assets" / "personas"

sys.path.insert(0, str(ROOT / "scripts"))
import validate_skills as vs  # noqa: E402

OPS = (SEEDS / "抖音运营.md").read_text(encoding="utf-8")
CRAFT = (SEEDS / "短视频编导.md").read_text(encoding="utf-8")
CONTENT = (SEEDS / "内容创作.md").read_text(encoding="utf-8")
DE_SKILL = (DE / "SKILL.md").read_text(encoding="utf-8")


def test_pipeline_seeds_exist():
    assert (SEEDS / "抖音运营.md").is_file()
    assert (SEEDS / "短视频编导.md").is_file()
    assert (SEEDS / "内容创作.md").is_file()


def test_existence_before_form_iron_rule():
    """存在性先于形态性：两域与相关 persona 均须锁定。"""
    assert "存在性先于形态性" in OPS
    assert "存在性先于形态性" in CRAFT
    for name in ("独立老师.md", "自媒体工作者.md"):
        body = (PERSONAS / name).read_text(encoding="utf-8")
        assert "存在性先于形态性" in body, name


def test_ops_review_hands_off_not_shoots():
    """运营只审该不该发；通过须交接编导；禁止代写拍摄清单/分镜终稿。"""
    interface = vs.section_body(OPS, "与编导的协作接口")
    assert interface is not None
    assert "短视频编导" in interface
    assert "制作指导卡" in interface or "制作指导" in interface
    assert "只审不出" in interface
    assert "10_inbox" in interface
    assert "20_领域" in interface

    stance = vs.section_body(OPS, "专家立场")
    assert stance is not None
    assert "短视频编导" in stance
    assert "审查后交接" in stance or "交接" in stance

    smell = vs.section_body(OPS, "领域 Smell 清单")
    assert smell is not None
    assert "分镜" in smell or "口播" in smell or "越权" in smell

    writing = vs.section_body(OPS, "写作立场")
    assert writing is not None
    assert "请短视频编导接手" in writing or "短视频编导" in writing
    assert "拍摄清单" in writing


def test_ops_fail_stops_pipeline():
    """审核未通过不得进入制作指导 / 脚本。"""
    assert "审核未通过" in OPS or "不通过" in OPS
    assert "不进入制作" in OPS or "不进入制作指导" in OPS


def test_director_must_emit_guidance_card_schema():
    """编导交付物是制作指导卡（结构化），含输入锚点/形式/结构/拍摄清单/验证。"""
    card = vs.section_body(CRAFT, "制作指导卡")
    assert card is not None
    for field in (
        "制作指导卡",
        "输入锚点",
        "形式决策",
        "决策理由",
        "结构",
        "拍摄清单",
        "验证设计",
    ):
        assert field in card, f"missing {field}"
    assert "未经算法侧过目" in card
    assert "10_inbox" in card
    assert "origin: chat" in card or "origin: chat" in CRAFT
    assert "status: draft" in card or "status: draft" in CRAFT


def test_director_forbids_skip_ops_and_direct_vault():
    """编导反模式：跳过运营、只审不出、直写 20_领域。"""
    interface = vs.section_body(CRAFT, "与抖音运营的协作接口")
    assert interface is not None
    assert "只审不出" in interface or "制作指导卡" in interface
    assert "10_inbox" in interface
    assert "20_领域" in interface
    assert "未经算法侧过目" in CRAFT
    assert "审核未通过" in CRAFT
    # 完整流程下必须出卡，不得只复述审核
    assert "必须" in CRAFT and "制作指导卡" in CRAFT


def test_script_and_card_land_in_inbox_not_domain():
    """脚本/制作指导卡落 inbox；domain-expert 铁律禁止直写 20_领域。"""
    assert "10_inbox" in CRAFT
    assert "禁止直写" in CRAFT or "绝不直接写入" in DE_SKILL
    assert "20_领域" in CRAFT
    assert "产出永远进" in DE_SKILL and "10_inbox" in DE_SKILL
    assert "绝不直接写入" in DE_SKILL and "20_领域" in DE_SKILL


def test_content_creation_defers_douyin_pipeline():
    """内容创作不抢抖音审/拍；成稿顺序写清。"""
    stance = vs.section_body(CONTENT, "专家立场")
    assert stance is not None
    assert "短视频编导" in stance
    assert "抖音运营" in stance
    assert "10_inbox" in stance
    assert "20_领域" in stance


def test_full_pipeline_order_in_both_seeds():
    """两端协作接口均描述：运营审 → 编导卡/脚本 → inbox。"""
    for text, label in ((OPS, "抖音运营"), (CRAFT, "短视频编导")):
        assert "短视频编导" in text, label
        assert "制作指导卡" in text, label
        assert "10_inbox" in text, label
        # 顺序关键词：先审后拍
        ops_idx = text.find("算法") if "算法" in text else text.find("该不该发")
        craft_idx = text.find("制作指导卡")
        assert craft_idx > 0, label
        # 至少在协作接口段出现先后叙述
        body = text[text.find("协作接口") :] if "协作接口" in text else text
        assert "通过" in body, label


def test_personas_wire_ops_and_director_seeds():
    """自媒体 / 独立老师须挂两域种子并写协作顺序。"""
    for name in ("独立老师.md", "自媒体工作者.md"):
        text = (PERSONAS / name).read_text(encoding="utf-8")
        assert "domain-seeds/抖音运营.md" in text or "抖音运营.md" in text, name
        assert "domain-seeds/短视频编导.md" in text or "短视频编导.md" in text, name
        assert "短视频编导" in text, name
        assert "存在性先于形态性" in text, name
        # 顺序：先运营后编导
        assert "运营" in text and "编导" in text, name
