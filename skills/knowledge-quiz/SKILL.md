---
name: knowledge-quiz
description: 基于用户知识库进行逐题学习与间隔复习的 model-invoked companion。用户说“考我”“知识测验”“理解检查”“错题复习”，或需要从已有笔记检查真实掌握程度时触发。
license: MIT
compatibility: Requires Python 3 standard library for optional deterministic study-state management.
metadata:
  version: "1.0.0"
  companion: learning
---

# Knowledge Quiz

把知识库内容变成可追溯的逐题测验，并将掌握证据写回 Markdown 状态真源。测验负责检查理解，不替代 `domain-expert` 的事实审查。

## 边界

- 默认落点是 `00_系统/学习记录/`。
- 只读取用户指定范围、Atlas、MOC、双链和来源笔记；禁止直写 `20_领域/`，也不改来源正文。
- 对来源是否正确、是否过时没有把握时，标注待审查并交给 `domain-expert`；不要用答题结果替代事实审查。
- 只有用户明确要求导出副本时才写其他路径；掌握状态仍只以 `00_系统/学习记录/` 为真源。

## 开始前

1. 确认 vault 与本轮主题或文件范围。
2. 读取用户指定范围及其相关 Atlas/MOC，再读取 `00_系统/学习记录/掌握索引.md`；不存在时可初始化。
3. 从标题、定义、因果、对比、步骤、边界和跨笔记关系中提取候选概念。
4. 为候选生成稳定 `concept_id` 与 `question_signature`，按状态和来源变化过滤。

状态字段、Markdown 格式与变更规则见 `references/state-contract.md`。出题与判定规则见 `references/quiz-rules.md`。需要确定性管理时使用 `scripts/study_state.py`。

## 默认逐题循环

除非用户明确要求整套题或批量导出，否则一次只展示一题：

1. 选择候选：优先 `review_due`、`learning`、`unseen`；默认过滤 `mastered` 和历史上相同的 `question_signature`。
2. 提问：给出题目与必要上下文，不提前泄露答案。
3. 等待用户回答，不在同一轮追加下一题。
4. 判定：输出 `[正确]`、`[部分正确]` 或 `[需复习]`。
5. 反馈：依次给出来源、解析、薄弱点；来源用 `[[相对路径#标题]]` 追溯。
6. 回写：记录本题证据，安全更新掌握索引，并追加本会话记录。
7. 再选下一题，直到用户停止、范围耗尽或达到约定题数。

每题反馈使用：

```text
判定：<正确 | 部分正确 | 需复习>
来源：[[来源笔记#标题]]
解析：<答案成立的关键关系>
薄弱点：<具体缺口；没有则写“本题未发现”>
状态：<unseen | learning | mastered | review_due> -> <新状态>
```

`[部分正确]` 默认按未正确计入掌握证据，但可保留已答对部分供后续出题。

## 状态回写

一轮会话使用同一个 `session_id` 和同一个 `测验记录/<时间>-<主题>.md`。每题记录至少包含：

- 题目、用户答案与判定
- `concept_id`、`question_signature`、认知动作
- 来源定位与来源 fingerprint
- 解析、薄弱点、答题时间
- 回写前后状态

推荐命令：

```text
python3 scripts/study_state.py record --help
```

脚本路径相对于本 skill 目录；执行时按实际安装位置解析。脚本报错时先修正参数或路径，不用手工猜测并覆盖受控数据块。

## 掌握门槛

- 新概念为 `unseen`；出现答题证据后通常进入 `learning`。
- `mastered` 默认要求至少两个不同会话答对至少两个不同 `question_signature`，且这些正确证据中至少一题为应用题或关系题。
- 已掌握概念默认不再出题；用户主动复习时可显式纳入。
- 来源 fingerprint 变化后降为 `review_due`，新版本的掌握证据重新累计。
- 错题优先进入后续复习，但不得仅靠重复同一道题形成掌握；使用不同 `question_signature` 检查迁移。

## 完成标准

- 本轮每题都有判定、来源、解析、薄弱点与状态回写。
- 索引和会话记录一致，且写入仅发生在 `00_系统/学习记录/`。
- 所有来源可追溯；不确定事实已标注并交给 `domain-expert`。
- 结束时汇总本轮掌握变化与下一轮建议，不把答题次数等同于真实掌握。
