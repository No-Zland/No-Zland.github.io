#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> b(n), c(n);
    for (int i = 0; i < n; i++) cin >> b[i];
    for (int i = 0; i < n; i++) cin >> c[i];

    // 2n 个候选值摊平排序，窗口内要求每个下标至少出现一次
    vector<pair<int, int>> v;
    v.reserve(2 * n);
    for (int i = 0; i < n; i++) {
        v.push_back(make_pair(b[i], i));
        v.push_back(make_pair(c[i], i));
    }
    sort(v.begin(), v.end());

    int m = 2 * n, l = 0, covered = 0, ans = INT_MAX;
    vector<int> cnt(n, 0);
    for (int r = 0; r < m; r++) {
        if (cnt[v[r].second]++ == 0) covered++;
        while (covered == n) {
            ans = min(ans, v[r].first - v[l].first);
            if (--cnt[v[l].second] == 0) covered--;
            l++;
        }
    }
    cout << ans << "\n";
    return 0;
}
