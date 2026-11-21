#include <cstdio>
#include <string>
#include <algorithm>
using namespace std;

typedef __int128 i128;

// 输出顺序固定为 A->B, A->C, B->A, B->C, C->A, C->B
int pid_of(int s, int d) {
    if (s == 0) return d == 1 ? 0 : 1;  // A->B : A->C
    if (s == 1) return d == 0 ? 2 : 3;  // B->A : B->C
    return d == 0 ? 4 : 5;              // C->A : C->B
}

int n;
i128 memo[61][3][3][6];
bool vis[61][3][3];

void go(int nn, int s, int d, i128 res[6]) {
    if (vis[nn][s][d]) {
        for (int i = 0; i < 6; i++) res[i] = memo[nn][s][d][i];
        return;
    }
    for (int i = 0; i < 6; i++) res[i] = 0;
    if (nn == 1) {
        res[pid_of(s, d)] = 1;
    } else {
        int a = 3 - s - d;   // 唯一的辅助杆
        i128 t1[6], t2[6];
        go(nn - 1, s, a, t1);   // 先把 n-1 个盘子挪到辅助杆
        go(nn - 1, a, d, t2);   // 再把 n-1 个盘子从辅助杆挪到目标杆
        for (int i = 0; i < 6; i++) res[i] = t1[i] + t2[i];
        res[pid_of(s, d)] += 1; // 中间那一步
    }
    vis[nn][s][d] = true;
    for (int i = 0; i < 6; i++) memo[nn][s][d][i] = res[i];
}

void print128(i128 x) {
    if (x == 0) { printf("0"); return; }
    string s;
    while (x > 0) { s += char('0' + (int)(x % 10)); x /= 10; }
    reverse(s.begin(), s.end());
    fputs(s.c_str(), stdout);
}

int main() {
    if (scanf("%d", &n) != 1) return 0;
    i128 res[6];
    go(n, 0, 2, res);   // A -> C
    const char *names[6] = {"A->B", "A->C", "B->A", "B->C", "C->A", "C->B"};
    i128 sum = 0;
    for (int i = 0; i < 6; i++) {
        printf("%s:", names[i]);
        print128(res[i]);
        printf("\n");
        sum += res[i];
    }
    printf("SUM:");
    print128(sum);
    printf("\n");
    return 0;
}
