// 斐波那契：f(1)=f(2)=1，f(i)=f(i-1)+f(i-2)，顺推即可。
// k ≤ 50，f(50)=12586269025 超过 32 位，所以用 long long。
#include <cstdio>

int main() {
    int k;
    if (scanf("%d", &k) != 1) return 0;
    if (k <= 2) { puts("1"); return 0; }
    long long a = 1, b = 1;
    for (int i = 3; i <= k; ++i) {
        long long c = a + b;
        a = b;
        b = c;
    }
    printf("%lld\n", b);
    return 0;
}
