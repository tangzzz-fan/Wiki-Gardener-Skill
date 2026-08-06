---
name: review-reviser
description: 按 domain-expert 的 review-mode JSON 或人话审查报告逐条修订草稿，并输出 finding 处理账本。仅当用户明确要求“按审查报告修订”或“逐条应用 findings”时触发；普通润色、改写、审查或知识库整理不触发。
license: MIT
compatibility: No runtime scripts; expects a draft plus a domain-expert review-mode JSON or human-readable report.
metadata:
  version: "1.0.0"
  companion: domain-expert
---

# Review Reviser

把 `domain-expert` 的审查结论转成可追踪的草稿修改。这里只执行已批准的 findings，不重新审查，也不替知识库做收录决策。

## 输入门槛

开始前必须同时取得：

1. 草稿正文或草稿文件路径。
2. review-mode JSON，或能逐条识别优先级、位置、问题和修正建议的人话报告。

报告含糊、finding 无法定位、修正建议互相冲突时，将对应项标为 `blocked` 并向用户追问；不得自行补造审查结论。

## 写入边界

- 默认仅修改报告 `target` 指向的 `10_inbox/` 文件。
- 其他文件必须由用户明确指定；`20_领域/` 始终不可写。
- 只有粘贴草稿而无获准路径时，在对话中返回修订稿，不自行创建文件。
- 保持草稿状态；不得改为 `pass` 或 `seedling`，不得挂载、吸附、查重或改 MOC。
- 只做 findings 要求的最小修改。报告外的事实、结构或语气改动须另列建议，不混入本轮。

## 执行流程

### 1. 对齐

读取草稿与整份报告，为 findings 保留原顺序并分配稳定编号 `F-001`、`F-002`。逐条记录：

- severity
- location 与原文锚点
- correction
- basis
- 预期修改
- 状态：`ready`、`blocked` 或 `skipped`

JSON 字段缺失时从人话报告中提取；无法可靠提取则标 `blocked`。

### 2. 先展示计划

任何修改前，向用户展示：

```text
逐条修订计划

F-001 [high] <位置>
问题：<finding>
拟修改：<具体动作>
依据：<basis>
状态：ready

目标：<文件路径或“仅在对话中返回”>
范围：共 N 项；ready N，blocked N，skipped N

请批准该计划，或指出要调整、跳过的编号。
```

未得到明确批准时停止，不修改草稿。用户只批准部分编号时，仅执行该部分；计划变化后再次展示差异并获批。

### 3. 逐条应用

按编号执行已批准的 `ready` 项：

1. 修改前核对原文锚点仍匹配；不匹配则改为 `blocked`。
2. 应用最小充分修改，保留作者立场、语气和未被 finding 涉及的内容。
3. 修改后核对 correction 已落实，且未制造前后矛盾。
4. 记录修改前后摘要与实际位置。

不得把“无法核验”改写成确定事实。finding 要求保留 `[待核验]` 时原样保留。

### 4. 输出处理账本

```text
修订处理账本

F-001 [high] applied
位置：<实际位置>
处理：<修改摘要>
核对：<correction 如何落实>

F-002 [medium] blocked
原因：<无法执行的具体原因>

汇总：applied N，skipped N，blocked N
文件：<修改路径或“未写文件”>
状态：draft
下一步：<复审要求>
```

每个 finding 必须且只能出现一次，状态使用 `applied`、`skipped` 或 `blocked`。`applied` 只表示修改已执行，不表示审查通过。

### 5. high 复审门

只要本轮处理过 high finding：

1. 将修订稿与处理账本交给 `domain-expert` 审查模式复审。
2. 在复审结果返回前保持 `draft`，明确写“等待 domain-expert 复审”。
3. 若复审产生新 findings，把它们作为新一轮输入，重新走计划与批准。

没有 high finding 时也不得自行宣告 `pass`。是否通过、能否转 `seedling` 由 `domain-expert` 与用户后续确认；吸附由 `wiki-gardener` 另行处理。

## 完成标准

- 获批 finding 全部在账本中有唯一终态。
- 写入目标符合边界，未触碰 `20_领域/`。
- 草稿状态未被提升，未执行吸附。
- 处理过 high finding 时，已明确交给 `domain-expert` 复审或停在等待复审状态。
