// NC229915 分糖果（candy）
// 拿 K 颗，奖励 = K mod n，求 K 属于 [L,R] 时 K mod n 的最大值。
// 若 L、R 落在同一个 n 的倍数区间内，余数随 K 单调增，取 R%n；
// 否则区间里必然跨过一个 n 的倍数，可以取到 n-1。
#include <cstdio>

int main() {
    long long n, L, R;
    if (scanf("%lld %lld %lld", &n, &L, &R) != 3) return 0;
    if (L / n != R / n)
        printf("%lld\n", n - 1);
    else
        printf("%lld\n", R % n);
    return 0;
}
