// NC288220 麻将入门
// 题意：给定 1..9 的三张牌 a<=b<=c，判断是否构成刻子（三张相同）或顺子（连续三张）。
// 做法：两个条件各自判定一次，命中任一即输出 Yes，否则 No。
#include <cstdio>

int main() {
    int a, b, c;
    if (scanf("%d%d%d", &a, &b, &c) != 3) return 0;
    bool kezi = (a == b && b == c);              // 刻子
    bool shunzi = (b == a + 1 && c == b + 1);    // 顺子
    if (kezi || shunzi) printf("Yes\n");
    else printf("No\n");
    return 0;
}
