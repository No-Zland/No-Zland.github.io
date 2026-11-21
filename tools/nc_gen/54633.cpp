// 纪念品：每天可无限次买卖，且当日回款当日可用。
// 把第 d 天到第 d+1 天看成一次完全背包：买价 p[d][j]，收益 p[d+1][j]-p[d][j]，
// 容量是当前金币数；逐日把金币滚动放大。
#include <cstdio>
#include <vector>

int main() {
    int T, N;
    long long M;
    if (scanf("%d %d %lld", &T, &N, &M) != 3) return 0;

    std::vector<std::vector<long long>> p(T, std::vector<long long>(N));
    for (int i = 0; i < T; ++i)
        for (int j = 0; j < N; ++j) scanf("%lld", &p[i][j]);

    std::vector<long long> dp;
    for (int d = 0; d + 1 < T; ++d) {
        if (M <= 0) break;
        dp.assign((size_t)M + 1, 0);
        for (int j = 0; j < N; ++j) {
            long long cost = p[d][j];
            long long gain = p[d + 1][j] - p[d][j];
            if (gain <= 0 || cost > M) continue;
            for (long long c = cost; c <= M; ++c) {
                long long cand = dp[(size_t)(c - cost)] + gain;
                if (cand > dp[(size_t)c]) dp[(size_t)c] = cand;
            }
        }
        M += dp[(size_t)M];
    }
    printf("%lld\n", M);
    return 0;
}
