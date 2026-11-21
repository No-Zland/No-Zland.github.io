#include <iostream>
using namespace std;

int main() {
    int l, r;
    if (!(cin >> l >> r)) return 0;
    // 奇数下标恒为 1，偶数下标恒为 0，整个数组只有 1 和 0 两个值
    // 区间长度 1 时只出现一种下标奇偶性；长度 >= 2 时必同时含奇、偶下标
    cout << (l == r ? 1 : 2) << "\n";
    return 0;
}
