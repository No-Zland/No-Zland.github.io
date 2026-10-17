#include <bits/stdc++.h>
using namespace std;
int main()
{
  int n, m;
  char l ,r ;
  cin >> n;

  cin.get();
  string Chuan;
  getline( cin, Chuan);
  
  cin >> m;

  while(m --){
    cin.get();
    int sum;
    sum = 0;

    cin >> l >> r;
    cout << l << r << endl;
    if( Chuan[l] == '0' && r - l == 1)sum ++;
    for( int i = l; i < r; i ++){
      if( *(Chuan.begin() + i) == '1' && *(Chuan.begin() + i + 1) == '0')sum += 1;
      cout << *(Chuan.begin() + i);
    }
    cout << sum << endl;
  }

  return 0;
}