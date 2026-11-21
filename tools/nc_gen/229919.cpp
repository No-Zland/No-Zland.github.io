// NC229919 插入排序（sort）
// 题面给出的插入排序只在 a[j] < a[j-1] 时交换相邻两项，是稳定排序。
// 所以 a_x 排序后的位置 = 1 + 满足 (a_y, y) 字典序小于 (a_x, x) 的 y 的个数。
// 用 pbds 有序集合维护全部 (值, 下标) 二元组，order_of_key 直接给出该计数。
#include <cstdio>
#include <vector>
#include <utility>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

typedef std::pair<long long, int> PII;
typedef __gnu_pbds::tree<PII, __gnu_pbds::null_type, std::less<PII>,
                         __gnu_pbds::rb_tree_tag,
                         __gnu_pbds::tree_order_statistics_node_update> ordered_set;

int main() {
    int n, Q;
    if (scanf("%d %d", &n, &Q) != 2) return 0;
    std::vector<long long> a(n + 1);
    ordered_set st;
    for (int i = 1; i <= n; ++i) {
        scanf("%lld", &a[i]);
        st.insert(PII(a[i], i));
    }
    while (Q--) {
        int op;
        scanf("%d", &op);
        if (op == 1) {
            int x;
            long long v;
            scanf("%d %lld", &x, &v);
            st.erase(PII(a[x], x));
            a[x] = v;
            st.insert(PII(v, x));
        } else {
            int x;
            scanf("%d", &x);
            printf("%d\n", (int)st.order_of_key(PII(a[x], x)) + 1);
        }
    }
    return 0;
}
