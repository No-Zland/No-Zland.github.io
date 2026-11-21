// NC293611 小s的签到题
// 题意：n 道题，每道题给出「通过人数/提交人数」，通过人数最多的题为签到题，
//       并列时输出题号字典序最小的那个。
// 做法：只比较 '/' 前的人数，同时维护「当前最大人数 + 该人数下最小的字母」。
#include <cstdio>
#include <vector>
using namespace std;

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<char> id(n);
    for (int i = 0; i < n; ++i) {
        char buf[8];
        if (scanf("%7s", buf) != 1) return 0;
        id[i] = buf[0];
    }
    long long best = -1;
    char ans = 'Z';
    for (int i = 0; i < n; ++i) {
        char s[64];
        if (scanf("%63s", s) != 1) return 0;
        long long pass = 0;
        for (int k = 0; s[k] && s[k] != '/'; ++k) pass = pass * 10 + (s[k] - '0');
        if (pass > best) {                       // 严格更大才替换
            best = pass;
            ans = id[i];
        } else if (pass == best && id[i] < ans) {
            ans = id[i];                         // 人数相同，取字母更小的
        }
    }
    printf("%c\n", ans);
    return 0;
}
