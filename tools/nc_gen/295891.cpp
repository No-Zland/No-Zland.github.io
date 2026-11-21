#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    if (!(cin >> n)) return 0;
    vector<long long> a(n + 1);
    for (int i = 1; i <= n; i++) cin >> a[i];

    int q;
    cin >> q;
    while (q--) {
        int l, r;
        cin >> l >> r;
        // 要求 b 的前缀和恰好是 a[l..r]：b_1 = a_l，b_i = a_i - a_{i-1}
        for (int i = l; i <= r; i++) {
            long long val = (i == l) ? a[l] : a[i] - a[i - 1];
            cout << val << (i == r ? '\n' : ' ');
        }
    }
    return 0;
}
