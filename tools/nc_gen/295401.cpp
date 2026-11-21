#include <cstdio>
#include <vector>
using namespace std;

// ans = 所有长度 L 的区间、所有排列中，该区间第 (floor(L/2)+1) 小元素的连乘积。
// 同长度的区间对称同分布，共 n-L+1 个，于是
//   ans = prod_{L=1..n} ( prod_{v=1..n} v^{C(v-1,k-1)*C(n-v,L-k)*L!*(n-L)!} )^{n-L+1}
// 其中 k = floor(L/2)+1。指数对 MOD-1 取模（MOD 是素数）；
// 组合数用 Pascal 加法递推算 mod (MOD-1)，全程只用加法。
static const long long MOD = 1610612741LL;
static const long long P2 = MOD - 1;

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    int K = n / 2 + 1;                 // 需要的最大列号
    size_t W = (size_t)K + 1;
    // C[i][j] mod (MOD-1)，一维展开
    vector<unsigned int> C((size_t)(n + 1) * W, 0);
    for (int i = 0; i <= n; i++) {
        C[(size_t)i * W] = 1;
        int up = i < K ? i : K;
        for (int j = 1; j <= up; j++) {
            unsigned long long v = 0;
            if (j <= i - 1) v += C[(size_t)(i - 1) * W + j];
            if (j - 1 <= i - 1) v += C[(size_t)(i - 1) * W + (j - 1)];
            C[(size_t)i * W + j] = (unsigned int)(v % (unsigned long long)P2);
        }
    }
    vector<long long> fact(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; i++) fact[i] = fact[i - 1] * i % P2;

    vector<long long> ex(n + 1, 0);
    for (int L = 1; L <= n; L++) {
        int k = L / 2 + 1;
        int a = k - 1, b = L - k;
        long long mult = fact[L] * fact[n - L] % P2;
        mult = mult * (n - L + 1) % P2;
        for (int v = 1; v <= n; v++) {
            long long A = C[(size_t)(v - 1) * W + a];   // 比 v 小的 v-1 个数中选 a 个进区间
            long long B = C[(size_t)(n - v) * W + b];   // 比 v 大的 n-v 个数中选 b 个进区间
            long long e = A * B % P2 * mult % P2;
            ex[v] += e;
            if (ex[v] >= P2) ex[v] -= P2;
        }
    }
    long long ans = 1;
    for (int v = 1; v <= n; v++) {
        if (!ex[v]) continue;
        long long t = 1, base = v % MOD, e = ex[v];
        while (e) {
            if (e & 1) t = t * base % MOD;
            base = base * base % MOD;
            e >>= 1;
        }
        ans = ans * t % MOD;
    }
    printf("%lld\n", ans);
    return 0;
}
