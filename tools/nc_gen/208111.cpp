#include <cstdio>
#include <cctype>
#include <cstdlib>
#include <iostream>
#include <string>
using namespace std;

// 凯撒密码：0-9、A-Z、a-z 连成一条 62 长度环，解密时整体回退 d 位。
static const char *TAB = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

int main() {
    string line;
    if (!getline(cin, line)) return 0;
    // 取出被引号包住的那一段作为密文，引号后面（或逗号后）的整数是偏移量
    string cipher;
    size_t l = line.find('"'), r = (l == string::npos ? string::npos : line.find('"', l + 1));
    size_t p;
    if (l != string::npos && r != string::npos) {
        cipher = line.substr(l + 1, r - l - 1);
        p = r + 1;
    } else {
        size_t c = line.find(',');
        cipher = line.substr(0, c);
        p = (c == string::npos ? line.size() : c + 1);
    }
    int d = 0;
    while (p < line.size() && !(isdigit((unsigned char)line[p]) || line[p] == '-')) ++p;
    int sign = 1;
    if (p < line.size() && line[p] == '-') { sign = -1; ++p; }
    for (; p < line.size() && isdigit((unsigned char)line[p]); ++p) d = d * 10 + (line[p] - '0');
    d = (sign * d) % 62;
    if (d < 0) d += 62;

    string plain;
    for (char ch : cipher) {
        int idx = -1;
        for (int i = 0; i < 62; ++i)
            if (TAB[i] == ch) { idx = i; break; }
        if (idx < 0) { plain += ch; continue; }          // 环外字符原样保留
        plain += TAB[(idx - d + 62) % 62];
    }
    printf("\"%s\"\n", plain.c_str());
    return 0;
}
