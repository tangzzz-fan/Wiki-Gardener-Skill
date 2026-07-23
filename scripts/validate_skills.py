#!/usr/bin/env python3
"""
validate_skills.py — 开源前结构校验

检查每个 skill 目录：
  - SKILL.md 存在且 YAML frontmatter 合法
  - name 与文件夹名一致、符合 kebab-case
  - description 非空且 ≤ 1024 字符
  - SKILL.md 正文 < 500 行
  - 引用的 references/scripts/assets 路径存在
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

SKILL_DIRS = ("wiki-gardener", "domain-expert")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(
    r"`((?:references|assets|scripts)/[A-Za-z0-9_./\-]+)`"
)


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


def check_dup_scan_import(root: Path) -> list[str]:
    script = root / "wiki-gardener" / "scripts" / "dup_scan.py"
    if not script.is_file():
        return ["wiki-gardener: 缺少 scripts/dup_scan.py"]
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
    for name in SKILL_DIRS:
        skill_dir = root / name
        if not skill_dir.is_dir():
            all_errors.append(f"缺少 skill 目录: {name}")
            continue
        all_errors.extend(check_skill(skill_dir))

    all_errors.extend(check_dup_scan_import(root))

    if all_errors:
        print("FAIL: structure validation")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print("OK: structure validation passed")
    for name in SKILL_DIRS:
        md = (root / name / "SKILL.md").read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(md)
        print(f"  - {name}: description {len(meta['description'])} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
