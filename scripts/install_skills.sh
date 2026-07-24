#!/usr/bin/env bash
# 一键安装本仓库全部知识库 skill（短命令，对齐 Matt Pocock / skills.sh）。
# 默认：全局安装全部 skill，并尝试拉起 setup-knowledge-skills。
#
# 用法：
#   ./scripts/install_skills.sh              # -g，装全部，随后 setup
#   ./scripts/install_skills.sh --no-setup   # 只装不引导
#   ./scripts/install_skills.sh -a cursor    # 额外参数原样传给 skills add
#   REPO=./ ./scripts/install_skills.sh      # 从本地路径装（开发自测）
#
# 等价手写：
#   npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y --skill '*'
#   然后在 Agent 里运行 /setup-knowledge-skills
set -euo pipefail

REPO="${REPO:-tangzzz-fan/Wiki-Gardener-Skill}"
DO_SETUP=1
ADD_ARGS=()

for arg in "$@"; do
  case "$arg" in
    --no-setup) DO_SETUP=0 ;;
    *) ADD_ARGS+=("$arg") ;;
  esac
done

# 若用户没指定 -g/-p，默认全局（个人知识库场景）
has_scope=0
for arg in "${ADD_ARGS[@]+"${ADD_ARGS[@]}"}"; do
  case "$arg" in
    -g|--global|-p|--project) has_scope=1 ;;
  esac
done
if [[ "$has_scope" -eq 0 ]]; then
  ADD_ARGS=(-g "${ADD_ARGS[@]+"${ADD_ARGS[@]}"}")
fi

echo "→ Installing all skills from ${REPO}"
npx --yes skills@latest add "$REPO" --skill '*' -y "${ADD_ARGS[@]}"

if [[ "$DO_SETUP" -eq 0 ]]; then
  echo "OK: installed (setup skipped). Run setup-knowledge-skills in your agent when ready."
  exit 0
fi

echo
echo "→ Launching setup-knowledge-skills (post-install guide)"
echo "  （若当前环境无法交互拉起 Agent，请新开对话并说：运行 setup-knowledge-skills）"
echo

# skills use：生成引导 prompt；若检测到 Agent 则尝试交互启动
set +e
npx --yes skills@latest use "${REPO}@setup-knowledge-skills" 2>/dev/null
USE_STATUS=$?
set -e

if [[ "$USE_STATUS" -ne 0 ]]; then
  echo "[警告] 未能自动拉起 setup。请在 Agent 中手动说："
  echo "  运行 setup-knowledge-skills / 刚装完知识库技能，带我开始"
fi

echo "OK: install finished"
