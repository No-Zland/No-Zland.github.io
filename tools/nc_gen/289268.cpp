// NC289268 冒险猫猫参上！！
// 题意：构造 n 个正整数 a[1..n]，满足 |a[i]-a[i+1]|=1，且总石子数 sum a[i] <= 3n（可不全用完）。
// 做法：按周期 6 循环取值 1 2 3 4 3 2（爬坡再下坡），每 6 个格子的和为 15 < 18 = 3*6，
//       任意前缀和都不超过 3*格子数；相邻差恒为 1，且都 >= 1，满足全部约束。
#include <cstdio>

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    const int cyc[6] = {1, 2, 3, 4, 3, 2};
    while (T--) {
        int n;
        scanf("%d", &n);
        for (int i = 0; i < n; ++i) {
            printf("%d", cyc[i % 6]);
            putchar(i + 1 < n ? ' ' : '\n');
        }
    }
    return 0;
}
