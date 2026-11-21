#include <cstdio>
#include <vector>
#include <queue>
#include <algorithm>
#include <utility>
using namespace std;

// 小苯的区间选数2.0
// 要给 0,1,2,... 每个值各找一个互不相同的区间覆盖它，
// 贪心：按左端点扫描值 v，候选区间里右端点最小的优先（活动安排式匹配）。
int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n;
        scanf("%d", &n);
        vector<pair<int, int>> seg(n);
        for (int i = 0; i < n; i++) scanf("%d %d", &seg[i].first, &seg[i].second);
        sort(seg.begin(), seg.end());
        priority_queue<int, vector<int>, greater<int>> pq;
        int idx = 0, ans = 0;
        // 最多只能匹配 n 个值：MEX <= n
        for (int v = 0; v < n; v++) {
            while (idx < n && seg[idx].first <= v) {
                pq.push(seg[idx].second);
                idx++;
            }
            while (!pq.empty() && pq.top() < v) pq.pop();
            if (pq.empty()) break;
            pq.pop();
            ans = v + 1;
        }
        printf("%d\n", ans);
    }
    return 0;
}
