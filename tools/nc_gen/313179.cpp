#include <cstdio>
#include <vector>
#include <numeric>
using namespace std;

// 邻合：被修改的位置取值可任意，总能同时和左右邻接，
// 于是问题等价于「选最少的点覆盖所有 gcd=1 的相邻边」，即路径子图的最小点覆盖。
// 从左往右贪心：边坏且左端点没被选，就选右端点。
int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n;
        scanf("%d", &n);
        vector<int> a(n);
        for (int i = 0; i < n; i++) scanf("%d", &a[i]);
        int cnt = 0;
        bool selPrev = false; // 上一个位置是否已被修改
        for (int i = 0; i + 1 < n; i++) {
            bool bad = std::gcd(a[i], a[i + 1]) == 1;
            if (bad && !selPrev) {
                cnt++;
                selPrev = true;
            } else {
                selPrev = false;
            }
        }
        printf("%d\n", cnt);
    }
    return 0;
}
