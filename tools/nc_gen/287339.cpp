#include <cstdio>
using namespace std;

int main() {
    long long x, y;
    if (scanf("%lld %lld", &x, &y) != 2) return 0;
    unsigned long long base;
    if (x == 1) base = 10ULL;                 // 10^1
    else if (x == 2) base = 1000000000ULL;    // 10^9
    else base = 1000000000000000000ULL;       // 10^18
    printf("%llu\n", base + (unsigned long long)y);
    return 0;
}
