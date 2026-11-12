//1.new运算符创建一个指针,直接申请内存,delete进行释放
//int *p = new int[12];

//2.new动态分配数组
// int main(){
//     CandyBar *pc = new CandyBar[3];
//     strcpy(pc[0].brand,"Mocha Munch");
//     pc[0].weight = 2.3;
//     pc[0].calorie = 350;
//     strcpy(pc[1].brand,"Hershey bar");
//     (pc + 1) -> weight = 4.2;// 等于pc[1].weight (*p).b
//     pc[1].calorie = 550;
//     strcpy(pc[1].brand,"Musketeers");
//     pc[2].weight = 2.6;
//     pc[2].calorie = 430;
//     cout << "My 1st CandyBar is " << pc->brand << "." << endl;
//     //此处省略输出
//     delete [] pc;
//     //在程序结束时 ,必须手动调用delete回收存储空间
//     return 0;
// }


//3.模板类array
//#include <array>
//array < char , 30 > actor;//char actor[30];

//vector动态数组(可变长数组),随时增添数值和删除元素
//不使用using指令
/*
#include <vector>
#include <string.h>
#include <array>
const int size = 10;
std::vector < std::string > vest(size);
std::array < std::string , size > arst;
*/

//4.结构体动态分配内存
/*
fish *pf = new fish;
cout << "Enter the kind of fish:"
cin >> pf -> kind
*/

/*struct Student{
    char name[20];
    int age;
}*/
/*5.结构体变量定义struct fish{
    char kind[20];
    int weight;
    float length;
}petes = {"BigFish",12,4.5}*/
//或者fish petes = {"BigFish",12,4.5};
