#include "algorithm"
//sort -> O(nlogn)复杂度

//对数组进行排序
//sort(pos, end, *比较函数);
//比较函数：自定义函数或者lanbda表达式

/*lanbda表达式：sort(v.begin(), v.end(), [](const int &u, const int &v)){
    return u > v;
};*///[] -> & 拷贝转成引用

//sort(a + 1, a + n + 1)
//左闭右开 默认升序

#include <bits/stdc++.h>
using namespace std;
vector<int> v ;
int main(){
    sort(v.begin(), v.end());

}
//重载小于号？
struct Node{
    int u, v;
    bool operator < (const Node &m)const//只有一个参数？
    //operator 小于这个函数的名字
    {
        //u为第一关键字，v为第二关键字
        return u == m.u ? v < m.v : u > m.u;//u相等优先排v，否则排u？
    }
}