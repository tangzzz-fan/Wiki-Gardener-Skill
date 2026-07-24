#!/usr/bin/env python3
"""
check_no_emoji.py — 禁止 skill 包与关键文档使用 emoji

扫描范围：两个 skill 目录、AGENTS.md、CLAUDE.md、README.md、scripts/。
tests/fixtures 与中文使用说明允许历史示例，但默认也扫；用 --strict 全仓扫描。

用法：
    python3 scripts/check_no_emoji.py
    python3 scripts/check_no_emoji.py --strict
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 覆盖常见 emoji 与杂项符号表情（不含中文标点）
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # misc symbols & pictographs, supplemental
    "\U0001FA00-\U0001FAFF"  # extended-A
    "\U00002700-\U000027BF"  # dingbats
    "\U00002600-\U000026FF"  # misc symbols
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0000200D"  # ZWJ
    "\U0000231A-\U0000231B"
    "\U000023E9-\U000023F3"
    "\U000023F8-\U000023FA"
    "\U000025AA-\U000025AB"
    "\U000025B6"
    "\U000025C0"
    "\U000025FB-\U000025FE"
    "\U00002B05-\U00002B07"
    "\U00002B1B-\U00002B1C"
    "\U00002B50"
    "\U00002B55"
    "\U00002934-\U00002935"
    "\U00002194-\U00002199"
    "]+",
    flags=re.UNICODE,
)

# 常见「伪 emoji」文本符号（用码点定义，避免本文件自检误报）
BANNED_CHARS = {
    chr(c)
    for c in (
        0x1F389,  # party popper
        0x1F50D,  # magnifying glass
        0x1F331,  # seedling
        0x1F4C4,  # page
        0x270D,   # writing hand (base)
        0x1F4DD,  # memo
        0x1F534,  # red circle
        0x1F7E1,  # yellow circle
        0x1F7E2,  # green circle
        0x2705,   # check mark button
        0x274C,   # cross mark
        0x1F4AC,  # speech
        0x26A0,   # warning
    )
}

DEFAULT_GLOBS = [
    "skills/**/*",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs/**/*",
    ".github/**/*",
    "scripts/validate_skills.py",
    "scripts/pack_skills.sh",
    "scripts/install_skills.sh",
    "scripts/check_no_emoji.py",
]

SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".skill"}
SKIP_NAMES = {".DS_Store", ".git"}


def iter_files(root: Path, strict: bool) -> list[Path]:
    files: list[Path] = []
    if strict:
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SKIP_NAMES or part == ".git" for part in p.parts):
                continue
            if p.suffix.lower() in SKIP_SUFFIXES:
                continue
            if "pytest_cache" in p.parts or "__pycache__" in p.parts:
                continue
            files.append(p)
        return files

    for pattern in DEFAULT_GLOBS:
        for p in root.glob(pattern):
            if p.is_file() and p.suffix.lower() not in SKIP_SUFFIXES:
                files.append(p)
    return sorted(set(files))


def find_hits(text: str) -> list[str]:
    hits: list[str] = []
    for m in EMOJI_RE.finditer(text):
        hits.append(m.group())
    for ch in BANNED_CHARS:
        if ch in text:
            hits.append(ch)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument(
        "--strict",
        action="store_true",
        help="扫描全仓（含使用说明与 tests）",
    )
    args = ap.parse_args()
    root = args.root.resolve()

    bad: list[str] = []
    for path in iter_files(root, args.strict):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        hits = find_hits(text)
        if hits:
            uniq = " ".join(dict.fromkeys(hits))
            bad.append(f"{path.relative_to(root)}: {uniq}")

    if bad:
        print("Found emoji / banned symbols:")
        for line in bad:
            print(f"  - {line}")
        return 1

    scope = "strict (whole repo)" if args.strict else "skill packages + core docs"
    print(f"OK: no emoji ({scope})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
