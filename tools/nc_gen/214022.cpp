#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdio>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<double> a(n);
    for (int i = 0; i < n; ++i) cin >> a[i];
    sort(a.begin(), a.end());

    double mid;
    if (n % 2 == 1) mid = a[n / 2];
    else mid = (a[n / 2 - 1] + a[n / 2]) / 2.0;

    long long r = llround(mid);
    if (fabs(mid - (double)r) < 1e-9) printf("%lld\n", r);  // 整数直接输出
    else printf("%.2f\n", mid);                             // 小数保留两位
    return 0;
}
