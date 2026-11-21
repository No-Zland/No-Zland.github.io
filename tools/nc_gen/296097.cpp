// NC296097 外卖券
// 八折券实付 4x/5，无门槛 5 元券实付 x-5，
// 比较 4x/5 与 x-5 等价于比较 4x 与 5x-25，即比较 x 与 25。
#include <cstdio>

int main() {
    long long x;
    if (scanf("%lld", &x) != 1) return 0;
    // 两边同乘 5 做整数比较，避开浮点误差
    long long payDiscount = 4 * x;        // 八折：0.8x = 4x/5
    long long payCoupon = 5 * (x - 5);    // 5 元券：x-5
    if (payDiscount < payCoupon)
        printf("8\n");
    else if (payDiscount > payCoupon)
        printf("5\n");
    else
        printf("0\n");
    return 0;
}
