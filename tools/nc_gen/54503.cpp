#include <cstdio>

// 定闹钟：总分钟数对 1440 取模，再拆回时和分，均补足两位。
int main() {
    long long h, m, k;
    while (scanf("%lld:%lld %lld", &h, &m, &k) == 3) {
        long long t = ((h * 60 + m + k) % 1440 + 1440) % 1440;
        printf("%02lld:%02lld\n", t / 60, t % 60);
    }
    return 0;
}
