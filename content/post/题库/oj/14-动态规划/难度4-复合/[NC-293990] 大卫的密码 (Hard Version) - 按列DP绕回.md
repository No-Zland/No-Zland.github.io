---
title: 大卫的密码 (Hard Version)
aliases:
  - NC293990
pid: NC293990
url: https://ac.nowcoder.com/acm/problem/293990
contest:
difficulty: 4
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

与 Easy 版同模型，只是 n、m 放大到 2e3，必须把每列 O(n^2) 的转移压到 O(n)。结论：列号单调不减，路径即「每列一段向下的连续段（长度 ≤ n，只绕一圈）+ 一次向右」，记 S_j(r) 为第 j 列前 r 行之和、T_j = S_j(n)，则 dp_j[r] = S_j(r) + max( max_{e≤r}(dp_{j-1}[e] - S_j(e-1)), T_j + max_{e>r}(dp_{j-1}[e] - S_j(e-1)) )。推导：e ≤ r 时段和是 S_j(r)-S_j(e-1)，e > r 时是 T_j-S_j(e-1)+S_j(r)，S_j(r) 都能提出来，剩下的分别取前缀、后缀最大值，于是每列线性，总状态 4e6。

---

### 题目描述

> 大卫想要完成送露西去月球的梦想，但首先他需要从保险箱中取一笔钱，他忘记密码是多少了，这该怎么办……
>
> 本题为问题的困难版本，两题的唯一区别在于变量  $n$  与  $m$  的数据范围。
>
> 给定一个  $n\times m$  的网格图，我们使用  $(i,j)$  表示网格中从上往下数第  $i$  行和从左往右数第  $j$  列的单元格。左上角为  $(1,1)$ ，右下角为  $(n,m)$ ，每个格子包含一个整数价值，使用  $a_{i,j}$  表示。
>
> 一个光标在上面移动，从  $(s,1)$  出发，每次可以向右或者向下移动，每个格子至多经过一次。当光标移动到  $(n,i) \left(1\le i\le m \right)$  格子，也就是最后一行的某个格子时，继续向下移动则会到达  $(1,i)$  格子。大卫需要移动光标到达  $(t,m)$ ，求最终大卫能获取的最大价值和。
>
> 注意本题的时间限制。本题数据量较大，我们建议您选取较快的读入方式。

**输入描述**

> 第一行输入四个整数  $n,m,s,t \left(1\le n,m\le\mathbf{2 \times 10^3};\ 1\le s,t\le n\right)$ 
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
// NC293990 大卫的密码 (Hard Version)
// 题意与 Easy 版完全相同，只有 n,m 范围从 500 放大到 2000。
// 做法：按列 DP，O(nm)。
//   路径的列号单调不减，所以每列只是一段「向下」的连续段（可绕回，长度 <= n），
//   相邻两列之间用一次「向右」连接，最后落在 (t,m)。
//   记 S_j(r) 为第 j 列 1..r 的前缀和、T_j = S_j(n)，e 为本列入口行、r 为出口行：
//     e <= r: 段和 = S_j(r) - S_j(e-1)
//     e >  r: 段和 = T_j - S_j(e-1) + S_j(r)
//   两种情形都能把 S_j(r) 提到外面，剩下的分别取 e<=r 与 e>r 的最大值（前缀/后缀最大值）。
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
            dp[r] = pre[r] - pre[s - 1];
        else
            dp[r] = (T - pre[s - 1]) + pre[r];
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

做 Easy 版时我就没打算写 O(n^2) 的转移：n 从 500 到 2000，朴素做法的乘法次数会从 1.2e8 涨到 8e9，换数据范围必然翻车，所以干脆一步到位。关键是看出入口 e 与出口 r 的两种相对位置各自只贡献一个「与 e 有关」的项：入口在出口上方时是 -S_j(e-1)，入口在下方绕回时多一个整列和 T_j，于是把这两类分别用前缀最大值、后缀最大值预处理，每个 r 就能 O(1) 拼出答案。落地时踩的坑主要在实现层面：网格按行读入再按列扫会跳内存，2000×2000 也还好，实测 0.2 秒左右；另外 dp 初值必须是很小的负数，因为价值可能是负的，用 0 会选出非法入口。最后拿 Easy 版同一份逻辑对拍过随机小数据，两版输出一致。

#### 卡点与关键一步

- 下标与边界：`suf[r+1]` 在 r = n 时不存在，要给哨兵值，否则会读到越界或把非法入口当合法。
- 一列最多 n 格，绕回分支只能加一次 T_j，加两次等于绕两圈、重复计数。
- 4e6 个格子的和可到 2e11，`int` 必溢出，DP 与答案都用 `long long`；读入量大，别用慢速 cin。

#### 复杂度

| 项 | 值 |
|---|---|
| 时间复杂度 | O(nm) |
| 空间复杂度 | O(nm) |
