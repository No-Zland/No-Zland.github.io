// NC294819 袋鼠将军的部下选择
// 差异度 d_i = |a_i - k|，要求选恰好 m 个使最大差异度最小。
// 把 d_i 升序排序，答案就是第 m 小的 d_i：取差异度最小的 m 个人最稳。
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    std::vector<long long> d;
    while (T--) {
        int n, m;
        long long k;
        scanf("%d %d %lld", &n, &m, &k);
        d.resize(n);
        for (int i = 0; i < n; ++i) {
            long long a;
            scanf("%lld", &a);
            d[i] = a > k ? a - k : k - a;
        }
        // 只需要第 m 小的元素，nth_element 平均 O(n)
        std::nth_element(d.begin(), d.begin() + (m - 1), d.end());
        printf("%lld\n", d[m - 1]);
    }
    return 0;
}
