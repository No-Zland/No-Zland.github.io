//Q:输入一个长度为 m 的整数序列 接下来再输入 m 个询问 , 每个询问输入一对 l , r
//对于每个询问 , 输出原序列中第 l 个数到 r 个数的和
// #include <iostream>
// using namespace std;
// const int N = 100010;

// int n,m;
// int a[N],s[N];
// int main(){
//     cin >> n >> m;
//     for(int i = 0;i < n;i ++){
//         cin >> a[i];
//     }
//     //前缀和初始化
//     for(int i = 0;i < n;i ++){
//         s[i] = s[i - 1] + a[i];
//     }

//     while(m --){
//         int l , r;
//         cin >> l >> r;
//         cout << s[r] - s[l - 1] << endl;
//     }
//     return 0;
// }

//二维数组前缀和
//Q:输入一个 n 行 m 列的整数矩阵 , 再输入q个询问 , 每个询问包含四个整数x1,x2,y1,y2,表示每个子矩阵的左上角坐标和右上角坐标 
//对于每个询问输出子矩阵中所有数的和
//左上角(1,1)到右下角(i,j)前缀和预处理公式           s[i][j] = s[i - 1][j] + s[i][j - 1] + a[i][j] - s[i - 1][j - 1]
//以(x1,y1)为左上角,(x2,y2)为右下角的子矩阵的和为是  s[x2,y2] - s[x1 - 1,y2] - s[x2,y1 - 1] + s[x1 - 1,y1 -1]
#include <iostream>
using namespace std;

const int N = 1010;
int n , m , q;
int s[N][N];

int main(){
    cin >> n >> m >> q;
    for(int i = 0;i <= N;i ++){
        for(int j = 1;j <= m;j ++){
            cin >> s[i][j];
        }
    }

    for(int i = 1;i <= n;i ++){
        for(int j = 1;j <= m;j ++){
            s[i][j] += s[i - 1][j] + s[i][j - 1] - s[i -1][j - 1];
        }
    }

    while(q --){
        int x1,x2,y1,y2;
        cin >> x1 >> y1 >> x2 >> y2;
        cout << s[x2][y2] - s[x1 - 1][y2] - s[x2][y1 - 1] + s[x1 - 1][y1 - 1];
    }

    return 0;
}
