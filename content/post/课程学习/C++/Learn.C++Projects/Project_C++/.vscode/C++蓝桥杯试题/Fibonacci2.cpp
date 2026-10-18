#include <bits/stdc++.h>
using namespace std;
using ll = long long;

ll Fibonacci(ll n){
    ll f;
    if(n == 0){
        return 0;
    }
    else if(n == 1){
        return 1;
    }
    else {
        f = Fibonacci(n - 1) + Fibonacci(n - 2);
        return f;
    }
}

ll SumFibonacci(ll n){
    ll sum = 0;
    while(n){
        sum += Fibonacci(n --);
    }
    return sum;
}

int main(){
    ll n;
    cin >> n;
    cout << SumFibonacci(n);
    return 0;
}