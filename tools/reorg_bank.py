# -*- coding: utf-8 -*-
"""把题库里的算法题按「知识点 / 难度」移动到二级目录，并生成各层索引。"""
import collections
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW = os.path.join(ROOT, "content", "post", "题库", "算法题复盘（Review）")
LEVEL_NAME = {1: "难度1-入门", 2: "难度2-基础", 3: "难度3-模型", 4: "难度4-复合", 5: "难度5-压轴"}


def knowledge(tags, title):
    s = " ".join(tags)
    if "动态规划" in s:
        return "14-动态规划"
    if "博弈论" in s or "组合数学" in s:
        return "13-组合与博弈"
    if "字符串/" in s:
        return "15-字符串"
    if "数论" in s:
        return "12-数论"
    if "图论/树" in s or "换根" in s:
        return "11-树"
    if "图论/最短路" in s or "最小生成树" in s:
        return "10-最短路与生成树"
    if "图论" in s:
        return "09-图论基础"
    if "并查集" in s or "哈希" in s or "平衡树" in s or "离散" in s:
        return "08-并查集与哈希"
    if "数据结构/栈" in s or "数据结构/队列" in s or "数据结构/堆" in s:
        return "07-栈队列堆"
    if "二分" in s:
        return "05-二分"
    if "前缀和" in s or "双指针" in s:
        return "04-前缀和与双指针"
    if "位运算" in s or "高精度" in s or "进制" in s:
        return "06-位运算与进制"
    if "递归" in s or "递推" in s:
        return "03-递推与递归"
    if "贪心" in s or "构造" in s:
        return "02-贪心与构造"
    return "01-模拟与枚举"


def parse(path):
    t = open(path, encoding="utf-8").read()
    mt = re.search(r"(?m)^title:\s*(.+)$", t)
    title = mt.group(1).strip() if mt else os.path.splitext(os.path.basename(path))[0]
    tags = []
    m = re.search(r"(?ms)^tags:\s*\n((?:\s*-\s*.+\n)+)", t)
    if m:
        tags = [x for x in re.findall(r"-\s*(\S+)", m.group(1)) if x.startswith("算法/")]
    md = re.search(r"(?m)^difficulty:\s*(\d)", t)
    lv = int(md.group(1)) if md else 2
    return title, tags, lv


def main(apply=False):
    plan = []
    for dirpath, _, files in os.walk(REVIEW):
        for f in files:
            if not f.endswith(".md") or f == "_index.md" or f.startswith("00 "):
                continue
            src = os.path.join(dirpath, f)
            title, tags, lv = parse(src)
            kp = knowledge(tags, title)
            plan.append((src, f, kp, lv, title))
    cnt = collections.Counter((kp, lv) for _, _, kp, lv, _ in plan)
    for (kp, lv), n in sorted(cnt.items()):
        print(f"{kp:22s} {LEVEL_NAME[lv]:12s} {n}")
    print("total", len(plan), "dirs", len({k for k, _ in cnt}))

    if not apply:
        return

    moved = 0
    for src, f, kp, lv, title in plan:
        dst_dir = os.path.join(REVIEW, kp, LEVEL_NAME[lv])
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, f)
        if os.path.abspath(src) != os.path.abspath(dst):
            if not os.path.exists(dst):
                shutil.move(src, dst)
                moved += 1

    # 知识点目录的 _index.md
    by_kp = collections.defaultdict(list)
    for src, f, kp, lv, title in plan:
        by_kp[kp].append((lv, title))
    for kp, items in by_kp.items():
        d = os.path.join(REVIEW, kp)
        meta = os.path.join(d, "_index.md")
        if os.path.exists(meta):
            continue
        levels = sorted({lv for lv, _ in items})
        lines = ["---", f"title: {kp.split('-', 1)[1]}", "---", "",
                 f"本类共 {len(items)} 篇，按难度分在 " + "、".join(f"难度{lv}" for lv in levels) + " 子目录。", ""]
        open(meta, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("moved", moved)


if __name__ == "__main__":
    main("--apply" in sys.argv)
