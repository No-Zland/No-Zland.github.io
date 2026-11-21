#include <cstdio>

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        long long x;
        scanf("%lld", &x);
        unsigned int u = (unsigned int)(int)x;  // 截断到 32 位，即为补码位模式
        char buf[33];
        for (int b = 31; b >= 0; b--) buf[31 - b] = ((u >> b) & 1u) ? '1' : '0';
        buf[32] = '\0';
        puts(buf);
    }
    return 0;
}
