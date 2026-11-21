// NC289264 和猫猫一起起舞！
// 题意：魔法从 U/D/L/R 某个方向射来，输出一个与它垂直的方向。
// 做法：上下方向来袭就向左右躲（统一输出 R），左右方向来袭就向上下躲（统一输出 D）。
#include <cstdio>

int main() {
    char c;
    if (scanf(" %c", &c) != 1) return 0;
    char ans;
    if (c == 'U' || c == 'D') ans = 'R';   // 竖直方向 -> 水平躲避
    else ans = 'D';                        // 水平方向 -> 竖直躲避
    printf("%c\n", ans);
    return 0;
}
