// NC293975 树到云端
// 题意：树上边权为 1，t_i = sum_j val_j * dis(i,j)，已知整棵树与 t，反求正整数 val。
// 关键关系（换根）：设 W = sum val，边 (p -> v)（p 为父）对应的子树权和为 S_v，则
//   t_v - t_p = (W - S_v) - S_v = W - 2 S_v   =>   S_v = (W - (t_v - t_p)) / 2
// 又因为 sum_{v != root} S_v = sum_x val_x * depth(x) = t_root，于是
//   (n-1) W - sum_{v != root} (t_v - t_p) = 2 t_root  =>  W 唯一确定。
// 得到 W 后可算出所有 S_v，再自上而下作差：val_v = S_v - sum_{child} S_c（根用 W 代替 S_root）。
#include <algorithm>
#include <climits>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
using namespace std;

namespace io {
const int SZ = 1 << 16;
char buf[SZ];
int len = 0, pos = 0;
inline int gc() {
    if (pos == len) {
        len = (int)fread(buf, 1, SZ, stdin);
        pos = 0;
        if (len <= 0) return -1;
    }
    return (unsigned char)buf[pos++];
}
inline long long readInt() {
    int c = gc();
    long long x = 0;
    int sgn = 1;
    while (c != -1 && (c < '0' || c > '9') && c != '-') c = gc();
    if (c == '-') { sgn = -1; c = gc(); }
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x * sgn;
}
} // namespace io

int main() {
    int n = (int)io::readInt();
    size_t E = 2 * (size_t)(n - 1) + 2;
    vector<int> head(n + 1, -1), to(E), nxt(E);
    int ec = 0;
    for (int i = 1; i < n; ++i) {
        int u = (int)io::readInt(), v = (int)io::readInt();
        to[ec] = v; nxt[ec] = head[u]; head[u] = ec++;
        to[ec] = u; nxt[ec] = head[v]; head[v] = ec++;
    }
    vector<long long> t(n + 1);
    for (int i = 1; i <= n; ++i) t[i] = io::readInt();

    // 迭代 BFS 定根为 1，n 可达 6e5，不能递归
    vector<int> par(n + 1, 0), order;
    order.reserve(n);
    order.push_back(1);
    par[1] = 0;
    for (size_t k = 0; k < order.size(); ++k) {
        int u = order[k];
        for (int e = head[u]; e != -1; e = nxt[e]) {
            int v = to[e];
            if (v == par[u]) continue;
            par[v] = u;
            order.push_back(v);
        }
    }

    long long K = 0;                               // sum_{v != root} (t_v - t_par(v))
    for (int i = 1; i < n; ++i) K += t[order[i]] - t[par[order[i]]];
    long long W = (2 * t[1] + K) / (n - 1);        // 总点权和

    vector<long long> S(n + 1, 0), ans(n + 1, 0);
    for (int i = 1; i < n; ++i) {
        int v = order[i];
        S[v] = (W - (t[v] - t[par[v]])) / 2;       // 子树权和
    }
    for (int v = 1; v <= n; ++v) ans[v] = (v == 1 ? W : S[v]);
    for (int i = 1; i < n; ++i) {                  // 减去每个孩子的整棵子树
        int v = order[i];
        ans[par[v]] -= S[v];
    }

    string out;
    out.reserve((size_t)n * 8);
    char tmp[32];
    for (int i = 1; i <= n; ++i) {
        int ln = snprintf(tmp, sizeof(tmp), "%lld", ans[i]);
        if (i > 1) out.push_back(' ');
        out.append(tmp, ln);
    }
    out.push_back('\n');
    fwrite(out.data(), 1, out.size(), stdout);
    return 0;
}
