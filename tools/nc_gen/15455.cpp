#include <cstdio>

// 三位水仙花数：各位立方和等于自身，枚举 [m,n] 内所有数判断。
int main() {
    int m, n;
    if (scanf("%d %d", &m, &n) != 2) return 0;
    for (int x = m; x <= n; ++x) {
        if (x < 100 || x > 999) continue;
        int a = x / 100, b = x / 10 % 10, c = x % 10;
        if (a * a * a + b * b * b + c * c * c == x) printf("%d\n", x);
    }
    return 0;
}
