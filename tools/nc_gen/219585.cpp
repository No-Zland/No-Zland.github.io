#include <iostream>
#include <string>
using namespace std;

const long long MOD = 998244353;

int main() {
    // 读成字符串：题面没给 d 的范围，按任意长度的非负整数处理
    string s;
    if (!(cin >> s)) return 0;
    long long dm = 0;
    for (char c : s) {
        if (c < '0' || c > '9') continue;
        dm = (dm * 10 + (c - '0')) % MOD;
    }
    const long long INV2 = (MOD + 1) / 2;  // 2 在 mod 998244353 下的逆元
    long long a = (dm + 1) % MOD;
    long long b = (dm + 2) % MOD;
    long long ans = a * b % MOD * INV2 % MOD;  // C(d+2, 2) = (d+1)(d+2)/2
    cout << ans << "\n";
    return 0;
}
