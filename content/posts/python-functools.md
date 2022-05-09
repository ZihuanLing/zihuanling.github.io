---
title: "Python Functools: 几个有意思的工具函数"
date: 2022-05-05T09:38:45+08:00
tags: [python]
categories: [python]
showToc: true
TocOpen: false
draft: true
hidemeta: false
comments: false
# description: "Desc Text."
# canonicalURL: "https://canonical.url/to/page"
# disableHLJS: true # to disable highlightjs
disableShare: false
hideSummary: false
searchHidden: false
ShowReadingTime: true
ShowBreadCrumbs: true
ShowPostNavLinks: true
---

functools 模块应用于高阶函数，即参数或（和）返回值为其他函数的函数，如装饰器、sorted函数的key参数等。通常来说，此模块功能适用于所有可调用对象。

https://docs.python.org/zh-cn/3/library/functools.html

发现functools里面有几个有意思的函数，记录一下：

## cmp_to_key

将(旧式的)比较函数转换为新式的 [key function](https://docs.python.org/zh-cn/3/glossary.html#term-key-function) . 在类似于 [`sorted()`](https://docs.python.org/zh-cn/3/library/functions.html#sorted) ， [`min()`](https://docs.python.org/zh-cn/3/library/functions.html#min) ， [`max()`](https://docs.python.org/zh-cn/3/library/functions.html#max) ， [`heapq.nlargest()`](https://docs.python.org/zh-cn/3/library/heapq.html#heapq.nlargest) ， [`heapq.nsmallest()`](https://docs.python.org/zh-cn/3/library/heapq.html#heapq.nsmallest) ， [`itertools.groupby()`](https://docs.python.org/zh-cn/3/library/itertools.html#itertools.groupby) 等函数的 key 参数中使用。此函数主要用作将 Python 2 程序转换至新版的转换工具，以保持对比较函数的兼容。

比较函数意为一个可调用对象，该对象接受两个参数并比较它们，结果为小于则返回一个负数，相等则返回零，大于则返回一个正数。key function则是一个接受一个参数，并返回另一个用以排序的值的可调用对象。

实例：

使用sorted + cmp_to_key，实现逆序排序

```python
from functools import cmp_to_key
def mycmp(a, b):
    return b - a
arr = [1,9,3,7,8,2]
arr = sorted(arr, key=cmp_to_key(mycmp))
print(arr)
```

输出：

```
[9, 8, 7, 3, 2, 1]
```

一般的 `key function` 只接受一个参数，使用`cmp_to_key`，可以实现自定义的排序逻辑，如上述，也可以实现其他逻辑，比较经典的是 [leetcode-179最大数](https://leetcode-cn.com/problems/largest-number/)，要求我们将数字按照特定的规律排序，然后返回一个长的字符串，参考答案：

```python
class Solution:
    def largestNumber(self, nums: List[int]) -> str:
        # 第一步：定义比较函数，把最大的放左边
        # 第二步：排序
        # 第三步：返回结果
        def compare(x, y): return int(y+x) - int(x+y)
        nums = sorted(map(str, nums), key=cmp_to_key(compare))
        print(cmp_to_key)
        return "0" if nums[0]=="0" else "".join(nums)
```

如上述的排序，也可以做一个自定义的排序逻辑，如：如果是偶数，排序在前面，奇数排序在后面，然后奇数和偶数各自排序：

```python
def mycmp(a, b):
    # 排序函数
    if a % 2 == b % 2:
        # 同为奇数或者偶数，较小者排在前面
        return a - b
    elif a % 2 == 0:
        # a 为偶数，排在前面
        return 1
    else:
        # b为偶数，排在前面
        return -1
```

输出：

```
[2, 8, 1, 3, 7, 9]
```

## partial

返回一个新的 [partial对象](https://docs.python.org/zh-cn/3/library/functools.html#partial-objects)，当被调用时其行为类似于 *func* 附带位置参数 *args* 和关键字参数 *keywords* 被调用。 如果为调用提供了更多的参数，它们会被附加到 *args*。 如果提供了额外的关键字参数，它们会扩展并重载 *keywords*。 大致等价于:

```python
def partial(func, /, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = {**keywords, **fkeywords}
        return func(*args, *fargs, **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc
```

例子：比如封装int，构造一个二进制转10进制的函数：

```python
from functools import partial
bin2dec = partial(int, base=2)
bin2dec.__doc__ = "Convert binary string to decimal int"
print(bin2dec("100100"))
```

输出：36

## wrapps

这是一个便捷更新 装饰器wrapper的函数，一般情况下，函数使用装饰器包装过后，调用 `func.__name__`输出的是装饰器的wrapper名称，如：

```python
def decorator(f):
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper
  
@decorator
def func():
    print('in func.')

print(func.__name__)
```

输出： wrapper

如果 decorator 加上了 wraps：

```python
from functools import wraps
def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper
  
@decorator
def func():
    print('in func.')

print(func.__name__)
```

输出：func

