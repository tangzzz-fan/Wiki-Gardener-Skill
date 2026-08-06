# vNext 路线与释出

本文区分当前稳定能力、需要显式开启的能力和后续路线，避免用户把“仓库里有”误解成“本机已装且已经配置”。

## 当前稳定

- 核心三件套：setup 引导、园丁初始化/吸附/园艺、领域专家执笔/审查
- 思考 companion：grill、选题共鸣、内容诊断、口播逻辑、对标拆解
- 修订 companion：按专家审查报告修订，修后按严重度复审
- 呈现 companion：HTML 演示、正文配图、封面提示词
- 质量门禁：结构校验、无 emoji 检查、契约测试、打包烟测

稳定不等于全部自动执行。`split`、`merge`、迁移、归档和拒收仍须人工批准。

## 可选与实验

- `mcp-image` / `luma-vision` 是宿主级可选能力；未配置时配图和封面回退到提示词或 shot list
- HTML 演示的在线部署与 PDF 导出依赖外部工具，使用前会单独确认
- L2 Agent 行为评测仍是人工运行，不作为自动 CI 结论

## 后续路线

- 从决策日志生成健康快照：批准率、孤儿率、域增长和自治建议
- 固定 prompt、vault 快照和评分器的半自动 L2 评测
- 统一仓库版本、tag、CHANGELOG 与 GitHub Release 流程
- 更完整的 Python / Node 兼容矩阵

## 释出检查

修改 skill 后至少运行：

```bash
python3 scripts/validate_skills.py
python3 scripts/check_no_emoji.py
python3 scripts/score_constitution.py --all-goldens
python3 -m pytest -v
```

发布后，用户执行：

```bash
npx skills@latest update -g -y
```

然后再次运行 `setup-knowledge-skills`，刷新 vault 内 `00_系统/技能包说明.md`。Skill 更新不会覆盖用户的宪章、域档案或笔记。
