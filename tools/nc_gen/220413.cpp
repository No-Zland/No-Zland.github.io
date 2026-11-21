#include <cstdio>

// 及格率/优秀率：百分号前四舍五入（.5 进位），用整数运算避免浮点误差。
// round(100*cnt/n) = floor((200*cnt+n)/(2n))
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    int pass = 0, good = 0;
    for (int i = 0; i < n; ++i) {
        int s;
        if (scanf("%d", &s) != 1) return 0;
        if (s >= 60) ++pass;
        if (s >= 85) ++good;
    }
    printf("%d%%\n", (int)((2LL * 100 * pass + n) / (2LL * n)));
    printf("%d%%\n", (int)((2LL * 100 * good + n) / (2LL * n)));
    return 0;
}
