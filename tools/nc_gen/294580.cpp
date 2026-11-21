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
