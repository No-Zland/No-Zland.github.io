#include <cstdio>
#include <cstdlib>

// 箭形/菱形图案：共 2n+1 行，第 i 行与中轴距离 d = |i-n|，
// 星号数 = n+1-d，缩进 = 2d；按样例第一行顶格输出。
int main() {
    int n;
    while (scanf("%d", &n) == 1) {
        for (int i = 0; i < 2 * n + 1; ++i) {
            int d = abs(i - n);
            int cnt = n + 1 - d;
            int lead = (i == 0 ? 0 : 2 * d);
            for (int k = 0; k < lead; ++k) putchar(' ');
            for (int k = 0; k < cnt; ++k) putchar('*');
            putchar('\n');
        }
    }
    return 0;
}
