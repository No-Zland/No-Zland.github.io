//A-数组数组 

#include <bits/stdc++.h>//万能头文件 
using namespace std;//预编译指令 
#define all(x) (x).begin(),(x).end()//
int main()
{
    ios::sync_with_stdio(0); cin.tie(0);
    cout << fixed << setprecision(15);
    int T; cin >> T;
    while (T--)
    {
        int n, m, i, j;
        cin >> n;
        vector<int> a(n);
        for (int &x : a) cin >> x, x = x == -1;
        if (count(all(a), 1) > 1 || reduce(all(a), 0) % 2 == 0) cout << "Alice\n";
        else
        {
            int x = find(all(a), 1) - a.begin();
            if (n % 2 == 1 && x == n / 2) cout << "Bob\n";
            else cout << "Alice\n";
 
        }
    }
}
