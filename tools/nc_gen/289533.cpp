#include <cstdio>
#include <algorithm>
using namespace std;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        long long x, y, n;
        scanf("%lld %lld %lld", &x, &y, &n);
        // 由 2x <= y 可证只有 floor(z/x)=floor(z/y)=0 时才可能相等
        long long ans = min(n, x - 1);
        printf("%lld\n", ans);
    }
    return 0;
}
