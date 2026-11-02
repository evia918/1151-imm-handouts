#!/usr/bin/env python3
"""
1151 互動媒體製作｜W10–W18 網頁版講義產檔腳本
用法：python3 _build/build.py          （在 repo 根目錄執行）
說明：
  - 樣式沿用 w5.html（基底＋W05 擴充：程式碼區塊、檢核點 details）與 w6.html（compare / stat）
  - 翻頁腳本沿用 w9.html（通用版，不含 W05 互動示範）
  - 各週內容放在 _build/wNN.html，第一行為 META 註解（JSON），其餘為 <section class="slide"> 片段
  - 底線開頭資料夾不會被 GitHub Pages（Jekyll）發布
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_build"


def extract(path, start, end):
    """擷取既有講義中 start…end 之間的區塊（含標記本身）"""
    s = (ROOT / path).read_text(encoding="utf-8")
    i = s.index(start)
    j = s.index(end, i) + len(end)
    return s[i:j]


# --- 1. 共用樣式：w5 全部 CSS ＋ w6 的 compare/stat ＋本批新增 ---
css = extract("w5.html", "<style>", "</style>")
w6_css = extract("w6.html", "<style>", "</style>")
w6_extra = "\n".join(
    line for line in w6_css.splitlines()
    if re.match(r"^\.(compare|stat)", line) or line.startswith("@media(max-width:640px){.compare")
)
EXTRA = """
/* ===== W10–W18 擴充 ===== */
%s
pre.code.wrap{white-space:pre-wrap;word-break:break-all}
.route{border-radius:14px;padding:16px 18px;background:var(--surface);border:1px solid var(--line-soft);box-shadow:var(--shadow)}
.route.a{border-top:3px solid var(--ai)} .route.b{border-top:3px solid var(--brand)}
.route .tag{display:block;margin-bottom:6px}
.chk{list-style:none;padding-left:0}
.chk li{padding-left:1.6em;position:relative}
.chk li::before{content:"□";position:absolute;left:0;color:var(--brand);font-family:var(--f-mo)}
.big-num{font-family:var(--f-la);font-weight:800;font-size:clamp(28px,5vw,40px);color:var(--brand);line-height:1}
.flow{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13.5px}
.flow span{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:6px 10px}
.flow i{font-style:normal;color:var(--ink-3);font-family:var(--f-mo)}
""" % w6_extra
css = css.replace("</style>", EXTRA + "</style>")

# --- 2. 共用翻頁腳本（w9 通用版） ---
script = extract("w9.html", "<script>", "</script>")

HEAD = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>互動媒體製作 {cn}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,500;0,600;0,700;0,800;1,500&family=IBM+Plex+Mono:wght@400;600&family=Noto+Sans+TC:wght@400;500;700;900&display=swap">
{css}
</head>
<body>
<header class="topbar">
  <div class="brand">互動媒體製作 · <span>{cn}</span></div>
  <div class="lockchip">分段交付制 · AI Agent 協作</div>
  <div class="sp"></div>
  <a class="tbtn" href="index.html" style="text-decoration:none">目錄</a>
  <button class="tbtn" id="themebtn" type="button">◐</button>
</header>
<div class="progress"><i id="bar"></i></div>

<main class="stage" id="stage" tabindex="-1">
{body}
</main>

<nav class="navbar">
  <button class="navbtn" id="prevBtn" type="button">← 上一頁</button>
  <div class="counter"><b id="curNo">1</b> / <span id="totNo">1</span>　<span id="curLabel"></span></div>
  <select class="jump" id="jump" aria-label="跳到指定頁面"></select>
  <button class="navbtn" id="nextBtn" type="button">下一頁 →</button>
</nav>

{script}
</body>
</html>
"""

for src in sorted(SRC.glob("w*.html")):
    raw = src.read_text(encoding="utf-8")
    first, body = raw.split("\n", 1)
    meta = json.loads(re.match(r"<!--META (.*)-->", first).group(1))
    out = HEAD.format(cn=meta["cn"], css=css, body=body.strip(), script=script)
    (ROOT / src.name).write_text(out, encoding="utf-8")
    n = body.count('class="slide')
    print(f"built {src.name}: {n} slides")
