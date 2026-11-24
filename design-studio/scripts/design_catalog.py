"""Look up design references and render portable style specimens."""

import argparse
import html
import json
import re
import sys
import unicodedata
from pathlib import Path


CATALOG = Path(__file__).resolve().parents[1] / "references" / "catalog"
SOURCES = {
    "artisan": ("artisan-*.json", "设计流派与样式变量"),
    "huashu": ("huashu.json", "按交付物分类的设计样张索引"),
    "design-md": ("design-md.json", "按风格家族分类的 DESIGN.md 参考"),
    "anchors": ("anchors.json", "前端视觉方向"),
    "palettes": ("palettes.json", "行业配色"),
    "type": ("type.json", "西文字体组合"),
    "diagram": ("diagrams.json", "图表与示意图选型"),
}
CSS_NAME = re.compile(r"[A-Za-z0-9-]+\Z")
CSS_UNSAFE = re.compile(
    r"[;{}<>\\\x00-\x1f\x7f]|/\*|\*/|\b(?:url|expression|image-set|src|attr)\s*\(",
    re.IGNORECASE,
)
HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?\Z")


def load_catalog():
    entries = {}
    for source, (pattern, _) in SOURCES.items():
        paths = sorted(CATALOG.glob(pattern))
        if not paths:
            raise ValueError(f"目录文件缺失 {pattern}")
        for path in paths:
            for entry in json.loads(path.read_text(encoding="utf-8")):
                key = f"{source}:{entry['slug']}"
                if key in entries:
                    raise ValueError(f"目录编号重复 {key}")
                entries[key] = {**entry, "id": key, "source": source}
    return entries


def normalize(value):
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[\W_]+", " ", value).strip()


def search(entries, query, source=None):
    query = normalize(query)
    if not query:
        raise ValueError("请输入可检索的风格名、别名或分类")
    terms = query.split()
    matches = []
    for entry in entries.values():
        if source and entry["source"] != source:
            continue
        names = [normalize(value) for value in (
            entry["slug"], entry["name"], *entry.get("aliases", []),
        )]
        category = normalize(entry["category"])
        keywords = " ".join((*names, category))
        if query in names or query == category:
            priority = 0
        elif any(query in name for name in names):
            priority = 1
        elif all(term in keywords for term in terms):
            priority = 2
        else:
            continue
        matches.append((priority, normalize(entry["name"]), entry["id"], entry))
    return [item[-1] for item in sorted(matches)]


def resolve(entries, selector):
    key = unicodedata.normalize("NFKC", selector).casefold().strip()
    if key in entries:
        return entries[key]
    matches = [
        entry for entry in search(entries, selector)
        if normalize(selector) in {
            normalize(value) for value in (
                entry["slug"], entry["name"], *entry.get("aliases", []),
            )
        }
    ]
    if len(matches) == 1:
        return matches[0]
    if matches:
        keys = "、".join(entry["id"] for entry in matches[:10])
        raise ValueError(f"“{selector}”有多个匹配项，请使用完整编号，例如 {keys}")
    raise ValueError(f"找不到“{selector}”，可先用 search 查看编号")


def preview_entry(entry):
    fields = ("id", "name", "category", "aliases", "use", "layout", "reference")
    return {key: entry[key] for key in fields if key in entry}


def as_json(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def css_value(value):
    if isinstance(value, str) and value.strip() and not CSS_UNSAFE.search(value):
        return value.strip()
    return None


def print_tokens(entry):
    declarations = []
    skipped = 0
    for group, values in entry.get("tokens", {}).items():
        for key, raw in values.items():
            value = css_value(raw)
            if not value or not CSS_NAME.fullmatch(group) or not CSS_NAME.fullmatch(key):
                skipped += 1
                continue
            declarations.append(f"  --{group}-{key}: {value};")
    if not declarations:
        raise ValueError(f"{entry['id']} 暂无可导出的 CSS 变量")
    print(":root {\n" + "\n".join(declarations) + "\n}")
    if skipped:
        print(f"跳过 {skipped} 项含内嵌资源或不完整的 CSS 值，可用 show 查看原值。", file=sys.stderr)


def luminance(color):
    if not HEX_COLOR.fullmatch(color):
        raise ValueError(f"颜色须为 #RGB 或 #RRGGBB，收到 {color!r}")
    digits = color[1:]
    if len(digits) == 3:
        digits = "".join(char * 2 for char in digits)
    channels = [int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [
        v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
        for v in channels
    ]
    return sum(weight * channel for weight, channel in zip((0.2126, 0.7152, 0.0722), linear))


def contrast_ratio(foreground, background):
    low, high = sorted((luminance(foreground), luminance(background)))
    return (high + 0.05) / (low + 0.05)


def legible_text(preferred, background):
    if contrast_ratio(preferred, background) >= 4.5:
        return preferred
    return max(("#171717", "#FFFFFF", "#000000"), key=lambda value: contrast_ratio(value, background))


def swatch_card(entry):
    colors = {
        key: value for key, value in entry.get("tokens", {}).get("color", {}).items()
        if isinstance(value, str) and HEX_COLOR.fullmatch(value)
    }
    if not colors:
        raise ValueError(f"{entry['id']} 暂无可用于对比的纯色值")

    def get_color(default, *keys):
        return next((colors[key] for key in keys if key in colors), default)

    bg = get_color("#FFFFFF", "bg", "background", "canvas")
    fg = get_color(legible_text("#171717", bg), "text", "fg", "ink", "foreground")
    primary = get_color(fg, "primary", "accent", "link", "signal", "brand")
    on_primary = get_color("#FFFFFF", "on-primary", "primary-foreground", "on-accent")
    fonts = entry.get("tokens", {}).get("font", {})
    display = css_value(fonts.get("display")) or css_value(fonts.get("sans")) or "system-ui"
    body = css_value(fonts.get("sans")) or css_value(fonts.get("body")) or "system-ui"
    display_name = html.escape(entry["name"])
    safe_styles = html.escape(
        f"--sample-bg:{bg};--sample-ink:{legible_text(fg, bg)};"
        f"--sample-primary:{primary};--sample-on-primary:{legible_text(on_primary, primary)};"
        f"--sample-display:{display},system-ui,sans-serif;--sample-body:{body},system-ui,sans-serif;",
        quote=True,
    )
    swatches = "".join(
        f'<li><span style="background-color:{value}"></span>'
        f"<code>{html.escape(key)} {value.upper()}</code></li>"
        for key, value in colors.items()
    )
    metadata = [
        f"正文与背景 {contrast_ratio(fg, bg):.2f}:1",
        f"标题字体 {display}",
    ]
    if legible_text(fg, bg) != fg:
        metadata.append("样张正文使用可读性更高的颜色。")
    details = "".join(f"<p>{html.escape(line)}</p>" for line in metadata)
    reference = entry.get("reference", "")
    reference_link = ""
    if reference.startswith("https://github.com/"):
        reference_link = f'<a href="{html.escape(reference, quote=True)}">查看风格参考</a>'
    return f"""
      <article>
        <header class="card-head">
          <h2>{display_name}</h2>
          <p>{html.escape(entry["category"])}</p>
        </header>
        <section class="specimen" style="{safe_styles}" aria-label="{display_name}字体与色板样张">
          <div class="type-sample">Aa 设计有章法</div>
          <p>标题、正文与强调色的组合</p>
          <span class="accent-sample">强调色</span>
        </section>
        <div class="details">
          <ul class="swatches">{swatches}</ul>
          {details}
          {reference_link}
        </div>
      </article>"""


def write_comparison(entries, output):
    if not 2 <= len(entries) <= 6 or len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("请选择 2 至 6 个不同的风格或配色")
    output = output.expanduser().resolve()
    if output.suffix.lower() not in (".html", ".htm"):
        raise ValueError("样张的输出文件应使用 .html 或 .htm")
    cards = "".join(swatch_card(entry) for entry in entries)
    document = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>设计风格对比</title>
<style>
:root { color-scheme: light; background: #f3f0e9; color: #222821;
  font-family: system-ui, "PingFang SC", "Microsoft YaHei", sans-serif; }
* { box-sizing: border-box; }
body { margin: 0; }
main { max-width: 88rem; margin: auto; padding: clamp(1.25rem, 4vw, 4rem); }
h1 { margin: 0; font: 600 clamp(2rem, 5vw, 3.5rem)/1.15 Georgia, "Songti SC", SimSun, serif; }
.intro { margin: 0 0 1.75rem; padding: 0 0 1.4rem; border-bottom: 1px solid #9faaa0; }
.intro p { margin: .65rem 0 0; color: #46554b; }
.gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  gap: 1rem; align-items: start; }
article { min-width: 0; background: #fffdfa; border: 1px solid #bfc6ba; }
.card-head, .details { padding: 1rem; }
.card-head h2 { margin: 0; font-size: 1.15rem; overflow-wrap: anywhere; }
.card-head p, .details p { margin: .35rem 0 0; color: #46554b; overflow-wrap: anywhere; }
.specimen { min-height: 12rem; padding: 1.2rem; background: var(--sample-bg);
  color: var(--sample-ink); font-family: var(--sample-body); border-block: 1px solid #bfc6ba; }
.specimen p { margin: .7rem 0 1rem; }
.type-sample { font: 600 clamp(1.5rem, 2.6vw, 2.5rem)/1.15 var(--sample-display);
  overflow-wrap: anywhere; }
.accent-sample { display: inline-block; padding: .25rem .6rem; font-weight: 600;
  background: var(--sample-primary); color: var(--sample-on-primary); }
.swatches { padding: 0; margin: 0 0 1rem; display: grid; grid-template-columns: 1fr 1fr;
  gap: .5rem; list-style: none; }
.swatches li { display: flex; align-items: start; gap: .4rem; min-width: 0; }
.swatches span { flex: 0 0 1rem; height: 1rem; border: 1px solid #747d73; }
.swatches code { font-size: .78rem; overflow-wrap: anywhere; }
a { color: #234d36; display: inline-block; margin-top: .85rem; }
a:focus-visible { outline: 2px solid #234d36; outline-offset: 3px; }
</style>
</head>
<body>
<main>
  <header class="intro"><h1>设计风格对比</h1><p>比较配色、字形和正文可读性。</p></header>
  <section class="gallery" aria-label="风格样张">
""" + cards + """
  </section>
</main>
</body>
</html>
"""
    output.write_text(document, encoding="utf-8")
    print(output)


def parser_for_commands():
    parser = argparse.ArgumentParser(description="设计审美工坊的本地目录与样张工具")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("overview", help="查看各资料来源和条目数量")
    find = commands.add_parser("search", help="按风格名、分类或中文别名检索")
    find.add_argument("query", nargs="+")
    find.add_argument("--source", choices=SOURCES)
    find.add_argument("--limit", type=int, default=12)
    commands.add_parser("show", help="查看完整条目").add_argument("selector")
    commands.add_parser("tokens", help="输出可用 CSS 变量").add_argument("selector")
    compare = commands.add_parser("compare", help="生成独立 HTML 样张")
    compare.add_argument("selectors", nargs="+")
    compare.add_argument("-o", "--output", required=True, type=Path)
    contrast = commands.add_parser("contrast", help="计算实色文字与背景的对比")
    contrast.add_argument("foreground")
    contrast.add_argument("background")
    return parser


def main():
    parser = parser_for_commands()
    args = parser.parse_args()
    try:
        if args.command == "contrast":
            ratio = contrast_ratio(args.foreground, args.background)
            as_json({
                "ratio": f"{ratio:.2f}:1",
                "aa_normal_text": ratio >= 4.5,
                "aa_large_text": ratio >= 3,
                "aaa_normal_text": ratio >= 7,
            })
            return

        entries = load_catalog()
        if args.command == "overview":
            as_json({
                source: {"description": details[1], "count": sum(
                    entry["source"] == source for entry in entries.values()
                )}
                for source, details in SOURCES.items()
            })
        elif args.command == "search":
            if not 1 <= args.limit <= 200:
                raise ValueError("--limit 需要在 1 至 200 之间")
            matches = search(entries, " ".join(args.query), args.source)
            as_json({"total": len(matches), "results": [preview_entry(e) for e in matches[:args.limit]]})
        elif args.command == "show":
            as_json(resolve(entries, args.selector))
        elif args.command == "tokens":
            print_tokens(resolve(entries, args.selector))
        elif args.command == "compare":
            write_comparison([resolve(entries, selector) for selector in args.selectors], args.output)
    except (OSError, ValueError) as error:
        parser.exit(2, f"错误：{error}\n")


if __name__ == "__main__":
    main()
