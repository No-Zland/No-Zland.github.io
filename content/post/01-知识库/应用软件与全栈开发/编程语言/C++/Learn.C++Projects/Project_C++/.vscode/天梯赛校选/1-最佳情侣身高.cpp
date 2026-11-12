#include <bits/stdc++.h>
using namespace std;

int main(){
	int N;
	cin >> N;
	double f, m;
	
	while(N --){
		cin.get();
		char chr;
		cin.get(chr);
		cin.get();
		if(chr == 'F'){
			cin >> f;
			printf("%.2lf\n", f * 1.09);
		}
		else if(chr == 'M'){
			cin >> m;
			printf("%.2lf\n", m / 1.09);
		}
	}
} 