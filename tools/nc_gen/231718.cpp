#include <cstdio>
#include <vector>
#include <algorithm>
#include <functional>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    std::vector<long long> a(n);
    for (int i = 0; i < n; i++) scanf("%lld", &a[i]);
    std::sort(a.begin(), a.end(), std::greater<long long>());
    long long sum = 0;
    for (int i = 0; i < n / 2; i++) sum += a[i];
    printf("%lld\n", sum);
    return 0;
}
