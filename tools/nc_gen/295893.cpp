#include <iostream>
#include <algorithm>
#include <numeric>
using namespace std;

typedef long long ll;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    ll d, p;
    if (!(cin >> d >> p)) return 0;

    // a_i = (1 + (i-1)*d) mod p
    // 序列最小正周期 T = p / gcd(d, p)，一个周期内 T 个值互不相同。
    // 所以长度 L 的窗口里恰有 min(L, T) 种不同元素。
    ll g = __gcd(d, p);
    ll T = p / g;

    int q;
    cin >> q;
    while (q--) {
        ll l, r;
        cin >> l >> r;
        ll len = r - l + 1;

        if (p == 1) {
            // 边界：a_1 = 1 不在 [0,p) 内，数组是 1,0,0,0,...
            // 于是只有含下标 1 且长度 >= 2 的区间才有两种元素
            ll ans = (l == 1 && r >= 2) ? 2 : 1;
            cout << ans << "\n";
            continue;
        }
        cout << min(len, T) << "\n";
    }
    return 0;
}
