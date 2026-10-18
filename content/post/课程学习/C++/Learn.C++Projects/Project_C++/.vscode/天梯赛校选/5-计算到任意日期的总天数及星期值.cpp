#include <bits/stdc++.h>
using namespace std;
/*
2012 3 31

734502
734562
734593
Saturday
*/
//定义一年种每月份过了多少天
int month[12] = {31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365};
//无实际意义
enum day  { Monday, Tuesday ,Wednesday, Thursday ,Friday, Saturday, Sunday 
};
int main(){
	long long n , y , r;
	cin >> n >> y >> r;
	int i = 0;
	//判断输入年份是否为闰年，改变month二月份及后面月份天数
	if(n % 4 == 0 && n % 100 != 0 || n % 400 == 0){
		for(i = 1; i < 12; i ++){
			month[i] ++;
		}
	}
	//输入年份还未过
	n --; 
	long long sum = n * 365;
	//加上闰年的天数
	sum += n / 4 - n / 100 + n / 400 ;
	
	cout << sum << endl;
	
	if(y > 1){
		sum += month[y - 2];
		 //这里减去2是由于c++数组下标为0与该月份还未过完
	}
	cout << sum << endl;
	//天数
	sum += r;
	cout << sum << endl;
	//星期
	sum --;
	sum %= 7;
	
	switch(sum){
		case Monday:	cout << "Monday" 	<< endl;break;
		case Tuesday:	cout << "Tuesday" 	<< endl;break;
		case Wednesday:	cout << "Wednesday" << endl;break;
		case Thursday:	cout << "Thursday" 	<< endl;break;
		case Friday:	cout << "Friday" 	<< endl;break;
		case Saturday:	cout << "Saturday"  << endl;break;
		case Sunday	:	cout << "Sunday" 	<< endl;break;
	}
}