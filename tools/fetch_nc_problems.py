# -*- coding: utf-8 -*-
"""抓取牛客题库题目页（服务端渲染，无需登录），保存为 JSON，供写复盘博客使用。"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
OUT = os.path.join(os.path.dirname(__file__), "nc_problems")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("gbk", "replace")


def tex_img(m):
    src = m.group(1)
    if "equation?tex=" in src:
        q = src.split("equation?tex=", 1)[1]
        q = urllib.parse.unquote(q)
        q = q.replace(r"\hspace{15pt}", "").strip()
        if not q:
            return ""
        return f" ${q}$ "
    return f"\n![]({src})\n"


def html_to_text(s):
    s = re.sub(r"(?is)<script.*?</script>", "", s)
    s = re.sub(r"(?is)<style.*?</style>", "", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</p>", "\n\n", s)
    s = re.sub(r"(?i)</div>", "\n", s)
    s = re.sub(r"(?is)<img[^>]*src=\"([^\"]+)\"[^>]*>", tex_img, s)
    s = re.sub(r"(?i)<pre[^>]*>", "\n```\n", s)
    s = re.sub(r"(?i)</pre>", "\n```\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'"))
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def parse(pid, h):
    d = {"pid": pid, "url": f"https://ac.nowcoder.com/acm/problem/{pid}"}
    m = re.search(r"(?is)<title>(.*?)</title>", h)
    title = html_to_text(m.group(1)) if m else ""
    d["title"] = re.sub(r"[_\-]牛客竞赛OJ.*$", "", title).strip()

    m = re.search(r'(?is)<div class="subject-item-wrap">(.*?)</div>', h)
    d["limits"] = html_to_text(m.group(1)) if m else ""

    m = re.search(r'(?is)<div class="subject-question">(.*?)</div>\s*(?:<h2|<div class="question-oi"|</div>)', h)
    d["description"] = html_to_text(m.group(1)) if m else ""

    def section(name):
        pat = (r'(?is)' + name + r'.*?</h2>\s*<pre>(.*?)</pre>')
        mm = re.search(pat, h)
        return html_to_text(mm.group(1)) if mm else ""

    d["input"] = section("输入描述")
    d["output"] = section("输出描述")

    samples = []
    blocks = re.split(r'(?is)<div class="question-oi">', h)[1:]
    for b in blocks:
        pairs = re.findall(
            r'(?is)<textarea[^>]*data-clipboard-text-id="(input|output)(\d+)"[^>]*>(.*?)</textarea>', b)
        cur = {}
        for kind, idx, val in pairs:
            cur[kind] = html_to_text(val)
            if kind == "output":
                samples.append({"input": cur.get("input", ""), "output": cur.get("output", "")})
                cur = {}
    d["samples"] = samples
    return d


def work(pid):
    try:
        h = get(f"https://ac.nowcoder.com/acm/problem/{pid}")
        d = parse(pid, h)
        with open(os.path.join(OUT, f"{pid}.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print(f"ok {pid} {d['title']} samples={len(d['samples'])}", flush=True)
    except Exception as e:
        print(f"FAIL {pid}: {e}", flush=True)


def main(pids):
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(work, pids))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main([int(x) for x in sys.argv[1:]])
    else:
        items = json.load(open(os.path.join(os.path.dirname(__file__), "nc_accepted.json"), encoding="utf-8"))
        todo = [it["pid"] for it in items
                if not os.path.exists(os.path.join(OUT, f"{it['pid']}.json"))]
        print(f"todo {len(todo)}", flush=True)
        main(todo)
