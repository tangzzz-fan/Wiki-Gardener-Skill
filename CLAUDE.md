# CLAUDE.md

本文件供 Claude Code 及兼容工具读取。完整约定见 [AGENTS.md](./AGENTS.md)；此处重复关键硬约束以免漏读。

## 必须遵守

- **禁止 emoji**：所有生成内容（代码、文档、提交信息、对人输出）不得使用 emoji。用 `[高优先]`、`[同意]`、`[警告]` 等文本标签。
- **领域无关**：不要把 skill 改成绑定 iOS / IoT / Flutter 等单一领域；示例内容仅作演示。
- **禁止 Co-authored-by**：commit message 不得添加 `Co-authored-by`（含 Cursor / Agent）；见 AGENTS.md。
- **改完跑测**：`python3 scripts/validate_skills.py && python3 -m pytest -v`
- **未经要求不 commit / push**

更细的仓库约定与输出风格以 `AGENTS.md` 为准。
