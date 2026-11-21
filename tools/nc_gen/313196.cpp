#include <cstdio>
using namespace std;
typedef long long ll;

// 倍数：5 的倍数末位只能是 0 或 5，所以只要十进制里出现过 0 或 5，
// 就把它挪到最后一位（其余高位不会出现前导零问题，因为 n >= 1 至少有一个非零位）。
int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll n;
        scanf("%lld", &n);
        bool ok = false;
        while (n > 0) {
            int d = (int)(n % 10);
            if (d == 0 || d == 5) { ok = true; break; }
            n /= 10;
        }
        printf("%s\n", ok ? "YES" : "NO");
    }
    return 0;
}
