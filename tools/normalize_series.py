# -*- coding: utf-8 -*-
"""把「算法思维」每篇的真题清单替换成规格里的标准清单，并修正旧路径引用。"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "content", "post", "01-个人知识体系的构建", "算法思维")

meta = json.load(open(os.path.join(ROOT, "tools", "thinking", "meta.json"), encoding="utf-8"))
fixed = 0
for m in meta:
    spec = json.load(open(os.path.join(ROOT, "tools", "thinking", m["key"] + ".json"), encoding="utf-8"))
    path = os.path.join(D, spec["file"])
    t = open(path, encoding="utf-8").read()
    pat = re.compile(r"(## 七、真题清单\n\n(?:>.*?\n)+)(.*?)(?=\n## 八、)", re.S)
    if pat.search(t):
        t2 = pat.sub(lambda mm: mm.group(1) + "\n" + spec["list_md"] + "\n", t, count=1)
        if t2 != t:
            open(path, "w", encoding="utf-8", newline="\n").write(t2)
            fixed += 1
    else:
        print("NOLIST", spec["file"])
print("lists fixed", fixed)

# 旧路径 -> 新路径（题库）
for root, _, files in os.walk(os.path.join(ROOT, "content", "post")):
    for f in files:
        if not f.endswith(".md"):
            continue
        p = os.path.join(root, f)
        t = open(p, encoding="utf-8").read()
        if "02-竞赛科研经历与复盘/算法题复盘" in t:
            t2 = t.replace("02-竞赛科研经历与复盘/算法题复盘", "题库/算法题复盘")
            open(p, "w", encoding="utf-8", newline="\n").write(t2)
            print("path fixed", p)
