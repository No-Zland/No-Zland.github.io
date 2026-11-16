# -*- coding: utf-8 -*-
"""
板块式个人博客静态生成器
- 首页: 名言警句 + 知识卫星图（分类内环 + 文章外环，点一下直接进文章）
- 板块页: 该板块下的分类列表
- 分类页: 子分类列表，或文章阅读页
- 阅读页: 一篇文章一页，左侧目录与上一篇/下一篇组件，不再截断文章
- 左侧抽屉: 对外个人主页（GitHub / 哔哩哔哩 / 邮箱）与更新日历
- 支持浅色/暗色主题、中英切换（梁双宇 / Shine Leong）
"""
import os
import re
import math
import glob
import hashlib
import sys
import json
import html
import hashlib
import shutil
import stat
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
QUOTES_JSON = "[]"  # 名言警句，main() 中写入
NOTE_SECTIONS_JSON = "[]"  # 在线笔记的板块/分类选项
ASSET_VERSION = "0"  # 样式/脚本缓存版本，main() 中写入
QUOTES = []  # 名言列表，main() 中写入
DOC_TITLE = {}  # 文章标题，渲染时收集
DOC_TEXT = {}  # 文章纯文本，渲染时收集
NAV_SECTIONS = []  # 侧栏层级导航数据，main 中构建
SEARCH_TEXT_LIMIT = 30000  # 单篇索引的正文上限，避免超长笔记撑大索引
MAX_PDF_BYTES = 10 * 1024 * 1024  # GitHub Pages 只上传 10MB 以内的 PDF

def _load_cert_thumbs():
    path = os.path.join(ROOT, "assets", "certs", "manifest.json")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


CERT_THUMBS = {}

SECTION_SPECS = [
    {
        "slug": "01-个人知识体系的构建",
        "title": "个人知识体系的构建",
        "desc": "从计算机系统到应用开发的知识网络，按主题而非时间组织。",
        "color": "#2563eb",
        "layout": "map",
    },
    {
        "slug": "02-竞赛科研经历与复盘",
        "title": "竞赛科研经历与复盘",
        "desc": "每一次比赛与科研训练的时间线、复盘与题解。",
        "color": "#7c3aed",
        "layout": "timeline",
    },
    {
        "slug": "03-成果展示",
        "title": "成果展示",
        "desc": "做过的项目与拿到的证书。",
        "color": "#0ea5b7",
        "layout": "gallery",
    },
    {
        "slug": "书架",
        "title": "书架",
        "desc": "正在读的电子书，封面取 PDF 的第一页。",
        "color": "#b45309",
        "layout": "shelf",
    },
]


def nav_doc_list(rels, child_dirs):
    """把一批文档变成导航里的叶子条目（标题 + 锚点）。"""
    items = []
    for rel in rels:
        path = os.path.join(POST_DIR, rel)
        title = os.path.splitext(os.path.basename(rel))[0]
        try:
            title = extract_title(strip_frontmatter(read_text(path)), title)
        except OSError:
            pass
        items.append({
            "title": title,
            "href": doc_page_target(rel, child_dirs) + "#" + doc_anchor(rel),
        })
    return items


def build_nav_sections(sections, docs, child_dirs, dir_image_counts=None):
    """按真实目录递归建树：每一层目录都是节点，叶子是文章。"""

    def make(rel, depth):
        children = []
        for sub in sorted(child_dirs.get(rel, []), key=lambda r: natural_key(os.path.basename(r))):
            children.append(make(sub, depth + 1))
        direct = [r for r in docs if os.path.dirname(r) == rel]
        _imgs = dir_image_counts or {}
        img_docs = _imgs.get(rel.replace(os.sep, "/"), 0) or _imgs.get(rel, 0)
        total = len(docs_under(docs, rel)) if docs_under(docs, rel) else img_docs
        return {
            "rel": rel,
            "name": os.path.basename(rel),
            "depth": depth,
            "count": total,
            "docs": nav_doc_list(sorted(direct, key=natural_key), child_dirs),
            "children": children,
        }

    nav = []
    for section in sections:
        node = make(section["slug"], 1)
        nav.append({
            "slug": section["slug"],
            "title": section["title"],
            "color": section["color"],
            "total": len(docs_under(docs, section["slug"])),
            "tree": node,
        })
    return nav


def section_for_category(cat):
    first = cat.split(os.sep)[0]
    for spec in SECTION_SPECS:
        if spec["slug"] == first:
            return spec
    return None


def frontmatter_dict(text):
    """极简 frontmatter 解析：key: value 或 key:\n  - item。"""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    data = {}
    key = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            key = m.group(1).lower()
            val = m.group(2).strip().strip('"').strip("'")
            data[key] = val
        elif key and line.strip().startswith("-"):
            val = line.strip()[1:].strip().strip('"').strip("'")
            data[key] = (data.get(key) or "") + ("," if data.get(key) else "") + val
    return data


def folder_meta(rel):
    """读取目录下 _index.md 的 frontmatter，作为板块/分类的标题与说明。"""
    for name in ("_index.md", "index.md"):
        path = os.path.join(POST_DIR, rel, name)
        if not os.path.isfile(path):
            continue
        try:
            text = read_text(path)
        except OSError:
            continue
        fm = frontmatter_dict(text)
        body = strip_frontmatter(text).strip()
        first_line = ""
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                first_line = re.sub(r"[*_`>\-]", "", line).strip()
                break
        return {
            "title": fm.get("title") or "",
            "desc": fm.get("desc") or fm.get("description") or fm.get("summary") or first_line or "",
            "color": fm.get("color") or "",
        }
    return {}


def build_sections(l1):
    """顶层目录就是板块；板块下的子目录是分类。"""
    sections = []
    used = set()
    for spec in SECTION_SPECS:
        if spec["slug"] in l1:
            sections.append(dict(spec))
            used.add(spec["slug"])
    for name in l1:
        if name in used or name.startswith(".") or name == "资料库":
            continue
        sections.append({
            "slug": name,
            "title": name,
            "desc": "其他内容。",
            "color": "#64748b",
        })
    for section in sections:
        meta = folder_meta(section["slug"])
        if meta.get("title"):
            section["title"] = meta["title"]
        if meta.get("desc"):
            section["desc"] = meta["desc"]
        if meta.get("color"):
            section["color"] = meta["color"]
    return sections

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}
SKIP_DIRS = {"bin", "node_modules", "__pycache__", "00-导航"}  # 00-导航 只放 MOC/模板，不发布到博客

MATHJAX_HEAD = '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>'  # 旧版外链，已改为本地自托管

ROBOTS_TXT = """# 允许正常搜索引擎索引，但拒绝 AI 训练/批量抓取，并保护原始资源与搜索索引。
User-agent: *
Allow: /
Disallow: /assets/files/
Disallow: /assets/music/
Disallow: /assets/search-index.json
Crawl-delay: 10

User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: OAI-SearchBot
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: meta-externalagent
Disallow: /

User-agent: Amazonbot
Disallow: /

User-agent: cohere-ai
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: Omgilibot
Disallow: /

User-agent: Scrapy
Disallow: /

User-agent: python-requests
Disallow: /

User-agent: curl
Disallow: /

User-agent: wget
Disallow: /
"""


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
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def force_rmtree(path):
    """Windows 下 read-only 文件会让 rmtree 失败，先去掉只读属性。"""
    if not os.path.isdir(path):
        return
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            try:
                os.chmod(os.path.join(dirpath, name), 0o644)
            except OSError:
                pass
    shutil.rmtree(path)


def is_image(path):
    return os.path.splitext(path)[1].lower() in IMAGE_EXTS


# --------------------------------------------------------------------------- #
# 扫描 content/post, 收集文档、图片、以及每个目录的最早文件修改时间(作为创立时间)
# --------------------------------------------------------------------------- #
def scan():
    docs = []
    images = defaultdict(list)
    image_dirs = set()
    dir_image_counts = defaultdict(int)
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
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS and not d.endswith("_assets")]
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
                if rel_dir:
                    image_dirs.add(rel_dir)
                    dir_image_counts[rel_dir] += 1

    docs.sort(key=lambda r: natural_key(r.replace("\\", "/")))
    return docs, images, dir_earliest, image_dirs, dir_image_counts


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
    if os.path.exists(dest):
        try:
            os.chmod(dest, 0o644)
        except OSError:
            pass
    shutil.copy2(src_abs, dest)
    try:
        os.chmod(dest, 0o644)
    except OSError:
        pass
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
    for dirpath, dirnames, filenames in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        out_dir = dest if rel == "." else os.path.join(dest, rel)
        os.makedirs(out_dir, exist_ok=True)
        for name in filenames:
            target = os.path.join(out_dir, name)
            if os.path.exists(target):
                try:
                    os.chmod(target, 0o644)
                except OSError:
                    pass
            shutil.copy2(os.path.join(dirpath, name), target)
            try:
                os.chmod(target, 0o644)
            except OSError:
                pass


def load_music_playlist():
    path = os.path.join(ROOT, "music", "playlist.json")
    try:
        raw = json.loads(read_text(path))
        if isinstance(raw, list):
            return json.dumps(raw, ensure_ascii=False, separators=(",", ":"))
    except (OSError, ValueError):
        pass
    return "[]"


def load_quotes():
    """从阅读经历的《名人名言》里读取句子，每行格式：- 句子｜作者。"""
    path = os.path.join(POST_DIR, "阅读经历", "书籍资料", "名人名言.md")
    quotes = []
    try:
        text = read_text(path)
    except OSError:
        return quotes
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("- "):
            continue
        line = line[2:].strip()
        if not line:
            continue
        sep = "｜" if "｜" in line else ("|" if "|" in line else None)
        if sep:
            quote, author = line.rsplit(sep, 1)
        else:
            quote, author = line, "佚名"
        quote = re.sub(r"[*_`]", "", quote).strip()
        author = re.sub(r"[*_`]", "", author).strip()
        if quote:
            quotes.append({"text": quote, "author": author or "佚名"})
    return quotes


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
    try:
        os.chmod(dest, 0o644)
    except OSError:
        pass
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


def resolve_image_path(rel_url, md_dir):
    """图片可能写成：同目录文件名 / 同名 _assets 下的文件名 / 从 content/post 起的路径。"""
    candidates = [
        os.path.normpath(os.path.join(md_dir, rel_url)),
        os.path.normpath(os.path.join(POST_DIR, rel_url)),
    ]
    base = os.path.basename(rel_url)
    for assets_dir in sorted(glob.glob(os.path.join(md_dir, "*_assets"))):
        candidates.append(os.path.join(assets_dir, base))
    for candidate in candidates:
        if os.path.isfile(candidate) and is_image(candidate):
            return candidate
    return None


def preprocess(text, md_dir, out_dir, images):
    def std_img(m):
        alt = m.group(1)
        url = m.group(2).strip()
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url) or url.startswith(("data:", "/", "#")):
            return m.group(0)
        decoded = urllib.parse.unquote(url).replace("\\", "/")
        src_abs = resolve_image_path(decoded, md_dir)
        if src_abs:
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


def _math_body(lines):
    """块公式内容：有 \\ 但没有 \begin{...} 时套一层 gathered，MathJax 才会换行。"""
    body = "\n".join(lines)
    if "\\\\" in body and "\\begin{" not in body:
        return ["\\begin{gathered}"] + lines + ["\\end{gathered}"]
    return lines


def _inline_math(text):
    r"""把一行里的 \(..\) / \[..\] / $$..$$ 统一成 $..$（跳过行内代码）。"""
    chunks = re.split(r"(`[^`]*`)", text)
    for k, ch in enumerate(chunks):
        if ch.startswith("`") and ch.endswith("`") and len(ch) > 1:
            continue

        def wrap(inner):
            inner = inner.strip()
            if "\\\\" in inner and "\\begin{" not in inner:
                return "$\\begin{gathered}" + inner + "\\end{gathered}$"
            return "$" + inner + "$"

        ch = re.sub(r"\\\((.+?)\\\)", lambda m: wrap(m.group(1)), ch)
        # 只有内部出现 LaTeX 命令时才当公式，避免把 d \['k'] 这种转义方括号吃掉
        ch = re.sub(r"\\\[(.+?)\\\]",
                    lambda m: wrap(m.group(1)) if re.search(r"\\[a-zA-Z]+", m.group(1)) else m.group(0),
                    ch)
        ch = re.sub(r"\$\$(.+?)\$\$", lambda m: wrap(m.group(1)), ch)
        chunks[k] = ch
    return "".join(chunks)


def normalize_math(text):
    r"""让站点按 Obsidian 的写法认公式：

    - $$ / \[ 独占一行 = 块公式（前后补空行，交给 arithmatex）
    - 行内 \(..\) / \[..\] / $$..$$ = 行内公式
    - 块公式里裸的 \\ 自动包一层 gathered（MathJax 3 在裸 \[..\] 里不认 \\）
    """
    lines = text.splitlines()
    out = []
    in_fence = False
    buf = None

    def flush():
        out.append("$$")
        out.extend(_math_body(buf))
        out.append("$$")
        out.append("")

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        if buf is not None:
            if stripped in ("$$", "\\]"):
                flush()
                buf = None
            elif stripped:
                buf.append(stripped)
            continue

        if stripped in ("$$", "\\["):
            if out and out[-1].strip():
                out.append("")
            buf = []
            continue

        single = re.fullmatch(r"\$\$(.+?)\$\$", stripped)
        if single:
            if out and out[-1].strip():
                out.append("")
            buf = [single.group(1).strip()]
            flush()
            buf = None
            continue

        out.append(_inline_math(line))

    if buf is not None:
        flush()

    return "\n".join(out)


def indent_paragraphs(html_text, min_chars=24):
    """给长段落的 <p> 加上 p-indent 类（CSS 首行缩进两格）。

    引用块、列表、表格里的段落不动；短句（标签、图注、“输入：”这类）也不缩进。
    """
    parts = re.split(
        r"(<blockquote\b[^>]*>|</blockquote>|<li\b[^>]*>|</li>|<td\b[^>]*>|</td>|<th\b[^>]*>|</th>)",
        html_text,
        flags=re.I,
    )

    def mark(m):
        inner = m.group(1)
        plain = re.sub(r"<[^>]+>", "", inner)
        plain = re.sub(r"\s+", "", plain)
        if len(plain) < min_chars:
            return m.group(0)
        return '<p class="p-indent">' + inner + "</p>"

    depth = 0
    out = []
    for part in parts:
        low = part.lower()
        if low.startswith("<blockquote") or low.startswith("<li") or low.startswith("<td") or low.startswith("<th"):
            depth += 1
            out.append(part)
            continue
        if low.startswith("</blockquote") or low.startswith("</li") or low.startswith("</td") or low.startswith("</th"):
            depth = max(0, depth - 1)
            out.append(part)
            continue
        out.append(re.sub(r"<p>(.*?)</p>", mark, part, flags=re.S) if depth == 0 else part)
    return "".join(out)


def convert_md(text):
    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "sane_lists",
            "nl2br",               # 与 Obsidian 一致：单个换行就是换行
            "pymdownx.mark",       # ==高亮==
            "pymdownx.tilde",      # ~~删除~~ 与 ~下标~
            "pymdownx.caret",      # ^上标^
            "pymdownx.tasklist",   # - [ ] 任务列表
            "pymdownx.arithmatex", # $...$ / $$...$$ 公式
        ],
        extension_configs={"pymdownx.arithmatex": {"generic": True}},
        output_format="html5",
    )
    html_out = md.convert(text)
    # 表格单元格里连着几个空行会变成一串 <br>，塌缩成一个，避免行高爆炸
    html_out = re.sub(r"<img (?![^>]*\bloading=)", '<img loading="lazy" decoding="async" ', html_out)
    html_out = re.sub(
        r"<td([^>]*)>(.*?)</td>",
        lambda m: "<td" + m.group(1) + ">" + re.sub(r"(?:<br\s*/?>\s*){2,}", "<br>", m.group(2)) + "</td>",
        html_out,
        flags=re.S,
    )
    return indent_paragraphs(html_out)


def render_doc(rel, out_dir, images):
    abs_path = os.path.join(POST_DIR, rel)
    md_dir = os.path.dirname(abs_path)
    raw = read_text(abs_path)
    raw = strip_frontmatter(raw)
    title = extract_title(raw, os.path.splitext(os.path.basename(rel))[0])
    processed = preprocess(raw, md_dir, out_dir, images)
    processed = normalize_math(processed)
    processed = fix_tables(processed)
    body = convert_md(processed)
    DOC_TITLE[rel] = title
    DOC_TEXT[rel] = html_to_text(body)[:SEARCH_TEXT_LIMIT]
    return {"rel": rel, "title": title, "body": body}


# --------------------------------------------------------------------------- #
# 目录树与简介/创立时间
# --------------------------------------------------------------------------- #
def build_tree(docs, extra_dirs=()):
    dir_docs = defaultdict(list)
    for rel in docs:
        d = os.path.dirname(rel)
        dir_docs[d].append(rel)

    dirs_with_content = set(extra_dirs)
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
      'quotes-label': '名言警句',
      'quote-refresh': '换一句',
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
      'quotes-label': 'Quotes',
      'quote-refresh': 'Another',
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
MUSIC_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/></svg>'
NOTE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h4l10-10a2.8 2.8 0 0 0-4-4L4 16v4z"/><path d="M13.5 6.5 17.5 10.5"/></svg>'
SHELF_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h4v16H4zM10 4h4v16h-4zM17 5l3-1 4 15-3 1z"/></svg>'
SEARCH_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
BACK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 14 4 9l5-5"/><path d="M4 9h9.5a5.5 5.5 0 0 1 0 11H11"/></svg>'


def search_overlay_html():
    return """
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


def page(out_dir, title, body, with_math=False, is_home=False, parent_href=None, side_extra=""):
    style_href = quote_url(rel_from(out_dir, os.path.join(ASSET_DIR, "style.css"))) + "?v=" + ASSET_VERSION
    script_src = quote_url(rel_from(out_dir, os.path.join(ASSET_DIR, "app.js"))) + "?v=" + ASSET_VERSION
    music_base = "/assets/music"
    home_href = "/"
    drawer_html = build_drawer(out_dir)
    shelf_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "书架", "index.html")))
    note_href_top = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "写笔记", "index.html")))
    math = ""
    if with_math:
        mj = quote_url(rel_from(out_dir, os.path.join(ASSET_DIR, "mathjax", "tex-svg.js")))
        math = f'<script defer src="{mj}"></script>'
    back_href = parent_href or "/"
    back_hidden = "" if parent_href else " hidden"
    back_html = (
        f'<a class="icon-btn back-btn" href="{back_href}" title="返回上一级" '
        f'aria-label="返回上一级" data-i18n-title="back" data-i18n-aria-label="back"{back_hidden}>{BACK_SVG}</a>'
    )
    body_class = ' class="page-home"' if is_home else ""
    nav_html = "" if is_home else side_nav_for(out_dir)
    if nav_html:
        main_class = "main main-wide"
        side_html = (
        '<div class="side-column">' + nav_html + music_player_html() + side_extra + '</div>'
        '<button type="button" class="side-tab" data-side-toggle aria-label="收起侧栏" title="收起侧栏">&#8249;</button>'
        '<button type="button" class="side-tab-restore" data-side-toggle aria-label="展开侧栏" title="展开侧栏" hidden>&#8250;</button>'
    )
        main_inner = f'<div class="page-layout">{side_html}<div class="page-main">{body}</div></div>'
    else:
        main_class = "main"
        main_inner = body
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="author" content="梁双宇">
<meta name="robots" content="noai, noimageai, noarchive">
<meta name="googlebot" content="noarchive">
<meta name="copyright" content="© 2026 梁双宇 · CC BY-NC-SA 4.0">
<title>{esc(title)} · 梁双宇</title>
<link rel="stylesheet" href="{style_href}">
{math}
</head>
<body{body_class}>
{drawer_html}
{search_overlay_html()}
<div class="page-dim" id="pageDim" aria-hidden="true"></div>
<div class="brightness-control" data-brightness>
  <span class="brightness-icon" aria-hidden="true">☀</span>
  <span class="brightness-label">亮度</span>
  <input class="brightness-range" id="brightnessRange" type="range" min="60" max="100" step="1" value="85" aria-label="页面亮度">
  <span class="brightness-value" id="brightnessValue">85%</span>
</div>
<div class="note-agent" id="noteAgent">
  <button type="button" class="agent-toggle" id="agentToggle" aria-label="打开笔记助手" aria-expanded="false">
    <svg class="agent-avatar-svg" viewBox="0 0 120 140" role="img" aria-label="小双">
      <ellipse class="agent-shadow" cx="60" cy="127" rx="27" ry="5"/>
      <path class="agent-body" d="M30 101 Q60 82 90 101 L96 124 Q60 136 24 124 Z"/>
      <circle class="agent-head" cx="60" cy="58" r="30"/>
      <path class="agent-hair" d="M30 57 Q30 21 60 21 Q90 21 90 57 Q82 44 72 40 Q60 50 48 40 Q38 44 30 57"/>
      <path class="agent-ahoge" d="M62 23 Q68 10 78 14 Q70 18 67 27"/>
      <g class="agent-eyes">
        <ellipse cx="49" cy="61" rx="3.2" ry="4.2"/>
        <ellipse cx="71" cy="61" rx="3.2" ry="4.2"/>
      </g>
      <path class="agent-smile" d="M53 70 Q60 76 67 70"/>
      <circle class="agent-blush" cx="41" cy="69" r="4"/>
      <circle class="agent-blush" cx="79" cy="69" r="4"/>
      <path class="agent-collar" d="M50 105 L60 113 L70 105"/>
    </svg>
    <span class="agent-label">笔记助手</span>
  </button>
  <section class="agent-panel" id="agentPanel" hidden aria-label="笔记助手">
    <header class="agent-panel-head">
      <span class="agent-mini-avatar" data-agent-avatar aria-hidden="true"></span>
      <span class="agent-panel-title"><strong>小双</strong><small>站内笔记助手</small></span>
      <button type="button" class="agent-close" id="agentClose" aria-label="关闭笔记助手">&times;</button>
    </header>
    <div class="agent-messages" id="agentMessages" aria-live="polite"></div>
    <form class="agent-form" id="agentForm">
      <input class="agent-input" id="agentInput" type="text" placeholder="问：数学建模 / ADC / 最近更新…" autocomplete="off" maxlength="120">
      <button class="agent-send" type="submit" aria-label="发送">↑</button>
    </form>
    <div class="agent-hint">基于站内笔记检索，不调用外部模型；答案会带原文链接。</div>
  </section>
</div>
<header class="topbar">
  <button class="icon-btn" id="menuBtn" aria-label="打开个人主页">&#9776;</button>
  <a class="home-btn" href="{home_href}" title="返回首页" aria-label="返回首页" data-i18n-title="home" data-i18n-aria-label="home">{HOME_SVG}</a>
  <a class="icon-btn shelf-btn" href="{shelf_href}" title="书架" aria-label="书架">{SHELF_SVG}</a>
  <button type="button" class="icon-btn top-search" id="searchTrigger" data-home="{home_href}" aria-haspopup="dialog" aria-expanded="false" title="搜索文章" aria-label="搜索文章" data-i18n-title="search-title" data-i18n-aria-label="search-title">{SEARCH_SVG}</button>
  {back_html}
  <a class="brand" href="{home_href}"><span class="brand-name" data-i18n="brand">梁双宇</span><span class="brand-sep">·</span><span class="brand-site" data-i18n="site-title">个人博客</span></a>
  <div class="spacer"></div>
  <button type="button" class="icon-btn music-btn" id="musicToggle" title="播放 / 暂停" aria-label="播放 / 暂停" aria-pressed="false">{MUSIC_SVG}</button>
  <a class="icon-btn note-btn" href="{note_href_top}" title="在线写笔记" aria-label="在线写笔记">{NOTE_SVG}</a>
  <button class="icon-btn" id="langBtn" title="中英切换">EN</button>
  <button class="icon-btn" id="themeBtn" title="切换主题">&#9789;</button>
</header>
<main class="{main_class}">
{main_inner}
</main>
<script>window.BLOG_UPDATES = {UPDATES_JSON};</script>
<script>window.MUSIC_BASE = "{music_base}"; window.MUSIC_PLAYLIST = {MUSIC_JSON};</script>
<script>window.NOTE_SECTIONS = {NOTE_SECTIONS_JSON};</script>
<script>window.BLOG_QUOTES = {QUOTES_JSON};</script>
<script src="{script_src}"></script>
</body>
</html>
"""


def cat_item(name, href, count, created, intro, index=0, unit="篇文章"):
    return f"""
<a class="cat-item" href="{quote_url(href)}" style="--i:{min(index, 8)}">
  <div class="cat-title">{esc(name)}</div>
  <div class="cat-desc">{esc(intro)}</div>
  <div class="cat-meta"><span>{count} {esc(unit)}</span><span class="dot">·</span><span>创立于 {esc(created)}</span></div>
</a>
"""


def breadcrumb(d, out_dir):
    home_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    parts = [f'<a href="{home_href}">首页</a>']
    if d:
        comps = [c for c in d.split(os.sep) if c]
        rel = ""
        for i, c in enumerate(comps):
            rel = os.path.join(rel, c) if rel else c
            href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, rel, "index.html")))
            label = c
            if i == 0:
                section = section_for_category(c)
                if section:
                    label = section["title"]
            parts.append(f'<a href="{href}">{esc(label)}</a>')
    return '<div class="crumb">' + " / ".join(parts) + "</div>"


def side_nav_for(out_dir):
    if not NAV_SECTIONS:
        return ""

    parts = [p for p in os.path.relpath(out_dir, SITE_DIR).split(os.sep) if p and p != "."]
    prefixes = set()
    for i in range(1, len(parts) + 1):
        prefixes.add(os.sep.join(parts[:i]))

    home_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    library_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "资料库", "index.html")))
    note_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "写笔记", "index.html")))
    shelf_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "书架", "index.html")))
    library_active = os.path.basename(out_dir.rstrip(os.sep)) == "资料库"
    note_active = os.path.basename(out_dir.rstrip(os.sep)) == "写笔记"

    def page_href(rel):
        segs = rel.split(os.sep)
        page = os.path.join(rel, "index.html") if len(segs) <= 3 else os.path.join(*segs[:3], "index.html")
        return quote_url(rel_from(out_dir, os.path.join(SITE_DIR, page)))

    def doc_href(href):
        page, _, anchor = href.partition("#")
        url = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, page)))
        return url + ("#" + anchor if anchor else "")

    def doc_row(d, depth, active=False):
        cls = "page-nav-doc" + (" is-active" if active else "")
        return (
            '<a class="%s" style="--d:%d" href="%s" title="%s">'
            '<span class="page-nav-dot"></span><span class="page-nav-name">%s</span></a>'
            % (cls, depth, doc_href(d["href"]), esc(d["title"]), esc(d["title"]))
        )

    gallery_slugs = {s["slug"] for s in SECTION_SPECS if s.get("layout") == "gallery"}

    def leaf_chip(node, depth):
        return (
            '<a class="page-nav-chip" href="%s" title="%s" style="--d:%d">'
            '<span class="page-nav-chip-name">%s</span>'
            '<span class="page-nav-chip-count">%d</span></a>'
            % (page_href(node["rel"]), esc(node["name"].lstrip("_")),
               depth, esc(node["name"].lstrip("_")), node["count"])
        )

    def render_node(node, depth):
        kids = node["children"]
        docs = node["docs"]

        if not kids and not docs:
            if node["count"]:
                return ('<a class="page-nav-doc is-leaf" style="--d:%d" href="%s" title="%s">'
                        '<span class="page-nav-dot"></span><span class="page-nav-name">%s</span>'
                        '<span class="page-nav-count">%d</span></a>'
                        % (depth, page_href(node["rel"]), esc(node["name"].lstrip("_")),
                           esc(node["name"].lstrip("_")), node["count"]))
            return ""
        if depth <= 3:
            head = (
                '<summary><a class="page-nav-name" href="%s">%s</a>'
                '<span class="page-nav-count">%d</span></summary>'
                % (page_href(node["rel"]), esc(node["name"].lstrip("_")), node["count"])
            )
        else:
            head = (
                '<summary><span class="page-nav-name">%s</span>'
                '<span class="page-nav-count">%d</span></summary>'
                % (esc(node["name"].lstrip("_")), node["count"])
            )
        inner = [render_node(k, depth + 1) for k in kids]
        inner += [doc_row(d, depth) for d in docs]
        open_attr = " open" if node["rel"] in prefixes else ""
        return '<details class="page-nav-node" style="--d:%d"%s>%s%s</details>' % (
            depth, open_attr, head, "".join(inner))

    rows = []
    for section in NAV_SECTIONS:
        section_active = bool(parts) and section["slug"] == parts[0]
        section_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, section["slug"], "index.html")))
        rows.append(
            '<a class="quick-cat page-nav-section%s" href="%s" title="%s">'
            '<span class="quick-dot" style="background:%s"></span>'
            '<span class="quick-name">%s</span>'
            '<span class="quick-count">%d</span></a>'
            % (" is-active" if section_active else "", section_href, esc(section["title"]),
               section["color"], esc(section["title"]), section["total"])
        )
        if section_active:
            tree = section["tree"]
            inner = [render_node(k, 2) for k in tree["children"]]
            inner += [doc_row(d, 1) for d in tree["docs"]]
            rows.append('<div class="page-nav-tree">' + "".join(inner) + "</div>")

    return f"""
<aside class="quick-nav page-nav" aria-label="层级导航">
  <div class="quick-head">
    <div class="quick-kicker">导航栏</div>
    <div class="quick-total">{len(NAV_SECTIONS)} 个板块</div>
  </div>
  <nav class="page-nav-list">{''.join(rows)}</nav>
</aside>
"""


def doc_page_target(rel, child_dirs):
    """文档最终落在哪个页面（与 main() 里 doc_page_urls 的规则保持一致）。"""
    parts = [x for x in os.path.dirname(rel).split(os.sep) if x]
    if not parts:
        page = "index.html"
    elif len(parts) == 1:
        page = os.path.join(parts[0], "direct.html") if child_dirs.get(parts[0]) else os.path.join(parts[0], "index.html")
    elif len(parts) == 2:
        cat = os.path.join(parts[0], parts[1])
        page = os.path.join(cat, "direct.html") if child_dirs.get(cat) else os.path.join(cat, "index.html")
    else:
        page = os.path.join(*parts[:3], "index.html")
    return page.replace(os.sep, "/")


def frontmatter_tags(path, limit=4):
    """从 frontmatter 里取标签，用于卫星图悬停提示。"""
    try:
        text = read_text(path)
    except OSError:
        return []
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end < 0:
        return []
    block = text[:end]
    m = re.search(r"^tags:\s*(.*)$", block, re.M)
    if not m:
        return []
    tags = []
    inline = m.group(1).strip()
    if inline.startswith("["):
        for item in inline.strip("[]").split(","):
            item = item.strip().strip('"').strip("'").lstrip("#").strip()
            if item:
                tags.append(item)
    else:
        for line in block[m.end():].splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("-"):
                item = s[1:].strip().strip('"').strip("'").lstrip("#").strip()
                if item:
                    tags.append(item)
            elif re.match(r"^[^\s-][^:]*:", s):
                break
    return tags[:limit]


CAT_PALETTE = [
    "#2563eb", "#7c3aed", "#0ea5b7", "#f59e0b",
    "#ec4899", "#10b981", "#ef4444", "#6366f1",
]


def build_satellite(sections, docs, dir_docs, child_dirs, only=None):
    if only:
        sections = [s for s in sections if s["slug"] == only]
    """首页知识卫星图：中心是「我」，两个星系分别是知识库和实战库，Python 只打包数据。"""
    cats, items, legend, meta = [], [], [], []
    for section in sections:
        if not section["cats"]:
            continue
        added = False
        for cat_rel in section["cats"]:
            ds = docs_under(docs, cat_rel)
            if not ds:
                continue
            ci = len(cats)
            cats.append({
                "name": os.path.basename(cat_rel),
                "color": CAT_PALETTE[ci % len(CAT_PALETTE)],
                "count": len(ds),
                "rel": quote_url(os.path.join(cat_rel, "index.html")),
                "sec": len(meta),
            })
            added = True
            for rel in ds:
                title = DOC_TITLE.get(rel) or os.path.splitext(os.path.basename(rel))[0]
                href = quote_url(doc_page_target(rel, child_dirs)) + "#" + doc_anchor(rel)
                crumb = os.path.dirname(rel).replace(os.sep, " / ")
                items.append([title, href, ci, frontmatter_tags(os.path.join(POST_DIR, rel)), crumb])
        if added:
            meta.append({
                "name": section["title"],
                "color": section["color"],
                "rel": quote_url(os.path.join(section["slug"], "index.html")),
            })
            legend.append(
                '<span class="sat-legend-item"><i style="background:%s"></i>%s</span>'
                % (section["color"], esc(section["title"]))
            )

    payload = json.dumps(
        {"cats": cats, "docs": items, "sections": meta},
        ensure_ascii=False, separators=(",", ":"),
    )
    payload = payload.replace("</", "<\\/")
    fallback = "".join('<li><a href="%s">%s</a></li>' % (d[1], esc(d[0])) for d in items)

    return (
        '<div class="satellite" id="sections">\n'
        '<canvas class="sat-canvas" role="img" aria-label="知识卫星图：中心是我，拖动旋转、滚轮缩放，点击节点进入文章"></canvas>\n'
        '<div class="sat-tools">'
        '<button type="button" data-sat-zoom="in" title="放大" aria-label="放大">＋</button>'
        '<button type="button" data-sat-zoom="out" title="缩小" aria-label="缩小">－</button>'
        '<button type="button" data-sat-zoom="reset" title="复位" aria-label="复位">⟲</button>'
        '</div>\n'
        '<div class="sat-legend">' + "".join(legend) +
        '<span class="sat-hint">拖动旋转 · 右键/双指平移 · 滚轮缩放 · 点一次聚焦，再点进入</span></div>\n'
        '<ul class="sat-sr">' + fallback + '</ul>\n'
        '<script type="application/json" class="sat-data">' + payload + '</script>\n'
        '</div>'
    )


def build_home(docs, dir_docs, child_dirs, dir_earliest, out_dir):
    l1 = child_dirs.get("", [])
    sections = build_sections(l1)
    for section in sections:
        section["cats"] = child_dirs.get(section["slug"], [])
    quick_items = []
    article_total = 0
    for i, section in enumerate(sections):
        total = len(docs_under(docs, section["slug"]))
        article_total += total
        href = os.path.join(section["slug"], "index.html")
        quick_items.append(
            f'<a class="quick-cat" href="{quote_url(href)}" title="{esc(section["title"])}">'
            f'<span class="quick-dot" style="background:{section["color"]}"></span>'
            f'<span class="quick-name">{esc(section["title"])}</span>'
            f'<span class="quick-count">{total}</span></a>'
        )

    body = f"""
<h1 class="sr-only" data-i18n="home-title">梁双宇的个人博客</h1>
<div class="home-layout">
  <div class="side-column">
  <aside class="quick-nav" aria-label="导航栏" data-i18n-aria-label="quick-title">
    <div class="quick-head">
      <div class="quick-kicker" data-i18n="quick-title">导航栏</div>
      <div class="quick-total">{len(sections)} 个板块</div>
    </div>
    <div class="quick-label" data-i18n="quick-cats">板块</div>
    <nav class="quick-list" aria-label="板块目录">
      {''.join(quick_items)}
    </nav>
    <a class="quick-profile" href="#profile">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c.8-4 3.6-6 7-6s6.2 2 7 6"/></svg>
      <span data-i18n="quick-profile">个人信息 / 日历</span>
    </a>
  </aside>
  {music_player_html()}
  </div>
  <button type="button" class="side-tab" data-side-toggle aria-label="收起侧栏" title="收起侧栏">&#8249;</button>
  <button type="button" class="side-tab-restore" data-side-toggle aria-label="展开侧栏" title="展开侧栏" hidden>&#8250;</button>
    <div class="home-content">
    <div class="home-motto-block" id="sections">
      <div class="home-motto-head">
        <button type="button" class="quote-refresh" id="quoteRefresh" aria-label="换一句" data-i18n-aria-label="quote-refresh">↻ <span data-i18n="quote-refresh">换一句</span></button>
      </div>
      <h2 class="home-motto-text" id="homeQuote">{esc(QUOTES[0]["text"])}</h2>
      <div class="quote-author" id="homeQuoteAuthor">—— {esc(QUOTES[0]["author"])}</div>
    </div>
    <div class="section-grid">{build_satellite(sections, docs, dir_docs, child_dirs, only=(sections[0]["slug"] if sections else None))}</div>
    <div class="home-stats">{len(sections)} 个板块 · {article_total} 篇文章</div>
  </div>
</div>
"""
    return page(out_dir, "个人博客", body, is_home=True)


def parent_href_for(d, out_dir):
    if not d:
        return quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    parent = os.path.dirname(d)
    if not parent:
        return quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    target_dir = os.path.join(SITE_DIR, parent)
    return quote_url(rel_from(out_dir, os.path.join(target_dir, "index.html")))


def music_player_html():
    return f"""
<div class="music-player" id="musicPlayer">
  <div class="music-head">
    <span class="music-kicker">音乐</span>
  </div>
  <div class="music-track">
    <div class="music-title" data-music-title>暂无曲目</div>
    <div class="music-artist" data-music-artist>—</div>
  </div>
  <div class="music-progress">
    <input class="music-seek" data-music-seek type="range" min="0" max="1000" step="1" value="0" aria-label="播放进度">
    <span class="music-time" data-music-time>0:00</span>
  </div>
  <div class="music-controls">
    <button type="button" data-music-prev aria-label="上一首" title="上一首">⏮</button>
    <button type="button" data-music-play aria-label="播放" title="播放">▶</button>
    <button type="button" data-music-next aria-label="下一首" title="下一首">⏭</button>
    <button type="button" data-music-mode-btn aria-label="切换播放模式" title="顺序 / 随机 / 单曲循环">→</button>
    <button type="button" data-music-playlist-btn aria-label="播放歌单" title="播放歌单">≡</button>
    <button type="button" data-music-lyrics aria-label="歌词" title="歌词">♪</button>
  </div>
  <div class="music-playlist" data-music-playlist hidden></div>
  <audio id="musicAudio" preload="metadata"></audio>
</div>
"""



def _cat_date(name):
    """从目录名里取日期：202609 / 20260912 / 2026-09-12。"""
    m = re.match(r"^(\d{4})(\d{2})(\d{2})?", name)
    if not m:
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", name)
        if m:
            return "%s.%s.%s" % (m.group(1), m.group(2), m.group(3)), m.group(1) + m.group(2) + m.group(3)
        return None, ""
    y, mo, d = m.group(1), m.group(2), m.group(3)
    if d:
        return "%s.%s.%s" % (y, mo, d), y + mo + d
    return "%s.%s" % (y, mo), y + mo


def build_timeline(section, docs, dir_docs, child_dirs, dir_earliest, out_dir):
    rows = []
    for cat_rel in section["cats"]:
        name = os.path.basename(cat_rel)
        label, key = _cat_date(name)
        count = len(docs_under(docs, cat_rel))
        href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, cat_rel, "index.html")))
        intro = folder_intro(cat_rel, dir_docs, child_dirs)
        rows.append({
            "key": key or "0",
            "label": label or "未标注日期",
            "name": name,
            "href": href,
            "count": count,
            "intro": intro,
        })
    rows.sort(key=lambda r: r["key"], reverse=True)

    items = []
    for r in rows:
        items.append(
            '<div class="tl-item">'
            '<div class="tl-date">%s</div>'
            '<div class="tl-body">'
            '<a class="tl-card" href="%s"><h3>%s</h3><p>%s</p>'
            '<span class="tl-meta">%d 篇 · 进入 →</span></a>'
            '</div></div>'
            % (esc(r["label"]), r["href"], esc(r["name"]), esc(r["intro"]), r["count"])
        )
    if not items:
        items.append('<div class="tl-item"><div class="tl-date">—</div><div class="tl-body"><div class="tl-card"><h3>暂无记录</h3></div></div></div>')
    return '<div class="timeline">' + "".join(items) + '</div>'


def build_gallery(section, docs, dir_docs, child_dirs, dir_earliest, out_dir, images):
    """项目卡片墙：每个目录一张卡，证书墙也是同级的一张卡。"""
    cards = []
    for i, cat_rel in enumerate(section["cats"]):
        name = os.path.basename(cat_rel)
        count = len(docs_under(docs, cat_rel))
        folder = os.path.join(POST_DIR, cat_rel)
        unit = "篇文章"
        if count == 0 and os.path.isdir(folder):
            count = sum(1 for fn in os.listdir(folder)
                        if os.path.isfile(os.path.join(folder, fn)) and is_image(fn))
            if count:
                unit = "张图片"
        href = rel_from(out_dir, os.path.join(SITE_DIR, cat_rel, "index.html"))
        intro = folder_intro(cat_rel, dir_docs, child_dirs)
        meta = folder_meta(cat_rel)
        if meta.get("desc"):
            intro = meta["desc"]
        elif unit == "张图片":
            intro = "证书与获奖照片"
        display = name.lstrip("_")
        if meta.get("title"):
            display = meta["title"]
        cards.append(cat_item(display, href, count, folder_created(cat_rel, dir_earliest), intro, i, unit))

    return '<div class="gallery-grid">' + "".join(cards) + "</div>"


def build_section_page(section, l1, docs, dir_docs, child_dirs, dir_earliest, out_dir, images=None):
    items = []
    cats = section.get("cats", [])
    layout = section.get("layout", "cards")

    for i, cat_rel in enumerate(cats):
        count = len(docs_under(docs, cat_rel))
        href = rel_from(out_dir, os.path.join(SITE_DIR, cat_rel, "index.html"))
        intro = folder_intro(cat_rel, dir_docs, child_dirs)
        created = folder_created(cat_rel, dir_earliest)
        items.append(cat_item(os.path.basename(cat_rel), href, count, created, intro, i))

    direct = dir_docs.get(section["slug"], [])
    if direct:
        created = folder_created(section["slug"], dir_earliest)
        items.append(cat_item("散篇", "direct.html", len(direct), created, "未归入分类的散篇笔记", len(cats)))

    extra = ""
    if layout == "map":
        extra = build_satellite([section], docs, dir_docs, child_dirs, only=section["slug"])
    elif layout == "timeline":
        extra = build_timeline(section, docs, dir_docs, child_dirs, dir_earliest, out_dir)
    elif layout == "gallery":
        extra = build_gallery(section, docs, dir_docs, child_dirs, dir_earliest, out_dir, images or {})
    elif layout == "shelf":
        extra = build_shelf_grid(out_dir)
        if direct:
            href = rel_from(out_dir, os.path.join(SITE_DIR, section["slug"], "direct.html"))
            extra += (
                '<div class="shelf-notes"><a class="shelf-notes-link" href="%s">'
                "书架里的 %d 篇读书笔记 →</a></div>" % (quote_url(href), len(direct))
            )
    else:
        extra = '<div class="cat-list section-cats" style="--section-color:%s">%s</div>' % (
            section["color"], "".join(items))

    total = len(docs_under(docs, section["slug"]))
    home_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    body = f"""
<div class="crumb"><a href="{home_href}">首页</a> / {esc(section["title"])}</div>
<section class="section-hero" style="--section-color:{section["color"]}">
  <div class="section-hero-kicker">Section</div>
  <h1>{esc(section["title"])}</h1>
  <p>{esc(section["desc"])}</p>
  <div class="section-hero-meta">{len(cats)} 个分类 · {total} 篇文章</div>
</section>
{extra}
"""
    return page(out_dir, section["title"], body, parent_href=home_href)


def build_shelf_grid(out_dir):
    manifest_path = os.path.join(ROOT, "assets", "shelf", "manifest.json")
    if not os.path.isfile(manifest_path):
        return page(out_dir, "书架", '<div class="doc-body"><p>书架还是空的：先运行 <code>python tools/make_covers.py</code>。</p></div>')

    books = json.loads(read_text(manifest_path))
    groups = defaultdict(list)
    for b in books:
        parts = (b.get("folder") or "其他").split(" / ")
        top = "书架" if "书架" in parts else parts[0]
        groups[top].append(b)

    sections = []
    for top in sorted(groups):
        cards = []
        for b in groups[top]:
            cover = rel_from(out_dir, os.path.join(ASSET_DIR, "shelf", b["cover"]))
            inner = (
                '<div class="book-cover"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></div>'
                '<div class="book-title">%s</div>'
                '<div class="book-meta">%s · %.1f MB</div>'
                % (quote_url(cover), esc(b["title"]), b.get("w", 300), b.get("h", 400), esc(b["title"]), esc(b.get("folder", "")), b.get("size", 0))
            )
            if b.get("online"):
                href = rel_from(out_dir, os.path.join(SITE_DIR, copy_pdf(b["rel"])))
                cards.append(
                    '<a class="book" href="%s" target="_blank" rel="noopener" title="%s">%s</a>'
                    % (quote_url(href), esc(b["title"]), inner)
                )
            else:
                cards.append(
                    '<div class="book is-local" title="%s">%s<span class="book-badge">仅本地</span></div>'
                    % (esc(b["title"]), inner)
                )
        sections.append(
            '<section class="shelf-group"><h2 class="shelf-title">%s</h2>'
            '<div class="shelf-grid">%s</div></section>' % (esc(top), "".join(cards))
        )

    return (
        '<p class="shelf-desc">共 %d 本书，封面取 PDF 的第一页；点封面打开 PDF，“仅本地”表示体积太大没有上传。</p>'
        "%s"
    ) % (len(books), "".join(sections))


def build_note_page(out_dir):
    home_href = quote_url(rel_from(out_dir, os.path.join(SITE_DIR, "index.html")))
    body = f"""
<div class="crumb"><a href="{home_href}">首页</a> / 在线写笔记</div>
<div class="note-page-head">
  <h1>在线写笔记</h1>
  <div class="count">管理员专用 · 登录后才能写作与发布</div>
</div>
<section class="note-gate" data-note-gate>
  <div class="note-gate-lock" aria-hidden="true">🔒</div>
  <h2>管理员专用</h2>
  <p>访客只能阅读博客。写笔记、删除草稿和任务同步都需要先登录服务器。</p>
  <div class="note-gate-login" data-note-gate-login>
    <input class="note-input" type="password" data-note-gate-password placeholder="博客后台密码" autocomplete="off">
    <button type="button" class="note-publish" data-note-gate-btn>登录服务器</button>
  </div>
  <div class="note-gate-status" data-note-gate-status></div>
  <p class="note-gate-hint">如果在 GitHub Pages 看到此页，请改到 <a href="http://47.93.173.214/%E5%86%99%E7%AC%94%E8%AE%B0/">阿里云服务器版本</a> 登录。</p>
</section>
<div class="note-grid" data-note-editor hidden>
  <section class="note-card note-main">
    <div class="note-toolbar">
      <button type="button" data-note-new>新建</button>
      <button type="button" data-note-save>保存草稿</button>
      <button type="button" data-note-delete>删除草稿</button>
      <button type="button" data-note-export>导出 .md</button>
      <button type="button" data-note-copy>复制 Markdown</button>
    </div>
    <div class="note-fields">
      <div class="note-field">
        <label for="noteTitle">标题</label>
        <input class="note-input" id="noteTitle" data-note-title placeholder="例如：今天学到的一个新方法" maxlength="120">
      </div>
      <div class="note-field">
        <label for="noteSection">板块</label>
        <select class="note-select" id="noteSection" data-note-section></select>
      </div>
      <div class="note-field">
        <label for="noteCategory">分类</label>
        <select class="note-select" id="noteCategory" data-note-category></select>
      </div>
    </div>
    <textarea class="note-textarea" data-note-body placeholder="# 在这里写 Markdown&#10;&#10;支持标题、列表、代码块、链接和图片引用；写完后可导出或发布。"></textarea>
    <div class="note-preview-head"><span>实时预览</span><span data-note-count>0 字符</span></div>
    <div class="note-preview" data-note-preview></div>
  </section>
  <aside class="note-card note-side">
    <div class="note-side-kicker">本地草稿</div>
    <div class="note-drafts" data-note-drafts></div>
    <div class="note-token-box">
      <div class="note-side-kicker">服务器发布</div>
      <div class="note-server-state" data-note-server-state>正在检测服务器…</div>
      <button type="button" class="note-publish" data-note-server-publish hidden>发布到服务器</button>
      <div class="note-status" data-note-server-status></div>
    </div>
    <div class="note-token-box">
      <div class="note-side-kicker">GitHub 备用发布</div>
      <input class="note-input" type="password" data-note-token placeholder="Fine-grained GitHub Token" autocomplete="off">
      <label class="note-check"><input type="checkbox" data-note-remember>记住本次会话</label>
      <button type="button" class="note-publish" data-note-publish>发布到 GitHub</button>
      <div class="note-token-hint">
        需要只授权本仓库 <strong>Contents: Read and write</strong> 的 fine-grained token；令牌默认只放在当前标签页的 sessionStorage，不写入 localStorage。
        <a href="https://github.com/settings/tokens?type=beta" target="_blank" rel="noopener">创建 Token</a>
      </div>
      <div class="note-status" data-note-status></div>
    </div>
  </aside>
</div>
"""
    return page(out_dir, "在线写笔记", body, parent_href=home_href)


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


def doc_copyright(rel, out_dir):
    """文章底部版权说明；canonical 指向分类页里的文章锚点。"""
    page_dir = os.path.relpath(out_dir, SITE_DIR).replace(os.sep, "/")
    page_path = "" if page_dir == "." else page_dir + "/"
    canonical = "https://no-zland.github.io/" + urllib.parse.quote(page_path + "index.html", safe="/") + "#" + doc_anchor(rel)
    try:
        updated = datetime.fromtimestamp(os.path.getmtime(os.path.join(POST_DIR, rel))).strftime("%Y-%m-%d")
    except OSError:
        updated = ""
    updated_html = f" · 更新于 {esc(updated)}" if updated else ""
    return f"""
<footer class="doc-copyright">
  <div class="copyright-head"><span>版权说明</span><span>© 2026 梁双宇</span></div>
  <p>本文由梁双宇原创，采用 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh" target="_blank" rel="noopener license">CC BY-NC-SA 4.0</a> 许可。非商业转载请注明作者和原文链接；禁止未经授权的商业转载、批量复制或爬虫抓取。</p>
  <p class="copyright-meta">原文：<a href="{canonical}">{canonical}</a>{updated_html}</p>
</footer>
"""


def folder_wall(rel, out_dir):
    """把目录里的图片做成一面墙（证书、截图之类）。"""
    folder = os.path.join(POST_DIR, rel)
    if not os.path.isdir(folder):
        return ""
    items = []
    for fn in sorted(os.listdir(folder)):
        src = os.path.join(folder, fn)
        if not os.path.isfile(src) or not is_image(fn):
            continue
        title = os.path.splitext(fn)[0]
        rel_src = os.path.relpath(src, POST_DIR).replace(os.sep, "/")
        meta = CERT_THUMBS.get(rel_src)
        if meta and os.path.isfile(os.path.join(ASSET_DIR, "certs", meta["thumb"])):
            url = rel_from(out_dir, os.path.join(ASSET_DIR, "certs", meta["thumb"]))
            img = ('<img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">'
                   % (quote_url(url), esc(title), meta["w"], meta["h"]))
        else:
            url = copy_asset(src, out_dir)
            img = '<img src="%s" alt="%s" loading="lazy" decoding="async">' % (url, esc(title))
        items.append('<a class="cert-item" href="%s" target="_blank" rel="noopener">%s<span>%s</span></a>'
                     % (url, img, esc(title)))
    if not items:
        return ""
    title = folder_meta(rel).get("title") or os.path.basename(rel).lstrip("_")
    return ('<div class="page-head"><h1>%s</h1><div class="count">%d 张</div></div>'
            '<div class="cert-wall">%s</div>' % (esc(title), len(items), "".join(items)))


def build_reading_page(d, docs, dir_docs, child_dirs, images, out_dir, doc_list=None, parent_href=None):
    name = os.path.basename(d) if d else "全部文章"
    if doc_list is None:
        doc_list = docs_under(docs, d)
    if not doc_list and d:
        wall_html = folder_wall(d, out_dir)
        if wall_html:
            return page(out_dir, name, wall_html, parent_href=parent_href)

    articles = []
    for rel in doc_list:
        r = render_doc(rel, out_dir, images)
        articles.append(f'<article class="doc" id="{doc_anchor(rel)}" data-title="{esc(r["title"])}"><div class="doc-body">{r["body"]}</div>{doc_copyright(rel, out_dir)}</article>')

    content = ''.join(articles) if articles else '<div class="doc"><p>暂无文章</p></div>'
    side_extra = f"""
<div class="side-card reading-toc-card" data-reading-toc-card hidden>
  <div class="side-card-kicker">本篇目录</div>
  <nav class="reading-toc" data-reading-toc></nav>
</div>
<div class="side-card reading-pager-card" data-reading-pager-card hidden>
  <div class="side-card-kicker">文章</div>
  <div class="reading-pager-title" data-reading-pager-title></div>
  <div class="reading-pager-row">
    <button type="button" class="reading-pager-btn" data-reading-prev aria-label="上一篇">⏮</button>
    <span class="reading-pager-count" data-reading-count>第 1 / {len(articles)} 篇</span>
    <button type="button" class="reading-pager-btn" data-reading-next aria-label="下一篇">⏭</button>
  </div>
</div>
"""

    body = f"""
{breadcrumb(d, out_dir)}
<div class="page-head"><h1>{esc(name)}</h1><div class="count">共 {len(doc_list)} 篇文章</div></div>
<div class="reading-root" data-reading-root>
  <div class="doc-stack" data-doc-stack>{content}</div>
</div>
"""
    if parent_href is None:
        parent_href = parent_href_for(d, out_dir)
    return page(out_dir, name, body, with_math=True, parent_href=parent_href, side_extra=side_extra)


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def main():
    global AVATAR_NAME, UPDATES_JSON, NAV_SECTIONS, MUSIC_JSON, QUOTES_JSON, QUOTES, ASSET_VERSION, NOTE_SECTIONS_JSON, CERT_THUMBS
    CERT_THUMBS = _load_cert_thumbs()
    docs, images, dir_earliest, image_dirs, dir_image_counts = scan()
    dir_docs, child_dirs = build_tree(docs, image_dirs)

    # 默认不删除 site 根目录：Hugo server 可能占用文件。需要全量清理时使用 --clean。
    if "--clean" in sys.argv and os.path.exists(SITE_DIR):
        force_rmtree(SITE_DIR)
    os.makedirs(SITE_DIR, exist_ok=True)
    os.makedirs(ASSET_DIR, exist_ok=True)
    os.makedirs(RES_DIR, exist_ok=True)
    write_text(os.path.join(SITE_DIR, ".nojekyll"), "")
    write_text(os.path.join(SITE_DIR, "robots.txt"), ROBOTS_TXT)

    calendar_css = read_text(os.path.join(SRC_DIR, "calendar.css"))
    calendar_js = read_text(os.path.join(SRC_DIR, "calendar.js"))
    search_css = read_text(os.path.join(SRC_DIR, "search.css"))
    search_js = read_text(os.path.join(SRC_DIR, "search.js"))
    reading_css = read_text(os.path.join(SRC_DIR, "reading.css"))
    reading_mode_js = read_text(os.path.join(SRC_DIR, "reading-mode.js"))
    media_css = read_text(os.path.join(SRC_DIR, "media.css"))
    media_js = read_text(os.path.join(SRC_DIR, "media.js"))
    music_css = read_text(os.path.join(SRC_DIR, "music.css"))
    music_js = read_text(os.path.join(SRC_DIR, "music.js"))
    note_css = read_text(os.path.join(SRC_DIR, "note.css"))
    note_js = read_text(os.path.join(SRC_DIR, "note-editor.js"))
    agent_css = read_text(os.path.join(SRC_DIR, "agent.css"))
    brightness_js = read_text(os.path.join(SRC_DIR, "brightness.js"))
    agent_js = read_text(os.path.join(SRC_DIR, "agent.js"))
    quotes_js = read_text(os.path.join(SRC_DIR, "quotes.js"))
    satellite_js = read_text(os.path.join(SRC_DIR, "satellite.js"))
    nav_sync_js = read_text(os.path.join(SRC_DIR, "nav-sync.js"))
    sidebar_js = read_text(os.path.join(SRC_DIR, "sidebar.js"))
    anti_crawler_js = read_text(os.path.join(SRC_DIR, "anti-crawler.js"))
    spa_js = read_text(os.path.join(SRC_DIR, "spa.js"))
    style_text = CSS + "\n" + calendar_css + "\n" + search_css + "\n" + reading_css + "\n" + media_css + "\n" + music_css + "\n" + note_css + "\n" + agent_css
    app_text = JS + "\n" + calendar_js + "\n" + search_js + "\n" + reading_mode_js + "\n" + media_js + "\n" + music_js + "\n" + quotes_js + "\n" + satellite_js + "\n" + nav_sync_js + "\n" + sidebar_js + "\n" + note_js + "\n" + brightness_js + "\n" + agent_js + "\n" + anti_crawler_js + "\n" + spa_js
    write_text(os.path.join(ASSET_DIR, "style.css"), style_text)
    write_text(os.path.join(ASSET_DIR, "app.js"), app_text)

    mj_src = os.path.join(SRC_DIR, "mathjax", "tex-svg.js")
    if os.path.isfile(mj_src):
        mj_dir = os.path.join(ASSET_DIR, "mathjax")
        os.makedirs(mj_dir, exist_ok=True)
        shutil.copyfile(mj_src, os.path.join(mj_dir, "tex-svg.js"))
    ASSET_VERSION = hashlib.md5((style_text + app_text).encode("utf-8")).hexdigest()[:8]
    UPDATES_JSON = json.dumps(collect_updates(docs), ensure_ascii=False, sort_keys=True)
    MUSIC_JSON = load_music_playlist()
    QUOTES = load_quotes()
    if not QUOTES:
        QUOTES = [{"text": "生活不是等待暴风雨过去，而是学会在雨中跳舞。", "author": "维维安·格林"}]
    QUOTES_JSON = json.dumps(QUOTES, ensure_ascii=False, separators=(",", ":"))
    copy_music()
    AVATAR_NAME = copy_avatar()

    l1_sections = child_dirs.get("", [])
    sections = build_sections(l1_sections)
    for section in sections:
        section["cats"] = child_dirs.get(section["slug"], [])
    note_sections_data = []
    for spec in SECTION_SPECS:
        section_path = os.path.join(POST_DIR, spec["slug"])
        if not os.path.isdir(section_path):
            continue
        note_sections_data.append({
            "slug": spec["slug"],
            "title": spec["title"],
            "cats": [d for d in sorted(os.listdir(section_path))
                     if os.path.isdir(os.path.join(section_path, d)) and not d.startswith(".")],
        })
    NOTE_SECTIONS_JSON = json.dumps(note_sections_data, ensure_ascii=False, separators=(",", ":"))
    NAV_SECTIONS = build_nav_sections(sections, docs, child_dirs, dir_image_counts)

    page_count = 1
    doc_page_urls = {}
    home_index = os.path.join(SITE_DIR, "index.html")

    for section in sections:
        slug = section["slug"]
        section_out = os.path.join(SITE_DIR, slug)
        cats = section["cats"]
        direct = dir_docs.get(slug, [])

        if cats:
            html = build_section_page(section, l1_sections, docs, dir_docs, child_dirs, dir_earliest, section_out, images)
            write_text(os.path.join(section_out, "index.html"), html)
            page_count += 1

            if direct:
                parent = quote_url(rel_from(section_out, os.path.join(section_out, "index.html")))
                for rel in direct:
                    doc_page_urls[rel] = quote_url(os.path.join(slug, "direct.html"))
                html = build_reading_page(slug, docs, dir_docs, child_dirs, images, section_out, doc_list=direct, parent_href=parent)
                write_text(os.path.join(section_out, "direct.html"), html)
                page_count += 1

            for cat_rel in cats:
                cat_out = os.path.join(SITE_DIR, cat_rel)
                cat_subs = child_dirs.get(cat_rel, [])
                cat_direct = dir_docs.get(cat_rel, [])
                cat_parent = quote_url(rel_from(cat_out, os.path.join(SITE_DIR, slug, "index.html")))

                if cat_subs:
                    html = build_folder_page(cat_rel, docs, dir_docs, child_dirs, dir_earliest, cat_out)
                    write_text(os.path.join(cat_out, "index.html"), html)
                    page_count += 1
                    if cat_direct:
                        for rel in cat_direct:
                            doc_page_urls[rel] = quote_url(os.path.join(cat_rel, "direct.html"))
                        html = build_reading_page(cat_rel, docs, dir_docs, child_dirs, images, cat_out, doc_list=cat_direct, parent_href=cat_parent)
                        write_text(os.path.join(cat_out, "direct.html"), html)
                        page_count += 1
                    for sub_rel in cat_subs:
                        sub_out = os.path.join(SITE_DIR, sub_rel)
                        for rel in docs_under(docs, sub_rel):
                            doc_page_urls[rel] = quote_url(os.path.join(sub_rel, "index.html"))
                        html = build_reading_page(sub_rel, docs, dir_docs, child_dirs, images, sub_out, parent_href=cat_parent)
                        write_text(os.path.join(sub_out, "index.html"), html)
                        page_count += 1
                else:
                    for rel in docs_under(docs, cat_rel):
                        doc_page_urls[rel] = quote_url(os.path.join(cat_rel, "index.html"))
                    html = build_reading_page(cat_rel, docs, dir_docs, child_dirs, images, cat_out, parent_href=cat_parent)
                    write_text(os.path.join(cat_out, "index.html"), html)
                    page_count += 1
        else:
            custom = section.get("layout") in ("shelf", "gallery", "map", "timeline")
            html = build_section_page(section, l1_sections, docs, dir_docs, child_dirs, dir_earliest, section_out, images)
            write_text(os.path.join(section_out, "index.html"), html)
            page_count += 1
            if custom and direct:
                parent = quote_url(rel_from(section_out, os.path.join(section_out, "index.html")))
                for rel in direct:
                    doc_page_urls[rel] = quote_url(os.path.join(slug, "direct.html"))
                html = build_reading_page(slug, docs, dir_docs, child_dirs, images, section_out, doc_list=direct, parent_href=parent)
                write_text(os.path.join(section_out, "direct.html"), html)
                page_count += 1
            elif not custom:
                for rel in docs_under(docs, slug):
                    doc_page_urls[rel] = quote_url(os.path.join(slug, "index.html"))
                parent = quote_url(rel_from(section_out, home_index))
                html = build_reading_page(slug, docs, dir_docs, child_dirs, images, section_out, parent_href=parent)
                write_text(os.path.join(section_out, "index.html"), html)
                page_count += 1

    # 文章标题在渲染阶段才收集，首页卫星图要用到，所以首页最后生成
    home_html = build_home(docs, dir_docs, child_dirs, dir_earliest, SITE_DIR)
    write_text(os.path.join(SITE_DIR, "index.html"), home_html)

    pdfs = collect_pdfs()
    if os.path.isdir(PDF_DIR):
        force_rmtree(PDF_DIR)
    for pdf in pdfs:
        if pdf.get("available", True):
            pdf["path"] = copy_pdf(pdf["rel"])
    library_out = os.path.join(SITE_DIR, "资料库")  # 已下线：不再生成资料库页面

    cert_src = os.path.join(ROOT, "assets", "certs")
    if os.path.isdir(cert_src):
        cert_dst = os.path.join(ASSET_DIR, "certs")
        if os.path.isdir(cert_dst):
            force_rmtree(cert_dst)
        shutil.copytree(cert_src, cert_dst)
    shelf_src = os.path.join(ROOT, "assets", "shelf")
    if os.path.isdir(shelf_src):
        shelf_dst = os.path.join(ASSET_DIR, "shelf")
        if os.path.isdir(shelf_dst):
            force_rmtree(shelf_dst)
        shutil.copytree(shelf_src, shelf_dst)

    page_count += 1

    note_out = os.path.join(SITE_DIR, "写笔记")
    write_text(os.path.join(note_out, "index.html"), build_note_page(note_out))
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
        section = section_for_category(category_parts[0]) if category_parts else None
        if section and len(category_parts) > 1:
            category = f"{section['title']} / {category_parts[1]}"
        elif section:
            category = section["title"]
        else:
            category = category_parts[0] if category_parts else "未分类"
        search_index.append({
            "title": DOC_TITLE.get(rel, os.path.splitext(os.path.basename(rel))[0]),
            "url": "/" + page_url.lstrip("/") + "#" + doc_anchor(rel),
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
