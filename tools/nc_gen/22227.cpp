#include <iostream>
using namespace std;

int main() {
    int n, k, m;
    if (!(cin >> n >> k >> m)) return 0;
    // 以「起点为 0 号」的标准约瑟夫问题求解
    int f = 0;  // f(1) = 0
    for (int i = 2; i <= n; ++i) f = (f + m) % i;
    // 把编号平移回真实的起点 k
    cout << (f + k) % n << "\n";
    return 0;
}
