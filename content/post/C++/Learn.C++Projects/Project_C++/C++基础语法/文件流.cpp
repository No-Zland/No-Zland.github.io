//Q:编写一个程序,打开一个文件,指出该文件中包含多少个字符

#include <iostream>
#include <fstream>
using namespace std;
int main(){
    ifstream fin;//定义文件流对象
    string file_name;
    cout << "Enter the file name: ";
    getline(cin,file_name);
    //等待用户输入文件名
    fin.open(file_name);
    //通过文件流对象打开文件
    if(!fin.is_open()){
        cout << "Error to open file." << endl;
        exit(EXIT_FAILURE);
    }
    //如果在打开文件时出现错误,则终止程序;
    char read_char;
    int char_counter = 0;
    while(!fin.eof()){
        fin >> read_char;
        char_counter ++;
    }
    //通过eof函数判断是否到达文件末尾
    cout << "The file " << file_name << " contains" << char_counter << " character" << endl;
    fin.close();
    //关闭文件
    return 0;

}