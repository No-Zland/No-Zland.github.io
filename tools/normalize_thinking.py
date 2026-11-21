# -*- coding: utf-8 -*-
"""把每篇「算法思维」的真题清单替换成规格里的标准清单（修正方括号标题等）。"""
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
    if not os.path.exists(path):
        print("MISS", spec["file"])
        continue
    t = open(path, encoding="utf-8").read()
    pat = re.compile(r"(## 五、真题清单\n\n(?:>.*?\n)+)(.*?)(?=\n## 六、)", re.S)
    if not pat.search(t):
        print("NOLIST", spec["file"])
        continue
    new = pat.sub(lambda mm: mm.group(1) + "\n" + spec["list_md"] + "\n", t, count=1)
    if new != t:
        open(path, "w", encoding="utf-8", newline="\n").write(new)
        fixed += 1
print("fixed", fixed, "of", len(meta))
