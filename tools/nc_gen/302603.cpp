// NC302603 牛可乐打怪
// 题目：攻击力 a，防御力 d 可任意取非负整数；怪物完全复制玩家属性、血量 n、先手。
//       求使"自身受到总伤害最小"且在此前提下"攻击序列最短"的防御力 d。
//
// 记 x = a - d 为每一击的真实伤害，d>=0 => 1 <= x <= a（x=0 永远打不死）。
// 打死怪物需要 k = ceil(n/x) 次玩家出手；怪物先手，玩家第 k 次出手前怪物已出手 k 次
// （回合 1,3,5,...），所以总受伤 D = k*x = ceil(n/x)*x，它是 >= n 的、x 的最小倍数。
// 于是 D 的最小值恒为 n（x=1 必是 n 的约数），代价是出手最多；要在总伤害同为 n 的
// 方案里让攻击序列最短，就要 k 最小，即 x 取"不超过 a 的最大 n 的约数"。
// 答案 d = a - x。
#include <cstdio>
#include <vector>
#include <algorithm>

using namespace std;
typedef long long ll;

int main() {
    ll a, n;
    if (scanf("%lld %lld", &a, &n) != 2) return 0;
    // 枚举 n 的全部约数，取 <= a 的最大者
    vector<ll> divs;
    for (ll i = 1; i * i <= n; ++i) {
        if (n % i == 0) {
            divs.push_back(i);
            if (i != n / i) divs.push_back(n / i);
        }
    }
    ll x = 1;
    for (ll v : divs)
        if (v <= a) x = max(x, v);
    printf("%lld\n", a - x);
    return 0;
}
