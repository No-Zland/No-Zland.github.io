#include <iostream>
using namespace std;

int main() {
    int T;
    if (!(cin >> T)) return 0;
    while (T--) {
        long long N, K;
        cin >> N >> K;
        // K 只有 1 或 2，N <= 1e9，N^2 <= 1e18 用 long long 装得下
        long long x = 1;
        for (int i = 0; i < K; ++i) x *= N;
        // 反复求数位和，直到只剩一位
        while (x >= 10) {
            long long y = 0;
            while (x > 0) { y += x % 10; x /= 10; }
            x = y;
        }
        cout << x << "\n";
    }
    return 0;
}
