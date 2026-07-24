# Wiki Gardener × Domain Expert

用 AI 帮你**养一个会自己整理的笔记库**（Markdown 文件夹）。

你负责往里丢想法和资料；AI 负责问清你的品味、去重、挂索引、定期体检。  
不绑死某个行业——老师、工程师、自媒体都能用同一套，靠初始化时选画像 + 你的确认。

| 能力包 | 它帮你做什么 | 它不管什么 |
|---|---|---|
| **setup-knowledge-skills** | 装完后的一次性引导（选 vault、指路） | 定北极星、写正文 |
| **wiki-gardener**（园丁） | 建库、收纳、去重、体检 | 单篇事实对不对、帮你改文笔 |
| **domain-expert**（领域专家） | 按你指定的领域审稿 / 执笔 | 该不该收进库、放哪一格 |

协作习惯：**先审对不对，再决定收不收。**  
更细的用法：[园丁说明](./skills/wiki-gardener/docs/使用说明与调优指南.md) · [专家说明](./skills/domain-expert/docs/使用说明与调优指南.md)  
**已有乱库怎么接入**：[已有知识库接入](./docs/已有知识库接入.md)  
**克隆后按自己经验改**：[自定义与调教指南](./docs/自定义与调教指南.md)

---

## 推荐安装（短命令，对齐 Matt Pocock / skills.sh）

前提：本机有 **Node.js**（能跑 `npx`）。

### 一键装全部 + 拉起 setup

```bash
./scripts/install_skills.sh
```

等价于：全局安装本仓库 **全部** skill，并尝试启动 `setup-knowledge-skills`。

只想手写一行（装全部）：

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y --skill '*'
```

装完后若未自动进入引导，在 Agent 里说：

```text
运行 setup-knowledge-skills
```

或：「刚装完知识库技能，带我开始」。

### 以后怎么更新

作者 push 到 GitHub 后：

```bash
npx skills@latest update -g -y
```

不要写仓库名。Vault 里的笔记 / 宪章 **不会**被覆盖。

### 只装某几个（可选）

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill \
  --skill setup-knowledge-skills --skill wiki-gardener --skill domain-expert \
  -g -y
```

以后在 `skills/` 下新增 companion（如内容运营类）后，**同一条** `install_skills.sh` / `add … -g -y`（全量）即可带上新包，不必改用户肌肉记忆。

---

## 你还需要准备什么

1. 支持 Agent Skills 的环境（Claude Code / Codex / Cursor / WorkBuddy 等；Desktop 见备用）  
2. Node.js（仅安装 / 更新时需要）  
3. 一个空文件夹当 **vault**（可用 Obsidian，不是必须）——setup 会帮你确认路径

---

## 装好后怎么用

1. 跑完 **setup-knowledge-skills**（选定 vault）  
2. 对 vault 说：**「帮我初始化一个知识库」**（wiki-gardener）  
3. 审稿：**「以 xx 专家的身份，审一下这篇草稿」**（domain-expert）  

日常：材料进 `10_inbox/`，再说「整理一下 inbox」。

---

## 其他安装方式（备用）

### Claude Desktop / claude.ai

```bash
git clone https://github.com/tangzzz-fan/Wiki-Gardener-Skill.git
cd Wiki-Gardener-Skill
./scripts/pack_skills.sh
```

上传生成的 `*.skill`（含 setup / 园丁 / 专家）。Desktop 读账号内 Skills，不是 `~/.claude/skills/`。

### 手动拷贝

```bash
git clone https://github.com/tangzzz-fan/Wiki-Gardener-Skill.git
cd Wiki-Gardener-Skill
cp -R skills/wiki-gardener skills/domain-expert skills/setup-knowledge-skills ~/.claude/skills/
```

手拷没有 `skills update`；要更新请改走 `npx skills add`，或 `git pull` 后重拷。

---

## 装不上 / 没反应时

| 现象 | 先查什么 |
|---|---|
| `npx` 不可用 | 装 Node，或用手拷 / Desktop |
| 装完不知道下一步 | 说「运行 setup-knowledge-skills」 |
| AI 不像园丁 | `npx skills list -g` 是否有 `wiki-gardener` |
| `update` 找不到 | 是否曾用 `npx skills add` 安装 |
| 去重缺库 | `pip install -r requirements.txt`（仅 dup_scan） |

---

## 给想改包 / 跑测试的人

按自己经验自定义（域档案、防坑论、画像）：[docs/自定义与调教指南.md](./docs/自定义与调教指南.md)。  
给 Agent 的仓库约定：[AGENTS.md](./AGENTS.md)。

```bash
pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 scripts/check_no_emoji.py
python3 -m pytest -v
```

```
├── skills/                       # 对外分发的 skill
├── docs/自定义与调教指南.md       # 克隆后如何按个人经验改
├── scripts/install_skills.sh
└── tests/
```

新增 skill：在 `skills/<name>/` 放 `SKILL.md` 即可被 `npx skills` 发现；校验脚本会自动扫到（核心三件套仍为必选）。

## License

MIT
