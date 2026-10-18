#include <bits/stdc++.h>
#include <cstdlib>
#include <ctime>
#include <vector>
using namespace std;
//�����Ź�����ʾ����������
void Display_Number( int n, vector<int>&Show){
    srand(time(NULL));
    for(int i = 0; i < n; i ++){
        Show[i] = rand() % 81 + 1;
        for(int j = 0; j < i; j ++){
            if(Show[i] == Show[j]){
                i --;
                break;
            }
        }
       
    }
    sort(Show.begin(),Show.end());
}
//�û�����ʾ�����Ź���
void Display_User( vector<int>&Sudoku){
    for( int i = 0; i < 81; i ++){
        if(Sudoku[i] == 0)cout << "* ";
        else cout << Sudoku[i] << ' ';
        if(i % 9 == 8)cout << endl;
    }
}
//���������Ź���
void Display_Sudoku( int n, vector<int>&Sudoku){
    srand(time(NULL));
    vector<int>Show( n, 0);
    Display_Number( n, Show);

    for( int i = 0; i < n; i ++){
        Sudoku[Show[i]] = rand() % 9 + 1;
        int tem = Show[i] - 9;
        while(tem >= 0){
            if(Show[tem] == Show[i]){
                i --;
                break;
            }
            tem -= 9;
        }
        cout << Sudoku[Show[i]] << endl;
    }
    Display_User( Sudoku);
}
//����û�����������Ź���
void Check_Sudoku( vector<int>User_Sudoku_Tem){
    
    for(int i = 0; i < 81; i ++){
        if( User_Sudoku_Tem[i] > 9){
            cout << "The number that Sudoku was so big!\r\n";
            
        }
        int tem = i - 9;
        while(tem > i){
            if( User_Sudoku_Tem[i] == User_Sudoku_Tem[tem]){
                cout << "The Sudoku have error!\a\r\n";
                
            }
            tem -= 9;
        }
    }
    cout << "You win!\r\n";
}
//�û����뺯��
void Enter_Sudoku(){
    vector<int>User_Sudoku(81, 0);
    for(int i = 0; i < 81; i ++){
        cin >> User_Sudoku[i];
    }
    Check_Sudoku( User_Sudoku);
}
//�������� 
int main(){
    int n;
    vector<int>Sudoku( 81, 0);
    cin >> n;
    Display_Sudoku( n, Sudoku);  
    Enter_Sudoku();  
}