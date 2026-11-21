#include <iostream>
#include <string>
using namespace std;

int main() {
    string s;
    if (!(cin >> s)) return 0;
    string target = "Yes";
    bool ok = (s.size() == 3);
    if (ok) {
        for (int i = 0; i < 3; ++i) {
            char a = s[i], b = target[i];
            if (a >= 'a' && a <= 'z') a = char(a - 'a' + 'A');
            if (b >= 'a' && b <= 'z') b = char(b - 'a' + 'A');
            if (a != b) { ok = false; break; }
        }
    }
    cout << (ok ? "accept" : "wrong answer") << "\n";
    return 0;
}
