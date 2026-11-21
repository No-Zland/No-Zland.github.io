---
title: 16 字符串：哈希、KMP 与 Trie
aliases: []
tags:
  - 算法思维
  - 算法/字符串/哈希
updated: 2026-11-18
created: 2026-11-18 20:55
---

# 字符串：哈希、KMP 与 Trie

> 一句话本质：哈希把"逐字符比较"折成一个数，KMP 把"失配后重新对齐"折成一个 border 跳转，Trie 把"公共前缀"折成一条共享路径。

## 一、是什么

字符串题的原语只有三个：**判等**、**匹配**、**前缀**。哈希解决"两个子串是否相同"（$O(1)$ 比较），KMP 解决"模式串在文本串中出现的所有位置"（$O(n+m)$ 且主串指针不回退），Trie 解决"一堆串的公共前缀查询"（按字符走树）。

二者都不改变字符串本身，只是给它换一种**表示**：哈希换成数，KMP 换成前缀函数，Trie 换成树上的路径。选哪个表示，决定了复杂度。

识别信号：

- 问"两个子串是否相同""某串出现几次""最长重复子串"：哈希，$O(1)$ 比较。
- 在文本串里找模式串的所有出现，$n,m\le10^6$：KMP（或 Z 函数）。
- 问"循环节""最短重复单元""所有 border"：next 数组，周期是 $n-next[n]$。
- 问"多个串的最长公共前缀""前缀出现次数""字典序排序"：Trie。
- 问"与 $x$ 异或最大的数"、可持久化异或查询：0-1 Trie。
- 要在 $O(\log n)$ 内比较两个后缀/拼接串的字典序：哈希 + 二分 LCP。

不该用它的场景：

- 串很短、只比一次：暴力逐字符比更快，哈希是负优化。
- 需要确定性正确（对拍、构造证明、答案要唯一无概率）：单模哈希可能被卡，必须双模或换 SA/SAM。
- 哈希要支持修改：得挂线段树维护，代价比想象大。
- 字符集大、公共前缀又短：Trie 节点数爆炸，改哈希 + 排序更省。

## 二、形式

**数学形式。** 把串看成 $B$ 进制数，则

$$h[i]=h[i-1]\cdot B+s_i,\qquad \mathrm{hash}(l,r)=h[r]-h[l-1]\cdot B^{\,r-l+1}$$

KMP 的核心量是前缀函数：

$$next[i]=\max\bigl\{k<i\ \big|\ s[1..k]=s[i-k+1..i]\bigr\}$$

Trie 是一个五元组 $(\Sigma,Q,q_0,\delta,cnt)$：$q_0$ 是根，$\delta(u,c)$ 是走字符 $c$ 的出边，$cnt[u]$ 是经过 $u$ 的串数——它恰好等于"该节点代表的前缀出现了几次"。

**代码形式。** 哈希：两遍循环填 $h$ 与 $p$，一次减法取子串。KMP：两段同构的代码（求 next、做匹配），每段都是 `while (j && 不匹配) j = next[j]`。Trie：一条 `for (char c : s)` 循环，边走边建。

**数据形式。** 哈希存 `h1,h2,p1,p2` 四个数组（双模）；KMP 只存一个 `next[m+1]`；Trie 存 `trie[节点数][26]` 与 `cnt[]`，节点数上界是"所有串总长 + 1"，不是串数。

## 三、怎么理解

**直觉。** 哈希是"给每个串盖一个几乎唯一的章"；KMP 是"失配时，我已经知道这段文本的后缀长什么样，直接跳到它的最长 border 处继续比"；Trie 是"把 $n$ 个串的前缀重叠部分只存一次"。

**为什么正确。**

- 哈希：进制展开在不取模时是单射，取模后唯一风险是碰撞。双模把碰撞概率压到约 $1/(M_1M_2)\approx10^{-18}$，工程上够用；单模加固定 BASE 则可能被针对性构造。
- KMP：失配发生在 $p[j+1]$ 与 $s[i]$，说明 $s[i-j..i-1]=p[1..j]$。若存在更小的对齐使匹配继续，则 $p[1..k]=p[j-k+1..j]$，即 $k$ 是 $p[1..j]$ 的 border。取最长的 border 跳得最少，且任何可行起点都不会被跳过——所以"只回退模式串"不丢答案。求 next 时同理自我匹配，且 $next[i]\le next[i-1]+1$，故 `j` 单调回跳，$i$ 单调前进，总 $O(n)$。
- Trie 的 0-1 版：第 $b$ 位贡献 $2^b$，大于所有低位之和，所以每一位"能相反就相反"是局部最优也是全局最优（交换论证）。

**手推 1：哈希。** "abc"，$B=131$，不取模：$h_1=97$，$h_2=97\cdot131+98=12805$，$h_3=12805\cdot131+99=1677554$。取子串 "bc"：$h_3-h_1\cdot131^2=1677554-97\cdot17161=1677554-1664617=12937$，正好等于 $98\cdot131+99$。

**手推 2：next。** $s=$"aabaab"。逐位求最长真 border：

| $i$ | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 前缀 | a | aa | aab | aaba | aabaa | aabaab |
| $next[i]$ | 0 | 1 | 0 | 1 | 2 | 3 |

$n-next[n]=6-3=3$ 且 $6\bmod3=0$，故最小循环节是 "aab"。

## 四、怎么变成代码

**映射。**

- 哈希：`l,r` 用 **1 起**闭区间，减法后先 `+MOD` 再取模，避免负数；`p[i]` 是 $B^i$。
- KMP：`next` 通常 1 起，`next[1]=0`；匹配成功后 `j = next[j]` 才能找出重叠出现。
- Trie：`tot` 从 0 开始（0 是根），新节点 `++tot`；查询走不通立即返回 0。
- 边界：空串、单字符串；哈希的 `r-l+1` 与 `p` 下标必须对齐，差一位就是全错。

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <utility>

typedef long long ll;
const ll MOD1 = 1000000007LL, MOD2 = 1000000009LL, BASE = 131;

struct Hash {
    int n;
    std::vector<ll> h1, h2, p1, p2;
    explicit Hash(const std::string& s)
        : n((int)s.size()), h1(n + 1, 0), h2(n + 1, 0), p1(n + 1, 1), p2(n + 1, 1) {
        for (int i = 1; i <= n; ++i) {
            h1[i] = (h1[i - 1] * BASE + s[i - 1]) % MOD1;
            h2[i] = (h2[i - 1] * BASE + s[i - 1]) % MOD2;
            p1[i] = p1[i - 1] * BASE % MOD1;
            p2[i] = p2[i - 1] * BASE % MOD2;
        }
    }
    std::pair<ll, ll> get(int l, int r) const {       // 1 起，闭区间
        ll a = ((h1[r] - h1[l - 1] * p1[r - l + 1]) % MOD1 + MOD1) % MOD1;
        ll b = ((h2[r] - h2[l - 1] * p2[r - l + 1]) % MOD2 + MOD2) % MOD2;
        return {a, b};
    }
};

// KMP 的 next：nxt[i] 是 p[0..i-1] 的最长真 border 长度
std::vector<int> buildNext(const std::string& p) {
    int m = (int)p.size();
    std::vector<int> nxt(m + 1, 0);
    for (int i = 2, j = 0; i <= m; ++i) {
        while (j > 0 && p[i - 1] != p[j]) j = nxt[j];  // 失配只回跳模式串
        if (p[i - 1] == p[j]) ++j;                     // 能接上就延长
        nxt[i] = j;
    }
    return nxt;
}

int main() {
    std::string s, p;
    std::cin >> s >> p;
    Hash hs(s);
    std::vector<int> nxt = buildNext(p);
    int n = (int)s.size(), m = (int)p.size();
    for (int i = 1, j = 0; i <= n; ++i) {
        while (j > 0 && s[i - 1] != p[j]) j = nxt[j];
        if (s[i - 1] == p[j]) ++j;
        if (j == m) { std::cout << i - m + 1 << '\n'; j = nxt[j]; }
    }
    (void)hs;                                          // 本例只为展示两个骨架并存
    return 0;
}
```

## 五、具体例子

**1. 字符串哈希：双模 + $O(1)$ 取子串。**

问题：给串 $s$ 与 $q$ 次询问，每次判两个等长子串是否相同。

形式：$\mathrm{hash}(l,r)=h[r]-h[l-1]B^{r-l+1}$，双模各算一次，两个模数都相等才算相同。

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <utility>

typedef long long ll;
const ll MOD1 = 1000000007LL, MOD2 = 1000000009LL, BASE = 131;

struct Hash {
    int n;
    std::vector<ll> h1, h2, p1, p2;
    explicit Hash(const std::string& s)
        : n((int)s.size()), h1(n + 1, 0), h2(n + 1, 0), p1(n + 1, 1), p2(n + 1, 1) {
        for (int i = 1; i <= n; ++i) {
            h1[i] = (h1[i - 1] * BASE + s[i - 1]) % MOD1;
            h2[i] = (h2[i - 1] * BASE + s[i - 1]) % MOD2;
            p1[i] = p1[i - 1] * BASE % MOD1;
            p2[i] = p2[i - 1] * BASE % MOD2;
        }
    }
    std::pair<ll, ll> get(int l, int r) const {
        ll a = ((h1[r] - h1[l - 1] * p1[r - l + 1]) % MOD1 + MOD1) % MOD1;
        ll b = ((h2[r] - h2[l - 1] * p2[r - l + 1]) % MOD2 + MOD2) % MOD2;
        return {a, b};
    }
};

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::string s;
    std::cin >> s;
    Hash hs(s);
    int q;
    std::cin >> q;
    while (q--) {
        int l1, r1, l2, r2;
        std::cin >> l1 >> r1 >> l2 >> r2;
        if (r1 - l1 != r2 - l2) { std::cout << "No\n"; continue; }
        std::cout << (hs.get(l1, r1) == hs.get(l2, r2) ? "Yes\n" : "No\n");
    }
    return 0;
}
```

复杂度：预处理 $O(n)$，每次比较 $O(1)$，空间 $O(n)$。$B$ 要大于字符集（'z'=122，故取 131）。

**2. KMP：next 的含义与"主串指针不回退"。**

问题：求模式串 $p$ 在文本串 $s$ 中所有出现位置，并输出 next 数组。

形式：`nxt[i]` 是 $p[0..i-1]$ 的最长真 border；匹配时 `i` 只增不减，失配只让 `j = nxt[j]`。

```cpp
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::string s, p;
    std::cin >> s >> p;
    int n = (int)s.size(), m = (int)p.size();

    std::vector<int> nxt(m + 1, 0);
    for (int i = 2, j = 0; i <= m; ++i) {
        while (j > 0 && p[i - 1] != p[j]) j = nxt[j];
        if (p[i - 1] == p[j]) ++j;
        nxt[i] = j;
    }

    for (int i = 1, j = 0; i <= n; ++i) {              // i 永不回退
        while (j > 0 && s[i - 1] != p[j]) j = nxt[j]; // 只回退模式串
        if (s[i - 1] == p[j]) ++j;
        if (j == m) {                                  // 匹配成功
            std::cout << i - m + 1 << '\n';            // 起点，1 起
            j = nxt[j];                                // 继续找重叠出现
        }
    }
    for (int i = 1; i <= m; ++i) std::cout << nxt[i] << " \n"[i == m];
    return 0;
}
```

复杂度：求 next $O(m)$、匹配 $O(n)$，总计 $O(n+m)$，空间 $O(m)$。

**3. Trie：插入/查询，以及 0-1 Trie 求最大异或。**

问题（P8306）：维护若干模式串，每次询问某串是多少模式串的前缀。

形式：沿字符走，若在插入时把每个经过节点的 `cnt` 加一，则查询走到底读到的 `cnt` 就是"以它为前缀的串数"；走不通说明没有这个前缀。

```cpp
#include <iostream>
#include <string>

const int MAXNODE = 100005;      // 节点数上界 = 所有串总长 + 1
int trie[MAXNODE][26];
int cnt[MAXNODE];                // 经过该节点的串数 = 该前缀出现次数
int tot = 0;                     // 0 是根

void insert(const std::string& s) {
    int u = 0;
    for (char ch : s) {
        int c = ch - 'a';
        if (trie[u][c] == 0) trie[u][c] = ++tot;   // 没有就新建
        u = trie[u][c];
        ++cnt[u];
    }
}

int queryPrefix(const std::string& s) {
    int u = 0;
    for (char ch : s) {
        int c = ch - 'a';
        if (trie[u][c] == 0) return 0;             // 前缀不存在
        u = trie[u][c];
    }
    return cnt[u];
}

int main() {
    int n, q;
    std::cin >> n >> q;
    for (int i = 0; i < n; ++i) { std::string s; std::cin >> s; insert(s); }
    while (q--) {
        std::string s;
        std::cin >> s;
        std::cout << queryPrefix(s) << '\n';
    }
    return 0;
}
```

0-1 Trie 把"字符"换成"二进制位"，从高位到低位插入。查询与 $x$ 异或最大的数时，每一位尽量走与 $x$ 相反的儿子（走不了才走同侧），沿途把这一位的贡献加上：

```cpp
#include <iostream>

const int MAXBIT = 31;
const int MAXNODE = 100005 * 32;
int ch[MAXNODE][2];
int tot = 0;

void insert(int x) {
    int u = 0;
    for (int b = MAXBIT - 1; b >= 0; --b) {        // 高位在前
        int c = (x >> b) & 1;
        if (ch[u][c] == 0) ch[u][c] = ++tot;
        u = ch[u][c];
    }
}

int maxXor(int x) {
    int u = 0, res = 0;
    for (int b = MAXBIT - 1; b >= 0; --b) {
        int c = (x >> b) & 1;
        if (ch[u][c ^ 1] != 0) { res |= 1 << b; u = ch[u][c ^ 1]; }  // 优先走反位
        else u = ch[u][c];                                          // 否则只能同侧
    }
    return res;
}

int main() {
    int a[] = {3, 10, 5, 25, 2, 8};
    for (int x : a) insert(x);
    std::cout << maxXor(5) << '\n';                 // 5^25 = 28，最大
    return 0;
}
```

复杂度：插入与查询均 $O(\text{串长})$（0-1 Trie 是 $O(31)$），空间 $O(\text{总字符数}\times\text{字符集})$——$10^6$ 个节点 × 26 个 `int` 约 100MB，超限时改 `map` 或链式存儿子。

## 六、复杂度与易错点

| 算法 | 预处理 | 单次操作 | 空间 |
|---|---|---|---|
| 字符串哈希（双模） | $O(n)$ | $O(1)$ 子串比较 | $O(n)$ |
| KMP | $O(m)$ | 匹配 $O(n+m)$ | $O(m)$ |
| Trie | $O(\text{总长})$ | $O(\text{串长})$ | $O(\text{节点数}\times\Sigma)$ |
| 0-1 Trie | $O(31n)$ | $O(31)$ | $O(31n)$ |

- 子串哈希漏乘 $B^{r-l+1}$ 或下标差一位：短串能过、长串全错，写完先用手算样例验证。
- 减法不 `+MOD` 就取模：负数进数组，答案随机漂移。
- 单模 + 固定 BASE：遇到构造数据必被卡，重要比赛用双模或随机 BASE。
- KMP 的 next 混用 0 起与 1 起：`nxt[1]` 写成 1 会在失配时死循环。
- 匹配成功后忘 `j = nxt[j]`："aaa" 里找 "aa" 只报一次，重叠出现全漏。
- Trie 节点数组按"串数"开：多串共享前缀时 `tot` 超界，必须按总字符数开。

## 七、真题清单

> `[x]` = 你已经 AC 的题，`[ ]` = 待补；牛客记录截至 2026-11-18。

- [x] [凯撒密码](https://ac.nowcoder.com/acm/problem/208111) · 牛客
- [x] [括号串匹配](https://ac.nowcoder.com/acm/problem/282083) · 牛客
- [x] [好串](https://ac.nowcoder.com/acm/problem/21874) · 牛客
- [x] [相同的字符](https://ac.nowcoder.com/acm/problem/281546) · 牛客
- [x] [比较字符串](https://ac.nowcoder.com/acm/problem/282215) · 牛客
- [x] [字符串操作](https://ac.nowcoder.com/acm/problem/281576) · 牛客
- [ ] [【模板】KMP](https://www.luogu.com.cn/problem/P3375) · 洛谷
- [ ] [【模板】字符串哈希](https://www.luogu.com.cn/problem/P3370) · 洛谷
- [ ] [于是他错误的点名开始了](https://www.luogu.com.cn/problem/P2580) · 洛谷
- [ ] [【模板】字典树 / Trie](https://www.luogu.com.cn/problem/P8306) · 洛谷

## 八、下一步

1. 先打 P3375，把 next 数组打印出来和暴力求 border 对拍，确认 0 起/1 起没混。
2. P3370 先单模过，再换双模跑同一组数据，顺便想清楚"为什么有人会被卡"。
3. P2580 与 P8306 连着做：一个查"是否出现过"，一个查"作为前缀出现几次"，节点数组各按什么规模开。
4. 自测：说清 "aabaab" 的最小循环节；写出"判断 $s[l..r]$ 是否回文"的哈希表达式（正串 vs 反串对应段）；给 `{3,10,5,25,2,8}` 与 $x=5$ 手推 0-1 Trie 的每一步选择。
