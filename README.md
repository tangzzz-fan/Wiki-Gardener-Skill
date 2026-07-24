# Wiki Gardener × Domain Expert

用 AI 帮你**养一个会自己整理的笔记库**（Markdown 文件夹）。

你负责往里丢想法和资料；AI 负责问清你的品味、去重、挂索引、定期体检。  
不绑死某个行业——老师、工程师、自媒体都能用同一套，靠初始化时选画像 + 你的确认。

| 能力包 | 它帮你做什么 | 它不管什么 |
|---|---|---|
| **wiki-gardener**（园丁） | 建库、收纳、去重、体检 | 单篇事实对不对、帮你改文笔 |
| **domain-expert**（领域专家） | 按你指定的领域审稿 / 执笔 | 该不该收进库、放哪一格 |

协作习惯：**先审对不对，再决定收不收。**

更细的用法：[园丁说明](./wiki-gardener%20使用说明与调优指南.md) · [专家说明](./domain-expert%20使用说明与调优指南.md)

---

## 你只需要准备三样东西

1. 一台能跑 **Claude Code / Codex / Claude Desktop（claude.ai）/ WorkBuddy / Cursor** 的环境  
2. 本仓库（下载 ZIP，或 `git clone`）  
3. 一个空文件夹当笔记库（下文叫 **vault**；推荐用 Obsidian 打开，不是必须）

安装的本质就一句话：**把 `wiki-gardener` 和 `domain-expert` 两个文件夹，拷进该工具会扫描的「技能目录」。**

---

## 三分钟装好（按你的工具选）

先进入本仓库根目录（能看到 `wiki-gardener/`、`domain-expert/` 两个文件夹）。

### Claude Code

拷到用户级技能目录（所有项目都能用）：

```bash
mkdir -p ~/.claude/skills
cp -R wiki-gardener domain-expert ~/.claude/skills/
```

只想给当前项目用：拷到项目里的 `.claude/skills/`。  
装好后开新对话，可直接说话触发；也可试 `/wiki-gardener`（以目录名为准）。

### Codex（OpenAI）

```bash
mkdir -p ~/.agents/skills
cp -R wiki-gardener domain-expert ~/.agents/skills/
```

项目内共享则拷到仓库的 `.agents/skills/`。  
重启 Codex；在对话里用自然语言触发，或按 Codex 文档用 `$` / `/skills` 查看已装技能。

### Claude Desktop / claude.ai

适合不太碰终端的人：

1. 在本仓库运行一次打包（或请会终端的朋友帮你跑）：

   ```bash
   ./scripts/pack_skills.sh
   ```

   会得到 `wiki-gardener.skill`、`domain-expert.skill`（本质是 ZIP）。

2. 打开 **Claude / Claude Desktop → Settings（设置）→ Features / Capabilities（功能）**  
3. 在 **Skills** 处上传这两个文件（或把 `.skill` 改名为 `.zip` 再上传，视界面提示而定）  
4. 需开通带**代码执行 / 文件能力**的方案（Pro / Max 等；以 Anthropic 当前说明为准）

Desktop 的 Cowork / 云会话读的是账号里启用的 Skills，不是你电脑上的 `~/.claude/skills/`——请在设置里确认已启用。

### WorkBuddy

常见约定（与 Claude Code 类似）：

```bash
mkdir -p ~/.workbuddy/skills
cp -R wiki-gardener domain-expert ~/.workbuddy/skills/
```

项目级：`.workbuddy/skills/`。  
若你用的发行版扫描的是别的路径，在设置里搜「Skills」或按官方文档把这两个文件夹放进技能目录即可——**文件夹名保持 `wiki-gardener`、`domain-expert`，且内含 `SKILL.md`。**

### Cursor（可选）

```bash
mkdir -p ~/.cursor/skills
cp -R wiki-gardener domain-expert ~/.cursor/skills/
```

或项目内 `.cursor/skills/`。

---

## 装好后怎么用（背两句话就够）

在 Agent 里打开（或指定）你的 **vault 文件夹**，然后说：

1. **建库**：「帮我初始化一个知识库」  
   - 会先问你是哪类人（独立老师 / 工程师 / 自媒体…，或「都不像」）  
   - 预填内容给你改，**北极星必须你亲口确认**  
2. **审稿**：「以 xx 专家的身份，审一下这篇草稿」  
   - 需已有对应域档案（初始化时选过域，或后来建过）

日常：把材料丢进 vault 的 `10_inbox/`，再说「整理一下 inbox」。

---

## 装不上 / 没反应时

| 现象 | 先查什么 |
|---|---|
| AI 完全不像园丁 | 技能目录里是否真有 `…/skills/wiki-gardener/SKILL.md` |
| 只有一个 skill | 是否两个文件夹都拷了 |
| Claude Desktop 没有 Skills 入口 | 账号方案是否支持自定义 Skills / 代码执行 |
| 去重体检报错缺库 | 仅园艺脚本需要：`pip install -r requirements.txt`（日常建库、访谈可不装） |

路径因系统略有不同：macOS / Linux 用上面的 `~`；Windows 一般在用户目录下对应 `.claude`、`.agents`、`.workbuddy`、`.cursor` 文件夹（可用文件管理器显示隐藏项后粘贴）。

---

## 给想改包 / 跑测试的人

开源约定见 [AGENTS.md](./AGENTS.md)。本地校验：

```bash
pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 scripts/check_no_emoji.py
python3 -m pytest -v
```

行为评测清单：[tests/EVAL.md](./tests/EVAL.md)。  
Remote GitHub 导入（Cursor 等）可用但不稳定，**仍推荐拷贝文件夹**为主路径。

```
├── wiki-gardener/     # 园丁 skill
├── domain-expert/     # 领域专家 skill
├── scripts/           # 校验、打包
└── tests/             # 自动化 + 人工评测
```

Vault 里的宪章、决策日志、域档案属于**你的数据**；升级 skill 时不要覆盖 vault。

## License

MIT
