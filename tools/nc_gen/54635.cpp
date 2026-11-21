// 格雷码：按「前一半加前缀 0、后一半逆序加前缀 1」的反射构造，
// 编号为 k 的 n 位格雷码正是 g = k ^ (k >> 1)。
#include <cstdio>

int main() {
    int n;
    unsigned long long k;
    if (scanf("%d %llu", &n, &k) != 2) return 0;
    unsigned long long g = k ^ (k >> 1);
    for (int i = n - 1; i >= 0; --i) putchar(((g >> i) & 1ULL) ? '1' : '0');
    putchar('\n');
    return 0;
}
