"""Render docs/README.md and docs/README.fr.md as readable standalone HTML pages."""
import re
from pathlib import Path

import markdown

DOCS = Path(__file__).resolve().parent.parent / "docs"

PAGES = {
    "en": dict(src="README.md", out="README.en.html", other="README.fr.html", other_label="Français",
               toc="Contents", drawings="Drawings", lang_name="English",
               captions=["Plate", "Top case", "Bottom case", "Section A-A"],
               open_full="Open full size"),
    "fr": dict(src="README.fr.md", out="README.fr.html", other="README.en.html", other_label="English",
               toc="Sommaire", drawings="Dessins", lang_name="Français",
               captions=["Plaque", "Top case", "Bottom case", "Coupe A-A"],
               open_full="Ouvrir en grand"),
}
DRAWINGS = ["01_plate.svg", "02_top_case.svg", "03_bottom_case.svg", "04_section.svg"]

CSS = """
:root { --bg:#fbfaf8; --fg:#1f2328; --muted:#5d6670; --line:#e3e0da; --card:#ffffff;
        --accent:#b3141b; --accent-soft:#fbeaea; --code:#f3f1ed; --warn:#fff6e0; --warn-line:#e7b84a; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --bg:#16181c; --fg:#e6e6e6; --muted:#9aa3ad; --line:#2c3036; --card:#1d2025;
        --accent:#ff6b70; --accent-soft:#3a1d20; --code:#23262c; --warn:#2e2714; --warn-line:#a8842f; } }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin:0; background:var(--bg); color:var(--fg);
       font:16px/1.65 "Inter", system-ui, -apple-system, "Segoe UI", sans-serif; }
.layout { display:grid; grid-template-columns: 250px minmax(0, 1fr); max-width:1200px; margin:0 auto; gap:40px; padding:0 24px; }
nav { position:sticky; top:0; align-self:start; max-height:100vh; overflow:auto; padding:32px 0; font-size:14px; }
nav .lang { display:inline-block; margin-bottom:24px; padding:6px 12px; border:1px solid var(--line);
            border-radius:999px; color:var(--fg); text-decoration:none; background:var(--card); }
nav .lang:hover { border-color:var(--accent); color:var(--accent); }
nav h2 { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin:0 0 8px; }
nav ul { list-style:none; margin:0; padding:0; }
nav li a { display:block; padding:5px 10px; border-left:2px solid var(--line); color:var(--muted); text-decoration:none; }
nav li a:hover { color:var(--fg); border-left-color:var(--accent); }
main { padding:32px 0 96px; min-width:0; }
h1 { font-size:2.1rem; line-height:1.2; margin:0 0 16px; }
h2 { font-size:1.45rem; margin:56px 0 16px; padding-top:8px; border-top:1px solid var(--line); }
h3 { font-size:1.1rem; margin:32px 0 10px; }
p, li { max-width:75ch; }
a { color:var(--accent); }
strong { font-weight:650; }
code { font:0.88em/1.4 ui-monospace, "Cascadia Code", Consolas, monospace; background:var(--code);
       padding:2px 6px; border-radius:5px; }
pre { background:var(--code); padding:14px 16px; border-radius:8px; overflow:auto; }
pre code { padding:0; background:none; }
.table-wrap { overflow-x:auto; margin:16px 0; border:1px solid var(--line); border-radius:10px; background:var(--card); }
table { border-collapse:collapse; width:100%; font-size:15px; }
th, td { text-align:left; vertical-align:top; padding:9px 12px; border-bottom:1px solid var(--line); }
tr:last-child td { border-bottom:none; }
th { font-size:13px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); background:var(--code); }
thead tr th:empty { display:none; }
main > p:first-of-type { font-size:1.08rem; }
.callout { background:var(--warn); border-left:4px solid var(--warn-line); border-radius:8px; padding:4px 20px 8px; margin:24px 0; }
.callout h3 { margin-top:16px; }
ol { padding-left:0; counter-reset:step; list-style:none; }
ol > li { counter-increment:step; position:relative; padding:12px 16px 12px 56px; margin:10px 0;
          background:var(--card); border:1px solid var(--line); border-radius:10px; max-width:none; }
ol > li::before { content:counter(step); position:absolute; left:14px; top:11px; width:28px; height:28px;
                  border-radius:50%; background:var(--accent-soft); color:var(--accent); font-weight:700;
                  display:grid; place-items:center; font-size:14px; }
ol ol > li { background:transparent; border:none; padding:4px 0 4px 36px; margin:2px 0; }
ol ol > li::before { width:22px; height:22px; top:5px; left:0; font-size:12px; }
.drawings { display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:16px; }
figure { margin:0; background:#fff; border:1px solid var(--line); border-radius:10px; padding:12px; }
figure img { width:100%; height:auto; display:block; }
figcaption { margin-top:8px; font-size:14px; color:#444; display:flex; justify-content:space-between; }
figcaption a { color:#b3141b; }
@media (max-width: 860px) {
  .layout { grid-template-columns:1fr; gap:0; padding:0 16px; }
  nav { position:static; max-height:none; padding:20px 0 0; }
  nav ul { display:none; }
  h1 { font-size:1.7rem; }
}
"""


def _normalize_lists(text):
    """Python-Markdown needs 4-space indentation for nested lists."""
    return re.sub(r"^ {1,3}(?=(\d+\.|-) )", "    ", text, flags=re.M)


def _postprocess(html):
    html = re.sub(r"<table>", '<div class="table-wrap"><table>', html)
    html = html.replace("</table>", "</table></div>")
    # wrap the "⚠" section (h3 up to the next h2) in a callout box
    html = re.sub(r'(<h3 id="[^"]*">⚠.*?)(?=<h2)', r'<div class="callout">\1</div>', html, flags=re.S)
    return html


def build(lang):
    cfg = PAGES[lang]
    text = _normalize_lists((DOCS / cfg["src"]).read_text(encoding="utf-8"))
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "toc"],
                           extension_configs={"toc": {"toc_depth": "2-2"}})
    body = _postprocess(md.convert(text))
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    def h2s(tokens):
        for t in tokens:
            if t["level"] == 2:
                yield t
            yield from h2s(t["children"])
    toc = "".join(f'<li><a href="#{t["id"]}">{t["name"]}</a></li>' for t in h2s(md.toc_tokens))
    toc += f'<li><a href="#drawings">{cfg["drawings"]}</a></li>'
    figs = "".join(
        f'<figure><a href="drawings/{d}"><img src="drawings/{d}" alt="{c}" loading="lazy"></a>'
        f'<figcaption><span>{c}</span><a href="drawings/{d}">{cfg["open_full"]} ↗</a></figcaption></figure>'
        for d, c in zip(DRAWINGS, cfg["captions"]))
    page = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="layout">
<nav>
  <a class="lang" href="{cfg['other']}">🌐 {cfg['other_label']}</a>
  <h2>{cfg['toc']}</h2>
  <ul>{toc}</ul>
</nav>
<main>
{body}
<h2 id="drawings">{cfg['drawings']}</h2>
<div class="drawings">{figs}</div>
</main>
</div>
</body>
</html>
"""
    (DOCS / cfg["out"]).write_text(page, encoding="utf-8")
    print("wrote", cfg["out"])


if __name__ == "__main__":
    for lang in PAGES:
        build(lang)
