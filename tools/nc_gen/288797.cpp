#include <cstdio>
#include <vector>
#include <algorithm>
using namespace std;
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<long long> a(n);
    for (auto &v : a) scanf("%lld", &v);
    sort(a.begin(), a.end());
    bool ok = true;
    for (int i = 1; i < n; i++)
        if (a[i] == a[i - 1]) { ok = false; break; }
    puts(ok ? "YES" : "NO");
    return 0;
}
