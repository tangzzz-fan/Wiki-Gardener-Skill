# skills/

本仓库对外分发的 Agent Skills 目录（[skills.sh](https://skills.sh) / `npx skills` 会扫描此处）。

### 核心

| 目录 | 用途 |
|---|---|
| `setup-knowledge-skills/` | 安装后一次性引导（先跑这个） |
| `wiki-gardener/` | 知识库园丁；详细用法见 `docs/使用说明与调优指南.md` |
| `domain-expert/` | 领域专家（执笔 / 审查）；详细用法见 `docs/使用说明与调优指南.md` |

### Companion（可选工具）

| 目录 | 类 | 用途 |
|---|---|---|
| `grill-me/` | 思考 | 成文前追问，把模糊想法收成共识提纲 |
| `topic-resonate/` | 思考 | 选题/文稿是否真击中受众 |
| `content-diagnose/` | 思考 | 选题通过后怎么做成好内容（诊断不代写） |
| `script-flow/` | 思考 | 口播/脚本逻辑延续与划走风险 |
| `content-decomposer/` | 思考 | 对标内容拆解 → 可进 `10_inbox/` |
| `frontend-slides/` | 呈现 | 脚本/文稿 → HTML 演示；导出到 `90_export/` |
| `ian-xiaohei-illustrations/` | 呈现 | 正文配图提示与策略 |
| `gbro-cover-design/` | 呈现 | 封面提示词（本地 `config.md` 不入库） |

思考类产物默认可进 `10_inbox/`；呈现类不直写 `20_领域/`。协作流程（唤起与落盘）：仓库根目录 [docs/companion协作流程.md](../docs/companion协作流程.md)。新增 companion：**在本目录下新建同级文件夹**（内含 `SKILL.md`），不要放回仓库根目录。

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y
# 然后在 Agent 里运行 setup-knowledge-skills（安装脚本默认会尝试拉起）
```
