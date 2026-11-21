---
title: 大卫的密码 (Easy Version)
aliases:
  - NC294580
pid: NC294580
url: https://ac.nowcoder.com/acm/problem/294580
contest:
difficulty: 3
solved: 2025-05-29
reviewed: 2026-11-18
tags:
  - 算法/动态规划/线性
  - 算法/基础/前缀和
  - 平台/牛客
  - 状态/待复盘
updated: 2026-11-18 18:29
created: 2026-11-18 21:19
---

### 知识点：

模型是「网格上带竖直绕回的单向最大权路径」，做法是逐列 DP 再用前缀/后缀最大值优化。结论：列号单调不减，整条路径可拆成每列一段「向下」的连续段（段长 ≤ n，最多绕一整圈），列间靠一次向右衔接；记 S_j(r) 为第 j 列前 r 行之和、T_j = S_j(n)，则 dp_j[r] = S_j(r) + max( max_{e≤r}(dp_{j-1}[e] - S_j(e-1)), T_j + max_{e>r}(dp_{j-1}[e] - S_j(e-1)) )。推导：入口 e ≤ r 时段和是 S_j(r)-S_j(e-1)，e > r 绕回后是 T_j-S_j(e-1)+S_j(r)，与 e 有关的部分都可预先取最值，于是每列 O(n)、总 O(nm)。

---

### 题目描述

> 大卫想要完成送露西去月球的梦想，但首先他需要从保险箱中取一笔钱，他忘记密码是多少了，这该怎么办……
>
> 本题为问题的简单版本，两题的唯一区别在于变量  $n$  与  $m$  的数据范围。
>
> 给定一个  $n\times m$  的网格图，我们使用  $(i,j)$  表示网格中从上往下数第  $i$  行和从左往右数第  $j$  列的单元格。左上角为  $(1,1)$ ，右下角为  $(n,m)$ ，每个格子包含一个整数价值，使用  $a_{i,j}$  表示。
>
> 一个光标在上面移动，从  $(s,1)$  出发，每次可以向右或者向下移动，每个格子至多经过一次。当光标移动到  $(n,i) \left(1\le i\le m \right)$  格子，也就是最后一行的某个格子时，继续向下移动则会到达  $(1,i)$  格子。大卫需要移动光标到达  $(t,m)$ ，求最终大卫能获取的最大价值和。
>
> 注意本题的时间限制。本题数据量较大，我们建议您选取较快的读入方式。

**输入描述**

> 第一行输入四个整数  $n,m,s,t \left(1\le n,m\le\textbf{500};\ 1\le s,t\le n\right)$ 
> 此后  $n$  行，第  $i$  行输入  $m$  个整数  $a_{i,1},a_{i,2},\dots,a_{i,m} \left(-5\times 10^4 \le a_{i,j} \le 5\times 10^4\right)$ ，表示第  $i$  行每一个格子的价值。
>
>  $n\ m\ s\ t \\
> a_{1,1}\ a_{1,2}\dots a_{1,m}\\
> a_{2,1}\ a_{2,2}\dots a_{2,m}\\
> \vdots \\
> a_{n,1}\ a_{n,2}\dots a_{n,m}$

**输出描述**

> 输出一个整数，表示大卫能获取的最大价值和。

#### 示例 1

**输入**

```text
3 3 1 2
1 2 3
4 5 6
7 8 9
```

**输出**

```text
38
```

#### 示例 2

**输入**

```text
5 5 1 5
6 10 4 10 6
-6 6 10 3 -1
-10 9 -6 -10 10
-3 8 4 5 6
-5 -8 2 4 8
```

**输出**

```text
100
```

---

### 最终代码：

```cpp
// NC294580 大卫的密码 (Easy Version)
// 题意：n*m 网格，从 (s,1) 出发只能向右或向下（第 n 行再向下回到第 1 行），
//       每个格子至多经过一次，走到 (t,m) 结束，最大化经过格子的价值和。
// 关键观察：列号单调不减 => 路径 = 每列走一段「向下」的连续段（可绕回，长度 <= n），
//           然后向右进入下一列。于是可以按列 DP。
// 转移：记 S_j(r) 为第 j 列 1..r 的前缀和、T_j = S_j(n)，e 为入口行、r 为出口行：
//   e <= r 时段和 = S_j(r) - S_j(e-1)；e > r 时段和 = T_j - S_j(e-1) + S_j(r)。
//   dp_j[r] = S_j(r) + max( max_{e<=r}(dp_{j-1}[e] - S_j(e-1)),
//                           T_j + max_{e>r}(dp_{j-1}[e] - S_j(e-1)) )
//   前缀最大值 + 后缀最大值即可 O(n) 转移一列，总复杂度 O(nm)。
#include <algorithm>
#include <climits>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
using namespace std;

namespace io {
const int SZ = 1 << 16;
char buf[SZ];
int len = 0, pos = 0;
inline int gc() {
    if (pos == len) {
        len = (int)fread(buf, 1, SZ, stdin);
        pos = 0;
        if (len <= 0) return -1;
    }
    return (unsigned char)buf[pos++];
}
inline long long readInt() {
    int c = gc();
    long long x = 0;
    int sgn = 1;
    while (c != -1 && (c < '0' || c > '9') && c != '-') c = gc();
    if (c == '-') { sgn = -1; c = gc(); }
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x * sgn;
}
} // namespace io

int main() {
    int n = (int)io::readInt();
    int m = (int)io::readInt();
    int s = (int)io::readInt();
    int t = (int)io::readInt();
    vector<int> a((size_t)n * m);
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j)
            a[(size_t)i * m + j] = (int)io::readInt();

    const long long NEG = LLONG_MIN / 4;
    vector<long long> dp(n + 2), nd(n + 2), pre(n + 2), val(n + 2),
        pref(n + 2), suf(n + 2);

    // 第 1 列：只能从 s 向下走
    {
        long long acc = 0;
        for (int i = 1; i <= n; ++i) {
            acc += a[(size_t)(i - 1) * m];
            pre[i] = acc;
        }
    }
    long long T = pre[n];
    for (int r = 1; r <= n; ++r) {
        if (r >= s)
            dp[r] = pre[r] - pre[s - 1];            // 直接从 s 往下到 r
        else
            dp[r] = (T - pre[s - 1]) + pre[r];      // 绕回：s..n 再 1..r
    }

    for (int j = 1; j < m; ++j) {
        long long acc = 0;
        for (int i = 1; i <= n; ++i) {
            acc += a[(size_t)(i - 1) * m + j];
            pre[i] = acc;
        }
        T = pre[n];
        for (int e = 1; e <= n; ++e) val[e] = dp[e] - pre[e - 1];
        pref[0] = NEG;
        for (int i = 1; i <= n; ++i) pref[i] = max(pref[i - 1], val[i]);
        suf[n + 1] = NEG;
        for (int i = n; i >= 1; --i) suf[i] = max(suf[i + 1], val[i]);
        for (int r = 1; r <= n; ++r) {
            long long b2 = (r + 1 <= n) ? T + suf[r + 1] : NEG;
            nd[r] = pre[r] + max(pref[r], b2);
        }
        dp.swap(nd);
    }
    printf("%lld\n", dp[t]);
    return 0;
}
```

*代码为参考实现（按题意重写并用样例验证），非本人原始提交。*

---

### 解题思路

第一反应是这看着像普通的网格最大路径，可「最后一行向下回到第一行」把无后效性打破了：同一列可以绕回，还可能重复走格子。我先固定路径形态——因为只能向右或向下，列号绝不回退，所以一列里走过的格子必然是从入口往下数的一段连续区间，最多绕一圈，绝不会出现两段。这样状态就好设了：dp[r] 表示走到当前列第 r 行的最大和，转移枚举上一列的出口行 e。朴素转移是一列 O(n^2)，n=500 勉强能过，但我想要能直接套到加强版的写法，就把式子按 e ≤ r 与 e > r 拆开，把含 S_j(r) 的项提到最外层，剩下的用前缀最大值和后缀最大值各扫一遍，一列压到 O(n)。写之前我先用暴力 DFS 在小网格上随机对拍，确认绕回、单格段、起点即终点这些形态都没漏。

#### 卡点与关键一步

- 段长上限是 n：e > r 的绕回分支只覆盖 e..n 与 1..r，转移里只能加一个 T_j，加两个就等于绕了两圈并重复计数。
- 价值可为负，dp 初值要用足够小的负数而不是 0，否则不合法的入口会被选中。
- 终点固定是 (t,m)，最后一列也要按「入口 e 走到 t」的段来算，不能取最后一列的最大值。答案可达 4e6×5e4，必须 `long long`。

#### 复杂度

| 项 | 值 |
|---|---|
| 时间复杂度 | O(nm) |
| 空间复杂度 | O(nm) |
