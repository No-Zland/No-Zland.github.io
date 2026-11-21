---
title: Nowcoder Weekly Contest
aliases:
  - NC313668
pid: NC313668
url: https://ac.nowcoder.com/acm/problem/313668
contest:
difficulty: 1
solved: 2026-03-09
reviewed: 2026-11-18
tags:
  - 算法/基础/模拟
  - 平台/牛客
  - 状态/待复盘
updated: 2026-11-18 18:29
created: 2026-11-18 18:29
---

### 知识点：

结论：rating 不超过 1599 就是 rated，所以只需判断 x≤1599，成立输出 Rated，否则输出 Unrated。题面把边界写得很明确，“不超过”包含 1599，因此 1599 是 rated、1600 是 unrated，等号归属是唯一容易出错的地方。本题没有任何算法成分，属于读题加分支输出，考查把自然语言条件准确翻译成代码，以及输出单词的大小写。数据范围到 4000，int 足够，不需要排序或任何数据结构。

---

### 题目描述

> 牛客周赛对于 rating 不超过  $1599$  的选手是 rated 的（即比赛会影响选手的 rating）。
>
> 现在给定小苯当前的 rating，请你判断他打这场牛客周赛是否 rated。

**输入描述**

> 输入一个整数  $x\left(0\leqq x \leqq 4 \times 10^3 \right)$ ，表示小苯当前的 rating。

**输出描述**

> 如果小苯打这场比赛是 rated，输出  $\texttt{Rated}$ ，否则输出  $\texttt{Unrated}$ 。

#### 示例 1

**输入**

```text
1500
```

**输出**

```text
Rated
```

#### 示例 2

**输入**

```text
1600
```

**输出**

```text
Unrated
```

---

### 最终代码：

```cpp
#include <cstdio>

// 题面给出 rated 的边界：rating 不超过 1599 即 rated。
// 取等号也算，所以判断 x <= 1599。
int main() {
    int x;
    if (scanf("%d", &x) != 1) return 0;
    printf("%s\n", x <= 1599 ? "Rated" : "Unrated");
    return 0;
}
```

*代码为参考实现（按题意重写并用样例验证），非本人原始提交。*

---

### 解题思路

第一反应这题就是签到：读一个整数，和 1599 比大小。写之前特意回到题面确认“不超过”的含义，确认 1599 本身也算 rated，于是条件写成 x<=1599 而不是 x<1599。接着注意输出是 Rated / Unrated，首字母大写、其余小写，必须和样例完全一致，不能顺手写成 YES/NO。样例 1500 和 1600 正好卡在边界两侧，跑一遍就能确认分支方向没反。整个程序只有读入、比较、输出三步，没有循环也没有数组。

#### 卡点与关键一步

- 1599 属于 rated，边界不要写成严格小于
- 输出是 Rated / Unrated，注意大小写
- 题目问的是是否 rated，不要输出 YES / NO

#### 复杂度

| 项 | 值 |
|---|---|
| 时间复杂度 | O(1) |
| 空间复杂度 | O(1) |
