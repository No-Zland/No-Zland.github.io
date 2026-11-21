#include <cstdio>
#include <cstdlib>
#include <algorithm>
using namespace std;

int main() {
    int n, k;
    if (scanf("%d %d", &n, &k) != 2) return 0;
    char buf[100005];
    scanf("%s", buf);
    long long ans = 0;
    // 相邻对 (i,i+1) 被多少长度为 k 的窗口覆盖
    for (int i = 0; i + 1 < n; i++) {
        long long d = llabs((long long)buf[i + 1] - (long long)buf[i]);
        long long lo = max(0, i - k + 2);   // 窗口起点 st 满足 st+k-1 >= i+1
        long long hi = min(i, n - k);       // 且 st <= i
        if (hi >= lo) ans += d * (hi - lo + 1);
    }
    printf("%lld\n", ans);
    return 0;
}
