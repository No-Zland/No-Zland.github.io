//AC代码
// 汉诺塔是一个经典问题，相传在古印度圣庙中，有一种被称为汉诺塔(Hanoi)的游戏。
// 该游戏是在一块铜板装置上，有三根杆(编号A、B、C)，在A杆自下而上、由大到小按顺序放置n个金盘。
// 游戏的目标：把A杆上的金盘全部移到C杆上，并仍保持原有顺序叠好。操作规则：每次只能移动一个盘子，并且在移动过程中三根杆上都始终保持大盘在下，小盘在上，操作过程中盘子可以置于A、B、C任一杆上。
// 汉诺塔以及其衍生问题往往使用递归来求解，也是学习和理解递归很好的老师。
// 其伪代码如下
// Function Hanoi(n,a,b,c)
//     if n==1 then
//         print(a+'->'+c)
//     else
//         Hanoi(n-1,a,c,b)
//         print(a+'->'+c)
//         Hanoi(n-1,b,a,c)
//     end if
// end Function 

// 牛牛很快就理解了代码的意思并且写出了求解汉诺塔的程序，他现在想研究汉诺塔的规律。
// 请你统计以下信息：A->B,A->C,B->A,B->C,C->A,C->B的次数，以及所有移动的总步数。
// #include<bits/stdc++.h>
// using namespace std;
// using LL=long long;
// int main(){
//     int n;cin>>n;
//     vector<vector<LL>> a(n+1,vector<LL>(4));
//     a[1][1]=1;
//     for(int i=2;i<=n;i++){
//         a[i][0]=a[i-1][1]+a[i-1][2];
//         a[i][1]=a[i-1][0]*2+1;//
//         a[i][2]=a[i-1][3]*2+(i-1)/2;//
//         a[i][3]=a[i-1][2]*2;
//     }
    
//     cout<<"A->B:"<<a[n][0]<<endl;
//     cout<<"A->C:"<<a[n][1]<<endl;
//     cout<<"B->A:"<<a[n][2]<<endl;
//     cout<<"B->C:"<<a[n][0]<<endl;
//     cout<<"C->A:"<<a[n][3]<<endl;
//     cout<<"C->B:"<<a[n][2]<<endl;
//     cout<<"SUM:"<<a[n][0]*2+a[n][1]+a[n][2]*2+a[n][3]<<endl;
// }

/*
已知规律
AB  AC  BA  BC  CA  CB
0   1   0   0   0   0
1   1   0   1   0   0
1   3   1   1   0   1
4   3   1   4   2   1
4   9   6   4   2   6
15  9   6   15  12  6
*/
//修改我的AC代码
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
ll a[4] = {0,1,0,0};//现在一组代表{AB, AC, BA, CA};
ll b[4] = {0,1,0,0};//负责保存上一次的数组,对下一组进行计算
bool hanoi(ll n){
     
    for(ll i = 2;i <= n;i ++){
        ll count =  pow(2, i) - 1;//n层汉诺塔需要移动的总次数
        a[1] = b[0] * 2 + 1;//先得到现在一组的AC
        if(i > 1){
            a[0] = b[1] + b[2];
        }
        if(i > 2){
            a[2] = b[3] * 2 + (i - 1) / 2;
        }
        if(i > 3){
            a[3] = 2 * b[2];
        }
        
        b[0] = a[0];
        b[2] = a[2];
        b[3] = a[3];
        b[1] = a[1];
    }
    
    return true;
}

int main(){
    ll n;
    cin >> n;
    hanoi(n);
    cout << "A->B:" << a[0] << endl;//AB == BC
    cout << "A->C:" << a[1] << endl;
    cout << "B->A:" << a[2] << endl;//BA == CB
    cout << "B->C:" << a[0] << endl;
    cout << "C->A:" << a[3] << endl;
    cout << "C->B:" << a[2] << endl;
    ll i = 0, sum = pow(2, n) - 1;
    int count[100] = {0};
    cout << "SUM:" << ( a[0] + a[2] ) * 2 + a[1] + a[3];
    // //样例点只通过75%的问题出在这里
    // cout << "SUM:";
    // while(sum){//数字表示为e计数法, 将其数值存入数组
    //     count[i ++] = sum % 10; 
    //     sum /= 10;
    // }
    // i --;
    // while(i >= 0){
    //     cout << count[i];
    //     i --;
    // }
    
}

#include <bits/stdc++.h>
using namespace std;
using ll = long long;
ll a[4] = {0,0,0,0};
ll b[4] = {0,0,0,0};
bool hanoi(ll n){
     
    for(ll i = 1;i <= n;i ++){
        ll count =  pow(2, i) - 1;
        a[1] = count - 2 * ( b[0] + b[2] ) - b[3];
        if(i > 1){
            a[0] = b[1] + b[2];
        }
        if(i > 2){
            a[2] = b[0] + b[3];
        }
        if(i > 3){
            a[3] = 2 * b[2];
        }
        
        b[0] = a[0];
        b[2] = a[2];
        b[3] = a[3];
        a[1] = (ll)count - 2 * ( b[0] + b[2] ) - b[3];
        b[1] = a[1];
    }
    
    return true;
}

int main(){
    ll n;
    cin >> n;
    hanoi(n);
    cout << "A->B:" << a[0] << endl;
    cout << "A->C:" << a[1] << endl;
    cout << "B->A:" << a[2] << endl;
    cout << "B->C:" << a[0] << endl;
    cout << "C->A:" << a[3] << endl;
    cout << "C->B:" << a[2] << endl;
    ll i = 0, sum = pow(2, n) - 1;
    int count[100] = {0};
    while(sum){
        count[i ++] = sum % 10; 
        sum /= 10;
    }
    i --;
    cout << "SUM:";
    while(i >= 0){
        cout << count[i];
        i --;
    }
    
}