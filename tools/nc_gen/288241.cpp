// NC288241 数数入门
// 题意：n 层三角塔，第 i 层有 i 个数。平衡要求每个 a[i][j] <= a[i+1][j] 且 <= a[i+1][j+1]。
// 做法：逐层读入，读第 i 层时用上一层（i-1 个数）校验所有支撑关系，任一处不满足即标记 No。
#include <cstdio>

const int MAXN = 1005;
int prevRow[MAXN], curRow[MAXN];

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n;
        scanf("%d", &n);
        bool ok = true;
        for (int i = 1; i <= n; ++i) {
            for (int j = 1; j <= i; ++j) scanf("%d", &curRow[j]);
            // 上一层第 j 块必须被本层的 j、j+1 两块托住，且都不小于它
            if (i > 1) {
                for (int j = 1; j <= i - 1; ++j) {
                    if (prevRow[j] > curRow[j] || prevRow[j] > curRow[j + 1]) ok = false;
                }
            }
            for (int j = 1; j <= i; ++j) prevRow[j] = curRow[j];
        }
        printf(ok ? "Yes\n" : "No\n");
    }
    return 0;
}
