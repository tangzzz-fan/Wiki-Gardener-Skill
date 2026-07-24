# 吸附工作流（Intake）

新内容进入知识库的标准处理流程。

## 目录

1. 主流程
2. 域路由
3. 指标体系与评分
4. 决策矩阵
5. 诊断单 Schema
6. 人话卡片翻译规则
7. 执行与日志

---

## 1. 主流程

```
新内容 → 域路由 → 检索 Atlas 找候选挂载点（相似度 top-N）
→ 关系判定 → 指标评分 → 决策矩阵出结论 → 生成诊断单
→ （按自治阶梯）人工批准或直接执行 → 执行 → 写决策日志
→ 更新 MOC 与双向链接
```

落盘位置：新建/合并后的笔记优先放入与总 MOC 分区同名的 `20_领域/<分区名>/`；无匹配分区时暂放 `20_领域/_未归类/`，并提示用户归入或新增分区（一层即可，不擅自深嵌）。

## 2. 域路由

优先级从高到低，**低置信度时问人，不猜**：
1. 内容自带 frontmatter `domain:` 字段
2. 术语命中统计：与 `00_系统/domains/` 各域档案的术语表比对，取命中率最高且显著领先第二名的域
3. 以上都失败 → 用人话问用户：「这篇更像属于 X 还是 Y，还是个新主题？」

命中无对应域档案且该主题笔记 ≥ 5 篇 → 提示用户是否开新域（用 `assets/templates/domain-pack.md` 建档）。

## 3. 指标体系与评分

对内容逐项评 1–5 分（5 最差/最需处理），并在诊断单中给出依据：

| 指标 | 含义 | 评分锚点 |
|---|---|---|
| info_density | 信息密度（反向：5 = 水分大） | 有效知识点数/百字；通篇复述常识 = 5 |
| redundancy | 与库内笔记的冗余度 | 与某篇 > 85% 重叠 = 5；全新 = 1 |
| topic_consistency | 主题一致性（5 = 多主题混杂） | 各段与标题的语义方差 |
| concept_load | 概念负载（5 = 一篇引入 > 3 个新核心概念） | 数新术语/新概念 |
| freshness | 时效性 | 引用已废弃 API/旧版本 = 5 |

时效性判断必须加载对应域档案中的时效性锚点，无域档案时标注"未经领域核验"。

## 4. 决策矩阵

按优先级从上到下判定，命中即停：

```
1. freshness = 5 且属事实性错误  → correct（先经域档案核验）
2. redundancy ≥ 4                → 合并（见 gardening.md 去重协议）
3. topic_consistency ≥ 4         → split（拆分后每个碎片重新走本流程）
4. 不符合宪章排斥标准             → 拒收 → 90_archive/
5. info_density ≥ 4              → compress
6. 表述问题（句长/受众不匹配）     → rewrite
7. 全新且符合宪章                 → 创建原子笔记，挂载 MOC
```

**顺序即铁律**：结构手术（合并/拆分）永远先于文字润色（压缩/改写）。

## 5. 诊断单 Schema

每个非平凡决策生成一份诊断单（JSON），这是机器间契约：

```json
{
  "target": "10_inbox/xxx.md",
  "domain": "ios 或 null",
  "diagnosis": {
    "info_density": 3,
    "redundancy": 4,
    "topic_consistency": 2,
    "concept_load": 2,
    "freshness": "ok"
  },
  "decision": "merge",
  "operation_hint": "合并进 20_领域/iOS 踩坑与 API/BLE 配网流程.md，保留其独有段落 2 段",
  "related_notes": ["20_领域/iOS 踩坑与 API/BLE 配网流程.md"],
  "reason": "与现有笔记 87% 重叠，独有内容为实战踩坑两段",
  "confidence": 0.85,
  "requires_approval": true
}
```

规则：L3 操作（split/merge/迁移/归档/拒收）永远 `requires_approval: true`；confidence < 0.7 一律升级人工。

## 6. 人话卡片翻译规则

诊断单展示给用户时必须翻译为卡片格式，禁止直接展示 JSON：

```
《标题》
（一句人话说发现了什么）和库里的《xxx》有 87% 重复。
建议：合并进旧笔记，你新写的两段独有内容会保留。
[同意]  [保留两篇]  [我有别的想法]
```

要点：先说发现，再说建议，理由口语化，选项三选一；禁止 emoji。批量场景可将多张卡片汇总为一次确认（见 setup-wizard.md 批量吸附）。

## 7. 执行与日志

- 文本类执行（rewrite/compress/correct/split 的具体落笔）：按编辑规范执行，保持知识骨架与既有链接不动
- 结构类执行（merge/迁移/归档）：移动文件后必须更新全库反向链接与两侧 MOC；归档到 `90_archive/` 而非删除，正本注明来源
- 每个决策按 `assets/templates/decision-log.md` 写日志，理由栏必填
- 新建笔记遵循 `assets/templates/note.md` 的原子笔记格式（frontmatter + 标题即结论 + ≥1 个入链挂载）
