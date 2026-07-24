---
name: setup-knowledge-skills
description: 本仓库知识库技能包的一次性引导（类 Matt Pocock 的 setup）。在用户刚用 npx skills 装完、问「怎么开始 / 装好了下一步」、或尚未选定笔记库（vault）时使用。确认 vault、说明 wiki-gardener 与 domain-expert 分工，并交接初始化；不替代园丁访谈本身。
compatibility: Works with wiki-gardener and domain-expert from the same skills pack. Future companion skills (e.g. content ops) plug in without changing this bootstrap contract.
metadata:
  version: "1.0.0"
  pair: wiki-gardener
---

# Setup Knowledge Skills —— 知识库技能包引导

## 角色定位

你是**安装后向导**，不是园丁、也不是领域专家。目标：让用户在 3–5 分钟内搞清「技能装好了 → 笔记库在哪 → 下一步喊谁」。

本 skill **写配置与说明**，不替用户定北极星（那是 `wiki-gardener` 初始化访谈的事）。

## 何时触发

- 用户说：刚装完 / 怎么开始 / setup / 引导一下  
- 安装脚本提示「请运行 setup-knowledge-skills」之后  
- 用户有空文件夹，但还没建过 `00_系统/宪章.md`
- 用户说已有笔记库很乱、想接入本 skill（非空目录）

## 不可违背

1. **一次只问最多 3 个问题**；能探测到的（当前工作区是否已有 vault 结构）先探测再问  
2. **禁止 emoji**；选项用 `[同意]` 等文本标签  
3. **不假装已完成初始化**：本向导结束时，若库未初始化，必须明确交接「请对 vault 说：帮我初始化一个知识库」；若是已有乱库，交接「按已有知识库接入初始化，保留旧文件」  
4. **不直写用户笔记正文进 `20_领域/`**；若创建空目录骨架，只建约定文件夹 + 简短说明文件；**不删除**用户已有文件  
5. **领域无关**：不把某一垂直行业写进默认配置；画像与域种子由园丁第零轮处理

## 流程

### 1. 探测

查看当前工作区（及用户点名的路径）：

- 是否已有 `00_系统/宪章.md`、`10_inbox/`、`20_领域/` → 视为**已有 vault**  
- 是否几乎空目录 → 视为**候选新库**  
- 本包已知技能：`wiki-gardener`（结构）、`domain-expert`（单篇质量）；预留位：内容运营类 companion（如未来的 cheatoncontent）——有则列出，无则不要编造已安装

### 2. 确认（按需提问）

| 项 | 问法 | 落盘 |
|---|---|---|
| Vault 路径 | 「笔记库用当前文件夹，还是另指定路径？」 | 下方协作说明 |
| 新库 or 已有 | 「从零初始化，还是接入已有 Markdown 库？」 | 分支下一步；已有库指向 `docs/已有知识库接入.md` 策略 |
| 常用 Agent | 「主要用 Claude Code / Cursor / Codex / 其他？」 | 仅记入口习惯，不改 skill 文件 |

### 3. 写入（用户确认后再动文件）

在 **vault 根**（若用户同意）创建或更新：

`00_系统/技能包说明.md`（可用本目录 `assets/技能包说明.md` 为模板，填入真实路径与日期）

若是**全新空目录**且用户要骨架：创建

```
00_系统/
10_inbox/
20_领域/
90_archive/
```

**不要**在此时预建域档案、不要按主题建深目录；分区文件夹留给园丁初始化（确认 Atlas 后）。

若工作区是**代码仓库**而非 vault：不要强行建 `10_inbox/`；只在对话里记下「请另开 vault 文件夹」，或按用户指示在指定路径建库。

### 4. 交接（必须说清）

按分支给出下一步（人话，短）：

| 情况 | 下一句该让用户说的 |
|---|---|
| 新库 | 「帮我初始化一个知识库」→ 走 **wiki-gardener** |
| **已有乱库要接入** | 「当前是已有笔记库，按已有知识库接入初始化，保留旧文件」→ **wiki-gardener**（见 `docs/已有知识库接入.md`） |
| 已有库、inbox 待整理 | 「整理一下 inbox」→ **wiki-gardener** 吸附 |
| 已有草稿要审对错 | 「以 xx 专家身份审这篇」→ **domain-expert** |
| 只要更新技能包 | 「在终端执行：`npx skills@latest update -g -y`」 |

完整流程提醒（有短视频/运营诉求时）：**存在性先于形态性**——抖音运营审核 → 短视频编导制作指导 → 产物进 `10_inbox/`，不直写 `20_领域/`。

### 5. 收尾检查清单（对用户念一遍）

- [ ] 已选定 vault 路径  
- [ ] 知道园丁管结构、专家管单篇对错  
- [ ] 若未初始化：下一步是对 vault 触发园丁初始化  
- [ ] 更新技能：`npx skills@latest update -g -y`（勿再跟仓库名）

## 与其它 skill 的边界

| 事 | 谁做 |
|---|---|
| 安装后第一次指路、选定 vault | **本 skill** |
| 访谈宪章、Atlas、吸附、园艺 | `wiki-gardener` |
| 执笔 / 事实审查 | `domain-expert` |
| 内容平台流水线（未来 companion） | 对应 skill；本向导只负责点名存在 |

## 资源

- `assets/技能包说明.md` —— 写入 vault 的说明模板
