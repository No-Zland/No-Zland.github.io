// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;

// bool jiecheng(ll n){
//     ll add = 1;
//     while(n --){
//         add *= n;
//     }

//     if(add < 0){
//         cout << "it wrroy!" << endl;
//         return false;
//     }
//     cout << add << endl;
//     return true;
// }

// int main(){
//     uint32_t n;
//     cin >> n;
//     jiecheng(n);
// }

// #include<stdio.h>
// void Hanoi(int n,char a,char b,char c)
// {
//     if(n==1)
//     printf("%c->%c\n",a,c);
//     else
//     {
//         //把上面n-1个盘子，从a通过c移到b
//         Hanoi(n-1,a,c,b);
//         printf("%c->%c\n",a,c);
//         Hanoi(n-1,b,a,c);
//         //把b上n-1个盘子从b通过a移到c 
//     }
//  } 
//  int main()
//  {
//      //scanf("%d",&n);
//      Hanoi(3,'A','B','C');
//      return 0;
//   }

#include  <stdlib.h>
#include  <stdio.h>
#include  <time.h>
int main(void)
{ 
  int  magic;               
  int  guess;               
  int  counter;             /*记录人猜次数的计数器变量*/   
  srand(time(NULL)); 
  magic = rand() % 100 + 1; 
  counter = 0;              /*计数器变量count初始化为0*/
  do{
    printf("Please guess a magic number:");
    scanf("%d", &guess);        
    counter++;            /*计数器变量count加1*/
  if (guess > magic)          
    printf("Wrong! Too high!\n");
  else if (guess < magic)       
    printf("Wrong! Too low!\n");
  else
    printf("Right!\n");
  }while (guess != magic && counter < 10);        
  printf("counter = %d \n", counter);
  return 0;  
}
  