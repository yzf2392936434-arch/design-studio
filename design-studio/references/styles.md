# 选择设计风格

先找用户提供的品牌资料、页面和已有 CSS 变量。品牌颜色、真实字号和组件约束从可见证据读出。只有品牌名时，当前会话能读官方资料就核实，缺少可核实的内容时把色板写作提案。

## 用哪套资料

| 需求 | 本包资料 |
| --- | --- |
| 找一种设计流派并把它落实到界面 | [按流派查样式变量](catalog/README.md)。224 个流派，包含色彩、字体、间距、描边、圆角、阴影等分组。 |
| 按交付物找方向和线上样张 | [花叔样张索引](catalog/huashu.json)。网页、PPT、信息图、App、中文及东亚、小红书共 92 个索引。 |
| 看现成 DESIGN.md 怎么写 | [DESIGN.md 索引](catalog/design-md.json)。35 份按风格家族分类的示例，包括混搭参考。 |
| 做前端时快速锁定一套视觉语言 | [前端视觉方向](catalog/anchors.json)。8 个方向，带明确构图、颜色、字体、质感及 CSS 起始值。 |
| 找行业配色或字体组合 | [配色](catalog/palettes.json)与[字体](catalog/type.json)。64 套配色、39 套西文字体组合。字号、字体供应和中文字形在落地前验证。 |

## 方向怎么比较

1. 根据阅读任务、受众和内容密度定方向。有长正文的页面先看阅读节奏，后台先看可扫读性，展会或产品发布先看远距离识别度和素材。历史流派应用到界面时，从排版秩序、几何、色彩和印刷语言推导。
2. 给候选写具体差异。以头皮护理产品页为例，「暖色编辑排版」可以用近景产品照片、细分栏和大留白，「产品证据型」以功效证据与使用步骤形成首屏，「门店服务型」把预约与服务流程放在靠前位置。每个方向附配色、标题风格、素材需求和适用性。
3. 选定一套主规则。混搭时写明哪套控制版式，哪套只影响字体、颜色或纹理。标题或视觉装饰可以表现风格，按钮和正文仍需要清晰可读。

可供判断的风格家族包括编辑极简、暖色编辑、终端式、密集数据界面、深色电影感、俏皮撞色、通透未来、粗野主义和独立品牌。编辑极简适合长文或作品集，终端式适合命令和日志，深色电影感依赖扎实的原始影像，通透风格要验证纹理上方的文字对比。

## 可复用的 DESIGN.md

用户想把视觉方向交给下一次开发时，可以写成 `DESIGN.md`。包含用途和读者、主视觉规则、背景/正文/边框/强调/状态的颜色角色、字号和字体回退、间距和栅格、圆角与边框、主要组件及状态、响应式变化、图片策略和实际可验收条件。现有仓库已采用设计 token 时对照原命名更新。

## 本地命令

下例从 `SKILL.md` 所在的 `design-studio/` 目录运行，或将脚本改为实际绝对路径。Windows 可将 `python3` 换成 `py -3`。JSON 查询可用 `--source artisan`、`huashu`、`design-md`、`anchors`、`palettes`、`type`、`diagram` 过滤。

```text
python3 scripts/design_catalog.py overview
python3 scripts/design_catalog.py search 侘寂 --source artisan
python3 scripts/design_catalog.py search 小红书 --source huashu --limit 10
python3 scripts/design_catalog.py show artisan:bauhaus
python3 scripts/design_catalog.py show anchors:swiss
python3 scripts/design_catalog.py tokens artisan:bauhaus
python3 scripts/design_catalog.py compare artisan:zen-wabisabi artisan:bauhaus anchors:swiss --output ./style-comparison.html
python3 scripts/design_catalog.py contrast "#33302A" "#F2EDE4"
```

`compare` 生成可独立打开的 HTML 配色与字体样张，适用于有可用色板的条目。它使用系统可用字体。页面方向预览另按用户内容和尺寸制作。花叔样张和 DESIGN.md 参考用结果中的 `reference` 链接打开。
