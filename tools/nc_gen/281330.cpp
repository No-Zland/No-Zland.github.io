#include <iostream>
using namespace std;

int main() {
    long long x;
    if (!(cin >> x)) return 0;
    cout << x << "\n";
    // 按指数 b 从小到大枚举所有 a^b = x（a,b 都是正整数）
    for (long long b = 1;; ++b) {
        // 底数至少为 2；若 2^b 都超过 x，后面更大的 b 更不可能，直接结束
        long long t = 1;
        bool over2 = false;
        for (long long i = 0; i < b; ++i) {
            t *= 2;
            if (t > x) { over2 = true; break; }
        }
        if (over2) break;

        for (long long a = 2;; ++a) {
            long long p = 1;
            bool bigger = false;
            for (long long i = 0; i < b; ++i) {
                if (p > x / a) { bigger = true; break; }  // a^(i+1) 已超过 x
                p *= a;
            }
            if (bigger) break;  // a 再变大只会更大
            if (p == x) { cout << "=" << a << "^" << b << "\n"; break; }
        }
    }
    return 0;
}
