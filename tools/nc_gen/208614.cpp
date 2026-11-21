#include <cstdio>
#include <cstdlib>

// 打印菱形：共 2n-1 行，第 i 行与中轴的距离 d = |i-(n-1)|，
// 星号个数 = 2*(n-d)-1，缩进 = d；按样例第一行顶格输出。
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < 2 * n - 1; ++i) {
        int d = abs(i - (n - 1));
        int cnt = 2 * (n - d) - 1;
        int lead = (i == 0 ? 0 : d);
        for (int k = 0; k < lead; ++k) putchar(' ');
        for (int k = 0; k < cnt; ++k) putchar('X');
        putchar('\n');
    }
    return 0;
}
