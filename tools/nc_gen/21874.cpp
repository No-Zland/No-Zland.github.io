#include <cstdio>

// 插入 "ab" 的逆操作是删掉相邻的 "ab"。把 a 看成左括号、b 看成右括号，
// 则 s 是好串 ⇔ s 是合法的括号序列（任意前缀 a 的个数不少于 b 的个数，且总数相等）。
int main() {
    static char s[100005];
    if (scanf("%s", s) != 1) return 0;
    int bal = 0;
    bool ok = true;
    for (int i = 0; s[i]; ++i) {
        if (s[i] == 'a') {
            ++bal;
        } else if (s[i] == 'b') {
            if (--bal < 0) { ok = false; break; }  // 出现了无法匹配的 b
        } else {
            ok = false;  // 混入其它字符，一定不是好串
            break;
        }
    }
    if (bal != 0) ok = false;  // a、b 数量不等
    puts(ok ? "Good" : "Bad");
    return 0;
}
