# -*- coding: utf-8 -*-
"""把 tools/nc_gen/<pid>.json + 代码 + 题面组装成复盘博客 Markdown。

用法: python tools/assemble_posts.py [pid ...]
"""
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "tools", "nc_gen")
PROB = os.path.join(ROOT, "tools", "nc_problems")
OUT = os.path.join(ROOT, "content", "post", "02-竞赛科研经历与复盘", "算法题复盘（Review）")

TODAY = "2026-11-18"
REVIEWED = "2026-11-18"
CODE_NOTE = "*代码为参考实现（按题意重写并用样例验证），非本人原始提交。*"


def clean_name(s):
    s = re.sub(r'[\\/:*?"<>|\r\n\t]', "_", s or "")
    s = re.sub(r"\s+", " ", s).strip(" .")
    return s[:80] or "未命名"


def blockquote(text):
    if not text:
        return "> "
    return "\n".join(("> " + ln) if ln.strip() else ">" for ln in text.split("\n"))


def read_text(p):
    with open(p, encoding="utf-8") as f:
        return f.read().strip("\n")


def build(pid):
    pj = json.load(open(os.path.join(PROB, f"{pid}.json"), encoding="utf-8"))
    gj = json.load(open(os.path.join(GEN, f"{pid}.json"), encoding="utf-8"))

    cpp = os.path.join(GEN, f"{pid}.cpp")
    py = os.path.join(GEN, f"{pid}.py")
    if os.path.exists(cpp):
        code, lang = read_text(cpp), "cpp"
    elif os.path.exists(py):
        code, lang = read_text(py), "python"
    else:
        raise FileNotFoundError(f"缺少代码 {pid}")

    title = pj["title"].strip()
    core = (gj.get("core") or "基础").strip()
    tags = [t.strip() for t in (gj.get("tags") or []) if t.strip()]
    for must in ("平台/牛客", "状态/待复盘"):
        if must not in tags:
            tags.append(must)
    tags = list(dict.fromkeys(tags))

    parts = ["---", f"title: {title}"]
    parts.append("aliases:")
    parts.append(f"  - NC{pid}")
    parts.append(f"pid: NC{pid}")
    parts.append(f"url: {pj['url']}")
    parts.append("contest: ")
    parts.append("difficulty: ")
    parts.append(f"solved: {gj.get('solved') or TODAY}")
    parts.append(f"reviewed: {REVIEWED}")
    parts.append("tags:")
    for t in tags:
        parts.append(f"  - {t}")
    parts.append(f"updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    parts.append("---")
    parts.append("")

    parts.append("### 知识点：")
    parts.append("")
    parts.append((gj.get("knowledge") or "").strip())
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("### 题目描述")
    parts.append("")
    parts.append(blockquote(pj.get("description", "")))
    parts.append("")
    parts.append("**输入描述**")
    parts.append("")
    parts.append(blockquote(pj.get("input", "")))
    parts.append("")
    parts.append("**输出描述**")
    parts.append("")
    parts.append(blockquote(pj.get("output", "")))
    parts.append("")

    samples = pj.get("samples") or []
    for i, s in enumerate(samples, 1):
        label = f"#### 示例 {i}" if len(samples) > 1 else "#### 示例"
        parts.append(label)
        parts.append("")
        parts.append("**输入**")
        parts.append("")
        parts.append("```text")
        parts.append(s.get("input", "").rstrip("\n"))
        parts.append("```")
        parts.append("")
        parts.append("**输出**")
        parts.append("")
        parts.append("```text")
        parts.append(s.get("output", "").rstrip("\n"))
        parts.append("```")
        parts.append("")

    parts.append("---")
    parts.append("")
    parts.append("### 最终代码：")
    parts.append("")
    parts.append(f"```{lang}")
    parts.append(code)
    parts.append("```")
    parts.append("")
    parts.append(CODE_NOTE)
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("### 解题思路")
    parts.append("")
    parts.append((gj.get("approach") or "").strip())
    parts.append("")
    parts.append("#### 卡点与关键一步")
    parts.append("")
    parts.append((gj.get("pitfalls") or "- 无").strip())
    parts.append("")
    parts.append("#### 复杂度")
    parts.append("")
    parts.append("| 项 | 值 |")
    parts.append("|---|---|")
    parts.append(f"| 时间复杂度 | {gj.get('time') or '—'} |")
    parts.append(f"| 空间复杂度 | {gj.get('space') or '—'} |")
    parts.append("")

    fname = clean_name(f"[NC-{pid}] {title} - {core}") + ".md"
    path = os.path.join(OUT, fname)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts).rstrip("\n") + "\n")
    return fname


def main(pids):
    items = json.load(open(os.path.join(ROOT, "tools", "nc_todo.json"), encoding="utf-8"))
    todo = {str(x["pid"]) for x in items}
    if not pids:
        pids = [str(x["pid"]) for x in items]
    made, missing = [], []
    for pid in pids:
        if pid not in todo:
            continue
        try:
            made.append(build(pid))
        except Exception as e:
            missing.append((pid, str(e)))
    for m in made:
        print("OK  ", m)
    for pid, why in missing:
        print("SKIP", pid, why)
    print(f"total {len(made)} written, {len(missing)} skipped")


if __name__ == "__main__":
    main(sys.argv[1:])
