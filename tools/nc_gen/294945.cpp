// NC294945 经典校招题
// 题意：从第 0 阶走到第 n 阶，每步可上 1 阶或 2 阶，求最少步数。
// 结论：步数 = ceil(n/2) = (n+1)/2。
//   下界：k 步最多上 2k 阶，2k >= n => k >= ceil(n/2)。
//   构造：floor(n/2) 次 2 阶 + (n mod 2) 次 1 阶，恰好 ceil(n/2) 步。
#include <cstdio>
int main() {
    long long n;
    while (scanf("%lld", &n) == 1) printf("%lld\n", (n + 1) / 2);
    return 0;
}
