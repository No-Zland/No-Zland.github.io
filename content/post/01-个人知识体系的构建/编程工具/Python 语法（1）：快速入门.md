---
tags:
  - "#Python/语法"
updated: 2026-11-14 23:58
---
## 一、基础语法：缩进

Python 用 **缩进区分代码块**，通常为 4 个空格；同一分支的代码必须保持 **相同缩进**。

```python
if True:
    print("缩进正确")
    print("同一代码块")
print("代码块结束")
```

缩进错误会直接导致 `IndentationError`。不要混用 Tab 和空格。

---

## 二、基本数据类型

### 1. 整数（int）

| 要点 | 说明 |
|---|---|
| 进制表示 | 二进制 `0b1010`、八进制 `0o12`、十六进制 `0xa`，均对应十进制 10 |
| 大整数 | Python 自动支持任意长度整数，无溢出限制 |

```python
a = 0b1010      # 10
b = 0o12        # 10
c = 0xa         # 10
d = 123456789012345678901234567890  # 大整数
```

### 2. 浮点数（float）

| 方法/函数 | 作用 | 示例 |
|---|---|---|
| `is_integer()` | 判断浮点数是否为整数（无小数部分） | `5.0.is_integer()` → `True` |
| `round(x, n)` | 四舍五入保留 n 位小数 | `round(3.14159, 2)` → `3.14` |

```python
x = 5.0
print(x.is_integer())   # True
print(round(3.14159, 2))  # 3.14
```

### 3. 字符串（str）

| 操作 | 说明 | 示例 |
|---|---|---|
| 转义字符 | `\n` 换行、`\t` 制表符、`\\` 反斜杠 | `"Hello\tWorld\n"` |
| `strip()` | 去掉首尾空白 | `"  hi  ".strip()` → `"hi"` |
| `upper()` / `lower()` | 转大写 / 转小写 | `"Ab".upper()` → `"AB"` |
| `split(sep)` | 按分隔符分割为列表 | `"a,b,c".split(",")` → `['a', 'b', 'c']` |
| `join(iterable)` | 用指定字符串拼接可迭代对象 | `"-".join(['a', 'b'])` → `"a-b"` |
| 三引号字符串 | 支持多行文本 | `"""第一行\n第二行"""` |

```python
s = "  Hello,World  "
print(s.strip())          # "Hello,World"
print(s.strip().split(","))  # ['Hello', 'World']
print("-".join(["a", "b"]))  # "a-b"
```

### 4. 布尔值（bool）与真值判定

**布尔判定规则：**

非空值、非 0 数值视为 `True`；

空字符串、空列表、空字典、`None`、`0`、`0.0` 视为 `False`。

```python
print(bool(""))      # False
print(bool([]))      # False
print(bool({}))      # False
print(bool(None))    # False
print(bool(0))       # False
print(bool("0"))     # True
```

---

## 三、表达式与运算符

### 1. 优先级与结合性

![[Python 运算符优先级与结合性.jpeg]]

**易错点：**

- `is` 比较对象身份（内存地址），`==` 比较值。
- `and`、`or` 具有短路特性。
- 比较运算支持链式写法：`1 < x < 10`。
- 幂运算 `**` 是右结合：`2 ** 3 ** 2` 等价于 `2 ** (3 ** 2)`。
- 赋值运算也是右结合：`a = b = 0` 等价于 `a = (b = 0)`。

### 2. 短路求值

`and` 和 `or` 具有短路特性：

| 运算符 | 短路规则 | 示例 |
|---|---|---|
| `and` | 第一个为 `False` 则返回该值；否则返回最后一个值 | `3 > 2 and 5` → `5`；`3 > 4 and 5` → `False` |
| `or` | 第一个为 `True` 则返回该值；否则返回最后一个值 | `3 > 4 or 5` → `5` |
| `not` | 逻辑取反 | `not 0` → `True` |

```python
a = 0
b = 10

if a != 0 and b / a > 1:  # a != 0 为假，右侧 b / a 不执行
    print("不会到这里")

if a == 0 or b / a > 1:   # a == 0 为真，右侧 b / a 不执行
    print("会到这里")
```

常用于 **“先判空、再使用”**，例如 `if p is not None and p.value > 0:`。

---

## 四、类型转换

Python 中不同类型混合运算时，通常需要 **显式转换**，隐式转换较少。

### 1. 常用转换函数

| 函数 | 作用 | 示例 |
|---|---|---|
| `int(x)` | 转整数，浮点截断 | `int(3.99)` → `3` |
| `float(x)` | 转浮点数 | `float("3.14")` → `3.14` |
| `str(x)` | 转字符串 | `str(123)` → `"123"` |
| `bool(x)` | 按真值规则转布尔 | `bool(0)` → `False` |

```python
print(int(3.99))      # 3，截断，不是四舍五入
print(float("3.14"))  # 3.14
print(str(123))       # "123"
print(bool(""))       # False
```

### 2. 注意事项

1. **浮点转整数是截断**，不是四舍五入；需要四舍五入用 `round()`。
2. **字符串转数字** 时格式必须合法，否则抛 `ValueError`。
3. **隐式转换** 主要在数值运算中发生，例如 `int + float` 结果为 `float`。
4. 不要把 `bool` 当整数滥用，虽然 `True == 1`、`False == 0`，但语义上应区分。

---

## 五、变量与作用域

变量是程序中用于存储数据的名字，Python 中变量不需要声明类型。

```python
age = 18          # 定义并赋值
score = 95.5
name = "Tom"

age = 20          # 重新赋值，覆盖旧值
```

### 1. 作用域

| 类型/关键字 | 定义位置 | 作用范围 | 关键点 |
|---|---|---|---|
| 局部变量 | 函数内部 | 仅函数内有效 | 函数调用结束后销毁；函数外不可访问 |
| 全局变量 | 函数外部 | 整个模块文件 | 函数内可读取；默认不能直接修改 |
| `global` | 函数内声明 | 指向全局变量 | 允许在函数内修改全局变量 |
| `nonlocal` | 嵌套函数的内层函数 | 指向外层函数的局部变量 | 允许修改外层函数变量，非全局变量 |

```python
global_var = 100

def func():
    global global_var
    global_var = 300   # 修改全局变量

def outer():
    outer_var = 10
    def inner():
        nonlocal outer_var
        outer_var = 20  # 修改外层函数变量
    inner()
    print(outer_var)    # 20
```

### 2. 同名变量

函数内局部变量与全局变量同名时，函数内 **优先访问局部变量**：

```python
x = 10

def func():
    x = 20
    print("func: x =", x)  # 20，访问局部变量

func()
print("main: x =", x)      # 10，访问全局变量
```

同名变量容易造成阅读混淆，实际项目中应尽量避免。

---

## 六、常量

Python 没有真正的常量关键字，通常用 **全大写变量名** 表示“约定常量”，提醒不要修改：

```python
PI = 3.14159
MAX_SIZE = 100
```

注意：这只是约定，运行时仍然可以重新赋值。需要强约束时，可通过类属性、枚举或第三方库实现，初学阶段用全大写约定即可。

---

## 七、分支结构

### 1. `if` 单分支

条件为 `True` 时执行代码块，否则跳过：

```python
if 条件表达式:
    代码块
```

```python
num = 10

if num > 0:
    print(f"{num} 是正数")
```

### 2. `if-else` 双分支

条件为 `True` 执行代码块 1，否则执行代码块 2：

```python
if 条件表达式:
    代码块1
else:
    代码块2
```

```python
num = 7

if num % 2 == 0:
    print(f"{num} 是偶数")
else:
    print(f"{num} 是奇数")
```

### 3. `if-elif-else` 多分支

依次判断条件，执行第一个为 `True` 的分支；都不满足执行 `else`：

```python
if 条件表达式1:
    代码块1
elif 条件表达式2:
    代码块2
else:
    代码块n
```

```python
score = 85

if score >= 90:
    print("等级：A")
elif score >= 80:
    print("等级：B")
elif score >= 60:
    print("等级：C")
else:
    print("等级：D")
```

**注意：**

- 条件从上到下判断，第一个为真的分支执行后，后续分支不再判断。
- 多分支条件顺序很重要。上例中 `score >= 90` 必须放在 `score >= 80` 之前，否则 95 分也会先命中 `>= 80`。
- Python 没有 `switch`，多条件匹配通常用 `if-elif` 或字典映射。

### 4. 条件表达式（三元运算）

简单二选一可用条件表达式：

```python
max_num = a if a > b else b
```

等价于：

```python
if a > b:
    max_num = a
else:
    max_num = b
```

适合简单赋值，嵌套过多会降低可读性，复杂逻辑仍应使用 `if-else`。

---

## 八、循环结构

Python 提供 `for` 和 `while` 两种循环。

### 1. `for` 循环：遍历序列

```python
for 变量 in 序列:
    循环体
```

```python
for i in range(1, 6):
    print(i, end=" ")   # 1 2 3 4 5
print()

for i in range(1, 11, 2):
    print(i, end=" ")   # 1 3 5 7 9
print()
```

**`range(start, stop, step)`：** 生成整数序列，默认 `start=0`、`step=1`，**不包含 `stop`**。

**遍历字典：**

```python
person = {"name": "Alice", "age": 20}

for key in person.keys():
    print(key)

for value in person.values():
    print(value)

for k, v in person.items():
    print(k, v)
```

`for` 可搭配 `else`：循环正常结束、未被 `break` 中断时执行。

```python
for i in range(3):
    print(i)
else:
    print("循环正常结束")
```

### 2. `while` 循环：先判断后执行

```python
while 条件表达式:
    循环体
```

```python
count = 1
while count <= 5:
    print(count)
    count += 1   # 更新条件，避免死循环
```

`while` 也可搭配 `else`：

```python
num = 3
while num > 0:
    print(num)
    num -= 1
else:
    print("num 变为 0，循环结束")
```

### 3. 两种循环的选择

| 循环 | 特点 | 适用场景 |
|---|---|---|
| `for` | 遍历序列或 `range()` | 循环次数已知或可迭代 |
| `while` | 先判断后执行 | 循环次数未知，依赖条件退出 |

两种循环可以互相转换，选择可读性最好的即可。

### 4. `break`：跳出当前循环

`break` 立即终止当前所在层级的循环：

```python
nums = [1, 3, 5, 7, 9]
target = 5

for num in nums:
    if num == target:
        print(f"找到目标：{num}")
        break
    print(f"当前元素：{num}")
```

`break` 只跳出 **当前所在层** 的循环，嵌套循环中不影响外层。

### 5. `continue`：跳过本次循环剩余部分

`continue` 跳过当前轮次剩余代码，进入下一轮：

```python
for i in range(1, 10):
    if i % 2 == 0:
        continue
    print(i, end=" ")   # 1 3 5 7 9
print()
```

**注意：**

- `continue` 不跳出循环，只跳过当前这一轮。
- `while` 循环中如果更新语句在 `continue` 之后，可能造成死循环，要确保条件能改变。

---

## 九、异常处理

Python 用 `try-except-else-finally` 捕获和处理异常。

**常见错误类型：** `IndexError`、`KeyError`、`ValueError`、`TypeError`、`ZeroDivisionError` 等。

```python
try:
    可能出错的代码
except 异常类型:
    异常处理
else:
    未发生异常时执行
finally:
    无论是否异常都执行
```

```python
try:
    num = int(input("请输入整数："))
    result = 10 / num
except ValueError:
    print("输入不是整数")
except ZeroDivisionError:
    print("除数不能为 0")
else:
    print("结果：", result)
finally:
    print("程序结束")
```

**要点：**

- `except` 可以捕获指定异常类型；不写类型会捕获所有异常，通常不推荐。
- `else` 在 `try` 块未发生异常时执行。
- `finally` 无论是否异常都会执行，常用于释放资源。
- 不要用异常代替正常流程控制，异常应处理“意外情况”。

---

## 十、函数

函数是封装可复用逻辑的代码块，通过 `def` 定义，核心是“输入参数 → 处理逻辑 → 返回结果”。

### 1. 函数定义

```python
def 函数名(参数列表):
    函数体
    return 返回值
```

```python
def add(a, b):
    result = a + b
    return result
```

- 函数名遵循标识符规则：字母、数字、下划线，不能以数字开头。
- 无返回值时默认返回 `None`。

### 2. 函数参数

#### 2.1 位置参数

必须按参数定义的顺序传递，数量需与形参一致。

```python
def greet(name, age):
    print(f"Hello, {name}! You are {age} years old.")

greet("Alice", 20)  # name="Alice"，age=20
```

#### 2.2 关键字参数

调用时通过 `参数名=值` 指定，可忽略顺序。

```python
greet(age=20, name="Bob")
```

#### 2.3 默认参数

定义时指定默认值，调用时可省略。默认参数必须放在位置参数之后；默认值建议用不可变对象，避免 `list` 等可变对象陷阱。

```python
def introduce(name, country="China"):
    print(f"I'm {name}, from {country}.")

introduce("Li Hua")          # 使用默认值
introduce("Anna", "USA")     # 覆盖默认值
```

#### 2.4 不定长参数

**`*args`：** 收集多余的位置参数，打包为元组。

```python
def sum_all(*args):
    print("参数元组：", args)
    return sum(args)

print(sum_all(1, 2, 3))  # 参数元组：(1, 2, 3) → 6
```

**`**kwargs`：** 收集多余的关键字参数，打包为字典。

```python
def print_info(**kwargs):
    print("参数字典：", kwargs)
    for k, v in kwargs.items():
        print(f"{k}: {v}")

print_info(name="Alice", age=20)
# 参数字典： {'name': 'Alice', 'age': 20}
```

**混合使用顺序：** 位置参数 → 默认参数 → `*args` → `**kwargs`。

```python
def func(a, b=0, *args, **kwargs):
    print(f"a={a}, b={b}, args={args}, kwargs={kwargs}")

func(1, 2, 3, 4, x=5, y=6)
# a=1, b=2, args=(3, 4), kwargs={'x': 5, 'y': 6}
```

### 3. 函数调用与返回值

```python
def add(a, b):
    return a + b

print(add(3, 5))  # 8
```

**多值返回：** 用逗号分隔，实际打包为元组，调用时可解包。

```python
def get_info():
    name = "Alice"
    age = 20
    return name, age  # 等价于 return (name, age)

info = get_info()
print(info)          # ('Alice', 20)

name, age = get_info()
print(name, age)     # Alice 20
```

**无返回值：** 未写 `return` 或只写 `return`，默认返回 `None`。

```python
def say_hello():
    print("Hello")

result = say_hello()
print(result)  # None
```

### 4. 函数嵌套

函数内部可以定义另一个函数，形成嵌套结构。

**作用域（单向性）：** 内层函数可访问外层函数的变量，但外层函数不能访问内层函数的变量。

**封装性：** 内层函数对外层不可见，仅在外部函数内部可用。

```python
def outer():
    x = 10  # 外层函数变量

    def inner():
        y = 20  # 内层函数变量
        print(f"内层访问外层变量：x={x}")
        print(f"内层变量：y={y}")

    inner()

outer()
# 内层访问外层变量：x=10
# 内层变量：y=20
```

### 5. lambda 匿名函数

格式：`lambda [参数]: 表达式`。表达式结果即返回值，适合简单逻辑。

```python
add = lambda a, b: a + b
print(add(3, 5))  # 8

max_num = lambda x, y: x if x > y else y
print(max_num(10, 20))  # 20
```

**限制：** 仅能包含一个表达式，不能有循环、复杂 `if-else` 语句等。

**用途：** 通常作为参数传递给高阶函数（如 `map`、`filter`、`sorted`），避免单独定义函数。

### 6. 高阶函数

高阶函数指接受函数作为参数或返回函数的函数。Python 内置的 `map`、`filter`、`sorted` 是典型例子。

#### 6.1 `map(func, iterable)`

将 `func` 应用于 `iterable` 的每个元素，返回迭代器（需转换为列表查看结果）。

```python
nums = [1, 2, 3, 4]
result = map(lambda x: x ** 2, nums)
print(list(result))  # [1, 4, 9, 16]
```

#### 6.2 `filter(func, iterable)`

保留 `func` 返回 `True` 的元素，返回迭代器。

```python
nums = [1, 2, 3, 4, 5, 6]
result = filter(lambda x: x % 2 == 0, nums)
print(list(result))  # [2, 4, 6]
```

#### 6.3 `sorted(iterable, key=func, reverse=False)`

对 `iterable` 排序，`key` 接受函数用于提取排序依据，`reverse=True` 为降序。

```python
words = ["apple", "banana", "cherry", "date"]
print(sorted(words, key=lambda s: len(s)))
# ['date', 'apple', 'banana', 'cherry']

person = [{"name": "Alice", "age": 20}, {"name": "Bob", "age": 18}]
print(sorted(person, key=lambda x: x["age"]))
# [{'name': 'Bob', 'age': 18}, {'name': 'Alice', 'age': 20}]
```

### 7. 函数作为参数传递

Python 中函数本身是一种数据类型，可以把函数作为参数传给另一个函数。

```python
def hello():
    print("hello")

def foo(func):
    func()

foo(hello)   # 正确：传函数本身，输出 hello
```

**常见错误：**

- `foo(hello())`：先调用 `hello()`，无返回值相当于传 `None`，会报 `'NoneType' object is not callable`。
- `foo(add)`：如果 `foo` 内部调用 `add()` 但未传所需参数，会报缺少参数错误。

---

## 十一、程序入口

Python 文件可以直接运行，也可以被作为模块导入。常用写法：

```python
def main():
    print("程序开始")
    # 主逻辑

if __name__ == "__main__":
    main()
```

**要点：**

- `__name__` 是 Python 自动设置的模块名。
- 直接运行文件时，`__name__` 为 `"__main__"`，会执行 `main()`。
- 被其他文件 `import` 时，`__name__` 为模块名，不会自动执行 `main()`。

这不是强制要求，但能让代码既可以独立运行，又可以被安全导入。

---

## 全文小结

- **缩进**：Python 用缩进区分代码块，同一代码块缩进必须一致。
- **基本数据类型**：`int`、`float`、`str`、`bool`，布尔判定记住“空/0/None 为 False”。
- **表达式与运算符**：注意 `is` 与 == 的区别、`and/or` 短路、链式比较、`**` 右结合。
- **类型转换**：常用 `int()`、`float()`、`str()`、`bool()`；浮点转整数是截断。
- **变量与作用域**：局部、全局、`global`、`nonlocal`，函数内修改全局变量要声明。
- **常量**：没有常量关键字，用全大写命名约定。
- **分支**：`if` / `elif` / `else`，条件表达式适合简单二选一。
- **循环**：`for` 遍历序列，`while` 条件循环，均可搭配 `else`；`break` / `continue` 只作用于当前层。
- **异常处理**：`try-except-else-finally`，按需捕获具体异常。
- **函数**：位置参数、关键字参数、默认参数、`*args`、`**kwargs`；`lambda` 适合简单表达式；`map` / `filter` / `sorted` 是常用高阶函数。
- **程序入口**：用 `if __name__ == "__main__":` 区分直接运行和模块导入。