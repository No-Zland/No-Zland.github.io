// NC304877 小苯的真假游戏
// 题目：n 个人围成一圈，i 声称左边 i-1（特别的 1 的左边是 n）说真话(1)/假话(0)，
//       求使人说的话真假与其声称一致的赋值方案数（每个 2^n 种局面中）。
//
// 记 x_i in {0,1} 为 i 是否说真，s_i 为 i 的声称。
// 若 x_i = 1，则 "左边的人说真" 成立 <=> x_{i-1} = s_i；
// 若 x_i = 0，则该声称是假的 <=> x_{i-1} = 1 - s_i。
// 合起来 x_{i-1} = s_i XOR (1 - x_i)：由 x_i 唯一确定 x_{i-1}。
// 于是只要枚举 x_1 的 2 种取值，绕环倒推一圈回来看是否自洽，方案数只可能是 0/1/2。
#include <cstdio>

using namespace std;
typedef long long ll;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n;
        scanf("%d", &n);
        static char buf[1000005];
        scanf("%s", buf);
        ll cnt = 0;
        for (int start = 0; start < 2; ++start) {
            int cur = start;  // 当前已知的 x_i
            bool ok = true;
            for (int step = 0; step < n; ++step) {
                int i = ((-step) % n + n) % n;  // step 0 -> 0, step 1 -> n-1, ...
                int left = (i - 1 + n) % n;
                int val = (buf[i] - '0') ^ (1 - cur);
                if (step == n - 1) {  // 回到起点，做自洽校验
                    if (val != start) ok = false;
                } else {
                    cur = val;
                }
            }
            if (ok) ++cnt;
        }
        printf("%lld\n", cnt % 998244353LL);
    }
    return 0;
}
