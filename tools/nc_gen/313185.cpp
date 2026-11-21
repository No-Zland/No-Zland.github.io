#include <cstdio>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n, m;
        scanf("%d %d", &n, &m);
        vector<string> s(n);
        for (int i = 0; i < n; i++) {
            static char buf[2005];
            scanf("%s", buf);
            s[i] = buf;
        }
        vector<int> c(m, 0);                    // 每一列 1 的个数
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
                if (s[i][j] == '1') c[j]++;

        for (int i = 0; i < n; i++) {
            long long base = 0;
            for (int j = 0; j < m; j++)        // 原串的邻居距离
                base += (s[i][j] == '1') ? (n - c[j]) : c[j];
            // 翻转第 j 位的增量 delta_j：
            // s=1: 该位贡献 n-c_j 变成 c_j-1   -> 2c_j-n-1
            // s=0: 该位贡献 c_j   变成 n-c_j-1 -> n-2c_j-1
            long long best = 0, cur = 0;        // 允许不操作（空区间）
            for (int j = 0; j < m; j++) {
                long long d = (s[i][j] == '1') ? (2LL * c[j] - n - 1)
                                               : (n - 2LL * c[j] - 1);
                cur = min(d, cur + d);          // 最小子段和（Kadane）
                best = min(best, cur);
            }
            printf("%lld\n", base + best);
        }
    }
    return 0;
}
