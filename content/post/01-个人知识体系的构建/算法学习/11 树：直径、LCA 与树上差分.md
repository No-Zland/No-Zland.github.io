---
title: 11 树：直径、LCA 与树上差分
aliases: []
tags:
  - 算法思维
  - 算法/图论/树
updated: 2026-11-18
created: 2026-11-18 20:55
---

# 树：直径、LCA 与树上差分

> 一句话本质：树上两点路径唯一，于是任意路径都能拆成「u 到根 + v 到根 − 2×lca 到根」；LCA 负责找汇合点，差分把整条路径压成四个单点标记。

## 一、是什么

树是连通无环的无向图：$n$ 个点恰有 $n-1$ 条边，任意两点间路径唯一。这条唯一性带来一整套专用工具——LCA（最近公共祖先）定位路径的汇合点，直径描述最远的两个点，树上差分把「路径修改」变成「单点标记 + 一次自底向上求和」。

识别信号：

- 输入 $n$ 个点、$n-1$ 条边，或题面直接说「保证是一棵树」。
- 出现「祖先」「子树」「$u$ 到 $v$ 的路径上」。
- 「对子树整体加」「子树内求和」——DFS 序把子树拍成连续区间，再套线段树或树状数组。
- 「树上最远的两个点」「最长的一条路径」——直径。
- 「每个点被多少条路径覆盖」「先加路径、最后统一问」——树上差分。
- $n\le 5\times 10^5$ 且要多次查路径——倍增 LCA 或树链剖分。

不该用它的场景：图有环就不是树，路径不唯一，回到 10 的最短路；边权带负还问直径，两遍 DFS 失效；只查一次路径且 $n$ 很小，BFS 记父亲就够，不必上倍增。

## 二、形式

距离公式（边权为 1）：

$$dist(u,v)=dep[u]+dep[v]-2\,dep\bigl[lca(u,v)\bigr]$$

倍增递推，$fa[k][u]$ 是 $u$ 的 $2^k$ 级祖先：

$$fa[0][u]=p,\qquad fa[k][u]=fa[k-1]\bigl[fa[k-1][u]\bigr]$$

直径的树形 DP 形式：$f[u]$ 是 $u$ 向下的最长链，$g[u]$ 是次长链，$D=\max_u\bigl(f[u]+g[u]\bigr)$。

点差分给路径覆盖计数：

$$d[u]{+}{+},\quad d[v]{+}{+},\quad d[lca]{-}{-},\quad d[fa[lca]]{-}{-}$$

自底向上求和后，$d[x]$ 就是经过 $x$ 的路径数。边差分只改一处：$d[u]{+}{+},\ d[v]{+}{+},\ d[lca]\mathrel{-}=2$，求和后 $d[x]$ 表示 $x$ 到父亲那条边的覆盖数。

代码骨架：`dfs(u,p)` 一遍求出 `dep` 与倍增表，`lca(u,v)` 两段跳，`addPath` 打四个标记，`collect` 自底向上合并。数据形式：`fa[LOG+1][N]` 二维表，`LOG` 取 $\lceil\log_2 n\rceil$；边权下放到儿子，用点权代替边权。

## 三、怎么理解

直觉：LCA 是两束「向上」的路径第一次撞上的点。倍增把「往上走 $d$ 步」按二进制拆成 $\log n$ 次跳跃：$d$ 的第 $k$ 位是 1 就跳 $2^k$ 级。差分是在两端记 $+1$，在汇合处把多算的扣掉，让子树和自动把标记摊回整条路径。

为什么正确：

- **LCA 必须先跳深度差**：深的点单独上移到同一深度，否则两点同时跳时，深的那个会先越过 LCA，落到 LCA 上方，之后再也回不来。拉平后若两点重合，LCA 就是它；否则从高位往低位试跳，只在 `fa[k][u] != fa[k][v]` 时跳，保证一步不越过 LCA，最终停在「LCA 的两个儿子」上，父亲即答案。
- **直径端点引理**：所有直径共享同一个中点 $m$，否则两条直径能拼出更长的路径。设从 $m$ 出发最深的两个分支深度为 $h_1\ge h_2$，则直径长为 $h_1+h_2$，两端点正是这两个分支的最深叶。对任意 $r$，离它最远的点 $a$ 一定落在最深的分支上：若 $a$ 在更浅的分支，换到 $h_1$ 分支的深叶，路径同过 $m$，距离不会变小。所以 $a$ 必是直径端点，两遍 DFS 正确。
- **差分**：把路径拆成 $u\to lca$ 与 $v\to lca$ 两条上行链。两端各 $+1$，沿子树和上传时恰好覆盖整条链；$lca$ 被两条链各算一次，所以 $-1$；再上传一级会把 $lca$ 的父亲也误算，所以 $fa[lca]$ 再 $-1$。边差分里「$lca$ 到父亲」这条边本就不该算，于是两处扣减合并成 $lca$ 处 $-2$。

手推 7 点树：$1$ 连 $2,3$，$2$ 连 $4,5$，$3$ 连 $6,7$，则 $lca(4,6)=1$、$lca(5,7)=1$。加路径 $4-5$、$6-7$、$4-6$ 后各点覆盖数为 $1{:}1,\ 2{:}2,\ 3{:}2,\ 4{:}2,\ 5{:}1,\ 6{:}2,\ 7{:}1$，最大覆盖 2。

## 四、怎么变成代码

映射：`fa[0][u] = p`，`dep[u] = dep[p] + 1`；`dep[0] = 0`、`fa[k][0] = 0` 是哨兵，保证跳过头停在下标 0 而不是读到脏值。`LOG` 按 $2^{LOG}\ge n$ 取：$n=10^5$ 取 17，$n=5\times10^5$ 取 19。

循环顺序：预处理先填 `fa[0]` 再递推倍增；查询先跳深度差（按位即可），再同步跳（必须高位优先）；差分先打标记，最后一遍 DFS 自底向上求和。

边界：$n=5\times10^5$ 的链会让递归 DFS 爆栈，改手写栈或 BFS 求 `dep`、`fa[0]` 后按层推倍增；点差分减 `fa[lca]` 前判是否为 0；多组数据清空 `diff` 与 `best`。

```cpp
// 显式标准头，不用 <bits/stdc++.h>
#include <cstdio>
#include <vector>
#include <algorithm>
using namespace std;

const int N = 100005, LOG = 17;   // 2^17 = 131072 > 1e5
vector<int> g[N];
int dep[N], fa[LOG + 1][N];
int diff[N], best;

void dfs(int u, int p) {
    fa[0][u] = p;
    dep[u] = dep[p] + 1;                       // dep[0] = 0 作哨兵
    for (int k = 1; k <= LOG; ++k)
        fa[k][u] = fa[k - 1][fa[k - 1][u]];    // 2^k 级祖先
    for (int v : g[u])
        if (v != p) dfs(v, u);
}

int lca(int u, int v) {
    if (dep[u] < dep[v]) swap(u, v);
    int d = dep[u] - dep[v];
    for (int k = 0; k <= LOG; ++k)
        if (d >> k & 1) u = fa[k][u];          // 第一步：拉平深度
    if (u == v) return u;
    for (int k = LOG; k >= 0; --k)             // 第二步：高位优先同步跳
        if (fa[k][u] != fa[k][v]) { u = fa[k][u]; v = fa[k][v]; }
    return fa[0][u];                           // 停在 LCA 的两个儿子
}

// 点差分：路径 u-v 上每个点覆盖数 +1
void addPath(int u, int v) {
    int w = lca(u, v);
    ++diff[u]; ++diff[v];
    --diff[w];                                 // w 被两条链各算一次
    if (fa[0][w]) --diff[fa[0][w]];            // 别让父亲被上传误算
}

int collect(int u, int p) {                    // 自底向上合并差分
    int s = diff[u];
    for (int v : g[u])
        if (v != p) s += collect(v, u);
    best = max(best, s);                       // 最大覆盖数
    return s;
}

void far(int u, int p, int d, int& node, int& mx) {
    if (d > mx) { mx = d; node = u; }
    for (int v : g[u])
        if (v != p) far(v, u, d + 1, node, mx);
}

int diameter(int root) {                       // 返回直径边数
    int a = root, b = root, mx = -1;
    far(root, 0, 0, a, mx);                    // 任意点 -> 最远点 a
    mx = -1;
    far(a, 0, 0, b, mx);                       // a -> 最远点 b
    return mx;
}

int main() {
    const int n = 7;
    int es[6][2] = {{1,2},{1,3},{2,4},{2,5},{3,6},{3,7}};
    for (auto& e : es) { g[e[0]].push_back(e[1]); g[e[1]].push_back(e[0]); }
    dfs(1, 0);
    printf("diam = %d\n", diameter(1));        // 4-2-1-3-6，长度 4
    addPath(4, 5); addPath(6, 7); addPath(4, 6);
    collect(1, 0);
    printf("lca(4,6)=%d lca(5,7)=%d maxcov=%d\n", lca(4, 6), lca(5, 7), best);
    return 0;
}
```

## 五、具体例子

### 1. 树的直径：两遍 DFS

**问题**：求树上最远两点的距离。

**形式**：从任意点出发找最远点 $a$，再从 $a$ 出发找最远点 $b$，$ab$ 即直径。

```cpp
#include <cstdio>
#include <vector>
#include <algorithm>
using namespace std;
const int N = 200005;
vector<int> g[N];

// 从 u 出发，最远点写入 node，距离写入 mx
void far(int u, int p, int d, int& node, int& mx) {
    if (d > mx) { mx = d; node = u; }
    for (int v : g[u])
        if (v != p) far(v, u, d + 1, node, mx);
}

// 返回直径边数，端点由 a、b 带出
int diameter(int root, int& a, int& b) {
    int mx = -1;
    far(root, 0, 0, a, mx);      // 第一遍：任意点 -> 最远点 a
    mx = -1;
    far(a, 0, 0, b, mx);         // 第二遍：a -> 最远点 b
    return mx;
}
```

**为什么是端点**：见上节「直径端点引理」——所有直径共中点，离任意点最远的点必落在最深分支上，而最深分支的深叶正是直径端点。若 $r$ 本身就在最深分支内，$a$ 是该分支最深叶，结论不变。

**复杂度**：两遍 DFS，$O(n)$ 时间、$O(n)$ 空间。

### 2. LCA 倍增查询

**问题**：多次询问 $u,v$ 的最近公共祖先。

**形式**：`fa[k][u]` 预处理 $O(n\log n)$，每次查询两段跳，$O(\log n)$。

```cpp
#include <cstdio>
#include <vector>
#include <algorithm>
using namespace std;
const int N = 500005, LOG = 19;   // 2^19 = 524288
vector<int> g[N];
int dep[N], fa[LOG + 1][N];

void dfs(int u, int p) {
    fa[0][u] = p;
    dep[u] = dep[p] + 1;
    for (int k = 1; k <= LOG; ++k)
        fa[k][u] = fa[k - 1][fa[k - 1][u]];
    for (int v : g[u])
        if (v != p) dfs(v, u);
}

int lca(int u, int v) {
    if (dep[u] < dep[v]) swap(u, v);
    int d = dep[u] - dep[v];
    for (int k = 0; k <= LOG; ++k)
        if (d >> k & 1) u = fa[k][u];            // 先把深度差跳掉
    if (u == v) return u;                         // v 是 u 的祖先
    for (int k = LOG; k >= 0; --k)
        if (fa[k][u] != fa[k][v]) { u = fa[k][u]; v = fa[k][v]; }
    return fa[0][u];
}
```

**为什么先跳深度差**：不拉平就同步跳，深的点会先跨过 LCA，两个点错位到同一祖先下方，答案变成 LCA 的祖先。拉平后再「只在祖先不同时跳」，等价于从 LCA 正下方一层层逼近。

**复杂度**：预处理 $O(n\log n)$，单次查询 $O(\log n)$，空间 $O(n\log n)$。

### 3. 树上差分：Max Flow

**问题**：P3128 给 $k$ 条路径，求被覆盖次数最多的点。

**形式**：每条路径打四个标记，最后一次子树和；答案取最大值。

```cpp
#include <cstdio>
#include <vector>
#include <algorithm>
using namespace std;
const int N = 50005, LOG = 16;
vector<int> g[N];
int dep[N], fa[LOG + 1][N], diff[N], best;

void dfs(int u, int p) {
    fa[0][u] = p; dep[u] = dep[p] + 1;
    for (int k = 1; k <= LOG; ++k)
        fa[k][u] = fa[k - 1][fa[k - 1][u]];
    for (int v : g[u]) if (v != p) dfs(v, u);
}

int lca(int u, int v) {
    if (dep[u] < dep[v]) swap(u, v);
    int d = dep[u] - dep[v];
    for (int k = 0; k <= LOG; ++k) if (d >> k & 1) u = fa[k][u];
    if (u == v) return u;
    for (int k = LOG; k >= 0; --k)
        if (fa[k][u] != fa[k][v]) { u = fa[k][u]; v = fa[k][v]; }
    return fa[0][u];
}

void addPath(int u, int v) {
    int w = lca(u, v);
    ++diff[u]; ++diff[v];
    --diff[w];                                  // w 被算了两次
    if (fa[0][w]) --diff[fa[0][w]];             // 父亲不该被上传
}

int collect(int u, int p) {
    int s = diff[u];
    for (int v : g[u])
        if (v != p) s += collect(v, u);
    best = max(best, s);
    return s;
}
```

**`lca` 处扣 $2$ 的来历**：点差分里 $w$ 先收一次 $+1$（来自 $u$）再一次 $+1$（来自 $v$），而路径上 $w$ 只该算一次，所以 $w$ 处扣 $1$；再从 $fa[w]$ 扣 $1$，挡住向父亲的上传。边差分把这两次合并记在 $w$ 上，写成 `diff[w] -= 2`——因为 $w$ 到父亲那条边本就不在路径上，点覆盖与边覆盖的差别只在这里。

**复杂度**：预处理 $O(n\log n)$，$k$ 条路径 $O(k\log n)$，合并 $O(n)$；空间 $O(n\log n)$。

## 六、复杂度与易错点

| 项 | 值 |
|---|---|
| 时间复杂度 | DFS 序 $O(n)$；直径两遍 DFS $O(n)$；LCA 预处理 $O(n\log n)$、单次 $O(\log n)$；$q$ 次路径差分 $O((n+q)\log n)$ |
| 空间复杂度 | 倍增表 $O(n\log n)$；邻接表 $O(n)$（树只有 $n-1$ 条边）；差分数组 $O(n)$ |

- `LOG` 取小了：$n=2\times10^5$ 还写 17，最高的点跳不到根。
- `dep[0]` 不是 0，或根的父亲没设 0，倍增会读到脏值。
- 同步跳从低位开始，容易越过 LCA；必须高位优先。
- 负权树用两遍 DFS 求直径，最远点不是端点，答案偏小。
- 点差分与边差分混用：点差分 $lca$ 处 $-1$ 且父亲 $-1$，边差分 $lca$ 处 $-2$。
- 差分后忘记自底向上合并，直接读 `diff[x]`，拿到的是标记不是覆盖数。

## 七、真题清单

> `[x]` = 你已经 AC 的题，`[ ]` = 待补；牛客记录截至 2026-11-18。

- [x] [树到云端](https://ac.nowcoder.com/acm/problem/293975) · 牛客
- [ ] [小红的树上路径查询（easy）](https://ac.nowcoder.com/acm/problem/281354) · 牛客 · 试过 1 次
- [ ] [【模板】最近公共祖先（LCA）](https://www.luogu.com.cn/problem/P3379) · 洛谷
- [ ] [没有上司的舞会](https://www.luogu.com.cn/problem/P1352) · 洛谷
- [ ] [最大子树和](https://www.luogu.com.cn/problem/P1122) · 洛谷
- [ ] [【USACO15DEC】 Max Flow P](https://www.luogu.com.cn/problem/P3128) · 洛谷
- [ ] [【JLOI2014】 松鼠的新家](https://www.luogu.com.cn/problem/P3258) · 洛谷

## 八、下一步

1. LCA 解决「查路径」，再往上是树链剖分：把路径拆成 $O(\log n)$ 段 dfn 区间，配线段树就能做路径修改，赛场上比倍增更常见。
2. 本篇没写点分治与虚树，「树上路径计数」「多次建虚树」遇到再补。
3. 自测：造一棵 7 点树，手算三条路径的覆盖数再和程序对，正好验证点差分的四个符号。
4. P1352 与 P1122 是树形 DP 的入门，接着进 15 的树形 DP 会顺很多。
