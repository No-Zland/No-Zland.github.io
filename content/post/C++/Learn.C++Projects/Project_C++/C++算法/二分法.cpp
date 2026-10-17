//整数二分
//浮点二分
//二分答案!!!
//On -> Ologn
//搜索范围
//确定check函数（mid）
//mid = (l + r)/ 2 ;  //7 / 2 == 3
//移动或返回 l 或 r 指针
//数组大小通常 10e6次方

//有序数组小到大
//lower_bound(first, last, val, comp);
//在[first, last)区间 返回第一个指向大于等于 val 的指针
//comp比较方式，可不用

//有序数组大到小
//upper_bound(first, last, val, comp);
//在[first, last)区间 返回第一个指向大于等于 val 的指针

//这里符号相反的原因在于所输入的val不一定存在，
//同时需要自行判断数组的排序输出指针加一或者减一

//less<tybe>()//适用于大到小
//greater<tybe>()//适用于小到大

#include <bits/stdc++.h>
using namespace std;
vector<int>myname(200) ;
int main(){
    int s[10];
    int i = 0;
    //100 99 1 2 8 1923 123 2453 11 78
    for(i = 0; i < 10; i ++){
        cin >> myname[i];
    }

    /* // sort(myname.begin(), myname.end());//结果输出都为0
    while( i ++ < 10){
    //     //getline(cin, myname[i]);//仅可以用于string 与 char
    //     cin >> myname[i] ;//会改变myname的地址
    // }
    // //降序
    // sort(myname.begin(), myname.end(), greater<int>());//升序
    */

    // for(i = 0; i < 10; i ++){
    //     cout << myname[i] << " ";
    // }
    // cout << endl;
    
    // cout << *(lower_bound(myname.begin(), myname.end(), 10, greater<int>()) - 1) << endl;
    // cout << *(lower_bound(myname.begin(), myname.end(), 10, greater<int>()) - 1) << endl;
    // cout << *(upper_bound(myname.begin(), myname.end(), 10, less<int>()) - 1) << endl;
    // cout << *(upper_bound(myname.begin(), myname.end(), 10, less<int>()) - 1) << endl;

    //升序左闭右开
    sort(myname.begin(), myname.end());//结果输出都为0

    for(i = 0; i < 10; i ++){
        cout << myname[i] << " ";
    }
    cout << endl;
    
    cout << *(lower_bound(myname.begin(), myname.end(), 10, greater<int>()) - 1) << endl;
    cout << *(lower_bound(myname.begin(), myname.end(), 10, greater<int>()) - 1) << endl;
    cout << *(upper_bound(myname.begin(), myname.end(), 10, less<int>()) - 1) << endl;
    cout << *(upper_bound(myname.begin(), myname.end(), 10, less<int>()) - 1) << endl;

    //不能用
    // sort(myname.begin(), myname.end(), less<int>());

    // for(i = 0; i < 10; i ++){
    //     cout << myname[i] << " ";
    // }
    // cout << endl;
    
    // cout << *(lower_bound(myname.begin(), myname.end(), 10, greater<int>()) - 1) << endl;
    // cout << *(lower_bound(myname.begin(), myname.end(), 10, greater<int>()) - 1) << endl;
    // cout << *(upper_bound(myname.begin(), myname.end(), 10, less<int>()) - 1) << endl;
    // cout << *(upper_bound(myname.begin(), myname.end(), 10, less<int>()) - 1) << endl;

    return 0;
}