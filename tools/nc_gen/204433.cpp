// NC204433 阶乘
// 题目：给定正整数 p，求最小的正整数 n，使 p | n!
//
// 思路：
//   把 p 质因数分解成 prod qi^ei。n! 能被 p 整除 <=> 对每个 qi 都有 v_{qi}(n!) >= ei。
//   v_q(n!) = n/q + n/q^2 + ... 关于 n 单调不减，所以每个素因子可以各自二分出最小的 n，
//   答案取这些 n 的最大值。
//   p <= 1e18 需要用 Miller-Rabin + Pollard-Rho 分解。
#include <cstdio>
#include <cstdint>
#include <vector>
#include <algorithm>
#include <numeric>

using namespace std;

typedef unsigned long long u64;
typedef __int128 i128;

static u64 mulmod(u64 a, u64 b, u64 m) { return (u64)((i128)a * b % m); }

static u64 powmod(u64 a, u64 d, u64 m) {
    u64 r = 1 % m;
    a %= m;
    while (d) {
        if (d & 1) r = mulmod(r, a, m);
        a = mulmod(a, a, m);
        d >>= 1;
    }
    return r;
}

static bool isPrime(u64 n) {
    if (n < 2) return false;
    static const u64 small[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    for (u64 p : small)
        if (n % p == 0) return n == p;
    u64 d = n - 1;
    int s = 0;
    while (!(d & 1)) { d >>= 1; ++s; }
    for (u64 a : small) {
        u64 x = powmod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        bool composite = true;
        for (int r = 1; r < s; ++r) {
            x = mulmod(x, x, n);
            if (x == n - 1) { composite = false; break; }
        }
        if (composite) return false;
    }
    return true;
}

static u64 pollard(u64 n) {
    if (n % 2 == 0) return 2;
    if (n % 3 == 0) return 3;
    for (u64 c = 1;; ++c) {
        u64 x = 2, y = 2, d = 1;
        auto f = [&](u64 v) { return (u64)(((i128)v * v + c) % n); };
        while (d == 1) {
            x = f(x);
            y = f(f(y));
            u64 diff = x > y ? x - y : y - x;
            d = std::gcd(diff, n);
        }
        if (d != n) return d;
    }
}

static void factor(u64 n, vector<u64> &v) {
    if (n == 1) return;
    if (isPrime(n)) { v.push_back(n); return; }
    u64 d = pollard(n);
    factor(d, v);
    factor(n / d, v);
}

// v_q(n!) = sum_{k>=1} n / q^k
static u64 legendre(u64 n, u64 q) {
    u64 s = 0;
    while (n) { n /= q; s += n; }
    return s;
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        u64 p;
        scanf("%llu", &p);
        if (p == 1) { printf("1\n"); continue; }
        vector<u64> f;
        factor(p, f);
        sort(f.begin(), f.end());
        u64 ans = 1;
        for (size_t i = 0; i < f.size();) {
            size_t j = i;
            while (j < f.size() && f[j] == f[i]) ++j;
            u64 q = f[i], e = (u64)(j - i);
            // 二分最小的 n 使 v_q(n!) >= e，上界 q*e 一定够（v_q((qe)!) >= e）
            u64 lo = 1, hi = q * e;
            while (lo < hi) {
                u64 mid = lo + (hi - lo) / 2;
                if (legendre(mid, q) >= e) hi = mid;
                else lo = mid + 1;
            }
            ans = max(ans, lo);
            i = j;
        }
        printf("%llu\n", ans);
    }
    return 0;
}
