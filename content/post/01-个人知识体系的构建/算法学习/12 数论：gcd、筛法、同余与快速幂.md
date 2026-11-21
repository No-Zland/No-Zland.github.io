---
title: 12 数论：gcd、筛法、同余与快速幂
aliases: []
tags:
  - 算法思维
  - 算法/数论/同余
updated: 2026-11-18
created: 2026-11-18 20:55
---

# 数论：gcd、筛法、同余与快速幂

> 一句话本质：数论把整数问题压到「因子」和「模」两个小结构上——gcd 与扩欧解线性关系，筛法批量造素数，快速幂在模下做乘法。

## 一、是什么

数论算法研究整数的整除结构：$a\mid b$、最大公约数、素数分解、同余 $a\equiv b\pmod m$。落到代码只有四件事：求 gcd、批量筛素数、解 $ax+by=c$ 型线性方程、在模意义下做乘除（逆元）。

识别信号：

- 「最大公约数」「最小公倍数」「约分」——gcd，分数先约分再运算。
- 「$n$ 以内有多少素数」「第 $k$ 个素数」——筛法。
- 「答案对 $10^9+7$ 取模」「要除以 $k$」——快速幂 + 逆元。
- 「$ax\equiv c\pmod m$」「$ax+by=c$ 有没有解」——裴蜀定理 + 扩欧。
- 「不能表示成 $ax+by$ 的最大整数」——Frobenius 结论 $ab-a-b$。
- 多个模数、两两互质——中国剩余定理。
- 数据到 $10^{18}$ 还要做乘法——`__int128` 或龟速乘。

不该用它的场景：模数是合数却用费马小定理求逆，算出来根本不是逆元；$n$ 到 $10^9$ 还想开数组筛，只能试除、分段筛或 Miller-Rabin；$\gcd(a,m)\ne1$ 时逆元不存在，得先约分或换方程。

## 二、形式

gcd 递推，边界是 $b=0$：

$$\gcd(a,b)=\gcd(b,\ a\bmod b),\qquad \gcd(a,0)=a$$

裴蜀定理：$ax+by=c$ 有整数解，当且仅当 $\gcd(a,b)\mid c$。

扩欧返回 $ax+by=g$ 的一组特解 $(x_0,y_0)$，通解为

$$x=x_0+k\cdot\frac{b}{g},\qquad y=y_0-k\cdot\frac{a}{g}$$

同余方程 $ax\equiv c\pmod m$ 等价于 $ax+my=c$，所以有解 $\iff g=\gcd(a,m)\mid c$。两边约掉 $g$ 得 $a'x\equiv c'\pmod{m'}$，此时 $\gcd(a',m')=1$，逆元存在：

$$x\equiv c'\cdot(a')^{-1}\pmod{m'}$$

线性筛的不变量：每个合数 $n$ 只在 $i=n/p$、$p=\operatorname{lpf}(n)$ 时被标记一次，且 $p\le\operatorname{lpf}(i)$。

快速幂把指数按二进制拆开：$a^e=\prod_k a^{b_k2^k}$。费马小定理：$p$ 为素数且 $p\nmid a$ 时

$$a^{p-1}\equiv1\pmod p\quad\Longrightarrow\quad a^{-1}\equiv a^{p-2}\pmod p$$

代码骨架：`exgcd` 递归回代；`inv` 把解归一到 $[0,m)$；`sieve` 维护 `primes[]` 与 `comp[]`；`qpow` 边平方边按位乘。数据形式都是整型数组，筛法开 $n+1$，倍增类不需要额外结构。

## 三、怎么理解

直觉：gcd 是「用短边量长边」，量到余 0 为止；扩欧把这个过程倒着回放，反推出系数；筛法让每个合数被它的最小质因子「认领」一次；快速幂把指数看成二进制，平方一次指数就翻一倍。

为什么正确：

- **gcd**：$d\mid a$ 且 $d\mid b$ $\iff$ $d\mid b$ 且 $d\mid(a-qb)$，两边公约数集合完全相同，最大元自然相同。每步余数至少减半，$O(\log\min(a,b))$。
- **扩欧回代**：设递归返回 $x',y'$ 满足 $bx'+(a\bmod b)y'=g$。代入 $a\bmod b=a-\lfloor a/b\rfloor b$，整理得 $ay'+b(x'-\lfloor a/b\rfloor y')=g$，所以新解是 $x=y'$、$y=x'-\lfloor a/b\rfloor y'$——这正是代码里先交换引用、再 `y -= a/b*x` 的来历。
- **线性筛**：若 $p\mid i$，则 $p$ 必是 $i$ 的最小质因子（$p$ 从小到大枚举，第一次整除）。此时若继续枚举 $p'>p$，$i\cdot p'$ 的最小质因子是 $p<p'$，它本应在 $i'=i\cdot p'/p$ 时由 $p$ 筛掉，现在筛就会重复，所以立即 break。漏筛不会发生：合数 $n$ 的最小质因子 $p$ 满足 $p\le\operatorname{lpf}(n/p)$，枚举到 $p$ 之前不会触发 break。
- **快速幂**：$e=\sum b_k2^k$，平方递推得到 $a^{2^k}$，按位乘起来即 $a^e$，每轮指数减半，$O(\log e)$。
- **费马**：$a,2a,\dots,(p-1)a$ 在模 $p$ 下是 $1,\dots,p-1$ 的一个排列，全部相乘得 $a^{p-1}(p-1)!\equiv(p-1)!$，约掉阶乘即 $a^{p-1}\equiv1$。

手推：$\gcd(48,36)$：$48=1\times36+12$，$36=3\times12+0$，得 12。$\operatorname{exgcd}(12,8)$：递归到 $(4,0)$ 返回 $g=4$；回代 $(8,4)$ 得 $x=0,y=1$；再回代 $(12,8)$ 得 $x=1,y=-1$，验证 $12-8=4$。快速幂 $2^{10}\bmod1000$：$10=(1010)_2$，$2^2=4$、$2^8=256$，$4\times256=1024\equiv24$。

## 四、怎么变成代码

映射：全部用 `long long`；`exgcd` 的引用参数就是两个解；`inv` 返回前必须 `(x % m + m) % m`，因为 C++ 负数取模仍为负；`lcm` 写成 `a / gcd(a,b) * b`，先除后乘防溢出。

循环顺序：快速幂的 `for` 里先 `a %= m`，每轮先判当前位再平方；筛法外层 $i$ 递增，内层质数从小到大，标记完立即判 `i % p == 0`。

边界：快速幂的初值写 `1 % m`，否则 $m=1$ 时错；扩欧 $b=0$ 是出口；筛法数组开 $n+1$；试除写 `i * i <= n`，不写 `sqrt`。

```cpp
// 显式标准头，不用 <bits/stdc++.h>
#include <cstdio>
#include <vector>
#include <algorithm>
using namespace std;
typedef long long ll;

ll gcd(ll a, ll b) { return b ? gcd(b, a % b) : a; }

// 快速幂：a^e mod m
ll qpow(ll a, ll e, ll m) {
    ll r = 1 % m;
    for (a %= m; e; e >>= 1, a = a * a % m)
        if (e & 1) r = r * a % m;
    return r;
}

// 扩欧：解 ax + by = g，返回 g
ll exgcd(ll a, ll b, ll& x, ll& y) {
    if (!b) { x = 1; y = 0; return a; }
    ll g = exgcd(b, a % b, y, x);
    y -= a / b * x;                       // 回代，换掉系数
    return g;
}

// 模 m 逆元，要求 gcd(a,m)=1；不存在返回 -1
ll inv(ll a, ll m) {
    ll x, y;
    if (exgcd(a, m, x, y) != 1) return -1;
    return (x % m + m) % m;               // 搬回 [0, m)
}

// 线性筛：primes 存素数，comp 标记合数
const int MAXN = 1000005;
int primes[MAXN], pcnt;
bool comp[MAXN];

void sieve(int n) {
    for (int i = 2; i <= n; ++i) {
        if (!comp[i]) primes[pcnt++] = i;
        for (int j = 0; j < pcnt; ++j) {
            int p = primes[j];
            if ((ll)i * p > n) break;
            comp[i * p] = true;           // 用最小质因子 p 认领 i*p
            if (i % p == 0) break;        // p 已是 i 的最小质因子
        }
    }
}

int main() {
    ll g = gcd(48, 36);
    printf("gcd=%lld lcm=%lld\n", g, 48 / g * 36);        // 12, 144
    printf("2^10 mod 1000 = %lld\n", qpow(2, 10, 1000));   // 24
    ll x, y;
    ll gg = exgcd(12, 8, x, y);
    printf("exgcd g=%lld x=%lld y=%lld\n", gg, x, y);      // 4, 1, -1
    printf("inv(3,7)=%lld inv(6,9)=%lld\n", inv(3, 7), inv(6, 9));  // 5, -1
    sieve(100);
    printf("pi(100)=%d\n", pcnt);                          // 25
    return 0;
}
```

## 五、具体例子

### 1. 裴蜀定理 + 扩展欧几里得

**问题**：$ax+by=c$ 何时有解？$ax\equiv c\pmod m$ 怎么求最小非负解？

**形式**：$ax+by=c$ 有解 $\iff \gcd(a,b)\mid c$；同余式等价于 $ax+my=c$，约掉 $g$ 后逆元存在，解为 $x\equiv(c/g)\cdot(a/g)^{-1}\pmod{m/g}$。

```cpp
#include <cstdio>
#include <algorithm>
using namespace std;
typedef long long ll;

ll exgcd(ll a, ll b, ll& x, ll& y) {
    if (!b) { x = 1; y = 0; return a; }
    ll g = exgcd(b, a % b, y, x);
    y -= a / b * x;
    return g;
}

// 解 ax ≡ c (mod m)，返回最小非负解；无解返回 -1
ll solveCong(ll a, ll c, ll m) {
    ll x, y;
    ll g = exgcd(a, m, x, y);
    if (c % g) return -1;                 // 裴蜀条件：gcd(a,m) | c
    ll mod = m / g;                       // 约掉 g，模数一起缩小
    x = (x % mod + mod) % mod;
    return x * (c / g) % mod;
}
```

**为什么能解**：$ax\equiv c\pmod m$ 等价于存在整数 $y$ 使 $ax+my=c$，这正是裴蜀定理的形式；有解后两边除以 $g$，$a/g$ 与 $m/g$ 互质，逆元一定存在，套快速幂或扩欧即可。

**复杂度**：$O(\log\min(a,m))$，空间即递归栈 $O(\log m)$。

### 2. 欧拉筛：每个合数只被最小质因子筛一次

**问题**：筛出 $n$ 以内所有素数，并保证线性时间。

**形式**：`i` 从小到大，用当前已知素数 `p` 去标记 `i*p`；一旦 `i % p == 0` 就停。

```cpp
#include <cstdio>
using namespace std;
const int N = 1000005;
int primes[N], cnt;
bool comp[N];

void sieve(int n) {
    for (int i = 2; i <= n; ++i) {
        if (!comp[i]) primes[cnt++] = i;      // 第 1 行：没被标记 -> 素数
        for (int j = 0; j < cnt; ++j) {
            int p = primes[j];                // 第 2 行：p 从小到大
            if ((long long)i * p > n) break;  // 第 3 行：越界即停
            comp[i * p] = true;               // 第 4 行：p 认领 i*p
            if (i % p == 0) break;            // 第 5 行：p 已是 i 的最小质因子
        }
    }
}
```

**逐行看 `i % p == 0` 的 break**：此时 $i=p\cdot k$，若继续枚举 $p'>p$，则 $i\cdot p'=p\cdot(kp')$ 的最小质因子是 $p$，它会在 $i'=kp'$ 那一轮被 $p$ 筛掉；现在筛就是重复。而所有合数都会被筛到：$n$ 的最小质因子 $p$ 满足 $p\le\operatorname{lpf}(n/p)$，所以枚举到 $p$ 时 `i % p` 还没触发 break。

**复杂度**：每个合数标记一次、每个素数入表一次，$O(n)$；空间 $O(n)$。

### 3. 快速幂 + 费马小定理求逆元

**问题**：求 $a^{-1}\bmod p$，$p$ 是大素数。

**形式**：$a^{p-1}\equiv1$，所以 $a\cdot a^{p-2}\equiv1$，逆元就是 $a^{p-2}\bmod p$。

```cpp
#include <cstdio>
using namespace std;
typedef long long ll;

ll qpow(ll a, ll e, ll m) {
    ll r = 1 % m;
    for (a %= m; e; e >>= 1, a = a * a % m)
        if (e & 1) r = r * a % m;
    return r;
}

// 适用条件：p 是素数，且 a % p != 0
ll invFermat(ll a, ll p) {
    return qpow(a, p - 2, p);
}
```

**适用条件**：$p$ 必须是素数且 $a$ 不被 $p$ 整除。反例：$p=9$（合数）、$a=2$，$2^{7}\bmod9=2$，可 $2$ 的逆元是 $5$（$2\times5=10\equiv1$），公式给出的是错值；合数模应改用扩欧，或欧拉定理 $a^{\varphi(m)-1}$。

**复杂度**：$O(\log p)$，空间 $O(1)$。

## 六、复杂度与易错点

| 算法 | 时间 | 空间 |
|---|---|---|
| gcd / exgcd | $O(\log\min(a,b))$ | $O(\log)$ 递归栈 |
| 快速幂 | $O(\log e)$ | $O(1)$ |
| 埃氏筛 | $O(n\log\log n)$ | $O(n)$ |
| 线性筛 | $O(n)$ | $O(n)$ |
| 试除分解 | $O(\sqrt n)$ | $O(1)$ |
| 费马求逆 | $O(\log p)$ | $O(1)$ |

- `lcm` 写成 `a * b / gcd`，$10^9$ 级别的两个数先溢出再除，结果完全随机。
- 快速幂忘了 `a %= m` 或初值写成 `1`，$m$ 很小时直接错。
- 合数模上套费马小定理，得到的数看着像逆元，其实乘回去不等于 1。
- 线性筛漏了 `i % p == 0` 的 break，一个合数被筛多次，退化成 $O(n\log n)$ 以上。
- 扩欧的解不归一，负数直接输出；要最小正整数解就 `(x % mod + mod) % mod`。
- 试除写 `i <= sqrt(n)`，每轮重算又慢又有精度问题，写 `i * i <= n`。

## 七、真题清单

> `[x]` = 你已经 AC 的题，`[ ]` = 待补；牛客记录截至 2026-11-18。

- [x] [素数判断](https://ac.nowcoder.com/acm/problem/14399) · 牛客
- [x] [【NOIP2017】小凯的疑惑](https://ac.nowcoder.com/acm/problem/16414) · 牛客
- [x] [最大公约数和最小公倍数](https://ac.nowcoder.com/acm/problem/280481) · 牛客
- [x] [判断素数](https://ac.nowcoder.com/acm/problem/280507) · 牛客
- [ ] [素数](https://ac.nowcoder.com/acm/problem/280624) · 牛客 · 试过 11 次
- [x] [既约分数](https://ac.nowcoder.com/acm/problem/280778) · 牛客
- [x] [【NOIP2014】解方程](https://ac.nowcoder.com/acm/problem/16499) · 牛客
- [x] [天神的密码](https://ac.nowcoder.com/acm/problem/26005) · 牛客
- [x] [小苯的GCD疑问2.0](https://ac.nowcoder.com/acm/problem/303596) · 牛客
- [ ] [小苯的GCD疑问1.0](https://ac.nowcoder.com/acm/problem/303589) · 牛客 · 试过 11 次
- [ ] [【模板】线性筛素数](https://www.luogu.com.cn/problem/P3383) · 洛谷
- [ ] [【模板】快速幂](https://www.luogu.com.cn/problem/P1226) · 洛谷
- [ ] [【模板】模意义下的乘法逆元](https://www.luogu.com.cn/problem/P3811) · 洛谷
- [ ] [【NOIP 2012 提高组】 同余方程](https://www.luogu.com.cn/problem/P1082) · 洛谷
- [ ] [【模板】裴蜀定理](https://www.luogu.com.cn/problem/P4549) · 洛谷
- [ ] [【模板】中国剩余定理（CRT）/ 曹冲养猪](https://www.luogu.com.cn/problem/P1495) · 洛谷

## 八、下一步

1. 数论的下一步是 [13 组合计数与博弈论](<13 组合计数与博弈论.md>)：阶乘预处理、组合数取模全靠这里的逆元与快速幂。
2. 本篇没写 BSGS、Miller-Rabin、Pollard-Rho。遇到「$10^{18}$ 判素数」「$10^{18}$ 分解」再补，它们都是快速幂与 gcd 的直接延伸。
3. 自测：手算 $1..30$ 的欧拉函数再和线性筛对；随机取 $a,m$ 解 $ax\equiv1$，用乘法验回去。
4. 《小凯的疑惑》已经 AC，但 $ab-a-b$ 的证明值得自己推一遍，那才是裴蜀定理真正的用法。
