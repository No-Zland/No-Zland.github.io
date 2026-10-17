# -*- coding: utf-8 -*-
"""
板块式个人博客静态生成器
- 首页: 座右铭 + 大板块卡片（竞赛 / 项目 / 科研 / 技能 / 课程 / 阅读 / 个人）
- 板块页: 该板块下的分类列表
- 分类页: 子分类列表，或文章阅读页
- 阅读页: 多篇文章默认分页阅读，可切换连续阅读；长文按章节分页
- 左侧抽屉: 对外个人主页（GitHub / 哔哩哔哩 / 邮箱）与更新日历
- 支持浅色/暗色主题、中英切换（梁双宇 / Shine Leong）
"""
import os
import re
import sys
import json
import html
import hashlib
import shutil
import urllib.parse
from collections import defaultdict
from datetime import datetime

import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "src")
POST_DIR = os.path.join(ROOT, "content", "post")
SITE_DIR = os.path.join(ROOT, "site")
ASSET_DIR = os.path.join(SITE_DIR, "assets")
RES_DIR = os.path.join(ASSET_DIR, "files")  # 复制的图片资源
PDF_DIR = os.path.join(RES_DIR, "pdf")  # 复制的 PDF 资料
AVATAR_NAME = None  # 站点头像文件名（位于 assets 下），main() 中检测
UPDATES_JSON = "{}"  # 博客更新日期统计，main() 中写入
MUSIC_JSON = "[]"  # 音乐播放列表，main() 中写入
DOC_TITLE = {}  # 文章标题，渲染时收集
DOC_TEXT = {}  # 文章纯文本，渲染时收集
NAV_SECTIONS = []  # 侧栏层级导航数据，main 中构建
SEARCH_TEXT_LIMIT = 30000  # 单篇索引的正文上限，避免超长笔记撑大索引
MAX_PDF_BYTES = 10 * 1024 * 1024  # GitHub Pages 只上传 10MB 以内的 PDF

SECTION_SPECS = [
    {
        "slug": "竞赛经历",
        "title": "竞赛经历",
        "desc": "数学建模、程序设计、嵌入式与算法竞赛的参赛记录、复盘和资料。",
        "color": "#7c3aed",
        "cats": ["竞赛", "数学建模"],
    },
    {
        "slug": "项目经历",
        "title": "项目经历",
        "desc": "从需求、设计到实现的项目记录。",
        "color": "#0ea5b7",
        "cats": ["项目"],
    },
    {
        "slug": "科研经历",
        "title": "科研经历",
        "desc": "参考文献、研究调研与科研训练记录。",
        "color": "#db2777",
        "cats": ["疲倦程度识别参考文献"],
    },
    {
        "slug": "技能学习",
        "title": "技能学习",
        "desc": "编程语言、Linux、AI、IT 素养与算法刷题的持续积累。",
        "color": "#2563eb",
        "cats": ["AI", "C++", "Python", "Linux系统", "IT素养", "算法与刷题"],
    },
    {
        "slug": "课程学习",
        "title": "课程学习",
        "desc": "计算机专业课程笔记、实验与知识整理。",
        "color": "#16a34a",
        "cats": ["C语言", "数字电路", "汇编语言与接口技术", "计算机组成原理", "通信协议"],
    },
    {
        "slug": "阅读及感悟",
        "title": "阅读及感悟",
        "desc": "书目、阅读计划，以及读书过程中的零散感悟。",
        "color": "#c2410c",
        "cats": ["书籍资料"],
    },
    {
        "slug": "个人与总结",
        "title": "个人与总结",
        "desc": "个人档案、阶段总结和实验报告合集。",
        "color": "#d4af37",
        "cats": ["个人", "实验总结"],
    },
]


def build_nav_sections(sections, docs, child_dirs):
    nav = []
    for section in sections:
        cats = []
        total = 0
        for cat in section["cats"]:
            count = len(docs_under(docs, cat))
            total += count
            subs = []
            for sub in child_dirs.get(cat, []):
                subs.append({
                    "rel": sub,
                    "name": os.path.basename(sub),
                    "count": len(docs_under(docs, sub)),
                })
            cats.append({"name": cat, "count": count, "subs": subs})
        nav.append({
            "slug": section["slug"],
            "title": section["title"],
            "color": section["color"],
            "total": total,
            "cats": cats,
        })
    return nav


def section_for_category(cat):
    for spec in SECTION_SPECS:
        if cat in spec["cats"]:
            return spec
    return None


def build_sections(l1):
    """按配置生成当前实际存在的大板块，未知分类归入“其他”。"""
    sections = []
    used = set()
    for spec in SECTION_SPECS:
        cats = [cat for cat in spec["cats"] if cat in l1]
        if not cats:
            continue
        section = dict(spec)
        section["cats"] = cats
        sections.append(section)
        used.update(cats)
    unknown = [cat for cat in l1 if cat not in used and not cat.startswith(".")]
    if unknown:
        sections.append({
            "slug": "其他",
            "title": "其他",
            "desc": "暂未归入其他板块的内容。",
            "color": "#64748b",
            "cats": unknown,
        })
    return sections

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}
SKIP_DIRS = {"bin", "node_modules", "__pycache__"}

MATHJAX_HEAD = '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>'


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def esc(s):
    return html.escape(str(s), quote=True)


def doc_anchor(rel):
    """为每篇文章生成稳定的页内锚点，用于搜索结果直接跳转。"""
    return "doc-" + hashlib.md5(rel.encode("utf-8")).hexdigest()[:10]


def html_to_text(s):
    """把渲染后的 HTML 压成纯文本，供搜索索引使用。"""
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def read_text(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def is_image(path):
    return os.path.splitext(path)[1].lower() in IMAGE_EXTS


# --------------------------------------------------------------------------- #
# 扫描 content/post, 收集文档、图片、以及每个目录的最早文件修改时间(作为创立时间)
# --------------------------------------------------------------------------- #
def scan():
    docs = []
    images = defaultdict(list)
    dir_earliest = {}  # 目录(相对) -> 最早 mtime

    def touch(rel_dir, mtime):
        d = rel_dir
        while True:
            if d not in dir_earliest or mtime < dir_earliest[d]:
                dir_earliest[d] = mtime
            if not d:
                break
            d = os.path.dirname(d)

    for dirpath, dirnames, filenames in os.walk(POST_DIR):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, POST_DIR)
        if rel_dir == ".":
            rel_dir = ""
        for fn in filenames:
            if fn.startswith(".") or fn.startswith("~"):
                continue
            abs_path = os.path.join(dirpath, fn)
            try:
                mtime = os.path.getmtime(abs_path)
            except OSError:
                continue
            touch(rel_dir, mtime)

            if fn.lower().endswith(".md"):
                if fn in ("_index.md", "个人简历.md"):
                    continue
                rel = os.path.relpath(abs_path, POST_DIR)
                docs.append(rel)
            elif is_image(abs_path):
                images[fn.lower()].append(abs_path)

    docs.sort(key=lambda r: natural_key(r.replace("\\", "/")))
    return docs, images, dir_earliest


def collect_updates(docs):
    """按文章文件修改日期统计博客更新次数，用于日历打卡。"""
    counts = defaultdict(int)
    for rel in docs:
        try:
            mtime = os.path.getmtime(os.path.join(POST_DIR, rel))
        except OSError:
            continue
        counts[datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")] += 1
    return dict(sorted(counts.items()))


def strip_frontmatter(text):
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, min(len(lines), 40)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:])
    return text


def extract_title(text, fallback):
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            t = s[2:].strip()
            t = re.sub(r"#+", "", t).strip()
            if t:
                return t
    return fallback


# --------------------------------------------------------------------------- #
# 资源复制与相对链接
# --------------------------------------------------------------------------- #
def rel_from(out_dir, target_abs):
    return os.path.relpath(target_abs, out_dir).replace("\\", "/")


def quote_url(path):
    return urllib.parse.quote(path.replace("\\", "/"), safe="/-_.!~*'()")


def copy_asset(src_abs, out_dir):
    rel = os.path.relpath(src_abs, POST_DIR)
    dest = os.path.join(RES_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src_abs, dest)
    return quote_url(rel_from(out_dir, dest))


def copy_avatar():
    """把根目录的头像复制到 assets；没有头像时返回 None，页面显示默认头像。"""
    candidates = ("头像.jpg", "头像.jpeg", "头像.png", "头像.webp", "avatar.jpg", "avatar.png")
    for name in candidates:
        src = os.path.join(ROOT, name)
        if os.path.isfile(src):
            ext = os.path.splitext(name)[1].lower()
            dest_name = "avatar" + ext
            shutil.copy2(src, os.path.join(ASSET_DIR, dest_name))
            return dest_name
    return None


def copy_music():
    src = os.path.join(ROOT, "music")
    if not os.path.isdir(src):
        return
    dest = os.path.join(ASSET_DIR, "music")
    shutil.copytree(src, dest, dirs_exist_ok=True)


def load_music_playlist():
    path = os.path.join(ROOT, "music", "playlist.json")
    try:
        raw = json.loads(read_text(path))
        if isinstance(raw, list):
            return json.dumps(raw, ensure_ascii=False, separators=(",", ":"))
    except (OSError, ValueError):
        pass
    return "[]"


def collect_pdfs():
    """收集 content/post 下的 PDF，跳过隐藏目录和依赖目录。"""
    pdfs = []
    for dirpath, dirnames, filenames in os.walk(POST_DIR):
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".") and d not in ("__pycache__", "node_modules", "site-packages")
        ]
        for name in filenames:
            if not name.lower().endswith(".pdf"):
                continue
            src = os.path.join(dirpath, name)
            rel = os.path.relpath(src, POST_DIR)
            parts = rel.split(os.sep)
            pdfs.append({
                "rel": rel,
                "title": os.path.splitext(name)[0],
                "folder": parts[0] if len(parts) > 1 else "根目录",
                "size": os.path.getsize(src),
                "available": os.path.getsize(src) <= MAX_PDF_BYTES,
                "path": "",
            })
    pdfs.sort(key=lambda item: (item["folder"], item["title"]))
    return pdfs


def copy_pdf(rel):
    """PDF 用路径哈希命名，避免中文文件名在 URL 中出问题。"""
    src = os.path.join(POST_DIR, rel)
    digest = hashlib.md5(rel.encode("utf-8")).hexdigest()[:10]
    dest = os.path.join(PDF_DIR, digest + ".pdf")
    os.makedirs(PDF_DIR, exist_ok=True)
    shutil.copy2(src, dest)
    return "assets/files/pdf/" + digest + ".pdf"


def resolve_wikilink_asset(name, md_dir, images):
    key = name.strip().lower()
    candidates = images.get(key, [])
    if not candidates:
        return None
    for c in candidates:
        if os.path.dirname(c) == md_dir:
            return c
    md_stem = os.path.splitext(os.path.basename(md_dir))[0]
    for c in candidates:
        parent = os.path.dirname(c)
        if os.path.dirname(parent) == md_dir and os.path.basename(parent) == f"{md_stem}_assets":
            return c
    return candidates[0]


def preprocess(text, md_dir, out_dir, images):
    def std_img(m):
        alt = m.group(1)
        url = m.group(2).strip()
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url) or url.startswith(("data:", "/", "#")):
            return m.group(0)
        decoded = urllib.parse.unquote(url)
        src_abs = os.path.normpath(os.path.join(md_dir, decoded))
        if os.path.isfile(src_abs) and is_image(src_abs):
            new_url = copy_asset(src_abs, out_dir)
            return f"![{alt}]({new_url})"
        return m.group(0)

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", std_img, text)

    def wiki_img(m):
        name = m.group(1).strip()
        width = (m.group(2) or "").strip()
        src_abs = resolve_wikilink_asset(name, md_dir, images)
        if not src_abs:
            return f'<p class="missing-img">[图片缺失: {esc(name)}]</p>'
        new_url = copy_asset(src_abs, out_dir)
        if width.isdigit():
            return f'<img src="{new_url}" alt="{esc(name)}" style="max-width:{width}px; height:auto;">'
        return f'![{esc(name)}]({new_url})'

    text = re.sub(r"!\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]", wiki_img, text)

    def wiki_link(m):
        target = m.group(1).strip()
        alias = (m.group(2) or "").strip()
        display = alias or target
        display = display.replace("\\", "/").split("/")[-1]
        return esc(display)

    text = re.sub(r"\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]", wiki_link, text)
    return text


def is_table_line(line):
    s = line.strip()
    return s.startswith("|") and "|" in s[1:]


def fix_tables(text):
    """合并被空行隔开的表格行, 使其能被表格扩展正确解析(Obsidian 风格导出常见)。"""
    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if is_table_line(line):
            out.append(line.rstrip())
            i += 1
            while i < n:
                nxt = lines[i]
                if is_table_line(nxt):
                    out.append(nxt.rstrip())
                    i += 1
                elif nxt.strip() == "":
                    j = i
                    while j < n and lines[j].strip() == "":
                        j += 1
                    if j < n and is_table_line(lines[j]):
                        i = j
                    else:
                        break
                else:
                    break
        else:
            out.append(line)
            i += 1
    return "\n".join(out)


def convert_md(text):
    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "sane_lists",
            "pymdownx.mark",       # ==高亮==
            "pymdownx.tilde",      # ~~删除~~ 与 ~下标~
            "pymdownx.caret",      # ^上标^
            "pymdownx.tasklist",   # - [ ] 任务列表
            "pymdownx.arithmatex", # $...$ / $$...$$ 公式
        ],
        extension_configs={"pymdownx.arithmatex": {"generic": True}},
        output_format="html5",
    )
    return md.convert(text)


def render_doc(rel, out_dir, images):
    abs_path = os.path.join(POST_DIR, rel)
    md_dir = os.path.dirname(abs_path)
    raw = read_text(abs_path)
    raw = strip_frontmatter(raw)
    title = extract_title(raw, os.path.splitext(os.path.basename(rel))[0])
    processed = preprocess(raw, md_dir, out_dir, images)
    processed = fix_tables(processed)
    body = convert_md(processed)
    DOC_TITLE[rel] = title
    DOC_TEXT[rel] = html_to_text(body)[:SEARCH_TEXT_LIMIT]
    return {"rel": rel, "title": title, "body": body}


# --------------------------------------------------------------------------- #
# 目录树与简介/创立时间
# --------------------------------------------------------------------------- #
def build_tree(docs):
    dir_docs = defaultdict(list)
    for rel in docs:
        d = os.path.dirname(rel)
        dir_docs[d].append(rel)

    dirs_with_content = set()
    for rel in docs:
        d = os.path.dirname(rel)
        while True:
            dirs_with_content.add(d)
            if d == "":
                break
            d = os.path.dirname(d)

    child_dirs = defaultdict(list)
    for d in dirs_with_content:
        if d == "":
            continue
        parent = os.path.dirname(d)
        child_dirs[parent].append(d)

    for d in child_dirs:
        child_dirs[d].sort(key=lambda r: natural_key(os.path.basename(r)))
    return dir_docs, child_dirs


def docs_under(docs, dir_rel):
    prefix = dir_rel + os.sep if dir_rel else ""
    return [r for r in docs if r.startswith(prefix)]


def folder_intro(d, dir_docs, child_dirs):
    subs = child_dirs.get(d, [])
    if subs:
        names = [os.path.basename(s) for s in subs]
        return "、".join(names[:6]) + (" 等" if len(names) > 6 else "")
    direct = dir_docs.get(d, [])
    if direct:
        titles = []
        for rel in direct[:4]:
            t = extract_title(read_text(os.path.join(POST_DIR, rel)), os.path.splitext(os.path.basename(rel))[0])
            titles.append(t)
        return "、".join(titles) + (" 等" if len(direct) > 4 else "")
    return "暂无简介"


def folder_created(d, dir_earliest):
    t = dir_earliest.get(d)
    if t is None:
        return ""
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d")


# --------------------------------------------------------------------------- #
# 样式与脚本
# --------------------------------------------------------------------------- #
CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
:root {
  --bg: #ffffff;
  --bg-soft: #f6f7fb;
  --card: #ffffff;
  --border: #e8e9f0;
  --text: #1f2430;
  --text-soft: #6b7280;
  --brand: #6d5ae0;
  --brand-soft: rgba(109, 90, 224, .10);
  --accent-cyan: #0ea5b7;
  --accent-green: #0e9f6e;
  --accent-purple: #7c3aed;
  --accent-blue: #2563eb;
  --accent-bg: rgba(109, 90, 224, .07);
  --accent-border: rgba(109, 90, 224, .18);
  --code-bg: #f1f2f7;
  --code-color: #c0392b;
  --pre-bg: #1e2330;
  --pre-color: #e6e9f0;
  --shadow: 0 10px 28px rgba(30, 40, 80, .08);
  --shadow-hover: 0 18px 44px rgba(78, 62, 190, .16);
  --drawer-grad: linear-gradient(135deg, #7c3aed 0%, #a855f7 30%, #06b6d4 68%, #2563eb 100%);
  --drawer-bg: linear-gradient(160deg, #f0e7ff 0%, #e3f8fb 46%, #e7efff 100%);
  --ease: cubic-bezier(.22, .61, .36, 1);
  --spring: cubic-bezier(.34, 1.56, .64, 1);
}
[data-theme="dark"] {
  --bg: #0e1a2b;
  --bg-soft: #132238;
  --card: #16263a;
  --border: #24364d;
  --text: #e6edf7;
  --text-soft: #9aa7bc;
  --brand: #d4af37;
  --brand-soft: rgba(212, 175, 55, .16);
  --accent-cyan: #3fb6a8;
  --accent-green: #4f9d7a;
  --accent-purple: #9a86e8;
  --accent-blue: #5b8def;
  --accent-bg: rgba(212, 175, 55, .08);
  --accent-border: rgba(212, 175, 55, .20);
  --code-bg: #20304a;
  --code-color: #ffb3a0;
  --pre-bg: #0b1422;
  --pre-color: #dbe3f0;
  --shadow: 0 10px 28px rgba(0, 0, 0, .35);
  --shadow-hover: 0 18px 44px rgba(0, 0, 0, .5);
  --drawer-grad: linear-gradient(135deg, #8a6d1f 0%, #d4af37 42%, #9a86e8 100%);
  --drawer-bg: linear-gradient(160deg, #102036 0%, #0c1728 50%, #111d31 100%);
}
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.7;
  transition: background .35s ease, color .35s ease;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--brand); text-decoration: none; }
button { font-family: inherit; }
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
}
a:focus-visible, button:focus-visible { outline: 2px solid var(--accent-cyan); outline-offset: 3px; }

.topbar {
  position: sticky; top: 0; z-index: 20; height: 60px;
  display: flex; align-items: center; gap: 10px; padding: 0 20px;
  background: var(--bg);
  background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: blur(10px); border-bottom: 1px solid var(--border);
  animation: topbar-in .45s var(--ease) backwards;
}
.icon-btn {
  border: 1px solid var(--border); background: var(--bg-soft); color: var(--text);
  min-width: 38px; height: 38px; padding: 0 10px; border-radius: 10px;
  font-size: 16px; cursor: pointer; line-height: 1; display: inline-flex;
  align-items: center; justify-content: center; gap: 6px;
  transition: transform .2s var(--ease), border-color .2s ease, color .2s ease,
    background .2s ease, box-shadow .2s ease;
}
.icon-btn:hover {
  border-color: var(--brand); color: var(--brand); transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(109, 90, 224, .16);
}
.icon-btn:active { transform: translateY(0) scale(.96); }
.icon-btn.spin { animation: icon-spin .5s var(--ease); }
.home-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; padding: 0;
  border: 1px solid var(--border); border-radius: 10px; background: var(--bg-soft);
  color: var(--text); font-size: 14px; font-weight: 600;
  transition: transform .2s var(--ease), border-color .2s ease, color .2s ease,
    background .2s ease, box-shadow .2s ease;
}
.home-btn:hover {
  border-color: var(--brand); color: var(--brand); transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(109, 90, 224, .16);
}
.home-btn:active { transform: translateY(0) scale(.96); }
.home-btn svg { width: 18px; height: 18px; transition: transform .25s var(--spring); }
.home-btn:hover svg { transform: translateY(-2px) scale(1.08); }
.back-btn svg { width: 18px; height: 18px; transition: transform .22s var(--ease); }
.back-btn:hover svg { transform: translateX(-3px); }
.page-home .back-btn { display: none; }
.brand {
  display: inline-flex; align-items: baseline; gap: 7px;
  font-size: 17px; font-weight: 700; color: var(--text); padding: 2px;
}
.brand-name, .brand-site { transition: color .2s ease; }
.brand-sep { color: var(--accent-cyan); font-weight: 400; opacity: .7; }
.brand-site {
  font-size: 13px; font-weight: 600; color: var(--text-soft); letter-spacing: .2px;
}
.brand:hover .brand-name { color: var(--brand); }
.brand:hover .brand-site { color: var(--accent-cyan); }
.spacer { flex: 1; }

.main { max-width: 860px; margin: 0 auto; padding: 30px 20px 90px; }

.page-title { margin: 8px 0 22px; font-size: 26px; letter-spacing: .5px; }
.crumb { font-size: 13px; color: var(--text-soft); margin-bottom: 6px; animation: fade-in .5s ease backwards; }
.crumb a { color: var(--text-soft); }
.crumb a:hover { color: var(--brand); }
.page-head { margin: 8px 0 20px; animation: card-in .5s .05s var(--ease) backwards; }
.page-head h1 { margin: 0 0 6px; font-size: 24px; }
.page-head .count { color: var(--text-soft); font-size: 14px; }

/* 分类单列列表 */
.cat-list { display: flex; flex-direction: column; gap: 14px; }
.cat-item {
  position: relative; display: block; overflow: hidden; padding: 18px 20px;
  border: 1px solid var(--border); border-left: 3px solid var(--brand);
  border-radius: 12px; background: var(--card);
  transition: transform .24s var(--ease), box-shadow .24s var(--ease),
    border-color .24s ease, background .24s ease;
  animation: card-in .55s var(--ease) backwards;
  animation-delay: calc(var(--i, 0) * 45ms);
}
.cat-item::after {
  content: ""; position: absolute; inset: -20% -60%; pointer-events: none;
  background: linear-gradient(115deg, transparent 35%, rgba(109, 90, 224, .10) 50%, transparent 65%);
  transform: translateX(-60%); transition: transform .65s var(--ease);
}
.cat-item:hover::after { transform: translateX(60%); }
.cat-item:hover {
  transform: translateY(-3px); box-shadow: var(--shadow-hover);
  border-color: var(--accent-border); border-left-color: var(--accent-cyan);
}
.cat-title { font-size: 17px; font-weight: 700; color: var(--text); transition: color .2s ease; }
.cat-item:hover .cat-title { color: var(--brand); }
.cat-desc { margin-top: 6px; color: var(--text-soft); font-size: 14px; }
.cat-meta { margin-top: 10px; display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: var(--text-soft); }
.cat-meta .dot { color: var(--accent-border); }

/* 阅读页文章 */
.doc {
  background: var(--card); border: 1px solid var(--border); border-radius: 14px;
  padding: 32px 36px; animation: card-in .55s var(--ease) backwards;
}
.doc:nth-of-type(2) { animation-delay: .06s; }
.doc:nth-of-type(3) { animation-delay: .12s; }
.doc:nth-of-type(n+4) { animation-delay: .18s; }

/* Markdown 内容排版 */
.doc-body { font-size: 15.5px; overflow-wrap: break-word; }
.doc-body h1 { font-size: 23px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin: 0 0 20px; }
.doc-body h2 { font-size: 20px; margin: 26px 0 12px; }
.doc-body h3 { font-size: 17px; margin: 22px 0 10px; }
.doc-body h1:first-child { margin-top: 0; }
.doc-body p { margin: 12px 0; }
.doc-body img { max-width: 100%; height: auto; border-radius: 8px; }
.doc-body ul, .doc-body ol { padding-left: 24px; margin: 12px 0; }
.doc-body li { margin: 4px 0; }
.doc-body blockquote {
  margin: 16px 0; padding: 10px 16px; border-left: 3px solid var(--brand);
  background: var(--accent-bg); color: var(--text-soft); border-radius: 0 8px 8px 0;
}
.doc-body code {
  background: var(--code-bg); color: var(--code-color); padding: 2px 6px;
  border-radius: 5px; font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; font-size: 13.5px;
}
.doc-body pre {
  background: var(--pre-bg); color: var(--pre-color); padding: 16px 18px; border-radius: 10px;
  overflow: auto; margin: 16px 0;
}
.doc-body pre code { background: transparent; color: inherit; padding: 0; font-size: 13px; }
.doc-body table { border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; display: block; overflow-x: auto; }
.doc-body th, .doc-body td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
.doc-body th { background: var(--bg-soft); font-weight: 600; }
.doc-body tr:nth-child(even) td { background: var(--bg-soft); }
.doc-body hr { border: none; height: 1px; background: var(--border); margin: 22px 0; }
.doc-body a { text-decoration: underline; text-underline-offset: 2px; }
.doc-body mark { background: var(--brand-soft); color: var(--brand); padding: 0 4px; border-radius: 4px; }
.doc-body del { opacity: .7; }
.doc-body .arithmatex { overflow-x: auto; overflow-y: hidden; }
.missing-img { color: var(--text-soft); font-size: 13px; font-style: italic; }

/* 抽屉 */
.drawer-overlay {
  position: fixed; inset: 0; background: rgba(10, 16, 28, .45); z-index: 40;
  opacity: 0; pointer-events: none; transition: opacity .28s ease;
  backdrop-filter: blur(3px);
}
.drawer-overlay.show { opacity: 1; pointer-events: auto; }
.drawer {
  position: fixed; top: 0; left: 0; bottom: 0; width: 360px; max-width: 88vw;
  background: var(--drawer-bg); z-index: 50; transform: translateX(-100%);
  transition: transform .32s var(--ease), box-shadow .32s ease;
  box-shadow: none;
  display: flex; flex-direction: column; overflow: hidden;
}
.drawer.show { transform: translateX(0); box-shadow: 0 0 40px rgba(10, 16, 28, .25); }
.drawer-head {
  position: relative; overflow: hidden; padding: 28px 24px 22px; color: #fff;
  background: var(--drawer-grad); background-size: 220% 220%; background-position: 0% 50%;
}
.drawer.show .drawer-head { animation: gradient-pan 9s ease-in-out infinite; }
.drawer-head::before, .drawer-head::after {
  content: ""; position: absolute; border-radius: 50%; pointer-events: none;
}
.drawer-head::before {
  width: 190px; height: 190px; top: -90px; right: -50px;
  background: radial-gradient(circle, rgba(255,255,255,.30) 0%, rgba(255,255,255,0) 68%);
  animation: blob-float 8s ease-in-out infinite;
}
.drawer-head::after {
  width: 150px; height: 150px; bottom: -80px; left: -40px;
  background: radial-gradient(circle, rgba(255,255,255,.18) 0%, rgba(255,255,255,0) 70%);
  animation: blob-float 11s ease-in-out infinite reverse;
}
.avatar {
  position: relative; z-index: 1; width: 66px; height: 66px; border-radius: 50%;
  background: rgba(255,255,255,.18); border: 2px solid rgba(255,255,255,.72);
  box-shadow: 0 10px 24px rgba(20,10,60,.28), inset 0 0 0 3px rgba(255,255,255,.14);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 14px; overflow: hidden; color: #fff;
  transition: transform .3s var(--spring), box-shadow .3s ease;
}
.avatar:hover {
  transform: scale(1.06) rotate(-2deg);
  box-shadow: 0 14px 30px rgba(20,10,60,.36), inset 0 0 0 3px rgba(255,255,255,.2);
}
.avatar-default { width: 36px; height: 36px; opacity: .92; }
.avatar-img {
  position: absolute; width: 200%; height: 200%; left: -50%; top: 0;
  object-fit: cover; display: block;
}
.drawer.show .avatar { animation: avatar-pop .6s var(--spring) backwards .08s; }
.drawer-name {
  position: relative; z-index: 1; font-size: 21px; font-weight: 700; letter-spacing: .5px;
}
.drawer-sub {
  position: relative; z-index: 1; font-size: 13px; opacity: .9;
  margin-top: 4px; letter-spacing: .2px;
}
.drawer.show .drawer-name { animation: slide-up .5s var(--ease) backwards .14s; }
.drawer.show .drawer-sub { animation: slide-up .5s var(--ease) backwards .2s; }
.drawer-close {
  position: absolute; z-index: 3; top: 14px; right: 14px; border: none; background: rgba(255,255,255,.2);
  color: #fff; width: 34px; height: 34px; border-radius: 9px; font-size: 18px; cursor: pointer;
  transition: background .2s ease, transform .25s var(--spring);
}
.drawer-close:hover { background: rgba(255,255,255,.34); transform: rotate(90deg); }
.drawer-body { flex: 1; overflow-y: auto; padding: 24px 24px 40px; }
.drawer-body::-webkit-scrollbar { width: 8px; }
.drawer-body::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--brand) 28%, transparent); border-radius: 8px;
}
.about-text {
  margin: 0 0 18px; color: var(--text-soft); font-size: 14.5px; line-height: 1.8;
}
.drawer.show .about-text { animation: slide-up .5s var(--ease) backwards .24s; }
.contact-list { display: flex; flex-direction: column; gap: 11px; }
.contact-item {
  display: flex; align-items: center; gap: 13px;
  padding: 11px 14px; border: 1px solid var(--border); border-radius: 14px;
  background: rgba(255, 255, 255, .84);
  box-shadow: 0 4px 16px rgba(40, 30, 90, .06);
  transition: transform .24s var(--ease), box-shadow .24s ease,
    border-color .24s ease, background .24s ease;
}
[data-theme="dark"] .contact-item { background: rgba(22, 38, 58, .9); }
.contact-item:hover {
  transform: translateX(5px); border-color: var(--accent-border);
  box-shadow: var(--shadow-hover); background: var(--card);
}
.contact-item::after {
  content: "›"; margin-left: 2px; color: var(--text-soft); opacity: .55;
  font-size: 20px; line-height: 1; transition: transform .2s ease, opacity .2s ease, color .2s ease;
}
.contact-item:hover::after { transform: translateX(3px); opacity: 1; color: var(--brand); }
.contact-icon {
  flex: 0 0 auto; width: 24px; height: 24px;
  display: grid; place-items: center; color: var(--brand); opacity: .9;
  transition: transform .28s var(--spring), opacity .2s ease;
}
.contact-item:hover .contact-icon { transform: scale(1.12); opacity: 1; }
.contact-icon svg { width: 22px; height: 22px; }
.contact-text { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.contact-label { font-weight: 600; color: var(--text); font-size: 14px; line-height: 1.35; white-space: nowrap; }
.contact-value {
  color: var(--text-soft); font-size: 12px; line-height: 1.5;
  word-break: break-all; transition: color .2s ease;
}
.contact-item:hover .contact-value { color: var(--brand); }
.drawer.show .contact-item { animation: contact-in .5s var(--ease) backwards; }
.drawer.show .contact-item:nth-of-type(1) { animation-delay: .28s; }
.drawer.show .contact-item:nth-of-type(2) { animation-delay: .35s; }
.drawer.show .contact-item:nth-of-type(3) { animation-delay: .42s; }

@keyframes icon-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes topbar-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: none; }
}
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes card-in {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: none; }
}
@keyframes avatar-pop {
  0% { opacity: 0; transform: scale(.72) rotate(-8deg); }
  60% { opacity: 1; transform: scale(1.06) rotate(2deg); }
  100% { opacity: 1; transform: scale(1) rotate(0); }
}
@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: none; }
}
@keyframes contact-in {
  from { opacity: 0; transform: translateX(-14px); }
  to { opacity: 1; transform: none; }
}
@keyframes gradient-pan {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
@keyframes blob-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(10px, 14px) scale(1.08); }
}

@media (max-width: 760px) {
  .brand-site, .brand-sep { display: none; }
}
@media (max-width: 640px) {
  .main { padding: 18px 14px 60px; }
  .doc { padding: 22px 18px; }
  .topbar { padding: 0 14px; gap: 8px; }
  .brand { font-size: 15px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .001ms !important; animation-iteration-count: 1 !important;
    transition-duration: .001ms !important; scroll-behavior: auto !important;
  }
}
"""

JS = """
(function () {
  var root = document.documentElement;
  var drawer = document.getElementById('drawer');
  var overlay = document.getElementById('overlay');
  var lastFocus = null;

  function openD() {
    if (drawer.classList.contains('show')) return;
    lastFocus = document.activeElement;
    drawer.classList.add('show');
    overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
    var closeBtn = document.getElementById('drawerClose');
    if (closeBtn) closeBtn.focus({ preventScroll: true });
  }
  function closeD() {
    if (!drawer.classList.contains('show')) return;
    drawer.classList.remove('show');
    overlay.classList.remove('show');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }
  document.getElementById('menuBtn').addEventListener('click', openD);
  document.getElementById('drawerClose').addEventListener('click', closeD);
  overlay.addEventListener('click', closeD);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeD(); });

  // 支持 #profile / #contact 直接打开个人主页
  function openFromHash() {
    if (location.hash === '#profile' || location.hash === '#contact') openD();
  }
  window.addEventListener('hashchange', openFromHash);
  openFromHash();
  document.querySelectorAll('a[href="#profile"], a[href="#contact"]').forEach(function (link) {
    link.addEventListener('click', function () { setTimeout(openD, 0); });
  });

  // 主题切换
  var themeBtn = document.getElementById('themeBtn');
  function applyTheme(t) {
    root.setAttribute('data-theme', t);
    themeBtn.textContent = t === 'dark' ? '\\u2600' : '\\u263E';
    themeBtn.setAttribute('aria-label', t === 'dark' ? '切换到浅色模式' : '切换到深色模式');
    try { localStorage.setItem('theme', t); } catch (e) {}
  }
  var savedTheme = null;
  try { savedTheme = localStorage.getItem('theme'); } catch (e) {}
  var sysDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(savedTheme || (sysDark ? 'dark' : 'light'));
  themeBtn.addEventListener('click', function () {
    themeBtn.classList.remove('spin');
    void themeBtn.offsetWidth;
    themeBtn.classList.add('spin');
    applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  });

  // 中英切换
  var langBtn = document.getElementById('langBtn');
  var I18N = {
    zh: {
      brand: '梁双宇',
      'site-title': '个人博客',
      'home-title': '梁双宇的个人博客',
      tagline: '个人博客 · 记录学习与成长',
      home: '首页',
      back: '返回上一级',
      'quick-title': '导航栏',
      'quick-search': '搜索文章',
      'quick-all': '全部板块',
      'quick-cats': '板块',
      'quick-profile': '个人信息 / 日历',
      'home-motto-label': '座右铭',
      'home-motto': '有时我想，要是人们把活着的每一天都看作是生命的最后一天该有多好哦！',
      'search-title': '搜索文章',
      'search-mode-fuzzy': '模糊匹配',
      'search-mode-exact': '完全匹配',
      'search-submit': '搜索',
      'search-close': '关闭搜索',
      'search-tip': '完全匹配要求整段文字连续出现；模糊匹配按空格拆词，命中任一关键词即可。',
      'search-suggest': '试试：',
      about: '你好，欢迎来到我的博客。这里记录我的学习笔记、竞赛与项目实践。'
    },
    en: {
      brand: 'Shine Leong',
      'site-title': 'Personal Blog',
      'home-title': "Shine Leong's Personal Blog",
      tagline: 'Personal Blog · Notes & Growth',
      home: 'Home',
      back: 'Back',
      'quick-title': 'Navigation',
      'quick-search': 'Search articles',
      'quick-all': 'All sections',
      'quick-cats': 'Sections',
      'quick-profile': 'Profile & calendar',
      'home-motto-label': 'Motto',
      'home-motto': 'Sometimes I think how wonderful it would be if people treated every day as the last day of their lives.',
      'search-title': 'Search articles',
      'search-mode-fuzzy': 'Fuzzy',
      'search-mode-exact': 'Exact',
      'search-submit': 'Search',
      'search-close': 'Close search',
      'search-tip': 'Exact matches the whole phrase; fuzzy splits keywords by spaces and matches any keyword.',
      'search-suggest': 'Try:',
      about: "Hi, welcome to my blog. Here I share my study notes, competitions and projects."
    }
  };
  function applyLang(lang) {
    root.setAttribute('lang', lang === 'en' ? 'en' : 'zh-CN');
    var dict = I18N[lang] || I18N.zh;
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (dict[key] != null) el.textContent = dict[key];
    });
    document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-title');
      if (dict[key] != null) el.title = dict[key];
    });
    document.querySelectorAll('[data-i18n-aria-label]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-aria-label');
      if (dict[key] != null) el.setAttribute('aria-label', dict[key]);
    });
    langBtn.textContent = lang === 'zh' ? 'EN' : '中';
    langBtn.setAttribute('aria-label', lang === 'zh' ? 'Switch to English' : '切换到中文');
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: lang } }));
    try { localStorage.setItem('lang', lang); } catch (e) {}
  }
  var savedLang = null;
  try { savedLang = localStorage.getItem('lang'); } catch (e) {}
  applyLang(savedLang === 'en' ? 'en' : 'zh');
  langBtn.addEventListener('click', function () {
    applyLang(root.getAttribute('lang') === 'zh-CN' ? 'en' : 'zh');
  });
})();
"""


def build_drawer(out_dir, avatar_name=None):
    avatar_name = avatar_name or AVATAR_NAME
    avatar_img = ""
    if avatar_name:
        avatar_src = quote_url(rel_from(out_dir, os.path.join(ASSET_DIR, avatar_name)))
        avatar_img = '<img class="avatar-img" src="' + avatar_src + '" alt="" onerror="this.style.display=\'none\'">'
    return f"""
<aside class="drawer" id="drawer" aria-label="个人主页">
  <div class="drawer-head">
    <button class="drawer-close" id="drawerClose" aria-label="关闭">&times;</button>
    <div class="avatar" aria-hidden="true">
      <svg class="avatar-default" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="3.6"/><path d="M4.5 20c.9-4 3.9-6.2 7.5-6.2s6.6 2.2 7.5 6.2"/></svg>
      {avatar_img}
    </div>
    <div class="drawer-name" data-i18n="brand">梁双宇</div>
    <div class="drawer-sub" data-i18n="tagline">个人博客 · 记录学习与成长</div>
  </div>
  <div class="drawer-body">
    <p class="about-text" data-i18n="about">你好，欢迎来到我的博客。这里记录我的学习笔记、竞赛与项目实践。</p>
    <div class="contact-list">
      <a class="contact-item" href="https://github.com/No-Zland" target="_blank" rel="noopener">
        <span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg></span>
        <span class="contact-text">
          <span class="contact-label">GitHub</span>
          <span class="contact-value">github.com/No-Zland</span>
        </span>
      </a>
      <a class="contact-item" href="https://space.bilibili.com/1445304721" target="_blank" rel="noopener">
        <span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.813 4.653h.854c1.51.054 2.769.578 3.773 1.574 1.004.995 1.524 2.249 1.56 3.76v7.36c-.036 1.51-.556 2.769-1.56 3.773s-2.262 1.524-3.773 1.56H5.333c-1.51-.036-2.769-.556-3.773-1.56S.036 18.858 0 17.347v-7.36c.036-1.511.556-2.765 1.56-3.76 1.004-.996 2.262-1.52 3.773-1.574h.774l-1.174-1.12a1.234 1.234 0 0 1-.373-.906c0-.356.124-.658.373-.907l.027-.027c.267-.249.573-.373.92-.373.347 0 .653.124.92.373L9.653 4.44c.071.071.134.142.187.213h4.267a.836.836 0 0 1 .16-.213l2.853-2.747c.267-.249.573-.373.92-.373.347 0 .662.151.929.4.267.249.391.551.391.907 0 .355-.124.657-.373.906zM5.333 7.24c-.746.018-1.373.276-1.88.773-.506.498-.769 1.13-.786 1.894v7.52c.017.764.28 1.395.786 1.893.507.498 1.134.756 1.88.773h13.334c.746-.017 1.373-.275 1.88-.773.506-.498.769-1.129.786-1.893v-7.52c-.017-.765-.28-1.396-.786-1.894-.507-.497-1.134-.755-1.88-.773zM8 11.107c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c0-.373.129-.689.386-.947.258-.257.574-.386.947-.386zm8 0c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c.017-.391.15-.711.4-.96.249-.249.56-.373.933-.373Z"/></svg></span>
        <span class="contact-text">
          <span class="contact-label">哔哩哔哩</span>
          <span class="contact-value">space.bilibili.com/1445304721</span>
        </span>
      </a>
      <a class="contact-item" href="mailto:ziwukui@qq.com">
        <span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/></svg></span>
        <span class="contact-text">
          <span class="contact-label">电子邮箱</span>
          <span class="contact-value">ziwukui@qq.com</span>
        </span>
      </a>
    </div>
    <section class="calendar" id="calendar" aria-label="博客更新日历与任务"></section>
  </div>
</aside>
<div class="drawer-overlay" id="overlay"></div>
<div class="toast" id="taskToast" role="status" aria-live="polite">
  <div class="toast-title" id="taskToastTitle"></div>
  <div class="toast-msg" id="taskToastMsg"></div>
  <button type="button" class="toast-close" id="taskToastClose" aria-label="关闭提醒">&times;</button>
</div>
"""


HOME_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>'
SEARCH_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
BACK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg>'


def page(out_dir, title, body, with_math=False, is_home=False, parent_href=None):
    style_href = quote_url(rel_from(out_dir, os.path.join(ASSET_DIR, "style.css")))
    script_src = quote_url(rel_from(out_dir, os.path.join(ASSET_DIR, "app.js")))
    music_base = quote_url(rel_from(out_dir, os.path.join(ASSET_DIR, "music")))
    home_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    drawer_html = build_drawer(out_dir)
    math = MATHJAX_HEAD if with_math else ""
    back_html = ""
    if parent_href:
        back_html = (
            f'<a class="icon-btn back-btn" href="{parent_href}" title="返回上一级" '
            f'aria-label="返回上一级" data-i18n-title="back" data-i18n-aria-label="back">{BACK_SVG}</a>'
        )
    body_class = ' class="page-home"' if is_home else ""
    nav_html = "" if is_home else side_nav_for(out_dir)
    if nav_html:
        main_class = "main main-wide"
        main_inner = f'<div class="page-layout">{nav_html}<div class="page-main">{body}</div></div>'
    else:
        main_class = "main"
        main_inner = body
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · 梁双宇</title>
<link rel="stylesheet" href="{style_href}">
{math}
</head>
<body{body_class}>
{drawer_html}
<header class="topbar">
  <button class="icon-btn" id="menuBtn" aria-label="打开个人主页">&#9776;</button>
  <a class="home-btn" href="{home_href}" title="返回首页" aria-label="返回首页" data-i18n-title="home" data-i18n-aria-label="home">{HOME_SVG}</a>
  <button type="button" class="icon-btn top-search" id="searchTrigger" data-home="{home_href}" aria-haspopup="dialog" aria-expanded="false" title="搜索文章" aria-label="搜索文章" data-i18n-title="search-title" data-i18n-aria-label="search-title">{SEARCH_SVG}</button>
  {back_html}
  <a class="brand" href="{home_href}"><span class="brand-name" data-i18n="brand">梁双宇</span><span class="brand-sep">·</span><span class="brand-site" data-i18n="site-title">个人博客</span></a>
  <div class="spacer"></div>
  <button class="icon-btn" id="langBtn" title="中英切换">EN</button>
  <button class="icon-btn" id="themeBtn" title="切换主题">&#9789;</button>
</header>
<main class="{main_class}">
{main_inner}
</main>
<script>window.BLOG_UPDATES = {UPDATES_JSON};</script>
<script>window.MUSIC_BASE = "{music_base}"; window.MUSIC_PLAYLIST = {MUSIC_JSON};</script>
<script src="{script_src}"></script>
</body>
</html>
"""


def cat_item(name, href, count, created, intro, index=0):
    return f"""
<a class="cat-item" href="{quote_url(href)}" style="--i:{min(index, 8)}">
  <div class="cat-title">{esc(name)}</div>
  <div class="cat-desc">{esc(intro)}</div>
  <div class="cat-meta"><span>{count} 篇文章</span><span class="dot">·</span><span>创立于 {esc(created)}</span></div>
</a>
"""


def breadcrumb(d, out_dir):
    home_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    parts = [f'<a href="{home_href}">首页</a>']
    if d:
        top = d.split(os.sep)[0]
        section = section_for_category(top)
        if section:
            section_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, section["slug"], "index.html")))
            parts.append(f'<a href="{section_href}">{esc(section["title"])}</a>')
        rel = ""
        for c in d.split(os.sep):
            rel = os.path.join(rel, c) if rel else c
            href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, rel, "index.html")))
            parts.append(f'<a href="{href}">{esc(c)}</a>')
    return '<div class="crumb">' + " / ".join(parts) + "</div>"


def side_nav_for(out_dir):
    if not NAV_SECTIONS:
        return ""

    parts = [p for p in os.path.relpath(out_dir, SITE_DIR).split(os.sep) if p and p != "."]
    active_section = None
    active_cat = None
    active_sub = None

    if parts:
        first = parts[0]
        if any(section["slug"] == first for section in NAV_SECTIONS):
            active_section = first
        else:
            active_cat = first
            section = section_for_category(first)
            active_section = section["slug"] if section else None
            if len(parts) > 1:
                active_sub = parts[1]

    home_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    library_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "资料库", "index.html")))
    library_active = os.path.basename(out_dir.rstrip(os.sep)) == "资料库"
    rows = []
    for section in NAV_SECTIONS:
        section_active = section["slug"] == active_section
        section_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, section["slug"], "index.html")))
        rows.append(
            f'<a class="quick-cat page-nav-section{" is-active" if section_active else ""}" '
            f'href="{section_href}" title="{esc(section["title"])}">'
            f'<span class="quick-dot" style="background:{section["color"]}"></span>'
            f'<span class="quick-name">{esc(section["title"])}</span>'
            f'<span class="quick-count">{section["total"]}</span></a>'
        )

        if section_active:
            cat_rows = []
            for cat in section["cats"]:
                cat_active = cat["name"] == active_cat
                cat_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, cat["name"], "index.html")))
                cat_rows.append(
                    f'<a class="page-nav-cat{" is-active" if cat_active else ""}" href="{cat_href}">'
                    f'<span class="page-nav-name">{esc(cat["name"])}</span>'
                    f'<span class="page-nav-count">{cat["count"]}</span></a>'
                )
                if cat_active and cat["subs"]:
                    sub_rows = []
                    for sub in cat["subs"]:
                        sub_active = active_sub is not None and os.path.basename(sub["rel"]) == active_sub
                        sub_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, sub["rel"], "index.html")))
                        sub_rows.append(
                            f'<a class="page-nav-subcat{" is-active" if sub_active else ""}" href="{sub_href}">'
                            f'<span class="page-nav-name">{esc(sub["name"])}</span>'
                            f'<span class="page-nav-count">{sub["count"]}</span></a>'
                        )
                    cat_rows.append('<div class="page-nav-subcats">' + "".join(sub_rows) + "</div>")
            rows.append('<div class="page-nav-sub">' + "".join(cat_rows) + "</div>")

    return f"""
<aside class="quick-nav page-nav" aria-label="层级导航">
  <div class="quick-head">
    <div class="quick-kicker">导航栏</div>
    <div class="quick-total">{len(NAV_SECTIONS)} 个板块</div>
  </div>
  <a class="page-nav-home" href="{home_href}">← 全部板块</a>
  <nav class="page-nav-list">{''.join(rows)}</nav>
  <a class="page-nav-home page-nav-library{' is-active' if library_active else ''}" href="{library_href}">PDF / 图片资料</a>
  {music_player_html()}
</aside>
"""


def build_home(docs, dir_docs, child_dirs, dir_earliest, out_dir):
    l1 = child_dirs.get("", [])
    sections = build_sections(l1)
    section_items = []
    quick_items = []
    article_total = 0
    for i, section in enumerate(sections):
        total = sum(len(docs_under(docs, cat)) for cat in section["cats"])
        article_total += total
        href = os.path.join(section["slug"], "index.html")
        tags = ''.join(f'<span>{esc(cat)}</span>' for cat in section["cats"])
        section_items.append(f"""
<a class="section-card" href="{quote_url(href)}" style="--i:{min(i, 8)};--section-color:{section['color']}">
  <div class="section-card-top">
    <span class="section-num">{i + 1:02d}</span>
    <span class="section-card-meta">{len(section['cats'])} 个分类 · {total} 篇文章</span>
  </div>
  <div class="section-card-title">{esc(section['title'])}</div>
  <div class="section-card-desc">{esc(section['desc'])}</div>
  <div class="section-tags">{tags}</div>
  <div class="section-card-enter">进入板块 <span>→</span></div>
</a>""")
        quick_items.append(
            f'<a class="quick-cat" href="{quote_url(href)}" title="{esc(section["title"])}">'
            f'<span class="quick-dot" style="background:{section["color"]}"></span>'
            f'<span class="quick-name">{esc(section["title"])}</span>'
            f'<span class="quick-count">{total}</span></a>'
        )

    body = f"""
<h1 class="sr-only" data-i18n="home-title">梁双宇的个人博客</h1>
<div class="home-layout">
  <aside class="quick-nav" aria-label="导航栏" data-i18n-aria-label="quick-title">
    <div class="quick-head">
      <div class="quick-kicker" data-i18n="quick-title">导航栏</div>
      <div class="quick-total">{len(sections)} 个板块</div>
    </div>
    <a class="quick-link" href="#sections">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
      <span data-i18n="quick-all">全部板块</span>
    </a>
    <a class="quick-link" href="资料库/index.html">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z"/><path d="M8 7h8M8 11h8M8 15h5"/></svg>
      <span>PDF / 图片资料</span>
    </a>
    <div class="quick-label" data-i18n="quick-cats">板块</div>
    <nav class="quick-list" aria-label="板块目录">
      {''.join(quick_items)}
    </nav>
    <a class="quick-profile" href="#profile">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c.8-4 3.6-6 7-6s6.2 2 7 6"/></svg>
      <span data-i18n="quick-profile">个人信息 / 日历</span>
    </a>
    {music_player_html()}
  </aside>
  <div class="home-content">
    <div class="home-motto-block" id="sections">
      <div class="home-motto-kicker" data-i18n="home-motto-label">座右铭</div>
      <h2 class="home-motto-text" data-i18n="home-motto">有时我想，要是人们把活着的每一天都看作是生命的最后一天该有多好哦！</h2>
      <div class="count">{len(sections)} 个板块 · {article_total} 篇文章</div>
    </div>
    <div class="section-grid">{''.join(section_items)}</div>
  </div>
</div>
<div class="search-overlay" id="searchOverlay" hidden>
  <div class="search-modal" role="dialog" aria-modal="true" aria-labelledby="searchTitle">
    <button type="button" class="search-close" id="searchClose" aria-label="关闭搜索" data-i18n-aria-label="search-close">&times;</button>
    <div class="search-head">
      <h2 id="searchTitle" data-i18n="search-title">搜索文章</h2>
    </div>
    <form class="search-form" id="searchForm" role="search">
      <span class="search-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      </span>
      <input id="searchInput" type="search" placeholder="搜索标题或正文，例如：指针、数学建模…" autocomplete="off" aria-label="搜索文章" data-i18n-aria-label="search-title">
      <button type="button" class="search-clear" id="searchClear" aria-label="清空搜索" hidden>&times;</button>
      <button type="submit" class="search-submit" data-i18n="search-submit">搜索</button>
    </form>
    <div class="search-bottom">
      <div class="search-tip" data-i18n="search-tip">完全匹配要求整段文字连续出现；模糊匹配按空格拆词，命中任一关键词即可。</div>
      <div class="search-mode" role="group" aria-label="匹配模式">
        <button type="button" class="mode-btn" data-mode="fuzzy" aria-pressed="true" data-i18n="search-mode-fuzzy">模糊匹配</button>
        <button type="button" class="mode-btn" data-mode="exact" aria-pressed="false" data-i18n="search-mode-exact">完全匹配</button>
      </div>
    </div>
    <div class="search-suggest" id="searchSuggest">
      <span data-i18n="search-suggest">试试：</span>
      <button type="button" data-query="C++">C++</button>
      <button type="button" data-query="指针">指针</button>
      <button type="button" data-query="Python">Python</button>
      <button type="button" data-query="数学建模">数学建模</button>
      <button type="button" data-query="实验报告">实验报告</button>
    </div>
    <div class="search-results" id="searchResults" aria-live="polite"></div>
  </div>
</div>
"""
    return page(out_dir, "个人博客", body, is_home=True)


def parent_href_for(d, out_dir):
    parent = os.path.dirname(d)
    if parent:
        target_dir = os.path.join(SITE_DIR, parent)
    else:
        section = section_for_category(d) if d else None
        target_dir = os.path.join(SITE_DIR, section["slug"]) if section else SITE_DIR
    return quote_url(rel_from(out_dir, os.path.join(target_dir, "index.html")))


def music_player_html():
    return f"""
<div class="music-player" id="musicPlayer">
  <div class="music-head">
    <span class="music-kicker">音乐</span>
    <span class="music-mode" data-music-mode>顺序</span>
  </div>
  <div class="music-track">
    <div class="music-title" data-music-title>暂无曲目</div>
    <div class="music-artist" data-music-artist>—</div>
  </div>
  <div class="music-progress">
    <div class="music-bar"><span data-music-progress></span></div>
    <span class="music-time" data-music-time>0:00</span>
  </div>
  <div class="music-controls">
    <button type="button" data-music-prev aria-label="上一首">‹</button>
    <button type="button" data-music-play>播放</button>
    <button type="button" data-music-next aria-label="下一首">›</button>
    <button type="button" data-music-mode-btn aria-label="切换播放模式">顺序</button>
    <button type="button" data-music-lyrics aria-label="歌词">歌词</button>
  </div>
  <audio id="musicAudio" preload="metadata"></audio>
</div>
"""



def build_section_page(section, l1, docs, dir_docs, child_dirs, dir_earliest, out_dir):
    items = []
    total = 0
    for i, cat in enumerate(section["cats"]):
        if cat not in l1:
            continue
        count = len(docs_under(docs, cat))
        total += count
        href = rel_from(out_dir, os.path.join(SITE_DIR, cat, "index.html"))
        intro = folder_intro(cat, dir_docs, child_dirs)
        created = folder_created(cat, dir_earliest)
        items.append(cat_item(cat, href, count, created, intro, i))

    home_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    body = f"""
<div class="crumb"><a href="{home_href}">首页</a> / {esc(section["title"])}</div>
<section class="section-hero" style="--section-color:{section["color"]}">
  <div class="section-hero-kicker">Section</div>
  <h1>{esc(section["title"])}</h1>
  <p>{esc(section["desc"])}</p>
  <div class="section-hero-meta">{len(section["cats"])} 个分类 · {total} 篇文章</div>
</section>
<div class="cat-list section-cats" style="--section-color:{section["color"]}">{''.join(items)}</div>
"""
    return page(out_dir, section["title"], body, parent_href=home_href)


def build_library_page(pdfs, out_dir):
    groups = defaultdict(list)
    for pdf in pdfs:
        groups[pdf["folder"]].append(pdf)

    sections = []
    for folder, items in groups.items():
        cards = []
        for pdf in items:
            size = pdf["size"] / 1024
            size_text = f"{size:.0f} KB" if size < 1024 else f"{size / 1024:.1f} MB"
            if pdf.get("available", True):
                href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, pdf["path"])))
                cards.append(
                    f'<button type="button" class="pdf-card" data-pdf-open '
                    f'data-pdf-url="{href}" data-pdf-title="{esc(pdf["title"])}">'
                    f'<span class="pdf-icon">PDF</span>'
                    f'<span class="pdf-name">{esc(pdf["title"])}</span>'
                    f'<span class="pdf-meta">{esc(folder)} · {size_text}</span>'
                    f'<span class="pdf-open">查看</span></button>'
                )
            else:
                cards.append(
                    f'<div class="pdf-card is-local">'
                    f'<span class="pdf-icon">PDF</span>'
                    f'<span class="pdf-name">{esc(pdf["title"])}</span>'
                    f'<span class="pdf-meta">{esc(folder)} · {size_text} · 超过 10MB</span>'
                    f'<span class="pdf-open">本地</span></div>'
                )
        sections.append(
            f'<section class="pdf-group"><h2>{esc(folder)}</h2>'
            f'<div class="pdf-grid">{"".join(cards)}</div></section>'
        )

    content = "".join(sections) if sections else '<div class="pdf-empty">还没有 PDF 资料。</div>'
    available_count = sum(1 for pdf in pdfs if pdf.get("available", True))
    local_count = len(pdfs) - available_count
    body = f"""
{breadcrumb("资料库", out_dir)}
<div class="page-head"><h1>资料库</h1><div class="count">{available_count} 份可在线查看{(' · ' + str(local_count) + ' 份本地大文件') if local_count else ''}</div></div>
<p class="library-lede">10MB 以内的 PDF 在线预览；更大的文件保留在本地，避免 GitHub Pages 超出体积限制。文章里的图片点击即可打开大图。</p>
{content}
<div class="pdf-viewer" id="pdfViewer" hidden>
  <div class="pdf-viewer-box">
    <div class="pdf-viewer-head">
      <span id="pdfViewerTitle"></span>
      <div class="pdf-viewer-actions">
        <a id="pdfViewerLink" href="#" target="_blank" rel="noopener">新窗口打开</a>
        <button type="button" id="pdfViewerClose" aria-label="关闭 PDF 预览">&times;</button>
      </div>
    </div>
    <iframe id="pdfViewerFrame" title="PDF 预览"></iframe>
  </div>
</div>
"""
    return page(out_dir, "资料库", body, parent_href=quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html"))))


def build_folder_page(d, docs, dir_docs, child_dirs, dir_earliest, out_dir):
    name = os.path.basename(d) if d else "首页"
    subs = child_dirs.get(d, [])
    items = []
    for i, s in enumerate(subs):
        sname = os.path.basename(s)
        href = os.path.join(sname, "index.html")
        intro = folder_intro(s, dir_docs, child_dirs)
        created = folder_created(s, dir_earliest)
        items.append(cat_item(sname, href, len(docs_under(docs, s)), created, intro, i))

    direct = dir_docs.get(d, [])
    if direct:
        created = folder_created(d, dir_earliest)
        items.append(cat_item("散篇", "direct.html", len(direct), created, "未归入子目录的散篇笔记", len(subs)))

    body = f"""
{breadcrumb(d, out_dir)}
<div class="page-head"><h1>{esc(name)}</h1><div class="count">共 {len(subs)} 个二级分类</div></div>
<div class="cat-list">{''.join(items)}</div>
"""
    return page(out_dir, name, body, parent_href=parent_href_for(d, out_dir))


def build_reading_page(d, docs, dir_docs, child_dirs, images, out_dir, doc_list=None):
    name = os.path.basename(d) if d else "全部文章"
    if doc_list is None:
        doc_list = docs_under(docs, d)
    articles = []
    titles = []
    for rel in doc_list:
        r = render_doc(rel, out_dir, images)
        titles.append(r["title"])
        articles.append(f'<article class="doc" id="{doc_anchor(rel)}" data-title="{esc(r["title"])}"><div class="doc-body">{r["body"]}</div></article>')

    content = ''.join(articles) if articles else '<div class="doc"><p>暂无文章</p></div>'

    mode = ""
    if len(articles) > 1:
        options = ''.join(
            f'<option value="{i}">{i + 1}. {esc(title)}</option>'
            for i, title in enumerate(titles)
        )
        mode = f"""
<div class="reading-mode" data-reading-mode>
  <div class="reading-mode-bar">
    <div class="reading-mode-info">
      <span class="reading-mode-badge">阅读模式</span>
      <span class="reading-mode-count" data-read-count>第 1 / {len(articles)} 篇</span>
      <span class="reading-mode-title" data-read-title>{esc(titles[0])}</span>
    </div>
    <div class="reading-mode-controls" data-read-controls>
      <button type="button" class="reading-mode-btn" data-read-prev>上一篇</button>
      <select data-read-select aria-label="选择文章">{options}</select>
      <button type="button" class="reading-mode-btn" data-read-next>下一篇</button>
    </div>
    <div class="reading-mode-toggle" role="group" aria-label="阅读模式">
      <button type="button" data-read-mode="paged" aria-pressed="true">分页阅读</button>
      <button type="button" data-read-mode="continuous" aria-pressed="false">连续阅读</button>
    </div>
  </div>
  <div class="doc-stack" data-doc-stack>{content}</div>
</div>"""
    else:
        mode = f'<div class="doc-stack" data-doc-stack>{content}</div>'

    body = f"""
{breadcrumb(d, out_dir)}
<div class="page-head"><h1>{esc(name)}</h1><div class="count">共 {len(doc_list)} 篇文章</div></div>
{mode}
"""
    return page(out_dir, name, body, with_math=True, parent_href=parent_href_for(d, out_dir))


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def main():
    global AVATAR_NAME, UPDATES_JSON, NAV_SECTIONS, MUSIC_JSON
    docs, images, dir_earliest = scan()
    dir_docs, child_dirs = build_tree(docs)

    # 默认不删除 site 根目录：Hugo server 可能占用文件。需要全量清理时使用 --clean。
    if "--clean" in sys.argv and os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    os.makedirs(SITE_DIR, exist_ok=True)
    os.makedirs(ASSET_DIR, exist_ok=True)
    os.makedirs(RES_DIR, exist_ok=True)
    write_text(os.path.join(SITE_DIR, ".nojekyll"), "")

    calendar_css = read_text(os.path.join(SRC_DIR, "calendar.css"))
    calendar_js = read_text(os.path.join(SRC_DIR, "calendar.js"))
    search_css = read_text(os.path.join(SRC_DIR, "search.css"))
    search_js = read_text(os.path.join(SRC_DIR, "search.js"))
    reading_css = read_text(os.path.join(SRC_DIR, "reading.css"))
    reading_js = read_text(os.path.join(SRC_DIR, "reading.js"))
    reading_mode_js = read_text(os.path.join(SRC_DIR, "reading-mode.js"))
    media_css = read_text(os.path.join(SRC_DIR, "media.css"))
    media_js = read_text(os.path.join(SRC_DIR, "media.js"))
    music_css = read_text(os.path.join(SRC_DIR, "music.css"))
    music_js = read_text(os.path.join(SRC_DIR, "music.js"))
    write_text(
        os.path.join(ASSET_DIR, "style.css"),
        CSS + "\n" + calendar_css + "\n" + search_css + "\n" + reading_css + "\n" + media_css + "\n" + music_css,
    )
    write_text(
        os.path.join(ASSET_DIR, "app.js"),
        JS + "\n" + calendar_js + "\n" + search_js + "\n" + reading_js + "\n" + reading_mode_js + "\n" + media_js + "\n" + music_js,
    )
    UPDATES_JSON = json.dumps(collect_updates(docs), ensure_ascii=False, sort_keys=True)
    MUSIC_JSON = load_music_playlist()
    copy_music()
    AVATAR_NAME = copy_avatar()

    l1_categories = child_dirs.get("", [])
    sections = build_sections(l1_categories)
    NAV_SECTIONS = build_nav_sections(sections, docs, child_dirs)

    home_html = build_home(docs, dir_docs, child_dirs, dir_earliest, SITE_DIR)
    write_text(os.path.join(SITE_DIR, "index.html"), home_html)

    page_count = 1
    for section in sections:
        section_out = os.path.join(SITE_DIR, section["slug"])
        html = build_section_page(section, l1_categories, docs, dir_docs, child_dirs, dir_earliest, section_out)
        write_text(os.path.join(section_out, "index.html"), html)
        page_count += 1

    pdfs = collect_pdfs()
    if os.path.isdir(PDF_DIR):
        shutil.rmtree(PDF_DIR, ignore_errors=True)
    for pdf in pdfs:
        if pdf.get("available", True):
            pdf["path"] = copy_pdf(pdf["rel"])
    library_out = os.path.join(SITE_DIR, "资料库")
    write_text(os.path.join(library_out, "index.html"), build_library_page(pdfs, library_out))
    page_count += 1

    doc_page_urls = {}
    for l1 in l1_categories:
        l1_out = os.path.join(SITE_DIR, l1)
        subs = child_dirs.get(l1, [])
        direct = dir_docs.get(l1, [])

        if subs:
            html = build_folder_page(l1, docs, dir_docs, child_dirs, dir_earliest, l1_out)
            write_text(os.path.join(l1_out, "index.html"), html)
            page_count += 1
            if direct:
                for rel in direct:
                    doc_page_urls[rel] = quote_url(os.path.join(l1, "direct.html"))
                html = build_reading_page(l1, docs, dir_docs, child_dirs, images, l1_out, doc_list=direct)
                write_text(os.path.join(l1_out, "direct.html"), html)
                page_count += 1
            for l2 in subs:
                l2_out = os.path.join(SITE_DIR, l2)
                for rel in docs_under(docs, l2):
                    doc_page_urls[rel] = quote_url(os.path.join(l2, "index.html"))
                html = build_reading_page(l2, docs, dir_docs, child_dirs, images, l2_out)
                write_text(os.path.join(l2_out, "index.html"), html)
                page_count += 1
        else:
            for rel in docs_under(docs, l1):
                doc_page_urls[rel] = quote_url(os.path.join(l1, "index.html"))
            html = build_reading_page(l1, docs, dir_docs, child_dirs, images, l1_out)
            write_text(os.path.join(l1_out, "index.html"), html)
            page_count += 1

    search_index = []
    for rel in docs:
        page_url = doc_page_urls.get(rel)
        if not page_url:
            continue
        try:
            mtime = os.path.getmtime(os.path.join(POST_DIR, rel))
        except OSError:
            mtime = 0
        category_parts = [p for p in os.path.dirname(rel).split(os.sep) if p]
        category = category_parts[0] if category_parts else "未分类"
        section = section_for_category(category)
        if section:
            category = f"{section['title']} / {category}"
        search_index.append({
            "title": DOC_TITLE.get(rel, os.path.splitext(os.path.basename(rel))[0]),
            "url": page_url + "#" + doc_anchor(rel),
            "category": category or "未分类",
            "date": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d") if mtime else "",
            "text": DOC_TEXT.get(rel, ""),
        })
    search_index.sort(key=lambda item: (item["date"], item["title"]), reverse=True)
    search_path = os.path.join(ASSET_DIR, "search-index.json")
    write_text(search_path, json.dumps(search_index, ensure_ascii=False, separators=(",", ":")))

    img_count = sum(len(fs) for _, _, fs in os.walk(RES_DIR))
    print(f"[完成] 生成 {page_count} 个页面, 复制 {img_count} 张图片 -> {SITE_DIR}")
    print(f"[搜索] 索引 {len(search_index)} 篇文章, {os.path.getsize(search_path) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
