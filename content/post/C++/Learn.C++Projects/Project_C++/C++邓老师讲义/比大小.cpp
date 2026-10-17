#include <bits/stdc++.h>
using namespace std;

int CompareAndSum( int &a, int &b){
    int maxnum = max( a ,b);
    a = maxnum;
    int minnum = min( a, b);
    b = minnum;
    return a + b;
}

int main(){
    int a, b;
    cin >> a >> b;
    CompareAndSum( a, b);
    cout << a << " " << b << " " <<CompareAndSum( a, b);
}