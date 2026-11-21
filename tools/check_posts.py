# -*- coding: utf-8 -*-
"""校验复盘 Markdown 的结构完整性。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "content", "post", "02-竞赛科研经历与复盘", "算法题复盘（Review）")
FENCE = chr(96) * 3

issues = []
files = [f for f in os.listdir(D) if f.endswith(".md") and f != "_index.md"]
for f in files:
    t = open(os.path.join(D, f), encoding="utf-8").read()
    if "\ufeff" in t:
        issues.append((f, "BOM"))
    if t.count(FENCE) % 2:
        issues.append((f, "unbalanced fence"))
    for sec in ("### 知识点", "### 题目描述", "### 最终代码", "### 解题思路",
                "#### 卡点与关键一步", "#### 复杂度"):
        if sec not in t:
            issues.append((f, "missing " + sec))
    if t.count("> ") < 2:
        issues.append((f, "no blockquote"))
print("files", len(files), "issues", len(issues))
for i in issues[:20]:
    print(i)
