# -*- coding: utf-8 -*-
"""给题库里的算法复盘打 1~5 难度，并生成难度索引。"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "content", "post", "题库", "算法题复盘（Review）")

PID_OVERRIDE = {
    "NC289292": 4, "NC293968": 5, "NOIP2014": 5, "NC295401": 4, "NC214022": 1,
    "NC293975": 4, "NC295729": 4, "NC293990": 4, "NC294580": 3, "NC293399": 3,
    "NC281550": 3, "NC16414": 2, "NC54633": 3, "NC204433": 3, "NC216216": 3,
    "NC299283": 3, "NC313179": 3, "NC303596": 3, "NC288078": 3, "NC307228": 3,
    "NC313660": 3, "NC294819": 3, "NC302603": 3, "NC14399": 2, "NC208614": 1,
    "NC289533": 3, "NC313185": 3, "NC295893": 2, "NC232608": 3, "CSP-42": 3,
}

TAG_RULES = [
    (r"动态规划/(区间|树形|状压|数位)", 4),
    (r"动态规划/", 3),
    (r"博弈论/", 3),
    (r"图论/(树|最短路|最小生成树|最小点覆盖)", 3),
    (r"数据结构/(平衡树|树状数组|线段树)", 4),
    (r"数据结构/(并查集|堆)", 3),
    (r"数据结构/(栈|队列)", 2),
    (r"数论/(裴蜀|扩展欧几里得|弗罗贝尼乌斯|中国剩余)", 3),
    (r"数论/", 2),
    (r"组合数学", 3),
    (r"字符串/字符串匹配", 3),
    (r"基础/二分答案", 3),
    (r"基础/(前缀和|双指针|贪心|二分)", 2),
    (r"基础/(递归|递推|位运算|高精度)", 2),
    (r"基础/", 1),
    (r"数学/", 2),
    (r"杂项/", 2),
]

RUBRIC = {
    1: "语法与模拟：会循环、分支、数组就能写，重点是把题面翻译对。",
    2: "基础算法：排序、前缀和/差分、双指针、贪心、递归、进制、栈队列、简单数论。",
    3: "经典模型：二分答案、线性/背包 DP、最短路、并查集、堆、组合计数、KMP。",
    4: "复合模型：区间/树形/状压/数位 DP、LCA、树上差分、最小点覆盖、复杂构造。",
    5: "压轴：多模型组合或需要强思维，场上不一定能独立推出来。",
}


def parse(path):
    t = open(path, encoding="utf-8").read()
    mt = re.search(r"(?m)^title:\s*(.+)$", t)
    title = mt.group(1).strip() if mt else os.path.splitext(os.path.basename(path))[0]
    mp = re.search(r"(?m)^pid:\s*(\S*)\s*$", t)
    pid = (mp.group(1).strip() if mp else "")
    tags = []
    m = re.search(r"(?ms)^tags:\s*\n((?:\s*-\s*.+\n)+)", t)
    if m:
        tags = [x for x in re.findall(r"-\s*(\S+)", m.group(1)) if x.startswith("算法/")]
    return title, pid, tags, t


def level_of(pid, title, tags):
    if pid in PID_OVERRIDE:
        return PID_OVERRIDE[pid]
    for reg, lv in TAG_RULES:
        if any(re.search(reg, x) for x in tags):
            return lv
    return 2


def set_difficulty(t, lv):
    if re.search(r"(?m)^difficulty:", t):
        return re.sub(r"(?m)^difficulty:.*$", f"difficulty: {lv}", t, count=1)
    return re.sub(r"(?m)^(solved:.*)$", f"difficulty: {lv}\n\\1", t, count=1)


def main():
    rows = []
    for f in sorted(os.listdir(D)):
        if not f.endswith(".md") or f == "_index.md":
            continue
        title, pid, tags, t = parse(os.path.join(D, f))
        lv = level_of(pid, title, tags)
        rows.append(dict(file=f, title=title, pid=pid, tags=tags, level=lv))
        new = set_difficulty(t, lv)
        if new != t:
            open(os.path.join(D, f), "w", encoding="utf-8", newline="\n").write(new)

    rows.sort(key=lambda r: (r["level"], r["title"]))
    dist = {lv: sum(1 for r in rows if r["level"] == lv) for lv in range(1, 6)}

    parts = ["---", "title: 算法题复盘", "created: 2026-11-06 20:29",
             "updated: 2026-11-18 21:10", "---", "",
             "# 算法题复盘 · 按难度分级", "",
             f"> 共 {len(rows)} 篇。难度 1~5 是「模型难度」，不是平台评分；同一档内按标题排序。",
             "> 这里的题都能在题库里点开，`difficulty` 字段已写进每篇 frontmatter。", "",
             "## 难度口径", "",
             "| 难度 | 含义 | 篇数 |", "|---|---|---|"]
    for lv in range(1, 6):
        parts.append(f"| {lv} | {RUBRIC[lv]} | {dist[lv]} |")
    parts.append("")

    for lv in range(1, 6):
        items = [r for r in rows if r["level"] == lv]
        if not items:
            continue
        parts.append(f"## 难度 {lv}（{len(items)} 篇）")
        parts.append("")
        for r in items:
            core = "、".join(t.split("/", 1)[1] for t in r["tags"][:2]) if r["tags"] else ""
            suffix = f" · {core}" if core else ""
            parts.append(f"- [{r['title']}](<{r['file']}>) · `{r['pid'] or '—'}`{suffix}")
        parts.append("")

    parts += ["## 怎么用", "",
              "1. 先刷 1~2 档，目标是「不看题解 20 分钟内写对」；",
              "2. 3 档是分水岭，每个模型至少 3 题，做完再进 4 档；",
              "3. 4~5 档按知识点成组刷，一次只攻一个模型，别混着刷；",
              "4. 每篇的 `difficulty` 可以手动改，改完这里不会自动重排——需要跑一次 `tools/classify_difficulty.py`。", ""]
    open(os.path.join(D, "_index.md"), "w", encoding="utf-8", newline="\n").write("\n".join(parts))
    print("total", len(rows), "dist", dist)


if __name__ == "__main__":
    main()
