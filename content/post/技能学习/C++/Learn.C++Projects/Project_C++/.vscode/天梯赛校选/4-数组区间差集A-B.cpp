#include <bits/stdc++.h>
using namespace std;
/*
20
11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
0 9 4 12
*/
int main(){
	int n;
	cin >> n;
	vector <int> num(n, 0);
    for(int i = 0; i < n; i ++){
		cin >> num[i];
	}
	int l1,l2,r1,r2;
	int flag = 0;
	cin >> l1 >> r1 >> l2 >> r2;
	if(l2 <= l1 && r1 <= r2 )cout << "void" << endl;
    //B是A的子集 左右有间隔输出
	else { 
        //闭区间不包括l2
		for(int i = l1; i < l2; i ++){
			cout << num[i] << " "; 
		}
		//闭区间不包括r2
		for(int i = r2 + 1; i <= r1; i ++){
			cout << num[i] << " "; 
		}
	}
	
}
