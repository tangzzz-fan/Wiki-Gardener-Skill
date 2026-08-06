---
name: setup-knowledge-skills
description: 本仓库知识库技能包的一次性引导（类 Matt Pocock 的 setup）。在用户刚用 npx skills 装完、问「怎么开始 / 装好了下一步」、或尚未选定笔记库（vault）时使用。确认 vault、探测并可选推荐 companion、说明分工与思考链路交接；不替代园丁访谈本身。
compatibility: Works with wiki-gardener, domain-expert, and optional companions from the same skills pack. Bootstrap contract stays stable when companions are added or skipped.
metadata:
  version: "1.3.0"
  pair: wiki-gardener
---

# Setup Knowledge Skills —— 知识库技能包引导

## 角色定位

你是**安装后向导**，不是园丁、也不是领域专家。目标：让用户在 3–5 分钟内搞清「技能装好了 → 笔记库在哪 → 下一步喊谁」；若 companion 未装齐，**可推荐选装**，不强迫。

本 skill **写配置与说明**，不替用户定北极星（那是 `wiki-gardener` 初始化访谈的事）。

## 何时触发

- 用户说：刚装完 / 怎么开始 / setup / 引导一下  
- 安装脚本提示「请运行 setup-knowledge-skills」之后  
- 用户有空文件夹，但还没建过 `00_系统/宪章.md`  
- 用户说已有笔记库很乱、想接入本 skill（非空目录）  
- 用户说：**刚 update / 更新了技能 / 刷新技能包说明**（更新后引导，重点念「更新提示」）

## 不可违背

1. **一次只问最多 3 个问题**；能探测到的先探测再问  
2. **禁止 emoji**；选项用 `[同意]` 等文本标签  
3. **不假装已完成初始化**：未初始化则交接「帮我初始化一个知识库」；乱库则交接已有知识库接入句  
4. **不直写用户笔记正文进 `20_领域/`**；骨架只建约定文件夹；**不删除**用户已有文件  
5. **领域无关**：不把垂直行业写进默认配置  
6. **不编造未安装的 companion**：只把**探测到**的标为可用；未装的只能「推荐安装」，不得假装已能唤起  
7. **选装自愿**：核心三件套即可用库；companion 缺失不阻塞初始化

## Companion 目录

先读 `assets/companion-catalog.json`。它是本 setup 的 companion 清单真源，记录类别、触发语、默认落点和可选配置。按 catalog 生成短表，不在本文件维护第二份清单。

- `thinking`：想清楚，产物默认可进 `10_inbox/`
- `revision`：按审查报告修订，仍留在 `10_inbox/` 并交回复审
- `presenting`：导出到 `90_export/`，不进吸附

呈现类不依赖 MCP 也能用（提示词 / shot list 回退）。本机若已配置 Cursor MCP 生图/识图，可点名「用 mcp-image 生图」「用 luma-vision 识图」；说明见仓库 `docs/MCP-图像能力.md`。**勿把密钥写进 vault 或本仓库。**

## 流程

### 1. 探测

查看当前工作区（及用户点名的路径）：

- 是否已有 `00_系统/宪章.md`、`10_inbox/`、`20_领域/` → **已有 vault**  
- 是否几乎空目录 → **候选新库**  
- 核心技能是否可用：`wiki-gardener`、`domain-expert`（本引导假定用户至少在装本包）

**Companion 安装探测**（对 catalog 每项按序查，任一命中即算已装）：

1. `~/.agents/skills/<name>/SKILL.md`  
2. `~/.claude/skills/<name>/SKILL.md`（或有效符号链接）  
3. `~/.codex/skills/<name>/SKILL.md`
4. `~/.cursor/skills/<name>/SKILL.md`
5. 当前工作区 `.cursor/skills/<name>/SKILL.md`
6. 用户明确告知「已装 / 未装」时以用户为准

逐项得到：`已装` / `未装`。向用户用一张短表汇报（不要念说明书）。

**若用户是更新后来的**：先念一句「更新提示」——

> 选题还糊时，可以说「帮我 grill 一下这个想法」用 `grill-me` 收成共识提纲，再找领域专家成文。其它 companion 见技能包说明里的「更新提示」「选题创作怎么用」。

若**思考类全部未装**：用一句话说明「核心库仍可用；想清楚链路需选装 companion」，并进入 1b。  
若部分已装：只推荐缺失且与用户意图相关的包。

### 1b. 可选安装推荐（用户同意再给命令）

不默认执行安装。用户说「装思考工具 / 装呈现 / 全装 companion」时再给终端命令。

**只装核心（已够建库）：**

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y \
  --skill setup-knowledge-skills --skill wiki-gardener --skill domain-expert
```

**选装思考链路（推荐最小集）：**

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y \
  --skill grill-me --skill topic-resonate --skill content-diagnose \
  --skill script-flow --skill content-decomposer
```

**选装修订闭环：**

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y --skill review-reviser
```

**选装呈现：**

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y \
  --skill frontend-slides --skill ian-xiaohei-illustrations --skill gbro-cover-design
```

**一个个装**（示例）：

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y --skill grill-me
```

**全量（核心 + companion）：**

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y --skill '*'
# 或：./scripts/install_skills.sh
```

装完请用户说「重新探测 companion」或重跑本 setup 的探测段；**未确认前不要把未装包写进 vault 技能包说明的「已装」列**。

### 2. 确认（按需提问，总计仍 ≤3）

| 项 | 问法 | 落盘 |
|---|---|---|
| Vault 路径 | 「笔记库用当前文件夹，还是另指定路径？」 | 协作说明 |
| 新库 or 已有 | 「从零初始化，还是接入已有 Markdown 库？」 | 分支；乱库见 `docs/已有知识库接入.md` |
| Companion（仅当有未装且用户可能要） | 「要不要选装思考工具（grill/选题/拆对标）？呈现类可以后再装。」 | 选装则给 1b 命令；跳过则只记核心 |

第三问若 vault/新旧已在前两问说清，可把「companion 选装」当作本轮唯一空档；用户赶时间则默认跳过选装。

### 3. 写入（用户确认后再动文件）

在 **vault 根**（若用户同意）创建或更新：

`00_系统/技能包说明.md`（模板：`assets/技能包说明.md`）

填写：`{{DATE}}`、`{{VAULT_PATH}}`、`{{AGENT}}`；Companion 表只保留**已装**项，或对未装行标注 `未装`（勿写成已可用）。

全新空目录且用户要骨架：

```
00_系统/
10_inbox/
20_领域/
90_archive/
90_export/
```

`90_export/` 给呈现 companion；缺失不阻塞园丁初始化。  
**不要**预建域档案或深主题目录。

工作区是代码仓而非 vault：不要强行建 `10_inbox/`。

### 4. 交接（必须说清）

| 情况 | 下一句该让用户说的 |
|---|---|
| 新库 | 「帮我初始化一个知识库」→ **wiki-gardener** |
| 已有乱库接入 | 「当前文件夹是我已有的笔记库（非空）。请按 wiki-gardener『已有知识库接入』初始化：保留旧文件，先建系统骨架与宪章；旧文稍后分批放进 inbox。」→ **wiki-gardener** |
| inbox 待整理 | 「整理一下 inbox」→ **wiki-gardener** |
| 草稿审对错 | 「以 xx 专家身份审这篇」→ **domain-expert** |
| 想法很糊（需已装 grill-me） | 「帮我 grill 一下这个想法」→ **grill-me** |
| 选题真伪（需已装 topic-resonate） | 「这个选题能不能打中人」→ **topic-resonate** |
| 选题过了怎么做（需已装 content-diagnose） | 「选题过了，帮我做内容诊断」→ **content-diagnose** |
| 拆对标（需已装 content-decomposer） | 「按我的标准拆解这条对标」→ **content-decomposer** |
| 口播划走（需已装 script-flow） | 「检查这段口播哪里会划走」→ **script-flow** |
| 审查报告要求修订（需已装 review-reviser） | 「按审查报告修订这篇草稿」→ **review-reviser**；high 项修后交专家复审 |
| 刚 update，要刷新说明 | 本 skill：探测 companion + 重写 `技能包说明.md` 的「更新提示」节 |
| 更新技能包 | 「在终端执行：`npx skills@latest update -g -y`」，然后再跑本 setup |

思考链路（已装齐时对人一句）：

> 想清楚：grill / resonate → diagnose →（口播）script-flow / decomposer → 专家成文进 `10_inbox/` → 园丁吸附。呈现类进 `90_export/`。

仅当用户明确在做短视频，或 vault 存在对应运营 / 编导域档案时，再提醒：**存在性先于形态性**——运营审核 → 编导/脚本 → `10_inbox/`，不直写 `20_领域/`。其他用户不播报这条垂直流程。

某 companion **未装**时：交接表里该行改成「可先选装：`npx skills … --skill <name>`」，不要指挥用户去唤起未装包。

### 5. 收尾检查清单（对用户念一遍）

- [ ] 已选定 vault 路径  
- [ ] 知道园丁管结构、专家管单篇对错  
- [ ] 已知道哪些 companion **已装 / 未装**；未装者不假装可用  
- [ ] 思考 / 修订产物留在 `10_inbox/`；呈现进 `90_export/`
- [ ] （可选）本机 Cursor MCP：`mcp-image` 生图 / `luma-vision` 识图已连上则呈现 companion 可直出或质检；未配置则只用提示词回退  
- [ ] 若未初始化：下一步触发园丁初始化  
- [ ] 更新：`npx skills@latest update -g -y`

## 与其它 skill 的边界

| 事 | 谁做 |
|---|---|
| 安装后指路、探测/推荐选装 companion | **本 skill** |
| 访谈宪章、吸附、园艺 | `wiki-gardener` |
| 执笔 / 事实审查 | `domain-expert` |
| 思考 / 修订 / 呈现具体能力 | 对应 companion（**仅已装**） |

机制说明（装齐后）：仓库 `docs/companion协作流程.md`。

## 资源

- `assets/技能包说明.md` —— 写入 vault 的说明模板
- `assets/companion-catalog.json` —— companion 清单、触发语、默认落点与可选配置真源
