//getline()函数

// #include <iostream>
// #include <cstring>//使用字符数组的处理函数
// using namespace std;
// int main(){
//     string name;
//     cout << "Please enter your name:";
//     getline(cin,name);//getline()函数的参数和字符数组的cin.getline()不同,前一个用于string后一个用于char
//     return 0;
// }

//cin       -> (int 或 char 或 string)
//cin.get(变量名) 
//cin.get(数组名, 字符个数)//数组末尾的休止符'\0' -> 实际值为n - 1 过滤不掉回车符
//cin.get(void)//吸收回车符
//cin.getline(数组名,字符个数)//超出数组长度会导致后面的读取报错
//getline(cin,变量名(string类))//'\0'不会保存在输入流中

//if(pos != npos)//判断字符串末尾npos

//string.replace(字串起始位置,替换长度,替换进去的字符串);/替换子字符串
//string.substr(起始位置,长度);//提取子字符串，长度 + 起始位置不要越界
//string.compare(string2);//if(return < 0)string < string2
//string 可以运用 算数运算符 比较
//常见遍历string数组的方法
/*for(int i = 0; i < length(string); ++ i){cout << string[i]}*/
/*for(auto i : string){
    cout << i;
    i = 'a';//不改变数值，复制出来而非引用出来
}
    
for(auto &i : string){
    cout << i;
    i = 'a';//会改变string的值
}*///auto进行枚举

#include <bits/stdc++.h>
using namespace std;
int main(){
    string s;
    getline(cin,s);
    //使用length()的时候建议加个int类型转换，length返回值是uint
    reverse(s.begin(),s.end());
    cout << s << endl;
}