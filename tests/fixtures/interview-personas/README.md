# 访谈人设（Interview Personas）

用于检验「知识库风格访谈」是否按方向产出可区分的宪章。

| 目录 | 风格 |
|---|---|
| `engineering-craft` | 工程实战（怕重复、重写） |
| `research-notes` | 研究笔记（怕过时、摘录） |
| `life-ops` | 生活决策（怕乱、混合） |
| `business-strategy` | 业务策略（怕找不到、重写） |

每个目录：

- `persona.json`：标准问答 + 期望指纹（`expect.*_any`）
- `宪章.golden.md`：符合指纹的黄金宪章（CI 锁定）

评分：

```bash
python3 scripts/score_constitution.py --all-goldens
python3 scripts/score_constitution.py --persona engineering-craft \
  --constitution /path/to/vault/00_系统/宪章.md --vault /path/to/vault
```

这些是**风格方向**样例，不是对具体行业的产品限定。
