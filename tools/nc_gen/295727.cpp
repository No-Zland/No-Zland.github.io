// NC295727 红橙
// 0 水、1 火、2 冰；水克火、火克冰、冰克水，
// 即小红赢当且仅当 y = (x+1) mod 3。
#include <cstdio>

int main() {
    int x, y;
    if (scanf("%d %d", &x, &y) != 2) return 0;
    if (x == y)
        printf("Draw\n");
    else if ((x + 1) % 3 == y)   // 水(0)->火(1)、火(1)->冰(2)、冰(2)->水(0)
        printf("Hongwins\n");
    else
        printf("chengwins\n");
    return 0;
}
