---
title: Cursor MCP 图像能力说明
topics: [mcp, ai, claude-code]
type: reference
date: 2026-08-06
status: active
---

# Cursor MCP 图像能力说明

本机已通过用户级 Cursor MCP 接入两类能力：**智谱识图**（`luma-vision`）与 **Gemini 文生图**（`mcp-image`）。配置不在本仓库内，密钥永不入库。

## 配置位置

| 项 | 路径 |
|----|------|
| MCP 总配置 | `~/.cursor/mcp.json`（权限建议 `600`） |
| 文生图输出目录 | `~/.cursor/mcp-image-output/` |

改完配置后：重启 Cursor，或打开 **Settings → MCP** 刷新，确认 `luma-vision`、`mcp-image` 为已连接。

## 1. 识图：`luma-vision`

| 项 | 值 |
|----|-----|
| MCP 名 | `luma-vision` |
| 包 | `luma-mcp`（npx） |
| 提供商 | 智谱 / BigModel（`MODEL_PROVIDER=zhipu`） |
| 模型 | `glm-4v-flash`（API 文档对话补全中的 GLM-4V-Flash） |
| 密钥环境变量 | `ZHIPU_API_KEY`（写在 `~/.cursor/mcp.json`） |
| 常用工具 | `image_understand` |

API 参考：[对话补全](https://docs.bigmodel.cn/api-reference/模型-api/对话补全)

### 约束（GLM-4V-Flash）

- 单次请求 **1 张图**
- **不支持 Base64**；优先本地绝对路径，或公网图片 URL
- 额度走智谱开放平台资源包；付费视觉模型余额不足时，Flash 仍可能可用

### 用法示例

把图片放到本地后，在对话里点名路径并说明要做什么：

```text
用 luma-vision / image_understand 分析这张图：
/Users/你的用户名/Downloads/screenshot.png
重点：截图表里每一列的含义，以及是否有报错。
```

合适场景：UI 截图解读、报错截图、OCR、示意图/架构图说明。

### 故障排查

| 现象 | 处理 |
|------|------|
| MCP 未出现 / 红灯 | 查 Node ≥ 18；刷新 MCP；看 Cursor MCP 日志 |
| `1113` 余额不足 | 到 [open.bigmodel.cn](https://open.bigmodel.cn/) 确认资源包；确认模型仍是 `glm-4v-flash` |
| 传图失败 | 改用绝对路径；不要贴 Base64；一次只给一张 |

## 2. 文生图：`mcp-image`

| 项 | 值 |
|----|-----|
| MCP 名 | `mcp-image` |
| 包 | `mcp-image`（npx，默认 Gemini 后端） |
| 密钥环境变量 | `GEMINI_API_KEY` |
| 输出目录 | `IMAGE_OUTPUT_DIR` → `~/.cursor/mcp-image-output` |
| 质量预设（工具参数） | 通常含 `fast` / `balanced` / `quality` |

### 用法示例

```text
用 mcp-image 生成一张知识库封面草图：
纯白背景，手绘小黑小人指着一块写着「Wiki」的白板，极简线稿。
保存到默认输出目录。
```

生成文件在 `~/.cursor/mcp-image-output/`。需要进仓库时，再手动拷到例如 `10_inbox/` 或素材目录，勿把该输出目录整夹提交。

### 故障排查

| 现象 | 处理 |
|------|------|
| 鉴权失败 | 确认 `GEMINI_API_KEY` 仍有效；可在 [Google AI Studio](https://aistudio.google.com/apikey) 核对 |
| 无输出文件 | 查 `IMAGE_OUTPUT_DIR` 是否存在、可写；看 MCP 日志 |
| 模型不可用 | 账号需具备 image 类模型（如 `gemini-*-image`）权限 |

## 与本知识库协作时的建议

1. **识图原料**：截图、白板照先落本地路径，再让 Agent 调 `luma-vision`；分析结果可写入笔记，图片本身按库规则另定是否入库。
2. **生图产物**：默认只当工作区草稿；要进库再 `git add` 明确路径，避免把整目录密钥侧文件混进提交。呈现 companion 约定落到 **`90_export/`**，不进 `20_领域/`。
3. **密钥**：只放在 `~/.cursor/mcp.json`；曾在聊天中出现过的 key 应轮换并更新该文件。
4. **命名约定**：对话里可说「用 luma 识图」「用 mcp-image 生图」，便于 Agent 选对 MCP。

### 与呈现 companion 的软接线（可选）

MCP 是**宿主能力**，不是 `npx skills` 安装依赖。呈现包约定：

| Companion | 有 `mcp-image` 时 | 无 MCP 时 |
|-----------|-------------------|-----------|
| `ian-xiaohei-illustrations` | 优先 `generate_image`（`16:9`）直出配图；可选 `luma-vision` 质检 | 内置生图或只交提示词 / shot list |
| `gbro-cover-design` | **必出提示词**后询问是否直出（`3:4`，可带人脸 `inputImagePath`） | 只交提示词，用户自选外部模型 |

核心 `wiki-gardener` / `domain-expert` **不**硬绑 MCP。未连接 MCP 时 companion 须降级，禁止假装已出图。

## 配置片段（不含真实密钥）

```json
{
  "mcpServers": {
    "luma-vision": {
      "command": "npx",
      "args": ["-y", "luma-mcp"],
      "env": {
        "MODEL_PROVIDER": "zhipu",
        "ZHIPU_API_KEY": "<你的智谱密钥>",
        "MODEL_NAME": "glm-4v-flash"
      }
    },
    "mcp-image": {
      "command": "npx",
      "args": ["-y", "mcp-image"],
      "env": {
        "GEMINI_API_KEY": "<你的 Gemini 密钥>",
        "IMAGE_OUTPUT_DIR": "/Users/<你的用户名>/.cursor/mcp-image-output"
      }
    }
  }
}
```

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-08-06 | 初版：接入 `luma-mcp` + `mcp-image`；识图模型定为 `glm-4v-flash` |
| 2026-08-06 | 补充：与 `ian-xiaohei` / `gbro-cover` 软接线约定；文档迁入 `docs/` |
