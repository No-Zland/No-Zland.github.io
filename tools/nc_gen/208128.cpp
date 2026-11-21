#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cctype>
using namespace std;

// 用 128 位兜底：二进制串可能比 long long 长
static string i128_to_string(__int128 x) {
    if (x == 0) return "0";
    bool neg = x < 0;
    unsigned __int128 u = neg ? (unsigned __int128)(-(x + 1)) + 1 : (unsigned __int128)x;
    string s;
    while (u) { s.push_back(char('0' + (int)(u % 10))); u /= 10; }
    if (neg) s.push_back('-');
    reverse(s.begin(), s.end());
    return s;
}

int main() {
    string all, line;
    while (getline(cin, line)) { all += line; all += '\n'; }

    string s;
    long long k = 0;

    size_t q1 = all.find('"');
    size_t q2 = (q1 == string::npos) ? string::npos : all.find('"', q1 + 1);

    if (q1 != string::npos && q2 != string::npos) {
        // 输入形如 "10110",2
        s = all.substr(q1 + 1, q2 - q1 - 1);
        size_t i = q2 + 1;
        while (i < all.size() && !isdigit((unsigned char)all[i])) i++;
        long long v = 0;
        while (i < all.size() && isdigit((unsigned char)all[i])) { v = v * 10 + (all[i] - '0'); i++; }
        k = v;
    } else {
        // 没有引号的退化情况：第一个数字串当二进制串，第二个当 k
        vector<string> tok;
        string cur;
        for (size_t i = 0; i < all.size(); i++) {
            char ch = all[i];
            if (isdigit((unsigned char)ch)) cur.push_back(ch);
            else { if (!cur.empty()) { tok.push_back(cur); cur.clear(); } }
        }
        if (!cur.empty()) tok.push_back(cur);
        if (tok.empty()) return 0;
        s = tok[0];
        if (tok.size() > 1) k = stoll(tok[1]);
    }

    if (s.empty()) { cout << 0 << "\n"; return 0; }

    int n = (int)s.size();
    k %= n;  // 右移超过一圈等价于取模
    string rot = s.substr(n - (int)k) + s.substr(0, n - (int)k);

    __int128 val = 0;
    for (size_t i = 0; i < rot.size(); i++) val = val * 2 + (rot[i] - '0');
    cout << i128_to_string(val) << "\n";
    return 0;
}
