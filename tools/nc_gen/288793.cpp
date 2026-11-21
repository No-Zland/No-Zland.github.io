// NC288793 夹心饼干
// 题意：给一个长度为 3 的字符串，判定首字母与末字母是否完全相同（区分大小写）。
// 做法：直接比较 s[0] 与 s[2]，相同输出 YES，否则输出 NO。
#include <iostream>
#include <string>

int main() {
    std::string s;
    if (!(std::cin >> s)) return 0;
    if (s.front() == s.back()) {
        std::cout << "YES" << "\n";
    } else {
        std::cout << "NO" << "\n";
    }
    return 0;
}
