#include <cstdio>
using namespace std;

int main() {
    long long a, b, c;
    if (scanf("%lld %lld %lld", &a, &b, &c) != 3) return 0;
    // 陡峭值 = |a-b| + |b-c|，为 0 当且仅当三个数全相等
    puts((a == b && b == c) ? "Yes" : "No");
    return 0;
}
