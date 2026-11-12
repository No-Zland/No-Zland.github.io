#include <bits/stdc++.h>
using namespace std;

int main(){
	long long n;
	cin >> n;
	long long sum = 0;
    //简单找规律可以发现要被3整除则另一个数必定为3的倍数
	if(n % 3 == 0)sum = n / 3 - 1;
    //特殊情况，若本身为3的倍数则存在两个数都为3的倍数的情况
	else {
        sum = (n - 1) / 3 * 2;
    }
	
	cout << sum << endl;
}