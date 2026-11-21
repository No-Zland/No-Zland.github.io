#include <cstdio>
using namespace std;
int main() {
    long long x;
    if (scanf("%lld", &x) != 1) return 0;
    long long sq = x * x;
    if (x > sq) puts("left");
    else if (x < sq) puts("right");
    else puts("equal");
    return 0;
}
