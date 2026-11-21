#include <cstdio>

// 构造等差数列的第三项。
// 若把 b 放在中间，则 c = 2b - a，三个数重排后必为 a, b, 2b-a（差为 b-a），
// 或 2b-a, b, a（差为 a-b），一定是等差数列。
// 若 2b-a <= 0（只可能发生在 a 比 b 大很多时），改用 c = 2a - b，
// 此时 c 必为正，且 a 落在中间，同样构成等差数列。
int main() {
    long long a, b;
    if (scanf("%lld %lld", &a, &b) != 2) return 0;
    long long c = 2 * b - a;
    if (c <= 0) c = 2 * a - b;
    printf("%lld\n", c);
    return 0;
}
