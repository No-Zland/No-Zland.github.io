#include <cstdio>

// 枚举四种运算，判断是否恰好有一种结果等于 C。
// 注意除法要求 A % B == 0，且 B 至少为 1，不会出现除零。
int main() {
    long long A, B, C;
    if (scanf("%lld %lld %lld", &A, &B, &C) != 3) return 0;
    bool ok = (A + B == C) || (A - B == C) || (A * B == C) ||
              (A % B == 0 && A / B == C);
    printf("%s\n", ok ? "YES" : "NO");
    return 0;
}
