#include <cstdio>

// 小紫每次可以拿任意个，所以只要轮到她且还有石子，
// 她就能一次拿光、让小红面对空堆而输。
// 因此小红想赢，只能在自己第一个回合就把 n 个石子全部拿完，
// 也就是 n <= 2（一次拿 1 或 2 个）。n >= 3 时小紫必胜。
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    printf("%s\n", n <= 2 ? "red" : "purple");
    return 0;
}
