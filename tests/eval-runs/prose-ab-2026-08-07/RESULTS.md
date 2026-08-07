# prose-ab-2026-08-07 运行报告

- 日期：2026-08-07
- 协议：pipeline A/B（`domain-expert` 锁稿 → `humanizer` / `human-writing` 后处理）
- 材料：`tests/eval-runs/prose-ab-2026-08-07/`
- 外部 skill：本机软链至 `~/.claude/skills/humanizer`、`human-writing`（**未**并入仓库 `skills/`）
- 限制：后处理未开独立 Agent 子会话（额度不足），由执行者按 skill 文本改写；评分开卷，方向性有效、不可当严格双盲

## 结果总表

| 题 | 类型 | 胜者 | A.S | B.S | C.S |
|---|---|---|---|---|---|
| T1 | 实操（CB 回调） | C | 23.5 | 24.5 | 26.5 |
| T2 | 立场（原子化） | C | 21.5 | 23.5 | 26.5 |
| T3 | 科普口吻（archive） | C | 22.5 | 23.5 | 26.5 |
| | **合计** | **C** | **67.5** | **71.5** | **79.5** |

S 加权见 [`rubric.md`](./rubric.md)。明细见 [`scoresheet.md`](./scoresheet.md)。

## 分维度解读

- **保真（D3）**：三臂三题均为 5。后处理约束「不增事实」可执行；Arm C 初稿曾把「仪表盘」误写成 Instruments，已在定稿前改回（说明 human-writing 节奏改写时仍有漂移风险，需人工扫一眼）。
- **人味与 AI 痕迹（D1+D2）**：A 基线可读但常带破折号、翻案式对举、金句收束；B 主要做轻 scrub；C 稳定抬到更高自然度，且 `check_prose.py` 三题 exit 0。
- **专业可读（D4）**：T1 技术清楚，后处理未伤术语；T2/T3 观点稿三臂接近，C 略更上口。
- **humanizer 与中文**：本轮中文仍获益（尤其去 `——`、削弱警句腔），增益小于 human-writing；英文词痕清单本就几乎未出现，不作为扣分项。

## 决策规则结论（事先约定，不挪标）

| 规则 | 命中 |
|---|---|
| B 或 C：Δ(D1+D2)≥0.5 且 D3 不降 → 值得可选后处理 | **B 命中（+0.83）**；**C 命中（+1.83）** |
| D3 平均降 ≥0.5 → 不接流水线 | 未命中 |
| humanizer 中文 Δ(D1+D2)<0.3 → 仅适合英/双语 scrub | **未命中**（本轮 +0.83） |

**建议（不改核心 skill，仅产品决策）**

1. **纯 domain-expert 已够用**作为知识库执笔基线：事实、挂载建议、域 Smell 对齐都在 A 上完成。
2. 若在意中文成稿的「读感」，把 **`human-writing` 作为可选后处理 companion** 接在执笔之后、审查之前或之后均可；默认不要写死进 `domain-expert` 铁律。
3. **`humanizer` 可作轻量第二选择**（尤其双语/英文段落，或只需去破折号与百科腔时）；中文长帖优先 human-writing。
4. 流水线接法保持「信息保真复查」一步：后处理后扫数字、专有工具名、`[待核验]`、用户立场句。

> 后续落地：`human-writing` 已作为呈现 companion 迁入 `skills/human-writing/`（默认 `90_export/`），见 `docs/companion协作流程.md` §3.3 与 `skills/human-writing/docs/为什么写得好.md`。

## 产物路径

```
tests/eval-runs/prose-ab-2026-08-07/
├── README.md
├── prompts.md
├── rubric.md
├── scoresheet.md
├── RESULTS.md          # 本文件
├── vault/              # sample-vault 拷贝 + Arm A inbox
└── drafts/T{1,2,3}/arm-{a,b,c}.md
```

## 复跑注意

- Arm A 已锁定；要改协议请新建 `prose-ab-<date>/`。
- 外部 skill 软链指向 `/tmp/prose-ab-skills-2026-08-07/`；机器重启后需按 `README.md` 重新 clone/软链。
