//计算平均值与高于平均值的数
#include <iostream>
#include <array>
using namespace std;
int main(){
    array<double,10>donation;
    //使用array模板定义数组,长度为10
    double input;
    int counter = 0;//元素数
    double average , sum = 0;//平均值,和
    int bigger = 0;//大于平均值的元素个数

    cout << "Enter the double numerial:";
    cin >> input;
    while(input != 0 && counter < 10){
        donation[counter ++] = input;
        cout << "No." << "Data input to Array." << endl;
        cout << "Enter the double numerial:";
        cin >> input;
    }
    //通过while循环输入数据,当输入非数字时或超过10个元素时退出循环
    for(int i = 0;i < counter;i ++){
        sum += donation[i];
    }
    average = sum / counter;
    //求和计算平均值
    for(int i = 0;i < counter;i ++){
        if(donation[i] > average){
            bigger ++;
        }
    }
    //通过遍历计算大于平均值的元素个数
    cout << "The Average is " << average << " and " << bigger;
    cout << " data bigger than average." << endl;
    return 0;
}