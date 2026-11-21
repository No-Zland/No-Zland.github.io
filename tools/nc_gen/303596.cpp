#include <cstdio>
#include <string>
#include <algorithm>
using namespace std;
typedef long long ll;
typedef __int128 i128;

// 小苯的GCD疑问2.0
// 固定最终 gcd = g，能选的最优集合就是 [1,n] 中 g 的全部倍数（含 g 本身，gcd 恰为 g），
// 此时 m = floor(n/g) 个倍数，SUM = g*m(m+1)/2，值 = g^2*m(m+1)/2。
// 需要 m >= k，即 g <= n/k。同一段 m 相同的 g 里取最大的 g。
int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll n, k;
        scanf("%lld %lld", &n, &k);
        ll maxg = n / k;
        i128 best = 0;
        ll g = 1;
        while (g <= maxg) {
            ll m = n / g;
            ll hi = n / m;          // 这一段 floor(n/x) 相同的最右端点
            if (hi > maxg) hi = maxg;
            ll mm = n / hi;         // 应与 m 相同
            i128 val = (i128)hi * mm * (i128)hi * (mm + 1) / 2;
            if (val > best) best = val;
            g = hi + 1;
        }
        if (best == 0) {
            printf("0\n");
        } else {
            string s;
            while (best > 0) {
                s.push_back('0' + (int)(best % 10));
                best /= 10;
            }
            reverse(s.begin(), s.end());
            printf("%s\n", s.c_str());
        }
    }
    return 0;
}
