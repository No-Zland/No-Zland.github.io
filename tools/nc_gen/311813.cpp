#include <iostream>
#include <string>

using namespace std;

// 比较 s 与 reverse(s)。设 n = |s|，反转串第 i 位就是 s[n-1-i]，
// 因此只需从两端向中间找第一对不相等的字符：
//   s[i] > s[n-1-i]  -> 原串更大，输出 left
//   s[i] < s[n-1-i]  -> 反转串更大，输出 right
// 全部配对相等（回文）时输出 equal。
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    if (!(cin >> s)) return 0;
    int n = (int)s.size();
    for (int i = 0; i < n / 2; ++i) {
        char l = s[i], r = s[n - 1 - i];
        if (l == r) continue;
        cout << (l > r ? "left" : "right") << '\n';
        return 0;
    }
    cout << "equal\n";
    return 0;
}
