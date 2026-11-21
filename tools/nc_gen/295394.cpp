#include <cstdio>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    int lt = 0, eq = 0, gt = 0;
    for (int i = 0; i < n; i++) {
        int x;
        scanf("%d", &x);
        if (x < 0) lt++;
        else if (x == 0) eq++;
        else gt++;
    }
    // 有严格大于也有严格小于 -> 可构造：大的取 mu+1、小的取 mu-1、等于的取 mu
    // 只有单侧偏离（全大于或全小于）-> 平均值必然被拉偏，不可能；全等于 -> 可以
    bool ok;
    if (lt && gt) ok = true;
    else if (lt || gt) ok = false;
    else ok = true;
    puts(ok ? "YES" : "NO");
    return 0;
}
