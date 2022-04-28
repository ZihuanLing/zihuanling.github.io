---
title: "LeetCode 179：最大数 -- 一道有点意思的题目"
date: 2022-04-28T22:24:12+08:00
tags: [leetcode, algorithm, python]
categories: [leetcode]
showToc: true
TocOpen: false
draft: false
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

今天做了一道有点意思的算法题目，在这里记录下。[提交记录](https://leetcode-cn.com/submissions/detail/306795694/)

## [leetcode 179: 最大数](https://leetcode-cn.com/problems/largest-number/)

给定一组非负整数 nums，重新排列每个数的顺序（每个数不可拆分）使之组成一个最大的整数。

注意：输出结果可能非常大，所以你需要返回一个字符串而不是整数。

 

示例 1：

输入：nums = [10,2]
输出："210"
示例 2：

输入：nums = [3,30,34,5,9]
输出："9534330"


提示：

1 <= nums.length <= 100
0 <= nums[i] <= 109

### 上最终AC代码：

```python
def greater(a, b):
    # 对比函数，a > b
    # a, b expect str
    return int(a + b) - int(b + a) > 0

# 快排
def pivot(arr, low, high):
    x = arr[high]
    j = low - 1
    for i in range(low, high):
        if greater2(arr[i], x):
            j += 1
            arr[i], arr[j] = arr[j], arr[i]
    j += 1
    arr[j], arr[high] = arr[high], arr[j]
    return j

def quick_sort(arr, low, high):
    if low < high:
        pi = pivot(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)

class Solution:
    def largestNumber(self, nums: List[int]) -> str:
        nums = [str(n) for n in nums]
        quick_sort(nums, 0, len(nums) - 1)
        if nums[0] == '0':
            return '0'
        return ''.join(nums)
```

*自己写一个快排有点多此一举的意思，完全可以用到python自带的sorted函数。*



## 分析

这是一道**中等**难度的题目，看到题目的第一眼，思路很简单：

1. 对数组排序
2. 将结果构造字符串返回

其主要难度在对数组的排序上，跟一般意义上的数值排序不一样，这不是简单的对比各自的数值，而是有一定规律的。

比如：`9 > 83 > 333`，一开始想到的是定义一个比较函数，用来做字符串的对比，写成这样：

```python
def greater(a, b):
    size_a, size_b = len(a), len(b)
    if size_a == size_b and a == b:
        return True
    mn = min(size_a, size_b)
    pre_a, pre_b = a[:mn], b[:mn]
    if pre_a == pre_b:
        # 前缀相等，尾部重新对比
        return greater(a[mn:], b) if size_a > size_b else greater(a, b[mn:])
    # 前缀不相等的情况
    elif pre_a > pre_b:
        return True
    else:
        return False
```

这里直接是用字符串对比的方式，来判断两个字符串的大小关系，比较繁琐。

然后用的是快排，自己写了个 `quick_sort`，用来对**nums数组**进行排序。这时候，我还不知道 有个叫`functools.cmp_to_key`的神奇东西，可以用来构建自己的比较器，传入`sorted`函数里面！

需要注意的是，数组里面可能**全部是0**，这是一个边界条件，这时候应该返回 0， 而不是0000之类的。

## 参考题解得到的惊人提示

### 提示1：使用 int(a + b)  - int(b + a) > 0

虽然提交的代码AC了，但是，看了下 [官方题解](https://leetcode-cn.com/problems/largest-number/solution/zui-da-shu-by-leetcode-solution-sid5/)，太强了，真是太强了！对于数学渣渣来说，看到的一通分析，完全蒙了。

大概可以总结为：

> 有两个非负整数x, y（字符串），想要对比他们拼接的字符串大小，可以直接用 int(x + y) - int(y + x) > 0 来判断x和y的拼接顺序。

有了这个，我就可以简化我的对比代码了：

```python
def greater(a, b):
    # 对比函数，a > b
    # a, b expect str
    return int(a + b) - int(b + a) > 0
```

惊呆了.jpg

将对比代码简化成了1行！数学和算法的魅力。。。

### 提示2：functools.cmp_to_key

本来对比较函数的优化已经让人惊讶了，然后我看到了这个：

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

满打满算，也就4行吧，看到用了 `cmp_to_key` 这个东西，我一开始寻思着： 这也没有定义，也没有import呀，哪儿来的

google一搜：`functools.cmp_to_key`，简单来说，这是一个可以把函数构造成 **可用于sorted排序的key **的函数，返回的是一个对象。

源代码定义如下：

```python
def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""
    class K(object):
        __slots__ = ['obj']
        def __init__(self, obj):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        __hash__ = None
    return K
```

有了这玩意儿，我之前写的快排可以说是浪费功夫（为啥没有早点遇上你）

## 最后

- 刷完题后，看一下官方或者是大神题解，可能有意想不到的收获，对自己的提升也是很大的

- python的functools看起来有很多有意思的东西，找个时间扒一扒！

