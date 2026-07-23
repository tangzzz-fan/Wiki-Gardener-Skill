#!/usr/bin/env bash
# 将 skill 目录打包为兼容 Claude Code / 部分 CLI 的 .skill（zip）文件。
# Cursor 也可直接从文件夹安装（推荐开源分发用目录 + git）。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

pack() {
  local name="$1"
  local out="${name}.skill"
  echo "→ 打包 ${name}/ → ${out}"
  rm -f "$out"
  # 排除 macOS 垃圾与测试产物
  zip -r "$out" "$name" \
    -x "**/.DS_Store" \
    -x "**/__pycache__/**" \
    -x "**/*.pyc" \
    >/dev/null
  unzip -l "$out" | tail -n +1 | head -n 20
  echo
}

pack wiki-gardener
pack domain-expert
echo "OK: pack complete"
ls -lh *.skill
