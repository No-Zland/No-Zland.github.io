// #include <stdio.h>
// int main(){
//     int a = 0, b = 1;
//     char c = 'A';
//     printf("a = %d, &a = %p\r\n", a, &a);
//     printf("b = %d, &b = %p\r\n", b, &b);
//     printf("c = %c, &c = %p\r\n", c, &c);
// }

// #include <stdio.h>
// void Fun( int *par);

// void Fun_1( int par){
//     printf("par = %d\n", par);
//     par = 2;
// }

// int main(){
//     int arg = 1;
//     printf("arg = %d\n", arg);
//     Fun_1( arg);
//     printf("arg = %d\n", arg);
//     Fun( &arg);
//     printf("arg = %d\n", arg);
    
//     return 0;
// }

// void Fun( int *par){
//     printf("par = %d\n", *par);
//     *par = 2;
// }

#include <stdio.h>

void Swap(int &x, int &y){
    x ^= y;
    y ^= x;
    x ^= y;
}

int main(){
    int x = 5, y = 2;
    Swap( x, y);
    printf("%d %d\n", x, y);
}