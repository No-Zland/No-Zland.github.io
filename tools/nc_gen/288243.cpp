#include <cstdio>
#include <cmath>
using namespace std;

// 第 p 个位置（从 1 开始）位于第几层：最小的 i 使 i(i+1)/2 >= p
long long row_of(long long p) {
    long double t = (long double)p;
    long long i = (long long)((sqrtl(8.0L * t + 1.0L) - 1.0L) / 2.0L);
    while (i > 0 && i * (i - 1) / 2 >= p) i--;
    while (i * (i + 1) / 2 < p) i++;
    return i;
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        long long n, l, r;
        scanf("%lld %lld %lld", &n, &l, &r);
        // 翻转区间内部任意一对父子边都会使大盘压小盘 -> No
        // 唯一可能破坏平衡的是「完全落在 [l,r] 内的一条边」，
        // 其最小可能右端点出现在父节点 p = l 上，为 l + row(l)
        long long p = l + row_of(l);
        puts(r < p ? "Yes" : "No");
    }
    return 0;
}
