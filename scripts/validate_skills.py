#!/usr/bin/env python3
"""
validate_skills.py — 开源前结构校验

检查每个 skill 目录：
  - SKILL.md 存在且 YAML frontmatter 合法
  - name 与文件夹名一致、符合 kebab-case
  - description 非空且 ≤ 1024 字符
  - SKILL.md 正文 < 500 行
  - 引用的 references/scripts/assets 路径存在
  - wiki-gardener 的 personas / domain-seeds 资产 schema 与交叉引用
  - wiki-gardener 的 dup_scan.py 可导入

用法：
    python3 scripts/validate_skills.py
    python3 scripts/validate_skills.py --root .
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILLS_CONTAINER = "skills"
# 至少要有的包（新增 companion 不必写进此元组，放进 skills/ 即可被发现）
REQUIRED_SKILLS = ("wiki-gardener", "domain-expert", "setup-knowledge-skills")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(
    r"`((?:references|assets|scripts)/[A-Za-z0-9_./\-]+)`"
)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
DOMAIN_SEED_REF_RE = re.compile(r"`domain-seeds/([^`]+?\.md)`")
DOMAINS_REF_RE = re.compile(r"`domains/([^`]+?\.md)`")
TITLE_RE = re.compile(r"^#\s+域档案：(.+?)\s*$", re.MULTILINE)

PERSONA_SECTION_PREFIXES = (
    "北极星候选",
    "收录标准种子",
    "推荐初始域",
    "推荐 Atlas 分区",
    "笔记类型模板",
    "访谈变体",
    "度量权重",
    "专家顾问团",
)
PERSONA_CONFIRM_MARKERS = ("用户确认", "亲口确认")
PERSONA_MECHANISM_FORBIDDEN = ("吸附流程", "dup_scan", "放权", "L3")

DOMAIN_SEED_SECTIONS = (
    "专家立场",
    "局部宪章",
    "术语表",
    "时效性锚点",
    "领域 Smell 清单",
    "写作立场",
    "常见误区",
    "执笔与审查协议",
)
ROT_MARKERS = ("腐烂", "更新")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        raise ValueError("SKILL.md 必须以 YAML frontmatter（---）开头")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter 未正确闭合")
    meta: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        # 跳过嵌套映射缩进行（如 metadata.version），只收顶层字段
        if line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip("\"'")
    return meta, parts[2]


def h2_titles(text: str) -> list[str]:
    return [m.group(1).strip() for m in H2_RE.finditer(text)]


def has_section_prefix(titles: list[str], prefix: str) -> bool:
    return any(t == prefix or t.startswith(prefix) for t in titles)


def section_body(text: str, prefix: str) -> str | None:
    """Return body under the first H2 whose title starts with prefix."""
    matches = list(H2_RE.finditer(text))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        if title == prefix or title.startswith(prefix):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            return text[start:end]
    return None


def check_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir.name}: 缺少 SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    try:
        meta, body = parse_frontmatter(text)
    except ValueError as e:
        return [f"{skill_dir.name}: {e}"]

    name = meta.get("name", "")
    desc = meta.get("description", "")

    if not name:
        errors.append(f"{skill_dir.name}: 缺少 name")
    elif name != skill_dir.name:
        errors.append(
            f"{skill_dir.name}: name='{name}' 与文件夹名不一致"
        )
    elif not NAME_RE.match(name):
        errors.append(f"{skill_dir.name}: name 不符合 kebab-case")

    if not desc:
        errors.append(f"{skill_dir.name}: description 为空")
    elif len(desc) > 1024:
        errors.append(
            f"{skill_dir.name}: description 超长（{len(desc)} > 1024）"
        )

    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    if line_count > 500:
        errors.append(
            f"{skill_dir.name}: SKILL.md 共 {line_count} 行，超过 500 行建议"
        )

    for ref in set(REF_RE.findall(text)):
        # 忽略带参数的伪路径，如 scripts/dup_scan.py <vault路径>
        clean = ref.split()[0]
        target = skill_dir / clean
        if not target.exists():
            errors.append(f"{skill_dir.name}: 引用缺失 → {clean}")

    # references / assets 内部相对链接（一层）
    for md in skill_dir.rglob("*.md"):
        rel = md.relative_to(skill_dir)
        content = md.read_text(encoding="utf-8")
        for m in re.findall(r"\]\(([^)#]+\.md)\)", content):
            if m.startswith(("http://", "https://", "#")):
                continue
            linked = (md.parent / m).resolve()
            try:
                linked.relative_to(skill_dir.resolve())
            except ValueError:
                errors.append(f"{rel}: 链接跳出 skill 目录 → {m}")
                continue
            if not linked.is_file():
                errors.append(f"{rel}: 断链 → {m}")

    return errors


def check_persona_file(path: Path, seeds_dir: Path) -> list[str]:
    """Validate one assets/personas/*.md pack. Exportable for tests."""
    errors: list[str] = []
    rel = path.name
    text = path.read_text(encoding="utf-8")
    titles = h2_titles(text)

    for prefix in PERSONA_SECTION_PREFIXES:
        if not has_section_prefix(titles, prefix):
            errors.append(f"personas/{rel}: 缺少章节「{prefix}」")

    if not any(m in text for m in PERSONA_CONFIRM_MARKERS):
        errors.append(
            f"personas/{rel}: 须含确认权红线表述"
            f"（{' / '.join(PERSONA_CONFIRM_MARKERS)}）"
        )

    for banned in PERSONA_MECHANISM_FORBIDDEN:
        if banned in text:
            errors.append(
                f"personas/{rel}: persona 不得写机制层补丁 → 发现「{banned}」"
            )

    for seed_name in DOMAIN_SEED_REF_RE.findall(text):
        target = seeds_dir / seed_name
        if not target.is_file():
            errors.append(
                f"personas/{rel}: 引用缺失 domain-seeds/{seed_name}"
            )

    for domain_name in DOMAINS_REF_RE.findall(text):
        seed = seeds_dir / domain_name
        if not seed.is_file():
            errors.append(
                f"personas/{rel}: 顾问团 domains/{domain_name} "
                f"无对应 domain-seeds/{domain_name}"
            )

    return errors


def check_domain_seed_file(path: Path) -> list[str]:
    """Validate one assets/domain-seeds/*.md pack. Exportable for tests."""
    errors: list[str] = []
    rel = path.name
    stem = path.stem
    text = path.read_text(encoding="utf-8")
    titles = h2_titles(text)

    for section in DOMAIN_SEED_SECTIONS:
        if not has_section_prefix(titles, section):
            errors.append(f"domain-seeds/{rel}: 缺少章节「{section}」")

    title_m = TITLE_RE.search(text)
    if not title_m:
        errors.append(f"domain-seeds/{rel}: 缺少「# 域档案：…」标题")
    else:
        title_name = title_m.group(1).strip()
        if title_name != stem:
            errors.append(
                f"domain-seeds/{rel}: 标题「{title_name}」与文件名 stem「{stem}」不一致"
            )

    stance = section_body(text, "专家立场")
    if stance is not None:
        if "身份" not in stance:
            errors.append(f"domain-seeds/{rel}: 专家立场须含「身份」")
        if "判断偏好" not in stance:
            errors.append(f"domain-seeds/{rel}: 专家立场须含「判断偏好」")

    protocol = section_body(text, "执笔与审查协议")
    if protocol is not None:
        for marker in ("开场必收", "执笔交付物", "审查必查", "10_inbox"):
            if marker not in protocol:
                errors.append(
                    f"domain-seeds/{rel}: 执笔与审查协议须含「{marker}」"
                )

    anchor = section_body(text, "时效性锚点")
    if anchor is not None and not any(m in anchor for m in ROT_MARKERS):
        errors.append(
            f"domain-seeds/{rel}: 时效性锚点须标注腐烂/更新频率提示"
        )

    return errors


def check_persona_and_domain_seeds(skill_dir: Path) -> list[str]:
    """Schema + cross-refs for wiki-gardener persona / domain-seed assets."""
    if skill_dir.name != "wiki-gardener":
        return []

    errors: list[str] = []
    personas_dir = skill_dir / "assets" / "personas"
    seeds_dir = skill_dir / "assets" / "domain-seeds"

    if not personas_dir.is_dir():
        return ["wiki-gardener: 缺少 assets/personas/"]
    if not seeds_dir.is_dir():
        return ["wiki-gardener: 缺少 assets/domain-seeds/"]

    persona_files = sorted(personas_dir.glob("*.md"))
    seed_files = sorted(seeds_dir.glob("*.md"))

    if not persona_files:
        errors.append("wiki-gardener: assets/personas/ 至少需要 1 个 persona")
    if not seed_files:
        errors.append("wiki-gardener: assets/domain-seeds/ 至少需要 1 个域种子")

    for path in persona_files:
        errors.extend(check_persona_file(path, seeds_dir))
    for path in seed_files:
        errors.extend(check_domain_seed_file(path))

    return errors


def discover_skill_dirs(root: Path) -> list[Path]:
    """Return skills/<name>/ directories that contain SKILL.md (one level)."""
    container = root / SKILLS_CONTAINER
    if not container.is_dir():
        return []
    found: list[Path] = []
    for p in sorted(container.iterdir()):
        if p.is_dir() and (p / "SKILL.md").is_file():
            found.append(p)
    return found


def check_dup_scan_import(root: Path) -> list[str]:
    script = root / SKILLS_CONTAINER / "wiki-gardener" / "scripts" / "dup_scan.py"
    if not script.is_file():
        return ["skills/wiki-gardener: 缺少 scripts/dup_scan.py"]
    # 语法检查，不要求本机已装 sklearn（那是运行时依赖）
    import py_compile

    try:
        py_compile.compile(str(script), doraise=True)
    except py_compile.PyCompileError as e:
        return [f"dup_scan.py 语法错误: {e}"]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="校验 skill 结构")
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="仓库根目录",
    )
    args = ap.parse_args()
    root: Path = args.root.resolve()

    all_errors: list[str] = []
    container = root / SKILLS_CONTAINER
    if not container.is_dir():
        all_errors.append(f"缺少 {SKILLS_CONTAINER}/ 目录")
        print("FAIL: structure validation")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    skill_dirs = discover_skill_dirs(root)
    names = {p.name for p in skill_dirs}
    for required in REQUIRED_SKILLS:
        if required not in names:
            all_errors.append(f"缺少 skill 目录: {SKILLS_CONTAINER}/{required}")

    for skill_dir in skill_dirs:
        all_errors.extend(check_skill(skill_dir))
        all_errors.extend(check_persona_and_domain_seeds(skill_dir))

    all_errors.extend(check_dup_scan_import(root))

    if all_errors:
        print("FAIL: structure validation")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print("OK: structure validation passed")
    for skill_dir in skill_dirs:
        md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(md)
        print(
            f"  - {skill_dir.name}: description {len(meta['description'])} chars"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
