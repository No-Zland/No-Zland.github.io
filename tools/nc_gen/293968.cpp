#include <cstdio>
#include <cstring>
#include <vector>
#include <algorithm>

// 廻文串 = w w' w w'（|w| = k >= 1），长度为 4k。
// 记 A = w w'，则 A 是长度 2k 的偶回文，t = A A。
// 反过来：t 是回文且 t 的前一半 A 是回文 <=> t = A A，A 回文。

static const int MAXN = 500005;
static char s[MAXN];
static int d2[MAXN];   // d2[i]：以 (i-1,i) 之间为偶中心的最长偶回文半径
static int vv[MAXN];   // vv[j] = j + d2[j]
static int n;

// ---------- 偶回文 Manacher ----------
static void manacher() {
    for (int i = 0, l = 0, r = -1; i < n; i++) {
        int k = (i > r) ? 0 : std::min(d2[l + r - i + 1], r - i + 1);
        while (i + k < n && i - k - 1 >= 0 && s[i + k] == s[i - k - 1]) k++;
        d2[i] = k;
        if (i + k - 1 > r) { l = i - k; r = i + k - 1; }
    }
}

// ---------- 线段树：区间内最左的 vv[j] >= 阈值 的位置 ----------
static int seg[4 * MAXN];
static void build(int node, int l, int r) {
    if (l == r) { seg[node] = vv[l]; return; }
    int mid = (l + r) >> 1;
    build(node << 1, l, mid);
    build(node << 1 | 1, mid + 1, r);
    seg[node] = std::max(seg[node << 1], seg[node << 1 | 1]);
}
// 返回 [ql,qr] 中最小的下标 j 满足 vv[j] >= th，没有返回 -1
static int findFirst(int node, int l, int r, int ql, int qr, int th) {
    if (r < ql || l > qr || seg[node] < th) return -1;
    if (l == r) return l;
    int mid = (l + r) >> 1;
    int res = findFirst(node << 1, l, mid, ql, qr, th);
    if (res != -1) return res;
    return findFirst(node << 1 | 1, mid + 1, r, ql, qr, th);
}

// ---------- 树状数组：离线数点 ----------
static int bit[MAXN];
static void bitAdd(int i, int val) {
    for (i++; i <= n; i += i & (-i)) bit[i] += val;
}
static int bitSum(int i) {  // [0..i]
    int r = 0;
    for (i++; i > 0; i -= i & (-i)) r += bit[i];
    return r;
}

int main() {
    if (scanf("%s", s) != 1) return 0;
    n = (int)strlen(s);
    manacher();
    for (int j = 0; j < n; j++) vv[j] = j + d2[j];

    // 计数：对偶中心 c（1..n-1）与半径 2k，
    // 条件 d2[c] >= 2k 且 d2[c-k] >= k，令 j = c-k，则 j in [c-D, c-1] 且 j+d2[j] >= c
    struct Query { int c, L, R; };
    std::vector<Query> qs;
    qs.reserve(n);
    for (int c = 1; c < n; c++) {
        int D = d2[c] / 2;
        if (D > 0) qs.push_back({c, c - D, c - 1});
    }
    std::sort(qs.begin(), qs.end(), [](const Query &a, const Query &b) { return a.c > b.c; });
    std::vector<int> ids(n);
    for (int i = 0; i < n; i++) ids[i] = i;
    std::sort(ids.begin(), ids.end(), [](int a, int b) { return vv[a] > vv[b]; });

    long long cnt = 0;
    int ptr = 0;
    for (size_t qi = 0; qi < qs.size(); qi++) {
        Query &q = qs[qi];
        while (ptr < n && vv[ids[ptr]] >= q.c) { bitAdd(ids[ptr], 1); ptr++; }
        cnt += bitSum(q.R) - bitSum(q.L - 1);
    }

    // 覆盖：对每个中心 c 取最大可行 k，得到区间 [c-2k, c+2k-1]
    build(1, 0, n - 1);
    std::vector<int> best(n + 1, -1);
    for (int c = 1; c < n; c++) {
        int D = d2[c] / 2;
        if (D <= 0) continue;
        int jmin = findFirst(1, 0, n - 1, c - D, c - 1, c);
        if (jmin == -1) continue;
        int k = c - jmin;
        int L = c - 2 * k, R = c + 2 * k - 1;
        if (R > best[L]) best[L] = R;
    }
    for (int p = 0; p < n; p++) if (best[p] < p) best[p] = p;  // 单字符一定可行
    int reach = -1;
    for (int p = 0; p < n; p++) {
        if (best[p] > reach) reach = best[p];
        best[p] = reach;   // best[p] = max{ maxEnd[l] : l <= p }
    }
    int steps = 0, covered = -1;
    while (covered < n - 1) {
        covered = best[covered + 1];
        steps++;
    }

    printf("%lld %d\n", cnt + n, steps);
    return 0;
}
