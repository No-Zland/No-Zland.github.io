// NC305093 ICPC Penalty
// 题目：n 次提交，最后一次在 t 分钟，最终状态 Accepted / Rejected，求本题罚时。
// 结论：Accepted => t + (n-1)*20；Rejected => 0。
#include <iostream>
#include <string>

using namespace std;

int main() {
    string s;
    long long n, t;
    cin >> s;
    cin >> n >> t;
    if (s == "Accepted")
        cout << t + (n - 1) * 20 << '\n';
    else
        cout << 0 << '\n';
    return 0;
}
