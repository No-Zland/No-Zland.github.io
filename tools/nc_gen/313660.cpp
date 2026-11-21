#include <cstdio>
#include <algorithm>
#include <vector>
#include <climits>

// 前缀加一 ⇒ 最终序列必然非增 c1>=c2>=...>=cn，且任意非增序列都可由前缀操作得到
// （对前缀 [1,i] 操作 c_i-c_{i+1} 次），过程中只增不减，故约束只需在终点满足。
// 又因非增，c_j <= c_i <= d_i (i<j)，于是每个位置的实际上界是前缀最小值 m_i。
// 在非增上界 m 下从右往左贪心：c_n=0，c_i=min(m_i, c_{i+1}+1)，能抬就抬一格。
int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n;
        scanf("%d", &n);
        std::vector<long long> m(n);
        long long cur = LLONG_MAX;
        for (int i = 0; i < n; ++i) {
            long long x;
            scanf("%lld", &x);
            cur = std::min(cur, x);
            m[i] = cur;
        }
        long long v = 0;  // 当前右侧已确定的 c 值（从 c_n=0 开始）
        int cnt = 1;      // 值 0 一定出现
        for (int i = n - 2; i >= 0; --i) {
            if (m[i] > v) {  // min(m_i, v+1) = v+1，产生一个新数值
                ++v;
                ++cnt;
            }
            // 否则 m_i == v，只能保持不变（m 非增保证 m_i >= v）
        }
        printf("%d\n", cnt);
    }
    return 0;
}
