#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    double m, q;
    cin >> n >> m >> q;
    
    double limit = 100 * m * m / (q * q);
    int cap = floor(limit);

    vector<int> u(n);
    vector<int> w(n);
    
    for(int i = 0;i < n; i ++){
        cin >> u[i];
    }
    
    for(int i = 0;i < n; i ++){
        double s;
        cin >> s;
        int k = round(s * 10);
        w[i] = k * k;
    }

    vector<int> dp(cap + 1, 0);
    for(int i = 0; i < n; i ++){
        for(int j = cap; j >= w[i]; j --){
            dp[j] = max(dp[j], dp[j - w[i]] + u[i]);
        }
    }

    int ans = 0;
    for(int i = 0; i <= cap; i ++){
        ans = max(ans, dp[i]);
    }
    cout << ans;

    return 0;
}
