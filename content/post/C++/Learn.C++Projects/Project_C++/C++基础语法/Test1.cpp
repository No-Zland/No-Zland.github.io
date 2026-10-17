// #include <iostream>//主要包含了系统的标准输入输出以及数据的声明和定义 
// using namespace std;
 
// int main(){
// 	cout << "Hello World!\n";
// 	//等于
// 	cout << "Hello World!" << endl;
// 	//等于
// 	cout << "Hello World!" << "\n";
// 	//等于
// 	char word = 'H';
// 	cout << word << "ello World!" << endl; 
// 	return 0;	
// } 


//找出编码为88的字符

// //#include <bits/stdc++.h>
// #include <iostream>
// using namespace std;//预编译指令
// #define long long ll;
// 
// int main(){
//     cout << (char)88 << endl;//C++的强制类型
//     cout.put(char(88));//通过cout.put函数直接输出
//     return 0;
// }


//类型转换

// #include <iostream>
// using namespace std;
// int main(){
    
//     double x1 , x2;
//     //先计算
//     int pos1 = int (x1 + x2);
//     int pos2 = (int)(x1 + x2);
//     //先类型转换
//     int pos3 = int(x1) + int(x2);

// }

//P33
//关键字auto自动判断变量类型
//char32_t类型前缀U , 固定长度的字符类型 wchar_t不够规范(宽字节)
//c风格字符串空字符表示结束 , 无法使用运算符
//string str = "Hello World!";//空白字符的输入需要特殊处理


//枚举
//enum Response{No,Yes,Maybe};//0,1,2

//int Months[12];
//&Months[0];//int类型数据单元地址
//&Months;//int[12]类型数据单元地址



//cout << (int*)"Love Story";


//strcpy()与strcat()函数

// #include <iostream>
// #include <cstring>
// using namespace std;
// const int SIZE = 20;
// int main(){
//     /*char fullname[SIZE * 2 + 1];
//     char firstname[SIZE],lastname[SIZE];*/
//     string fullname , lastname , firstname ;
//     cout << "Enter your firat name:";
//     //cin.getline(firstname,SIZE);
//     getline(cin,firstname);
//     cout << "Enter your last name:";
//     //cin.getline(lastname,SIZE);
//     getline(cin,lastname);
//     //strcpy(fullname,lastname);
//     //strcat(fullname,strcat(". ",firstname));
//     fullname = lastname + ". " + firstname ;
//     cout << "Here's the information in a single string:" << fullname << endl;
//     return 0;
// }


// #include <bits/stdc++.h>
// using namespace std;//预编译指令

// struct CandyBar{
//     char brand[20];
//     float weight;
//     unsigned int calorie;

// };

//计算空格和换行符数目的代码片段

// while(cin.getch()){//ch = cin.get()
//     if(ch == ' '){
//         space ++;
//     }
//     else if(ch == '\n'){
//         newline ++;
//     }
// }

//cctybe库函数
//toupper(char*)
//tolower(char*)
//isdigit(char*)
//islower(char*)
//isupper(char*)

