#include <bits/stdc++.h>
using namespace std;
/*
a1b3c51d
b23cc1
a1a
abc
***

29
*/
string str = "***";//定义结束字符串
int main(){
	string s1;
	int sum = 0;
	while(getline(cin, s1)&& s1 != str){
		int flag = 0;
		int tem = 0;//遇到只有一个或者一个数字都没有的时候
		for(int i = s1.size() - 1; i >= 0; i --){
			
			if(flag < 2){
				if(s1[i] >= '0' && s1[i] <= '9'){
					tem *= 10; 
					tem += s1[i] - '0';
					flag ++;
				}
				if(flag == 2){
					break;
				} 
			}	
		}
		
		sum += tem;
	}
	cout << sum << endl;
}