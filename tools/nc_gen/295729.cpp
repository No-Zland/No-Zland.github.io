// NC295729 黄
// 相邻不互质的位置对构成路径上的"坏边"。改一个数可以同时消掉它左右两条坏边，
// 而且改成大于 1e18 的质数后不与任何相邻数冲突。
// 于是答案 = 坏边组成的路径图的最小点覆盖，按链从左到右贪心即可。
#include <cstdio>
#include <vector>
#include <numeric>

typedef unsigned long long ull;

static const int BUFSZ = 1 << 24;
static char ibuf[BUFSZ];
static int ilen = 0, ipos = 0;

static inline int gc() {
    if (ipos == ilen) {
        ilen = (int)fread(ibuf, 1, BUFSZ, stdin);
        ipos = 0;
        if (ilen <= 0) return -1;
    }
    return ibuf[ipos++];
}

static inline ull readU() {
    int c = gc();
    while (c != -1 && (c < '0' || c > '9')) c = gc();
    ull x = 0;
    while (c >= '0' && c <= '9') {
        x = x * 10 + (ull)(c - '0');
        c = gc();
    }
    return x;
}

int main() {
    int T = (int)readU();
    std::vector<ull> a;
    while (T--) {
        int n = (int)readU();
        a.resize(n);
        for (int i = 0; i < n; ++i) a[i] = readU();
        long long ans = 0;
        bool chosen = false;   // 上一个位置是否已被"改过"
        for (int i = 0; i + 1 < n; ++i) {
            if (!chosen && std::gcd(a[i], a[i + 1]) > 1) {
                ++ans;         // 贪心：改右端点 i+1，顺带覆盖下一条边
                chosen = true;
            } else {
                chosen = false;
            }
        }
        printf("%lld\n", ans);
    }
    return 0;
}
