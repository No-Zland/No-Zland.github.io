#include <cstdio>
#include <vector>
using namespace std;

// 思路：BFS。结点是数值，边是 +k 和镜像（个位非 0 时）。
// 关键边界：镜像不改变位数，+k 只会变大，
// 所以一旦位数超过 digits(b) 就再也回不到 b —— 搜索范围限制在 [1, 10^d)。
int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    vector<int> dist;
    vector<int> q;
    while (T--) {
        long long a, b, k;
        scanf("%lld %lld %lld", &a, &b, &k);
        if (a == b) { puts("0"); continue; }
        int d = 0;
        for (long long t = b; t > 0; t /= 10) d++;
        long long lim = 1;
        for (int i = 0; i < d; i++) lim *= 10;   // 10^d
        if (a >= lim) { puts("-1"); continue; }  // 位数多于 b，只增不减

        dist.assign((size_t)lim, -1);
        q.clear();
        q.reserve(1 << 16);
        dist[(size_t)a] = 0;
        q.push_back((int)a);
        long long ans = -1;
        for (size_t h = 0; h < q.size() && ans < 0; h++) {
            int x = q[h];
            int dd = dist[(size_t)x];
            // 操作一：镜像
            if (x % 10 != 0) {
                long long m = 0;
                for (int y = x; y > 0; y /= 10) m = m * 10 + y % 10;
                if (m < lim && dist[(size_t)m] < 0) {
                    dist[(size_t)m] = dd + 1;
                    if (m == b) { ans = dd + 1; break; }
                    q.push_back((int)m);
                }
            }
            // 操作二：+k
            long long nx = (long long)x + k;
            if (nx < lim && dist[(size_t)nx] < 0) {
                dist[(size_t)nx] = dd + 1;
                if (nx == b) { ans = dd + 1; break; }
                q.push_back((int)nx);
            }
        }
        printf("%lld\n", ans);
    }
    return 0;
}
