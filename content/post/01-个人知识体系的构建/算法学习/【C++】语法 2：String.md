---
created: 2026-11-18 12:32
updated: 2026-11-18 12:33
---
## C++ 算法竞赛快速上手：`std::string`

竞赛里**默认用 `std::string`，不用 `char[]`**。Codeforces 的入门笔记明确写着：*“In competitive programming, we use STL string, not character arrays.”*OI-wiki 也指出，`string` 的使用比字符数组简单得多，且常数在 STL 容器中算优秀的。`char[]` 唯一的优势场景是极少数需要极致压常数或与 C 接口交互的地方，起步阶段一律用 `string`。

## 1. 定义、输入输出与基础属性

```cpp
string s;                       // 空串
string s = "codeforces";
string s(5, 'a');              // "aaaaa"

// 输入
cin >> s;                      // 读一个“单词”，遇空格/换行停止
getline(cin, s);               // 读一整行，保留空格

// 输出
cout << s << '\n';

// 基础属性
s.size();                      // 或 s.length()，返回长度（字符数）
s.empty();                     // 是否为空，等价于 s.size() == 0
s.clear();                     // 清空
```

`cin >> s` 和 `getline(cin, s)` 的关键区别：**`cin >> s` 遇空白就停**，适合读单个单词或 token；**`getline` 以换行符为界**，适合读含空格的整行。混用 `cin >>` 和 `getline` 时，`cin >>` 会留下换行符在缓冲区里，紧接着的 `getline` 会直接读到这个空行，必要时先用 `cin.ignore()` 消耗掉。

## 2. 访问与遍历：先读后改，分清 `auto` 与 `auto&`

```cpp
s[i];                          // 下标访问，不检查越界
s.front();                     // 首字符
s.back();                      // 末字符

// 只读遍历
for (char c : s) { /* 读 c */ }
for (const auto& c : s) { /* 读 c */ }

// 需要修改元素
for (auto& c : s) {
    c = toupper(c);            // 注意：toupper 作用于 char，不是 string
}
```

`s[i]` 不做越界检查，竞赛中为了速度通常直接用它；如果题目数据不保证下标合法，先用 `if` 判边界，不要依赖 `s.at(i)`，`at` 有额外检查开销。

## 3. 查找、截取与判空：最常用的三件套

### 3.1 `find` / `rfind`：返回的是下标，找不到是 `npos`

```cpp
size_t pos = s.find("abc");        // 首次出现的位置
size_t pos = s.rfind("abc");       // 最后一次出现的位置
size_t pos = s.find('x');          // 查找单个字符

if (pos != string::npos) {
    // 找到了，pos 是下标
} else {
    // 没找到
}
```

**`string::npos` 是一个特殊的无符号大数**（通常是 `size_t` 的最大值），`find` 找不到时返回它。必须用 `pos != string::npos` 判断，不要写成 `pos != -1`：`npos` 是无符号的，与 `-1` 比较时 `-1` 会被转换成同一个大数，逻辑上虽然能“碰巧”成立，但可读性和意图都不清晰。

### 3.2 `substr`：左闭右开，长度而不是结束位置

```cpp
string s = "codeforces";
string sub = s.substr(4, 6);       // "forces"：从下标 4 开始，取 6 个字符
string tail = s.substr(4);         // 从下标 4 到末尾
```

`substr(pos, len)` 的第二个参数是**长度**，不是结束下标。一个竞赛中常见但容易被忽略的行为：如果 `pos` 越界，**抛 `std::out_of_range` 异常**；如果 `len` 超出了剩余字符数，**安全地截到字符串末尾，不报错**。所以 `substr` 本身不会因为“取得太长”而崩溃，只会因为“起点不存在”而崩溃。

### 3.3 判空与清空

```cpp
if (s.empty()) { ... }
s.clear();
```

多组数据时，**每次处理前先 `clear()`**，不要指望 `string` 在作用域结束时自动“重置”成空串——它本来就是空的，但如果你在循环外声明了 `string`，每轮开始前清空是必要的习惯。

## 4. 修改：拼接用 `+=`，尾部增删用 `push_back` / `pop_back`

```cpp
s += "abc";                     // 尾部追加，竞赛最常用
s.push_back('x');               // 追加单个字符
s.pop_back();                   // 删除末尾一个字符（C++11）

s.insert(pos, t);               // 在 pos 处插入 t
s.erase(pos, len);              // 从 pos 开始删 len 个字符
s.erase(pos);                   // 删到末尾
s.replace(pos, len, t);         // 把从 pos 开始的 len 个字符替换为 t
```

`+=` 和 `push_back` 是竞赛中最高频的修改方式。`insert` 和 `erase` 在中间位置操作是 O(n) 的，如果题目需要在头部频繁插入/删除，要么换思路，要么评估数据范围是否允许。

## 5. 数值与字符串互转

```cpp
int x = stoi(s);                // string -> int
long long y = stoll(s);         // string -> long long
double z = stod(s);

string t = to_string(x);        // 数值 -> string
```

`stoi` 和 `to_string` 是竞赛中处理“数字以字符串形式给出”或“需要逐位处理数字”的标配。`stoi` 在字符串不是合法整数时抛异常；题目保证输入格式合法时直接使用，不必额外 try-catch。

## 6. 排序、反转与常用 `algorithm`

`string` 支持随机访问迭代器，标准算法可以直接用：

```cpp
sort(s.begin(), s.end());               // 按字符 ASCII 升序
sort(s.begin(), s.end(), greater<char>()); // 降序

reverse(s.begin(), s.end());

int cnt = count(s.begin(), s.end(), 'a');
auto it = find(s.begin(), s.end(), 'x'); // 注意这是 algorithm 的 find，返回迭代器
```

**`string::find` 和 `std::find` 是两个不同的东西**：`s.find(...)` 返回下标（`size_t`），`std::find(s.begin(), s.end(), ...)` 返回迭代器。竞赛中按子串查找用前者，按字符查找用后者或范围 `for` 都可以。

字符频率统计是 string 题目的常见子任务，标准写法：

```cpp
int freq[26] = {};
for (char c : s) {
    freq[c - 'a']++;
}
```

`c - 'a'` 把 `'a'~'z'` 映射到 `0~25`，这是字符串题目里最基础的哈希技巧。

## 7. 性能关键：SSO 与传参

### 7.1 短字符串不分配堆内存

主流标准库对 `std::string` 实现了**小字符串优化（SSO）**：长度在一定阈值内的字符串直接存储在对象内部的缓冲区里，不进行 `new`/`malloc`。GCC 的 libstdc++ 通常阈值是 **15 字符**，Clang 的 libc++ 是 **22 字符**，MSVC 是 **15 字符**左右。

这意味着：**竞赛中绝大多数短字符串（单词、短数字串）的 `string` 构造和拷贝几乎没有堆分配开销**，不需要因为“担心 `string` 比 `char[]` 慢”而退回字符数组。真正需要留意堆分配的是**长字符串**（超过 SSO 阈值）以及**大量拼接**。

### 7.2 传参：`const string&`，不要按值

函数参数如果传 `string` 按值，会发生整串拷贝；长字符串时开销明显。统一写：

```cpp
void process(const string& s);   // 只读
void modify(string& s);          // 需要修改外部
```

和基础篇里 `vector` 的建议一致：**只读用 `const&`，需要修改用 `&`，避免不必要的拷贝**。

### 7.3 避免在循环里用 `+` 反复拼接

`a + b` 会产生一个临时新字符串。在循环里 `s = s + c` 反复执行，如果是长字符串，可能触发多次重新分配和拷贝。**追加用 `+=` 或 `push_back`**，它们在容量足够时是均摊 O(1) 的。

## 8. 竞赛高频坑

**`cin >> s` 读不了空格。** 题目要求读整行（含空格）时，必须用 `getline(cin, s)`；如果前面刚用过 `cin >>`，记得先 `cin.ignore()` 吃掉残留换行符。

**`find` 的返回值必须和 `string::npos` 比较，不要用 `-1` 或 `>= 0`。** `npos` 是无符号大数，`pos >= 0` 永远为真，是隐蔽的逻辑错误。

**`substr` 的第二个参数是长度，不是结束下标。** `s.substr(2, 5)` 取的是从下标 2 开始的 5 个字符，不是 `[2, 5)`。起点越界会抛异常，长度越界不会。

**`s.size()` 返回无符号数。** 写 `for (int i = 0; i < s.size(); i++)` 时，如果 `s.size()` 为 0，`i < 0u` 的比较会出问题；更隐蔽的是 `s.size() - 1` 在空串时变成无符号的最大值。循环下标用 `int` 时，要么保证字符串非空，要么统一用 `size_t` 或 `int(s.size())`。竞赛中最省事的写法是 `for (int i = 0; i < (int)s.size(); i++)`。

**`toupper` / `tolower` 作用于单个 `char`，不作用于 `string`。** 需要整串转换时用循环或 `transform`，不要直接写 `toupper(s)`。

## 9. 最小可提交片段

把上述内容压缩成一个可以直接套用的片段：

```cpp
#include <bits/stdc++.h>
using namespace std;

void solve() {
    string s;
    getline(cin, s);                     // 或 cin >> s

    // 下标遍历
    for (int i = 0; i < (int)s.size(); i++) {
        // s[i]
    }

    // 查找
    size_t pos = s.find("ab");
    if (pos != string::npos) { /* ... */ }

    // 截取
    string sub = s.substr(0, min(3, (int)s.size()));

    // 排序 / 反转
    sort(s.begin(), s.end());
    reverse(s.begin(), s.end());

    // 数值
    // int x = stoi(s);
    // string t = to_string(123);
}
```

这一篇覆盖了起步阶段 95% 以上的 `string` 需求。`string` 本身的操作就这些，剩下的复杂度来自**题目里的字符串算法**（匹配、回文、DP 等），那是下一层的内容。