# skills/

本仓库对外分发的 Agent Skills 目录（[skills.sh](https://skills.sh) / `npx skills` 会扫描此处）。

| 目录 | 用途 |
|---|---|
| `setup-knowledge-skills/` | 安装后一次性引导（先跑这个） |
| `wiki-gardener/` | 知识库园丁；详细用法见 `docs/使用说明与调优指南.md` |
| `domain-expert/` | 领域专家（执笔 / 审查）；详细用法见 `docs/使用说明与调优指南.md` |

以后新增知识库相关 skill（例如内容运营 companion）时：**在本目录下新建同级文件夹**（内含 `SKILL.md`），不要放回仓库根目录。用户用同一条安装命令即可发现新包。

```bash
npx skills@latest add tangzzz-fan/Wiki-Gardener-Skill -g -y
# 然后在 Agent 里运行 setup-knowledge-skills（安装脚本默认会尝试拉起）
```
