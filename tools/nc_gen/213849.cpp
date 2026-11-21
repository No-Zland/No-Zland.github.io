// 优秀的拆分：拆成若干个互不相同的 2 的正整数次幂。
// 2 的正整数次幂都是偶数，故奇数无解；偶数按二进制位从高到低输出即可（2^0 位天然为 0）。
#include <cstdio>

int main() {
    unsigned long long n;
    if (scanf("%llu", &n) != 1) return 0;
    if (n & 1ULL) { puts("-1"); return 0; }

    bool first = true;
    for (int i = 63; i >= 0; --i) {
        if ((n >> i) & 1ULL) {
            if (!first) putchar(' ');
            printf("%llu", (unsigned long long)(1ULL << i));
            first = false;
        }
    }
    putchar('\n');
    return 0;
}
