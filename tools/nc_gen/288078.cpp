// NC288078 数组数组
// 题意：数组元素为 ±1，每步删除一个乘积恰为 1 的非空连续子数组（即含偶数个 -1），
//       删完后左右拼接，不能操作者败，问先手 Alice 是否必胜。
// 结论（枚举 SG 验证过 n<=20 的全部数组，见复盘）：
//       先手必败 <=> 数组中恰好只有一个 -1，且它左右两侧的 +1 个数相等。
// 其余情况先手必胜：-1 个数为偶数可一次删光；-1 个数为 0 时全是 +1（SG=n）；
//       -1 个数为奇数且 >=3 时，删掉中间 k-1 个 -1 并微调两侧 +1 的个数就能走到必败态。
#include <cstdio>

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n;
        scanf("%d", &n);
        int neg = 0, first = -1;
        for (int i = 0; i < n; ++i) {
            int x;
            scanf("%d", &x);
            if (x == -1) {
                ++neg;
                if (first < 0) first = i;
            }
        }
        bool bob = false;
        if (neg == 1) {
            int left = first;           // 左侧 +1 的个数
            int right = n - 1 - first;  // 右侧 +1 的个数
            if (left == right) bob = true;
        }
        printf(bob ? "Bob\n" : "Alice\n");
    }
    return 0;
}
