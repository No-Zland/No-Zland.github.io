#include <iostream>
#include <vector>
#include <queue>
#include <utility>
#include <climits>
using namespace std;

typedef long long ll;
typedef pair<ll, int> pli;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, M;
    if (!(cin >> N >> M)) return 0;

    vector<vector<pli>> g(N + 1);  // 点编号 0~N
    for (int i = 0; i < M; i++) {
        int u, v;
        ll w;
        if (!(cin >> u >> v >> w)) break;
        if (u < 0 || u > N || v < 0 || v > N) continue;
        g[u].push_back(make_pair(w, v));
    }

    const ll INF = LLONG_MAX;
    vector<ll> dist(N + 1, INF);
    vector<char> done(N + 1, 0);
    priority_queue<pli, vector<pli>, greater<pli>> pq;

    dist[0] = 0;
    pq.push(make_pair(0LL, 0));
    while (!pq.empty()) {
        pli top = pq.top();
        pq.pop();
        ll d = top.first;
        int u = top.second;
        if (done[u]) continue;
        done[u] = 1;
        for (size_t j = 0; j < g[u].size(); j++) {
            ll w = g[u][j].first;
            int v = g[u][j].second;
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.push(make_pair(dist[v], v));
            }
        }
    }

    ll best = -1;
    int bidx = -1;
    for (int i = 1; i <= N; i++) {
        if (dist[i] == INF) continue;  // 不可达的点不考虑
        if (dist[i] > best) { best = dist[i]; bidx = i; }  // 严格大于 => 并列取小编号
    }
    if (bidx != -1) cout << best << " " << bidx << "\n";
    return 0;
}
