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
  echo "→ packing ${src}/ → ${out}"
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
  # 勿用 head：pipefail 下大包 listing 会被 SIGPIPE(141) 弄挂（Linux CI）。
  # sed 会读完 stdin，只打印前 20 行。
  unzip -l "$out" | sed -n '1,20p'
  echo
}

pack_all() {
  while IFS= read -r -d '' skill_md; do
    name="$(basename "$(dirname "$skill_md")")"
    pack "$name"
  done < <(find skills -mindepth 2 -maxdepth 2 -name SKILL.md -print0 | sort -z)
}

# 用法：
#   ./scripts/pack_skills.sh              # 打包 skills/* 全部
#   ./scripts/pack_skills.sh wiki-gardener domain-expert setup-knowledge-skills
if [[ $# -gt 0 ]]; then
  for name in "$@"; do
    pack "$name"
  done
else
  pack_all
fi

echo "OK: pack complete"
ls -lh ./*.skill 2>/dev/null || true
