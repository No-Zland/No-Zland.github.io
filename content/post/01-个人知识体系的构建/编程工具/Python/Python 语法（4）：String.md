---
created: 2026-11-18 12:22
updated: 2026-11-18 12:23
---
# Python 语法索引

## 2. 输入输出与文本

### 2.1 查找与统计

```python
str.find(sub[, start[, end]])       # 找不到返回 -1
str.rfind(sub[, start[, end]])      # 从右向左找，找不到返回 -1
str.index(sub[, start[, end]])      # 找不到抛 ValueError
str.rindex(sub[, start[, end]])     # 从右向左找，找不到抛 ValueError
str.count(sub[, start[, end]])      # 统计出现次数
```

- **查找方法详解**：`find/rfind/index/rindex/count` 的返回值差异与区间参数
- **45 个字符串方法全览（查找部分）**：

### 2.2 修改与清理

```python
str.replace(old, new[, count])      # 全部替换，count 限制次数
str.strip([chars])                  # 去掉两端字符，默认空白
str.lstrip([chars])                 # 只去左边
str.rstrip([chars])                 # 只去右边
```

- **replace/strip/lstrip/rstrip 用法与注意点（返回新字符串，原串不变）**：
- **split/join/strip/replace 综合示例**：
- **replace 与 strip 的实际使用场景**：

### 2.3 分割与拼接

```python
str.split(sep=None, maxsplit=-1)    # 返回 list[str]
str.rsplit(sep=None, maxsplit=-1)   # 从右开始分割
str.splitlines(keepends=False)      # 按行界符分割
str.partition(sep)                  # 返回 (前, 分隔符, 后) 三元组
str.rpartition(sep)                 # 从右找分隔符
sep.join(iterable)                  # 用 sep 拼接可迭代对象
```

- **split/join 与 partition/rpartition 详解**：
- **split 的 maxsplit 与 join 的高效拼接**：
- **join 为什么比 `+` 拼接更高效**：

### 2.4 大小写与对齐

```python
str.lower()
str.upper()
str.casefold()                      # 更激进的小写，跨语言
str.capitalize()                    # 首字母大写，其余小写
str.title()                         # 每个单词首字母大写
str.swapcase()                      # 大小写互换
str.center(width[, fillchar])
str.ljust(width[, fillchar])
str.rjust(width[, fillchar])
str.zfill(width)                    # 右对齐，前补 0
```

- **大小写与对齐方法汇总**：
- **casefold 与 lower 的区别**：

### 2.5 判断与检测

```python
str.startswith(prefix[, start[, end]])
str.endswith(suffix[, start[, end]])
str.isalpha()
str.isdigit()
str.isalnum()
str.isspace()
str.isupper()
str.islower()
str.istitle()
```

- **is* 系列与 startswith/endswith 用法**：
- **判断方法返回布尔值的实际场景**：

### 2.6 字符串格式化

```python
f"{expr}"                           # f-string，推荐
f"{value:.2f}"                      # 数字精度
f"{value:>10}"                      # 对齐与宽度
f"{value=}"                         # 调试：输出表达式与值
"{0} {1}".format(a, b)             # str.format
"{name}".format_map(mapping)       # 用映射填充
"%s %.1f" % (s, num)               # % 旧式格式化
```

- **f-string 完整指南（表达式、数字格式化、调试）**：
- **f-string 入门与性能优势**：
- **str.format 官方语法**：

### 2.7 编码与字节转换

```python
str.encode(encoding='utf-8', errors='strict')   # -> bytes
bytes.decode(encoding='utf-8', errors='strict') # -> str
bytes(s, encoding='utf-8')
bytearray(s, encoding='utf-8')
```

- **encode/decode 的本质：str ↔ bytes**：
- **Python 3 字符串与字节的编解码实践**：