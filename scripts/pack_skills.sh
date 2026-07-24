#!/usr/bin/env bash
# 将 skills/* 打包为 Claude Desktop 可用的 .skill（zip）。
# 日常分发推荐：npx skills add（见 README / install_skills.sh）。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

pack() {
  local name="$1"
  local src="skills/${name}"
  local out="${name}.skill"
  if [[ ! -d "$src" ]]; then
    echo "skip: missing ${src}" >&2
    return 0
  fi
  echo "→ 打包 ${src}/ → ${out}"
  rm -f "$out"
  # zip 内顶层目录名为 skill 名（Desktop / 部分导入器期望）
  (
    cd skills
    zip -r "../${out}" "$name" \
      -x "**/.DS_Store" \
      -x "**/__pycache__/**" \
      -x "**/*.pyc" \
      >/dev/null
  )
  unzip -l "$out" | tail -n +1 | head -n 20
  echo
}

# 发现 skills/*/SKILL.md
while IFS= read -r -d '' skill_md; do
  name="$(basename "$(dirname "$skill_md")")"
  pack "$name"
done < <(find skills -mindepth 2 -maxdepth 2 -name SKILL.md -print0 | sort -z)

echo "OK: pack complete"
ls -lh ./*.skill 2>/dev/null || true
