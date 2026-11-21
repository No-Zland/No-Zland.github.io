# -*- coding: utf-8 -*-
"""校验「算法思维」系列：结构、真题清单一致性、链接来源。"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "content", "post", "01-个人知识体系的构建", "算法思维")
FENCE = chr(96) * 3

meta = json.load(open(os.path.join(ROOT, "tools", "thinking", "meta.json"), encoding="utf-8"))
issues = []

for m in meta:
    key = m["key"]
    spec = json.load(open(os.path.join(ROOT, "tools", "thinking", key + ".json"), encoding="utf-8"))
    path = os.path.join(D, spec["file"])
    if not os.path.exists(path):
        issues.append((key, "missing file"))
        continue
    t = open(path, encoding="utf-8").read()
    if t.count(FENCE) % 2:
        issues.append((key, "unbalanced fence"))
    for sec in ("## 一、识别信号", "## 二、核心讲解", "## 三、模板",
                "## 四、复杂度与易错点", "## 五、真题清单", "## 六、下一步"):
        if sec not in t:
            issues.append((key, "missing " + sec))
    mm = re.search(r"## 五、真题清单(.*?)(?=\n## 六、)", t, re.S)
    if not mm:
        issues.append((key, "no list section"))
        continue
    body = mm.group(1)
    got = [ln.strip() for ln in body.splitlines() if ln.strip().startswith("- [")]
    want = [ln.strip() for ln in spec["list_md"].splitlines() if ln.strip()]
    if got != want:
        issues.append((key, f"list mismatch got {len(got)} want {len(want)}"))
        for a, b in zip(got, want):
            if a != b:
                issues.append((key, "  got: " + a[:80] + " | want: " + b[:80]))
                break
    urls = re.findall(r"https?://[^\s\)\>]+", body)
    allowed = set()
    for ln in want:
        m2 = re.search(r"\((https?://[^\)]+)\)", ln)
        if m2:
            allowed.add(m2.group(1))
    extra = [u for u in urls if u not in allowed]
    if extra:
        issues.append((key, "extra urls: " + "; ".join(extra[:3])))
    if len(t) < 1500:
        issues.append((key, "too short"))

print("files", len(meta), "issues", len(issues))
for i in issues:
    print(i)
