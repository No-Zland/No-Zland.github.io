#include <iostream>
#include <string>
using namespace std;
int main() {
    string s;
    if (!(cin >> s)) return 0;
    size_t p = s.find_first_not_of('0');
    // 棰樼洰淇濊瘉鏁板€间负姝ｆ暣鏁帮紝鏁?p 涓€瀹氬瓨鍦紱淇濋櫓璧疯澶勭悊鍏ㄩ浂
    if (p == string::npos) cout << 0 << '\n';
    else cout << s.substr(p) << '\n';
    return 0;
}
