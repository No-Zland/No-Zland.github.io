# -*- coding: utf-8 -*-
"""扫描题库的「知识点/难度」目录，重生成难度总览页。"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW = os.path.join(ROOT, "content", "post", "题库", "算法题复盘（Review）")
LEVEL_NAME = {1: "难度1-入门", 2: "难度2-基础", 3: "难度3-模型", 4: "难度4-复合", 5: "难度5-压轴"}
RUBRIC = {
    1: "语法与模拟：会循环、分支、数组就能写，重点是把题面翻译对。",
    2: "基础算法：排序、前缀和/差分、双指针、贪心、递归、进制、栈队列、简单数论。",
    3: "经典模型：二分答案、线性/背包 DP、最短路、并查集、堆、组合计数、KMP。",
    4: "复合模型：区间/树形/状压/数位 DP、LCA、树上差分、最小点覆盖、复杂构造。",
    5: "压轴：多模型组合或强思维，场上不一定能独立推出来。",
}


def main():
    rows = []
    for dirpath, _, files in os.walk(REVIEW):
        for f in files:
            if not f.endswith(".md") or f in ("_index.md",) or f.startswith("00 "):
                continue
            p = os.path.join(dirpath, f)
            t = open(p, encoding="utf-8").read()
            mt = re.search(r"(?m)^title:\s*(.+)$", t)
            title = mt.group(1).strip() if mt else f
            md = re.search(r"(?m)^difficulty:\s*(\d)", t)
            lv = int(md.group(1)) if md else 2
            kp = os.path.relpath(dirpath, REVIEW).split(os.sep)[0]
            rel = os.path.relpath(p, REVIEW).replace(os.sep, "/")
            rows.append(dict(title=title, level=lv, kp=kp, rel=rel, file=f))

    rows.sort(key=lambda r: (r["level"], r["kp"], r["title"]))
    dist = {lv: sum(1 for r in rows if r["level"] == lv) for lv in range(1, 6)}

    out = ["---", "title: 算法题复盘 · 难度分级", "created: 2026-11-06 20:29",
           "updated: 2026-11-18 21:40", "---", "",
           "# 算法题复盘 · 知识点 × 难度", "",
           f"> 共 {len(rows)} 篇，位于 `题库/算法题复盘（Review）/<知识点>/<难度>/`。",
           "> 难度写在每篇 frontmatter 的 `difficulty` 字段；改完跑 `tools/make_bank_index.py` 重排本页。", "",
           "## 难度口径", "", "| 难度 | 含义 | 篇数 |", "|---|---|---|"]
    for lv in range(1, 6):
        out.append(f"| {lv} | {RUBRIC[lv]} | {dist[lv]} |")
    out.append("")

    for lv in range(1, 6):
        items = [r for r in rows if r["level"] == lv]
        if not items:
            continue
        out.append(f"## 难度 {lv}（{len(items)} 篇）")
        out.append("")
        cur_kp = None
        for r in items:
            if r["kp"] != cur_kp:
                cur_kp = r["kp"]
                out.append(f"### {r['kp']}")
                out.append("")
            out.append(f"- [{r['title']}](<{r['rel']}>)")
        out.append("")

    out += ["## 目录约定", "",
            "- 第一级：知识点（01 模拟与枚举 … 15 字符串），每个目录的 `_index.md` 写了本篇范围；",
            "- 第二级：难度 1~5，目录名带档位说明；",
            "- 文件名保留 `[平台-题号] 题目 - 核心考点`，方便搜索。", ""]
    open(os.path.join(REVIEW, "00 算法题复盘 · 难度分级.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("rows", len(rows), dist)


if __name__ == "__main__":
    main()
