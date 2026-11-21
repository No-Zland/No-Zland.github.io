# -*- coding: utf-8 -*-
"""按标题把牛客做题记录粗分到知识点桶，供算法思维系列选题单使用。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

RULES = [
    ("sp", r"最短路|最短路径|dijkstra|spfa|floyd|热浪|灾后重建|负环|差分约束|最小生成树|修路|公路|光纤|通信网"),
    ("tree", r"树|LCA|祖先|子树|直径|森林|叶|根"),
    ("graph", r"图|拓扑|连通|环|并查集|团伙|食物链|关押|家谱|网格|迷宫|岛屿|BFS|DFS"),
    ("comb", r"组合|排列|方案数|计数|卡特兰|容斥|博弈|Nim|SG|取石子|游戏|赢|胜"),
    ("dp2", r"区间|状压|数位|树形"),
    ("dp1", r"背包|纪念品|金币|分糖果|优惠券|外卖|股票|最大子段|最长上升|LIS|LCS|数字三角形|路径和|方案"),
    ("binary", r"二分|查找|搜索|跳石头|木材|分割|切|最小值最大|最大值最小"),
    ("prefix", r"前缀和|差分|区间和|子数组|连续|滑动窗口|双指针|数组查询"),
    ("numth", r"素数|质数|约数|公约数|公倍数|同余|模|幂|阶乘|进制|二进制|补码|位运算|数字根|数位和|回文数|水仙花|斐波那契|gcd|LCM|素数判断"),
    ("string", r"字符串|字符|回文|密码|凯撒|子串|匹配|字典序|名字|单词"),
    ("greedy", r"贪心|排队|接水|区间覆盖|选数|分配|分组|最少|最多|最优"),
    ("stackq", r"栈|队列|堆|优先|单调|括号|表达式|中缀|后缀"),
    ("rec", r"递归|递推|汉诺塔|爬楼梯|放苹果|分治|快速排序|归并"),
    ("bit", r"位|异或|与|或|移位|进制转换"),
    ("sim", r"输出|打印|图形|图案|菱形|三角形|矩阵|模拟|日期|时间|星期|季节|闰年|温度|面积|速度|成绩|统计|排序|列表|数组|计算|判断|比较|转换"),
]

CATCH_ALL = "sim"


def classify(title):
    t = title.lower()
    for key, pat in RULES:
        if re.search(pat, t, re.I):
            return key
    return CATCH_ALL


def main():
    items = json.load(open("tools/nc_all_problems.json", encoding="utf-8"))
    buckets = {}
    for it in items:
        buckets.setdefault(classify(it["title"]), []).append(it)
    for k in buckets:
        buckets[k].sort(key=lambda x: x["first"])
    json.dump(buckets, open("tools/nc_buckets.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for k, v in sorted(buckets.items(), key=lambda x: -len(x[1])):
        print(f"== {k} {len(v)}")
        print("   " + " | ".join(f"{x['pid']} {x['title']}" + ("✓" if x["ac"] else "") for x in v[:6]))


if __name__ == "__main__":
    main()
