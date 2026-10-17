#include <bits/stdc++.h>
using namespace std;

using ll = long long;
using ull = unsigned long long;
using pii = pair<int, int>;
using pll = pair<ll, ll>;
using vi = vector<int>;
using vll = vector<ll>;

const int INF = 0x3f3f3f3f;
const ll LINF = 0x3f3f3f3f3f3f3f3f;
const int MOD = 1e9 + 7;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);
    int n, m, k;
    cin >> n >> m >> k;

    vector<double>u(n);
    vector<double>o(n);
    vector<double>x(k);
    vector<double>y(k);


    double sum_u = 0;
    double sum_o = 0;
    int tem;

    for(size_t i = 0; i < n; i ++){
        cin >> u[i];
        sum_u += u[i];
        if(sum_u > m)tem = i;
    }

    for(size_t i = 0; i < n; i ++){
        cin >> o[i];
        if(i < tem)sum_o = sum_o + o[i] * o[i];
    }

    sum_o = pow(sum_o, 0.5);

    tem = 0;
    for(size_t i = 0; i < k; i ++){
        cin >> x[i];
        if(sum_o > x[i])tem = i;
    }
    
    for(size_t i = 0; i < k; i ++){
        cin >> y[i];
    }
    
    cout << y[tem];

    return 0;
}