# Wiki Gardener × Domain Expert

用 AI 帮你**养一个会自己整理的笔记库**（Markdown 文件夹）。

你负责往里丢想法和资料；AI 负责问清你的品味、去重、挂索引、定期体检。  
不绑死某个行业——老师、工程师、自媒体都能用同一套，靠初始化时选画像 + 你的确认。

| 能力包 | 它帮你做什么 | 它不管什么 |
|---|---|---|
| **setup-knowledge-skills** | 装完后的一次性引导（选 vault、指路） | 定北极星、写正文 |
| **wiki-gardener**（园丁） | 建库、收纳、去重、体检 | 单篇事实对不对、帮你改文笔 |
| **domain-expert**（领域专家） | 按你指定的领域审稿 / 执笔 | 该不该收进库、放哪一格 |
| **Companion**（可选） | 内容思考（选题/拆解/脚本）与呈现导出（演示/配图/封面） | 替代园丁吸附或专家审稿 |

协作习惯：**先审对不对，再决定收不收。** 呈现类默认落到 vault 的 `90_export/`，不直写 `20_领域/`。  
更细的用法：[园丁说明](./skills/wiki-gardener/docs/使用说明与调优指南.md) · [专家说明](./skills/domain-expert/docs/使用说明与调优指南.md) · [skills 目录说明](./skills/README.md) · [Companion 协作流程](./docs/companion协作流程.md)  
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

不要写仓库名。Vault 里的笔记 / 宪章 **不会**被覆盖；但 `00_系统/技能包说明.md` **也不会自动刷新**。

更新后请在 Agent 说：

```text
运行 setup-knowledge-skills
```

或「我刚更新了知识库技能，刷新一下技能包说明」——才会把 **companion / grill-me 选题提示** 写进你的 vault。

详见：[更新说明（已装用户）](./docs/更新说明.md) · [Companion 协作流程](./docs/companion协作流程.md)

### 只装某几个（可选）

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill \
  --skill setup-knowledge-skills --skill wiki-gardener --skill domain-expert \
  -g -y
```

只要思考 companion（示例）：

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y \
  --skill grill-me --skill topic-resonate --skill content-diagnose \
  --skill script-flow --skill content-decomposer
```

setup 引导会**探测本机已装哪些 companion**，未装的可推荐上述选装命令，不强迫。全量装齐后，**同一条** `install_skills.sh` / `add … --skill '*'` 即可。

---

## 你还需要准备什么

1. 支持 Agent Skills 的环境（Claude Code / Codex / Cursor / WorkBuddy 等；Desktop 见备用）  
2. Node.js（仅安装 / 更新时需要）  
3. 一个文件夹当 **vault**（可用 Obsidian，不是必须）——新建空目录或接入已有 Markdown 库都可以，建议不要直接使用本代码仓
4. Python 3（仅运行知识库去重体检时需要）；首次使用前执行 `pip install -r requirements.txt`

---

## 装好后怎么用

先运行 **setup-knowledge-skills** 选定 vault，再按你的情况复制一句：

**新库：**

> 帮我初始化一个知识库

**已有 Markdown / Obsidian 库：**

> 当前文件夹是我已有的笔记库（非空）。请按 wiki-gardener「已有知识库接入」初始化：保留旧文件，先建系统骨架与宪章；旧文稍后分批放进 inbox。

日常只需要记住这些：

| 想做什么 | 直接说 |
|---|---|
| 想法很糊 | 「帮我 grill 一下这个想法」 |
| 写成或审查一篇笔记 | 「以 \<领域\> 专家身份写 / 审这篇」 |
| 收进知识库 | 「整理一下 inbox」 |
| 查重复、孤儿和过期内容 | 「给知识库做个体检」 |
| 做演示、配图或封面 | 「把这篇做成 HTML 演示 / 配图 / 封面」 |

完整流向：

```text
想清楚（可选 companion）
  → 专家成文 / 审查 → 按报告修订 → 10_inbox/
  → 园丁吸附 → 20_领域/
  → 演示 / 配图 / 封面 → 90_export/
```

核心三件套已经能建库、执笔、审查和吸附；companion 是按需增强，不是使用门槛。

---

## 其他安装方式（备用）

### Claude Desktop / claude.ai

```bash
git clone https://github.com/tangzzz-fan/Wiki-Gardener-Skill.git
cd Wiki-Gardener-Skill
./scripts/pack_skills.sh
```

上传生成的 `*.skill`。不带参数时会打包 `skills/` 下全部包；Desktop 读账号内 Skills，不是 `~/.claude/skills/`。

### 手动拷贝

```bash
git clone https://github.com/tangzzz-fan/Wiki-Gardener-Skill.git
cd Wiki-Gardener-Skill
cp -R skills/* ~/.claude/skills/
```

手拷没有 `skills update`；要更新请改走 `npx skills add`，或 `git pull` 后重拷。全量拷会带上 companion；若只要核心三件套，可只拷 `wiki-gardener`、`domain-expert`、`setup-knowledge-skills`。

---

## 装不上 / 没反应时

| 现象 | 先查什么 |
|---|---|
| `npx` 不可用 | 装 Node，或用手拷 / Desktop |
| 装完不知道下一步 | 说「运行 setup-knowledge-skills」 |
| AI 不像园丁 | `npx skills list -g` 是否有 `wiki-gardener` |
| `update` 找不到 | 是否曾用 `npx skills add` 安装 |
| 去重缺库 | `pip install -r requirements.txt`（仅 dup_scan） |
| companion 被标成未装 | 重跑 setup；它会探测常见 Agent Skills 安装目录 |

---

## 给想改包 / 跑测试的人

按自己经验自定义（域档案、防坑论、画像）：[docs/自定义与调教指南.md](./docs/自定义与调教指南.md)。  
给 Agent 的仓库约定：[AGENTS.md](./AGENTS.md)。能力状态与释出节奏见 [vNext 路线与释出](./docs/vNext路线与释出.md)。

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
