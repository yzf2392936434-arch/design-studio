# 设计审美工坊 · 通用版

使用 [Agent Skills](https://agentskills.io/specification) 格式。技能入口是 [SKILL.md](SKILL.md)。内含 224 个设计流派及样式变量、92 个样张索引、35 份 DESIGN.md 索引、50 种图表选型，以及中文评审和制作流程。上游样张通过原链接访问。各项目的版本和授权见[来源说明](references/sources.md)。

## 选自己的 AI

Claude 网页或桌面版可以直接导入原 ZIP。进入 **Customize → Skills → + → Upload a skill**，选择 ZIP，导入后启用。若界面提示开启文件创建和代码执行，按账户设置启用。[Claude 官方说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

本地工具先解压压缩包，再把整个 `design-studio` 文件夹放进下表目录。表里的路径从你打开的项目根目录算起。放好后新开一轮会话。

| 工具 | 放入目录 | 如何使用 |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | 输入 `/design-studio`。[官方说明](https://code.claude.com/docs/en/skills) |
| Cursor | `.agents/skills/` | 在 Agent 对话输入 `/`，选择 `design-studio`。[官方说明](https://cursor.com/docs/skills) |
| Gemini CLI | `.agents/skills/` | 用 `/skills list` 确认，发消息「请用 design-studio……」。[官方说明](https://geminicli.com/docs/cli/skills/) |
| OpenCode | `.agents/skills/` | 直接说「请用 design-studio……」。[官方说明](https://opencode.ai/docs/skills/) |
| Codex | `.agents/skills/` | 输入 `$design-studio`，或发消息「请用 design-studio……」。[官方说明](https://learn.chatgpt.com/docs/build-skills) |
| VS Code GitHub Copilot | `.github/skills/` | 在聊天输入 `/` 并选择技能，或直接说设计需求。[官方说明](https://code.visualstudio.com/docs/agent-customization/agent-skills) |

以 Cursor 为例，复制完成后文件位置是 `你的项目/.agents/skills/design-studio/SKILL.md`。新建缺失的目录即可。参考资料和脚本要跟随整个文件夹一起复制。

## 普通 AI 聊天

DeepSeek、豆包、Kimi 或其他只有聊天入口的 AI，可以将 [chat-prompt.txt](references/chat-prompt.txt) 全文粘贴到新对话，然后上传截图或描述需求。这样可以进行审美体检、比较版式、拟定设计规范和规划图表。完整目录查询依赖 AI 能读取随包资料，生成文件和实际预览取决于该 AI 可用的工具。

## 可以这样说

- 「审美体检这张洗发水海报。保留产品包装和原文案，按优先级给三条能直接改的建议。」
- 「给这个品牌落地页出三个设计方向，每版写清首屏、色板和素材需求。」
- 「把这套门店服务画成泳道图，区分顾客、门店和总部。」

本地查询、CSS 变量、HTML 风格对比和文字对比度工具的用法见[风格和资料](references/styles.md)。这些辅助命令使用 Python 3 标准库。
