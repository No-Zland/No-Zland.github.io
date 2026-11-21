# -*- coding: utf-8 -*-
"""校验重写后的「算法思维」系列：八节结构 + 真题清单一致性。"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "content", "post", "01-个人知识体系的构建", "算法思维")
FENCE = chr(96) * 3

meta = json.load(open(os.path.join(ROOT, "tools", "thinking", "meta.json"), encoding="utf-8"))
SECS = ["## 一、是什么", "## 二、形式", "## 三、怎么理解", "## 四、怎么变成代码",
        "## 五、具体例子", "## 六、复杂度与易错点", "## 七、真题清单", "## 八、下一步"]
issues = []

for m in meta:
    spec = json.load(open(os.path.join(ROOT, "tools", "thinking", m["key"] + ".json"), encoding="utf-8"))
    path = os.path.join(D, spec["file"])
    if not os.path.exists(path):
        issues.append((m["key"], "missing"))
        continue
    t = open(path, encoding="utf-8").read()
    if t.count(FENCE) % 2:
        issues.append((m["key"], "unbalanced fence"))
    for sec in SECS:
        if sec not in t:
            issues.append((m["key"], "missing " + sec))
    mm = re.search(r"## 七、真题清单(.*?)(?=\n## 八、)", t, re.S)
    if not mm:
        issues.append((m["key"], "no list section"))
        continue
    got = [ln.strip() for ln in mm.group(1).splitlines() if ln.strip().startswith("- [")]
    want = [ln.strip() for ln in spec["list_md"].splitlines() if ln.strip()]
    if got != want:
        issues.append((m["key"], f"list mismatch {len(got)} vs {len(want)}"))
    if len(t) < 3000:
        issues.append((m["key"], "too short"))
    for need in ("为什么", "复杂度"):
        if need not in t:
            issues.append((m["key"], "missing " + need))

print("files", len(meta), "issues", len(issues))
for i in issues:
    print(i)
