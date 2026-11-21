#include <cstdio>

// 第 k 个阶段：连续 k 天每天 k 枚。按阶段累加，最后一段不足 k 天时按天补。
int main() {
    long long K;
    if (scanf("%lld", &K) != 1) return 0;
    long long ans = 0, day = 0;
    for (long long k = 1; day < K; ++k) {
        long long take = (K - day < k) ? (K - day) : k;  // 本阶段实际取几天
        ans += take * k;
        day += take;
    }
    printf("%lld\n", ans);
    return 0;
}
