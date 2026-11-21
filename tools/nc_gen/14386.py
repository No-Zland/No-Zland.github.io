# -*- coding: utf-8 -*-
import sys

# 水仙花数：设数有 N 位，判断各位数字的 N 次幂之和是否等于自身。
# 题面没给 Ai 上界，真正的水仙花数最大有 39 位，故用 Python 大整数，避免溢出。
def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    out = []
    for tok in data[1:1 + n]:
        digits = list(tok)
        N = len(digits)          # 位数 N
        if N < 3:                # 定义要求 N >= 3
            out.append("no")
            continue
        s = sum(int(ch) ** N for ch in digits)
        out.append("yes" if s == int(tok) else "no")
    sys.stdout.write("\n".join(out) + "\n")


main()
