#include <cstdio>
#include <algorithm>
#include <vector>

// 排序后相同的数聚在一起，扫一遍输出「数值 次数」。
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    std::vector<long long> a(n);
    for (int i = 0; i < n; ++i) scanf("%lld", &a[i]);
    std::sort(a.begin(), a.end());
    for (int i = 0; i < n;) {
        int j = i;
        while (j < n && a[j] == a[i]) ++j;
        printf("%lld %d\n", a[i], j - i);
        i = j;
    }
    return 0;
}
