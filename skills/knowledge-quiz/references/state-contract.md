# 学习状态契约

## 真源与写入边界

唯一状态真源：

- `00_系统/学习记录/掌握索引.md`
- `00_系统/学习记录/测验记录/<时间>-<主题>.md`

管理脚本只能在 `00_系统/学习记录/` 内创建或修改文件。来源笔记与 `20_领域/` 均为只读输入。

## 稳定标识

`concept_id` 由以下三项的规范化值生成：

1. 来源笔记相对 vault 的路径
2. 标题锚点
3. 概念键

同一概念必须始终使用同一组输入。概念键表达被测知识单元，不使用题面措辞。

`question_signature` 由以下三项生成：

1. `concept_id`
2. 认知动作：`recall`、`explain`、`application` 或 `relation`
3. 被测关系，例如“定义”“A 导致 B”“X 与 Y 的边界”

改写语气但未改变认知动作和被测关系时，signature 保持不变。

## 四种状态

- `unseen`：索引没有答题证据，或候选概念尚未写入索引。
- `learning`：已有答题证据，但未达到掌握门槛。
- `mastered`：来源当前版本上，至少两个不同会话答对至少两个不同 `question_signature`，且正确证据含 `application` 或 `relation`。
- `review_due`：已记录来源 fingerprint 与当前来源不一致，需要基于新版本复习。

同一会话重复答对只计一个正确会话；跨会话重复同一 `question_signature` 也不能单独形成掌握。来源变化后保留历史题目签名与总数用于审计，但当前版本的正确会话、正确题目签名和认知动作重新累计。

## 掌握索引格式

索引由人读摘要和受控 JSON 数据块组成：

```markdown
# 掌握索引

| concept_id | 状态 | 来源 | 当前版正确会话 |
|---|---|---|---:|
| c_... | learning | [[20_领域/示例.md#标题]] | 1 |

<!-- knowledge-quiz:data:start -->
```json
{
  "concepts": [],
  "version": 1
}
```
<!-- knowledge-quiz:data:end -->
```

脚本只解析标记之间的单个 JSON 围栏，并在每次写入时重建摘要表。`concepts` 按 `concept_id` 排序，列表字段去重并排序，以保证确定性 diff。

每个概念至少包含：

- `concept_id`、`source_path`、`heading_anchor`、`concept_key`
- `source_fingerprint`、`status`
- `asked_question_signatures`、`correct_question_signatures_current`
- `correct_sessions_current`、`qualifying_actions_current`
- `attempt_count`、`correct_count`
- `last_seen_at`、`last_question_signature`

## 会话记录格式

文件名使用 `<YYYYMMDD-HHMMSS>-<主题>.md`。文件头记录 `session_id` 与主题；每题使用一个 `## 题目 N` 章节，含人读字段及单行 JSON 审计记录。追加顺序就是作答顺序，不回写改写旧题。

## 安全更新

- 更新索引前验证 JSON 版本、标记唯一性与字段类型。
- 写入临时文件后使用原子替换，避免半写文件。
- 会话记录追加失败时将掌握索引回滚到写入前状态，避免只有一侧留下新证据。
- 所有写入目标解析后必须位于学习记录根目录内。
- 来源 fingerprint 使用来源文件原始字节的 SHA-256；找不到来源时停止回写并报告明确错误。
