#include <cstdio>

// 题面给出 rated 的边界：rating 不超过 1599 即 rated。
// 取等号也算，所以判断 x <= 1599。
int main() {
    int x;
    if (scanf("%d", &x) != 1) return 0;
    printf("%s\n", x <= 1599 ? "Rated" : "Unrated");
    return 0;
}
