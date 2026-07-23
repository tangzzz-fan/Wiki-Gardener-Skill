# Wiki Gardener × Domain Expert

一对互补的 [Agent Skills](https://agentskills.io)：把「Karpathy 风格 LLM wiki」从空库养到可审计的自生长知识库。

| Skill | 职责 | 不管什么 |
|---|---|---|
| **wiki-gardener** | 建库、吸附、去重、园艺审计、结构决策 | 单篇事实对不对、正文润色 |
| **domain-expert** | 以**用户指定领域**专家身份执笔 / 事实审查 | 该不该收、挂哪、重不重复 |

领域知识全部来自用户 vault 的 `00_系统/domains/`，**不绑定 iOS / IoT 或任何垂直行业**。仓库里的 BLE / MQTT 等内容只出现在 `tests/fixtures/`，供评测用。

协作顺序：**真实性先于结构性**——先 `domain-expert` 审查，再 `wiki-gardener` 吸附。

```
写/投 → 审查（对不对）→ 修订 → 吸附（该不该收、放哪）→ 挂载
```

中文详细用法与调优见：

- [wiki-gardener 使用说明与调优指南.md](./wiki-gardener%20使用说明与调优指南.md)
- [domain-expert 使用说明与调优指南.md](./domain-expert%20使用说明与调优指南.md)

仓库约定见 [AGENTS.md](./AGENTS.md) / [CLAUDE.md](./CLAUDE.md)（含：**禁止 emoji**）。

## 安装

### 方式 A：目录安装（推荐，最稳）

```bash
cp -R wiki-gardener domain-expert .cursor/skills/
# 或用户级：~/.cursor/skills/
# 亦兼容 .agents/skills/、~/.claude/skills/ 等
pip install -r requirements.txt   # 仅园艺去重需要
```

### 方式 B：Git submodule（团队项目）

把本仓作为 submodule 挂进业务仓库的 `.cursor/skills/` 或旁路目录再 symlink，Agent 从本地标准路径发现 skill，升级可 `git submodule update`。

### 方式 C：`.skill` 包

```bash
./scripts/pack_skills.sh
```

### 方式 D：Cursor「Remote Rule (GitHub)」——可用，但有坑

Cursor 文档支持从 GitHub 仓库导入。**理论上**根目录放 `wiki-gardener/`、`domain-expert/`（各含 `SKILL.md`）即可被发现。实务上请注意：

| 点 | 说明 |
|---|---|
| 导入 ≠ 一定进 Agent 上下文 | 社区反馈：Remote 导入后 UI 可能列出 skill，但模型上下文未可靠挂载（曾为已知问题；Nightly 有修复，Stable 以你当前版本为准） |
| Rules vs Skills | 「Remote Rule」入口名字偏 Rules；Skills 发现路径与 Rules 不完全同一套，远程场景更容易踩空 |
| 推荐兜底 | 对最终用户文档写清：优先 `cp` / submodule 到 `.cursor/skills/`；Remote 作可选捷径 |
| 本仓布局 | 根目录直接是两个 skill 文件夹，**符合**「仓库即 skill 源」；勿再包一层无 `SKILL.md` 的空壳 |

结论：**开源分发以「clone + 拷进 `.cursor/skills/`」为主路径**；Remote GitHub 作为便利选项写进 README，但不把它当成唯一安装保证。

## 快速验证

1. 「帮我初始化一个知识库」→ `wiki-gardener`
2. 「以 \<你的领域\> 专家身份审一篇草稿」→ `domain-expert`

## 测试与 CI

| 层 | 做什么 | 本地 / CI |
|---|---|---|
| **L0** | frontmatter、断链、行数 | `python3 scripts/validate_skills.py` |
| **L0b** | skill 包禁 emoji | `python3 scripts/check_no_emoji.py` |
| **L1** | `dup_scan` + 访谈人设黄金宪章指纹 | `python3 -m pytest -v` |
| **L2** | 固定提示词行为评测（含 A1-S 四人设风格） | [tests/EVAL.md](./tests/EVAL.md) |

```bash
pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 scripts/check_no_emoji.py
python3 -m pytest -v
```

GitHub Actions：`.github/workflows/ci.yml` 跑 L0 + L0b + L1 + 打包冒烟。L2 需在装好 skill 的 Agent 里对新会话勾选 EVAL（至少 A2 / A4 / B1 / C1）；`workflow_dispatch` 会打印提醒。

## 仓库结构

```
├── wiki-gardener/
├── domain-expert/
├── AGENTS.md / CLAUDE.md
├── scripts/           # validate / pack / check_no_emoji
├── tests/
│   ├── fixtures/sample-vault/   # 示例域，非产品限定
│   └── EVAL.md
└── .github/workflows/ci.yml
```

Vault 内用户资产（宪章、决策日志、域档案）不属于 skill 包；升级 skill 时不要覆盖用户 vault。

## License

MIT
