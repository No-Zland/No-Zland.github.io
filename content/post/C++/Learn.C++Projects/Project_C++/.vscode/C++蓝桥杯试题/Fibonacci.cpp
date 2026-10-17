#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int Fibonacci(ll n){
    if(n == 0){
        return 0;
    }
    else if(n <= 2){
        return 1;
    }
    else if(n > 2){
        ll num[2] = {1, 1};
        while(n -- > 1){
            num[1] += num[0];
            num[0] = num[1] - num[0];
        }
        return num[1];
    }
}

int main(){
    ll n;
    cin >> n;
    Fibonacci(n);
}