# Design Studio · 设计审美工坊（通用版）

使用 [Agent Skills](https://agentskills.io/specification) 格式的设计审美工坊。技能入口见 [`design-studio/SKILL.md`](design-studio/SKILL.md)。

内含 224 个设计流派及样式变量、92 个样张索引、35 份 DESIGN.md 索引、50 种图表选型，以及中文评审与制作流程。各上游项目的版本与授权见 [`design-studio/references/sources.md`](design-studio/references/sources.md)。

## 安装

把整个 `design-studio` 文件夹复制到对应工具的 skills 目录，例如：

| 工具 | 放入目录 |
| --- | --- |
| Claude Code | `.claude/skills/` |
| Cursor / Gemini CLI / OpenCode / Codex | `.agents/skills/` |
| VS Code GitHub Copilot | `.github/skills/` |

Claude 网页或桌面版可直接导入原始 ZIP（Customize → Skills → + → Upload a skill）。

## 授权

本仓库汇总整理自多个 MIT / Apache-2.0 授权项目，各自许可证全文保存在 [`design-studio/references/licenses/`](design-studio/references/licenses/)。
