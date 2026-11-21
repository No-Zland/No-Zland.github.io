#include <cstdio>
using namespace std;
typedef long long ll;

// 对和：floor((a+b)/2) = (a+b)/2 - [a,b 奇偶不同]/2。
// 求和项里每个 a_i 出现 (n-1) 次，得到 H = ((n-1)*S - P)/2，P 是异奇偶的对数。
int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n;
        scanf("%d", &n);
        ll s = 0, odd = 0;
        for (int i = 0; i < n; i++) {
            ll x;
            scanf("%lld", &x);
            s += x;
            if (x & 1) odd++;
        }
        ll p = odd * (n - odd); // 异奇偶对
        printf("%lld\n", ((ll)(n - 1) * s - p) / 2);
    }
    return 0;
}
