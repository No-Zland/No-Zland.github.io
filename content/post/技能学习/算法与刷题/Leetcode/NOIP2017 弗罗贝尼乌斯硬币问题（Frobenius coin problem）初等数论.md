![[NOIP2017 小凯的疑惑1.png]]
![[NOIP2017 小凯的疑惑2.png|697]]
```cpp
#include<bits/stdc++.h>
using namespace std;

int main() {
    long long a, b;
    cin >> a >> b;
    // 弗罗贝尼乌斯硬币问题（Frobenius coin problem）直接使用公式：最大不可表示的数 = a * b - a - b
    cout << a * b - a - b << endl;
    return 0;
}
```
根据数论中的弗罗贝尼乌斯硬币问题（Frobenius coin problem），当两个数互质时，所有大于等于 (a−1)(b−1)的整数都可以表示为 a 和 b 的线性组合，而最大的不可表示数正是 ab−a−b