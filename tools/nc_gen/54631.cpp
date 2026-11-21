#include <cstdio>

// 长度为 8 的 01 串，数其中字符 '1' 的个数。
int main() {
    char s[16];
    if (scanf("%s", s) != 1) return 0;
    int cnt = 0;
    for (int i = 0; i < 8; ++i)
        if (s[i] == '1') ++cnt;
    printf("%d\n", cnt);
    return 0;
}
