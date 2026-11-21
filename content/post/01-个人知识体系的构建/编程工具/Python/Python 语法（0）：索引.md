---
title: Python 语法（0）：知识点索引
tags:
  - "#Python/语法"
  - MOC
updated: 2026-11-17 22:45
created: 2026-11-17 21:57
---
# Python 语法索引

## 1. 词法与程序结构

### 1.1 缩进与代码块
```python
if cond:
for x in iterable:
while cond:
def f():
class C:
try:
```
[博客](博客链接)

### 1.2 注释与文档字符串
```python
# 单行注释
"""docstring"""
help(obj)
```
[博客](博客链接)

### 1.3 源文件编码
```python
# -*- coding: utf-8 -*-
```
[博客](博客链接)

### 1.4 标识符与关键字
```python
keyword.kwlist
str.isidentifier()
```
[博客](博客链接)

### 1.5 程序入口
```python
if __name__ == "__main__":
```
[博客](博客链接)

### 1.6 模块导入与包
```python
import module
from module import name as alias
__init__.py
__all__
```
[博客](博客链接)

## 2. 输入输出与文本

### 2.1 输入输出
```python
print(*objects, sep=' ', end='\n')
input(prompt='')
```
[博客](博客链接)

### 2.2 字符串不可变与常用方法
```python
s[0] = "x"          # 报错
str.strip(s)
str.split(s, sep=None)
str.join(sep, iterable)
str.replace(old, new, count=-1)
str.startswith(prefix)
str.find(sub)
str.encode(encoding='utf-8')
bytes.decode(b, encoding='utf-8')
```
[博客](博客链接)

### 2.3 字符串格式化
```python
f"{expr}"
str.format(*args, **kwargs)
str.format_map(mapping)
```
[博客](博客链接)

### 2.4 bytes 与 bytearray
```python
b"bytes"
bytes(s, encoding='utf-8')
bytearray(iterable)
```
[博客](博客链接)

## 3. 数字与运算

### 3.1 基本类型与真值判定
```python
int(x)
float(x)
bool(x)
```
[博客](博客链接)

### 3.2 None 判断
```python
x is None
x is not None
```
[博客](博客链接)

### 3.3 浮点比较与舍入
```python
math.isclose(a, b)
round(number, ndigits=None)
```
[博客](博客链接)

### 3.4 数字类型扩展
```python
complex(real, imag)
decimal.Decimal("0.1")
fractions.Fraction(n, d)
```
[博客](博客链接)

### 3.5 数学与数值函数
```python
abs(x)
divmod(a, b)
math.floor(x)
math.ceil(x)
math.isclose(a, b)
```
[博客](博客链接)

### 3.6 is 与 ==
```python
a is b
a == b
a is not b
```
[博客](博客链接)

### 3.7 and 与 or
```python
x or y
x and y
```
[博客](博客链接)

### 3.8 幂运算
```python
a ** b
-2 ** 2
2 ** 3 ** 2
```
[博客](博客链接)

### 3.9 整除与取模
```python
a // b
a % b
```
[博客](博客链接)

### 3.10 链式比较与 not
```python
1 < x < 10
not a == b
```
[博客](博客链接)

### 3.11 位运算与矩阵乘法
```python
a & b
a | b
a ^ b
~a
a << n
a >> n
a @ b
```
[博客](博客链接)

### 3.12 赋值表达式
```python
(n := expr)
```
[博客](博客链接)

## 4. 变量、对象与作用域

### 4.1 多重赋值与解包
```python
a = b = 0
a, b = 1, 2
a, *rest = seq
f(*args, **kwargs)
```
[博客](博客链接)

### 4.2 类型转换
```python
int(x)
float(x)
str(x)
bool(x)
list(iterable)
tuple(iterable)
set(iterable)
dict(iterable)
```
[博客](博客链接)

### 4.3 变量作用域
```python
global var
nonlocal var
globals()
locals()
```
[博客](博客链接)

### 4.4 引用、浅拷贝与深拷贝
```python
a = b
copy.copy(x)
list.copy()
copy.deepcopy(x)
```
[博客](博客链接)

### 4.5 del
```python
del name
del obj[key]
```
[博客](博客链接)

### 4.6 常量约定
```python
CONSTANT_NAME
enum.Enum
typing.Final
```
[博客](博客链接)

## 5. 控制流

### 5.1 分支与条件表达式
```python
if cond:
elif cond:
else:
a if cond else b
```
[博客](博客链接)

### 5.2 match 模式匹配
```python
match value:
    case pattern:
```
[博客](博客链接)

### 5.3 for 与 range
```python
for x in iterable:
range(stop)
range(start, stop, step)
```
[博客](博客链接)

### 5.4 循环 else
```python
for x in iterable:
else:
while cond:
else:
```
[博客](博客链接)

### 5.5 遍历时修改容器
```python
for x in lst[:]:
for k in list(d):
for k, v in d.copy().items():
```
[博客](博客链接)

### 5.6 break、continue、pass 与 Ellipsis
```python
break
continue
pass
...
```
[博客](博客链接)

## 6. 异常与断言

### 6.1 异常处理
```python
try:
except Exception as e:
except (A, B) as e:
else:
finally:
raise X from e
```
[博客](博客链接)

### 6.2 自定义异常与断言
```python
class MyError(Exception):
raise MyError(...)
assert cond, msg
```
[博客](博客链接)

## 7. 函数与函数式工具

### 7.1 函数定义与参数
```python
def f(pos, default=None, *args, kw_only, **kwargs):
def f(*, a, b):
```
[博客](博客链接)

### 7.2 返回值与函数对象
```python
return
return a, b
foo(bar)
foo(bar())
```
[博客](博客链接)

### 7.3 lambda 与闭包
```python
lambda args: expr
lambda i=i: i
def outer():
    def inner():
        nonlocal x
```
[博客](博客链接)

### 7.4 递归
```python
def f(n):
    return f(n - 1)
```
[博客](博客链接)

### 7.5 迭代协议
```python
iter(obj)
next(it)
next(it, default)
StopIteration
```
[博客](博客链接)

### 7.6 生成器
```python
def g():
    yield x
yield from iterable
```
[博客](博客链接)

### 7.7 推导式
```python
[expr for x in it if cond]
{expr for x in it if cond}
{k: v for k, v in it}
(expr for x in it if cond)
```
[博客](博客链接)

### 7.8 map、filter、zip、enumerate
```python
map(func, iterable)
filter(func, iterable)
zip(*iterables, strict=False)
enumerate(iterable, start=0)
```
[博客](博客链接)

### 7.9 any、all、sum、min、max
```python
any(iterable)
all(iterable)
sum(iterable, start=0)
min(iterable, key=None)
max(iterable, key=None)
```
[博客](博客链接)

### 7.10 排序与 key
```python
sorted(iterable, key=None, reverse=False)
list.sort(key=None, reverse=False)
operator.itemgetter(item)
```
[博客](博客链接)

### 7.11 装饰器与 functools
```python
@decorator
functools.wraps(func)
functools.partial(func, *args, **kwargs)
```
[博客](博客链接)

## 8. 上下文管理器与类型系统

### 8.1 上下文管理器
```python
with expr as x:
__enter__
__exit__
contextlib.contextmanager
```
[博客](博客链接)

### 8.2 类型注解
```python
x: int
def f(a: int) -> str:
typing.Optional[T]
typing.Union[A, B]
```
[博客](博客链接)

## 9. 容器类型

### 9.1 列表
```python
lst[start:stop:step]
lst[1:3] = [10]
lst.append(x)
lst.extend(iterable)
lst.insert(i, x)
lst.remove(x)
lst.pop(i=-1)
lst.index(x)
lst.count(x)
lst.clear()
lst.copy()
lst + other
lst * n
x in lst
```
[博客](博客链接)

### 9.2 元组
```python
(5,)
t = ([1],)
a, b = b, a
a, *rest = seq
tuple.count(x)
tuple.index(x)
```
[博客](博客链接)

### 9.3 字典
```python
d[key]
d.get(key, default=None)
d.setdefault(k, default)
d.update(other)
d.pop(k, default)
d.popitem()
d.clear()
d.copy()
d.items()
d.keys()
d.values()
dict.fromkeys(seq, value)
d1 | d2
{**d1, **d2}
```
[博客](博客链接)

### 9.4 集合
```python
set()
frozenset(iterable)
s.add(elem)
s.update(*others)
s.remove(elem)
s.discard(elem)
s.pop()
s.clear()
s.copy()
a | b
a & b
a - b
a ^ b
s.issubset(other)
s.issuperset(other)
s.isdisjoint(other)
dict.fromkeys(seq)
```
[博客](博客链接)

### 9.5 可变性总结
```python
list / dict / set
int / float / str / bool / tuple / frozenset
```
[博客](博客链接)

## 10. 文件、路径与配置

### 10.1 文件打开与模式
```python
open(file, mode='r', encoding='utf-8', errors='strict')
r / w / a / x / + / b
with open(...) as f:
```
[博客](博客链接)

### 10.2 文件读写
```python
f.read(size=-1)
f.readline(size=-1)
f.readlines(hint=-1)
for line in f:
f.write(s)
f.writelines(lines)
f.read(size)
f.write(b)
```
[博客](博客链接)

### 10.3 文件指针与大文件
```python
f.tell()
f.seek(offset, whence=0)
f.seek(0)
f.seek(0, 2)
while chunk := f.read(1 << 20):
```
[博客](博客链接)

### 10.4 文件对象属性与刷新
```python
f.flush()
f.closed
f.name
f.mode
```
[博客](博客链接)

### 10.5 路径与 os.path
```python
os.path.join(*paths)
os.path.exists(p)
os.path.isfile(p)
os.path.isdir(p)
os.getenv(key, default=None)
os.listdir(path='.')
os.makedirs(name, exist_ok=False)
```
[博客](博客链接)

### 10.6 pathlib
```python
Path.cwd()
Path.cwd() / "data" / "x.txt"
Path.read_text(encoding="utf-8")
Path.write_text(data, encoding="utf-8")
Path.exists()
Path.is_file()
Path.is_dir()
Path.glob(pattern)
Path.iterdir()
Path.mkdir(parents=True, exist_ok=False)
Path.unlink()
```
[博客](博客链接)

### 10.7 shutil 与 tempfile
```python
shutil.copy(src, dst)
shutil.copy2(src, dst)
shutil.copytree(src, dst)
shutil.move(src, dst)
shutil.rmtree(path)
tempfile.NamedTemporaryFile(...)
```
[博客](博客链接)

### 10.8 JSON、YAML 与 CSV
```python
json.dump(obj, f, ensure_ascii=False, indent=2)
json.load(f)
yaml.safe_load(stream)
csv.reader(f)
csv.writer(f)
csv.DictReader(f)
csv.DictWriter(f, fieldnames)
```
[博客](博客链接)