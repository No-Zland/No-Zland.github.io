#include <cstdio>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    static char s[105];
    scanf("%s", s);
    int low[26] = {0}, up[26] = {0};
    for (int i = 0; i < n; i++) {
        if (s[i] >= 'a' && s[i] <= 'z') low[s[i] - 'a'] = 1;
        else up[s[i] - 'A'] = 1;
    }
    bool ok = true;
    for (int i = 0; i < 26; i++)
        if (low[i] != up[i]) ok = false;
    puts(ok ? "YES" : "NO");
    return 0;
}
