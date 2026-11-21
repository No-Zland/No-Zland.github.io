#include <cstdio>

// 贪心：铜牌除了合成银牌没有别的用途，银牌除了合成金牌也没有别的用途，
// 所以每一轮都把能换的铜牌全部换成银牌，再把能换的银牌全部换成金牌。
// 合成金牌会返还 1 个铜牌，返还的铜牌进入下一轮继续参与合成。
// 每轮铜牌数会变成 c % x + 新增金牌数，规模至少缩小到 1/(x*y) 量级，
// 因此循环轮数是 O(log c) 级别，不会超时。
int main() {
    long long a, b, c, x, y;
    if (scanf("%lld %lld %lld %lld %lld", &a, &b, &c, &x, &y) != 5) return 0;

    while (true) {
        long long s = c / x;   // 本轮铜牌能合成的银牌
        b += s;
        c %= x;
        long long g = b / y;   // 本轮银牌能合成的金牌
        if (g == 0) break;
        b %= y;
        a += g;
        c += g;                // 每合成 1 个金牌返还 1 个铜牌
    }
    printf("%lld\n", a);
    return 0;
}
