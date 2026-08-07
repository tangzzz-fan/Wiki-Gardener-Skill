# prose-ab-2026-08-07 — domain-expert vs humanizer / human-writing

文案质量对照实验（pipeline A/B）。**不**替换核心 skill；结论见 `RESULTS.md`。

## 对照臂

| 臂 | 含义 |
|---|---|
| Arm A | 纯 `domain-expert` 执笔落盘稿（基线） |
| Arm B | Arm A 正文 → `humanizer` 改写（不增事实） |
| Arm C | Arm A 正文 + 材料清单 → `human-writing` 改稿（禁补假经历） |

## 协议摘要

1. 先按 `prompts.md` 脚本应答锁死 Arm A；中途禁止重写 A（要改协议另开目录）。
2. B / C 各自独立会话：只改「怎么说」，不读域档案改事实立场。
3. 盲评按 `rubric.md` 填 `scoresheet.md`，揭盲后写 `RESULTS.md`。
4. 中文为主；humanizer 英式词痕单独标注，不把英文偏置当成总质量分。

## 本机临时安装对照 skill（不并入本仓库 `skills/`）

```bash
# 任选你的 Agent skills 目录，例如：
npx skills add https://github.com/blader/humanizer.git --skill humanizer
npx skills add https://github.com/KKKKhazix/human-writing.git --skill human-writing
```

或手动 clone 后软链：

```bash
TMP=/tmp/prose-ab-skills-2026-08-07
git clone --depth 1 https://github.com/blader/humanizer.git "$TMP/humanizer"
git clone --depth 1 https://github.com/KKKKhazix/human-writing.git "$TMP/human-writing"
ln -sfn "$TMP/humanizer" ~/.claude/skills/humanizer
ln -sfn "$TMP/human-writing/human-writing" ~/.claude/skills/human-writing
```

本轮产物不依赖把它们拷进 Wiki-Gardener-Skill。`/tmp` 软链重启后需重做。

复跑前确认本仓库 `domain-expert` 可用（工作区 `skills/domain-expert` 或已 install）。

结论见同目录 [`RESULTS.md`](./RESULTS.md)。

## Vault

`vault/` 由 `tests/fixtures/sample-vault` 复制。Arm A 落在 `vault/10_inbox/`，并同步拷到 `drafts/Tn/arm-a.md`。

## 复跑步骤

1. 复制本目录协议文件；新建 `prose-ab-<date>/`，再拷 sample-vault。
2. 按 `prompts.md` 跑三次 domain-expert 执笔 → 锁 `arm-a.md`。
3. 同一正文分别走 humanizer / human-writing → `arm-b.md` / `arm-c.md`。
4. Arm C 可跑官方 `check_prose.py`。
5. 盲评 → 揭盲 → `RESULTS.md`（决策规则见 `rubric.md`）。

## 产物树

```
prose-ab-2026-08-07/
├── README.md
├── prompts.md
├── rubric.md
├── scoresheet.md
├── RESULTS.md
├── vault/
└── drafts/T{1,2,3}/arm-{a,b,c}.md
```
