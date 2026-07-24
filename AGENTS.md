# AGENTS.md

本仓库面向 Agent Skills 开源开发。所有在此仓库内工作的 Agent（含 Cursor、Claude Code 兼容工具）须遵守以下约定。

## 硬性约束

1. **禁止使用 emoji**  
   代码、Markdown、终端输出、人话卡片、审查报告、提交说明、PR 描述中均不得出现 emoji（含装饰性符号如勾叉表情变体）。用纯文本标签代替，例如 `[高优先]`、`[同意]`、`[警告]`。
2. **Skill 本体保持领域无关**  
   `wiki-gardener` / `domain-expert` / 同包 companion 不得写死某一垂直领域（如仅 iOS / IoT）。领域知识只存在于用户 vault 的 `00_系统/domains/`。文档与示例可用虚构域说明流程，但须标明「示例」。
3. **不擅自提交**  
   除非用户明确要求 commit / push，否则只改文件、不写 git 历史。
4. **禁止 Co-authored-by**  
   提交说明不得添加 `Co-authored-by`（含 Cursor / Agent 等）。作者仅保留实际 git author；amend / 新建 commit 均适用。
5. **改 skill 后跑校验**  
   `python3 scripts/validate_skills.py` 与 `python3 -m pytest -v` 须通过；涉及人话输出格式时同步改 `tests/EVAL.md`。

## 仓库地图

| 路径 | 用途 |
|---|---|
| `skills/` | 对外分发的全部 skill（`npx skills` 扫描此处） |
| `skills/setup-knowledge-skills/` | 安装后一次性引导 |
| `skills/wiki-gardener/` | 知识库园丁（`docs/` 下放使用与调优指南） |
| `skills/domain-expert/` | 领域专家（`docs/` 下放使用与调优指南） |
| `tests/fixtures/sample-vault/` | 评测用示例库（内含示例域，非产品限定） |
| `tests/fixtures/interview-personas/` | 访谈风格人设 + 黄金宪章 |
| `tests/EVAL.md` | L2 行为评测清单 |
| `docs/自定义与调教指南.md` | 克隆后按个人经验改域档案 / 种子 / 流程 |
| `scripts/` | `install_skills.sh`、校验、打包、禁 emoji、宪章风格评分 |

用户安装 / 更新：见根目录 README。短命令 `./scripts/install_skills.sh`（内部 `npx skills add … --skill '*'` + 尝试拉起 setup）。Desktop 用 `pack_skills.sh`。

新增 companion：在 `skills/<name>/` 新建包即可，勿放回仓库根目录。

## 输出风格

- 对用户：直接、简洁；少用加粗堆砌。
- 对人话卡片 / 审查摘要：纯文本结构，无 emoji 前缀。
- 机器契约（JSON 诊断单 / 审查报告）保持 schema 稳定。
