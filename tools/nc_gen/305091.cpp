// NC305091 小苯的无限数组
// 题目：a = {1,2,3,...}，每次删掉奇数下标元素、剩下的左移，问 k 次操作后 a_n。
// 结论：每操作一次等价于把所有值乘 2（保留下标 2,4,6,... 即原值 2,4,6,...），
//       所以 a_n = n * 2^k。
#include <cstdio>

using namespace std;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        long long n, k;
        scanf("%lld %lld", &n, &k);
        long long ans = n;
        for (long long i = 0; i < k; ++i) ans <<= 1;
        printf("%lld\n", ans);
    }
    return 0;
}
