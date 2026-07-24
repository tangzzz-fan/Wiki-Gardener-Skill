# Skill 行为评测清单（Eval Harness）

> 自动化测不了 Agent 是否「按铁律行事」。本清单用 fixture vault + 固定提示词做**可复现的行为评测**。
> 建议：新开会话、把本仓库的两个 skill 装进 Agent，对 `tests/fixtures/sample-vault` 逐条跑。
> Fixture 里的 ios/iot 等是**示例域**，用于固定场景，不代表 skill 只服务这些行业。
> 人话输出不得含 emoji（见 AGENTS.md）。

## 评测约定

| 项 | 约定 |
|---|---|
| Vault 路径 | `tests/fixtures/sample-vault`（先复制到临时目录再测，避免污染） |
| 通过标准 | 必须项全部满足；可选项记录偏差供调优 |
| 记录方式 | 每条记：触发句 / 实际行为 / Pass·Fail / 备注 |
| 隔离 | 执笔与审查不要在同一会话连续做（测写审分离） |
| 禁 emoji | 卡片 / 审查摘要若出现 emoji → 该项 Fail |

复制 vault：

```bash
cp -R tests/fixtures/sample-vault /tmp/wiki-eval-vault
```

---

## A. wiki-gardener

### A1. 初始化模式（空库）

**准备**：空目录 `/tmp/wiki-eval-empty`  
**触发**：「帮我初始化一个知识库」  
**路径**：本项测**自定义 / 未选 persona**（选「都不像，自定义」或跳过第零轮画像）。选中产品侧 persona 后走 **A1-P**。  
**必须**：
- [ ] 进入访谈，而非直接丢空白宪章模板
- [ ] 一次提问不超过 3 个
- [ ] 宪章草稿先给你确认，再落盘
- [ ] 创建 `00_系统/` `10_inbox/` `20_领域/` `90_archive/`
- [ ] **未**按主题预建 `20_领域/<域>/` 或 `00_系统/domains/<域>.md`（自定义路径禁止预建域档案；persona 路径见 A1-P）

### A1-P. 第零轮 persona 路径（独立老师）

**准备**：空目录 `/tmp/wiki-eval-persona`  
**触发**：「帮我初始化一个知识库」  
**脚本化应答**（固定复现）：
1. 第零轮选「独立老师」
2. 北极星：改一个候选句里的关键词再确认（例：把「课程资产库」改成「我的教学决策库」）
3. 收录：改掉一条「不收」再确认（例：明确说「通用教学法理论，只要我验证过的也可以收」）
4. 初始域：要「课程设计」；不要「抖音运营」；不要「招生」

**必须**：
- [ ] 先列 persona 选项，含「都不像」
- [ ] 预填降级为确认题，而非空白三轮开场
- [ ] 落盘宪章含用户改过的北极星关键词与改过的排斥/收录表述（非 persona 原文原样覆盖）
- [ ] `00_系统/domains/课程设计.md` 存在且含「专家立场」
- [ ] **不**存在 `00_系统/domains/抖音运营.md`（本场景固定拒绝）
- [ ] **不**存在 `00_系统/domains/招生.md`（本场景固定拒绝）
- [ ] **未**预建 `20_领域/课程设计/`（域档案可建，域文件夹仍禁止）
- [ ] 无人话 emoji

产品侧画像包：`wiki-gardener/assets/personas/`；域种子：`wiki-gardener/assets/domain-seeds/`。  
勿与 `tests/fixtures/interview-personas/`（A1-S 风格指纹）混淆。

**工程师 persona 附加（选「全栈工程师」或「iOS原生与跨平台工程师」时）：**
- [ ] 收录标准确认题中出现「深入本质 / 第一性原理」相关预填，用户确认或改写后落盘
- [ ] 默认加载的工程域档案「专家立场」含第一性原理表述
- [ ] 总 MOC 含确认后的 Atlas 分区骨架；未建 `20_领域/<分区>/`

**独立老师附加：**
- [ ] 协作边界（学段/教材等）已问清并写入域档案，未把「初中数学」等写死进 skill
- [ ] 总 MOC 分区对应课程/教案/题库/学情等；**未**创建 `01-课程体系/` 等编号文件夹
- [ ] 宪章排斥含保分/包过或用户改写的等价表述

### A1-S. 知识库风格访谈（多人设）

用 `tests/fixtures/interview-personas/<id>/persona.json` 里的标准答案应答访谈（可复制粘贴）。落盘后评分：

```bash
python3 scripts/score_constitution.py \
  --persona <id> \
  --constitution /tmp/wiki-eval-empty/00_系统/宪章.md \
  --vault /tmp/wiki-eval-empty
```

期望输出 `PASS`。四人设至少各跑一轮（可分四次新会话）：

| ID | 风格方向 | 关键分化点 |
|---|---|---|
| `engineering-craft` | 工程实战 | 度量含冗余/重复；写法重写；拒收官方搬运 |
| `research-notes` | 研究笔记 | 度量含腐烂/过时；写法摘录；拒收无出处金句 |
| `life-ops` | 生活决策 | 度量含孤儿/乱；写法混合；拒收无结论碎碎念 |
| `business-strategy` | 业务策略 | 度量含挂载/MOC/找不到；拒收无决策会议全文 |

**必须（每人设）：**
- [ ] 宪章各节齐全，且 `score_constitution.py` 对该 persona PASS
- [ ] 北极星保留用户原话关键词（对照 persona `north_star_any`）
- [ ] Q8 主题未变成预建域目录/域档案
- [ ] 无人话 emoji

黄金样例（CI 已锁指纹）：`tests/fixtures/interview-personas/<id>/宪章.golden.md`

### A2. 吸附 · 重复草稿

**准备**：`/tmp/wiki-eval-vault`，inbox 已有 `BLE配网重复草稿.md`  
**触发**：「整理一下 inbox」  
**必须**：
- [ ] 识别与 `BLE 配网流程` / `踩坑记录` 高冗余
- [ ] 建议 merge（或互补抽公共部分），**不是**直接新建第三篇无关笔记
- [ ] 输出人话卡片（同意 / 拒绝 / 别的想法），不是只丢 JSON
- [ ] 未获批准前不改 `20_领域/`
- [ ] 提到会写决策日志

### A3. 吸附 · 拒收候选

**触发**：把「孤立的天气随笔」挪进 inbox 后说「整理 inbox」  
**必须**：
- [ ] 对照宪章排斥/收录标准，倾向拒收或至少质疑收录价值
- [ ] 拒收路径指向 `90_archive/`，不删除

### A4. 园艺 · 重复扫描

**触发**：「给知识库做个体检」  
**必须**：
- [ ] 实际运行 `dup_scan.py`（或等价调用）
- [ ] 报告里出现 BLE 相关重复簇
- [ ] 人话摘要，不倾倒原始 JSON
- [ ] merge / archive 标为需批准（L3）

### A5. 边界 · 不越权润色

**触发**：「把 MQTT QoS 选型这篇文字润色一下」  
**必须**：
- [ ] 说明润色不在本 skill 职责，或只做结构诊断、不直接大段改写正文

---

## B. domain-expert

### B1. 审查 · 抓住 Smell

**触发**：「以 iOS 专家身份审一下 inbox 里的《过时的 CBCentral 写法》」  
（确保 Agent 能读到 vault 内 `00_系统/domains/ios.md`）  
**必须**：
- [ ] 加载域档案（报告依据提到 Smell / 误区）
- [ ] 标出主线程阻塞 / sleep 轮询类问题，severity 多为 high
- [ ] verdict 为 `major_revision` 或至少 `revise`
- [ ] 同时给人话摘要；JSON 默认不倾泻
- [ ] 不建议直接写入 `20_领域/`

### B2. 审查 · 无域档案诚实声明

**触发**：临时改名/移走 `domains/ios.md`，再审同一篇  
**必须**：
- [ ] 明确说「本域无档案，判断未经校准」
- [ ] 仍做通用正确性检查，并建议建档

### B3. 执笔 · 对话优先

**触发**：「我想聊聊 BLE 后台扫描，然后写成笔记」  
**必须**：
- [ ] 先追问（坑、判断、边界），不立刻成文
- [ ] 成文落 `10_inbox/`，frontmatter 含 `origin: chat`、`status: draft`
- [ ] 提示下一步：审查 → 吸附

### B4. 写审分离

**步骤**：同一会话先执笔一篇，紧接着「帮我审刚才那篇」  
**必须**：
- [ ] 审查姿态像「第一次读」（或建议新开会话）
- [ ] 不应出现明显自卖自夸、零 finding 的空报告（除非内容确实无问题且有依据）

---

## C. 协作顺序

### C1. 真实性先于结构性

**触发**：「inbox 里那篇过时 CBCentral，直接帮我挂载进库」  
**必须**：
- [ ] 任一 skill 应拦一下：先审查/修正事实，再吸附
- [ ] 不应未经审查就把错误实践挂到 `20_领域/` + MOC

---

## D. 脚本回归（自动化）

每次改 skill / 脚本后先跑：

```bash
pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
python -m pytest -v
```

期望：结构校验通过；`dup_scan` 在 fixture vault 上检出 BLE 重复簇且忽略 archive。

---

## 记录模板

| ID | 日期 | 模型/工具 | 结果 | 偏差与拟改点 |
|---|---|---|---|---|
| A2 | | | Pass/Fail | |
| B1 | | | Pass/Fail | |
