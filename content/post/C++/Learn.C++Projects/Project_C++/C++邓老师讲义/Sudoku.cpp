//#include  <stdlib.h>
//#include  <stdio.h>
//#include  <time.h>
//int main(void)
//{ 
//	int  magic;               
//	int  guess;               
//	int  counter;             /*记录人猜次数的计数器变量*/   
//  	srand(time(NULL)); 
//	magic = rand() % 100 + 1; 
//	counter = 0;              /*计数器变量count初始化为0*/
//	do{
//		printf("Please guess a magic number:");
//		scanf("%d", &guess);        
//		counter++;            /*计数器变量count加1*/
//		if (guess > magic)          
//		    printf("Wrong! Too high!\n");
//		else if (guess < magic)       
//		    printf("Wrong! Too low!\n");
//       else
//           printf("Right!\n");
//	}while (guess != magic && counter < 10);        
//	printf("counter = %d \n", counter);
//  return 0;  
//}
#include <bits/stdc++.h>
#include <cstdlib>
#include <ctime>
#include <vector>
using namespace std;
vector<int*>sudoku( 81 ,0);

void Show( int n, vector<int*>show_tem){
    srand(time(NULL));
    for(int i = 0; i < n; i ++){
        *show_tem[i] = rand() % 81 + 1;
    }
}

void Sudoku( int n, vector<int*>sudoku_tem){
    srand(time(NULL));
    vector<int*>show(n);
    Show( n, show);
    for( int i = 0; i < n; i ++){
        make:
            *sudoku_tem[*show[i]] = rand() % 9 + 1;
        int tem = *show[i] - 7;
        while(tem > 0){
            if(sudoku_tem[i] == sudoku_tem[tem])goto make;
            tem -= 7;
        }
    }
}

void Display(vector<int*>sudoku_tem){
    for( int i = 0; i < 81; i ++){
        if(i % 7 == 6)cout << *sudoku_tem[i] << endl;
        else cout << *sudoku_tem[i] << ' ';
    }
}

int main(){
    int n;
    cin >> n;
    Sudoku( n, sudoku);
    Display( sudoku);
}

