#include <cstdio>
using namespace std;

// ICPC Time：比赛从 n 点开始，持续 5 小时，24 小时制取模。
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    printf("%d\n", (n + 5) % 24);
    return 0;
}
