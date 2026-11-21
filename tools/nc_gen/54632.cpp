// 公交换乘：地铁产生优惠票（有效期 45 分钟、可抵不超过地铁票价的公交），
// 公交能用票一定用，且优先用最早获得的那张。
#include <cstdio>
#include <vector>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;

    long long total = 0;
    std::vector<int> ct, cp;      // 优惠票的产生时间、可抵票价
    std::vector<char> used;
    size_t head = 0;              // 已永久失效（过期或已用）的票的前缀

    for (int i = 0; i < n; ++i) {
        int type, t;
        long long price;
        scanf("%d %lld %d", &type, &price, &t);
        if (type == 0) {          // 地铁：付费并得到一张票
            total += price;
            ct.push_back(t);
            cp.push_back((int)price);
            used.push_back(0);
        } else {                  // 公交：在 45 分钟窗口内找最早可用的票
            while (head < ct.size() && (used[head] || t - ct[head] > 45)) ++head;
            int pick = -1;
            for (size_t j = head; j < ct.size(); ++j) {
                if (used[j] || t - ct[j] > 45) continue;
                if (cp[j] >= price) { pick = (int)j; break; }
            }
            if (pick >= 0) used[pick] = 1;
            else total += price;
        }
    }
    printf("%lld\n", total);
    return 0;
}
