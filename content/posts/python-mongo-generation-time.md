---
title: "使用mongodb自带的ObjectID获取记录生成时间"
date: 2022-06-01T14:02:38+08:00
tags: [mongodb, python]
categories: [python]
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

有些时候，我们在写入mongo数据的时候，可能需要记录这条数据的插入时间，我们一般情况下回给记录增加一个 create_time。

实际上，如果我们插入的数据含有 `ObjectId` 的话，那么其实这个id是包含了生成时间的，同时也可以作为记录的主键，一举多得。

以python为例，我们有这样一条记录：

```python
document = {
    "_id": ObjectId("5dfc8ac5d3fa12967b8888ec"),
    "user": "mike",
    "age": 19,
}
```

这时候，我们可以使用`ObjectId`自带的`generation_time`属性，获取这条记录的插入时间：

```python
time = ObjectId("5dfc8ac5d3fa12967b8888ec").generation_time
print(time)
```

输出：

```
datetime.datetime(2019, 12, 20, 8, 48, 5, tzinfo=<bson.tz_util.FixedOffset object at 0x7f874030f9a0>)
```

需要注意到的是，里面的时区信息，显示的是一个 FixedOffset，即固定偏移，我们看 `generation_time` 属性的定义：

```python

utc = FixedOffset(0, "UTC")
"""Fixed offset timezone representing UTC."""

class ObjectId(object):
    # ... 省略其他代码 ...
    @property
    def generation_time(self):
        """A :class:`datetime.datetime` instance representing the time of
        generation for this :class:`ObjectId`.

        The :class:`datetime.datetime` is timezone aware, and
        represents the generation time in UTC. It is precise to the
        second.
        """
        timestamp = struct.unpack(">I", self.__id[0:4])[0]
        return datetime.datetime.fromtimestamp(timestamp, utc)
```

可以看到这个属性是从一个时间戳生成的，并且生成的时候指定了固定的 UTC-0 时区，而我们是处于**东八区**，因此，如果直接使用 `generation_time` 属性的话，得到的时间并非我们当前时区的时间，还需要做一个转化，只需要简单的对 `datetime.datetime` 对象调用**astimezone**方法，即可：

```python
ObjectId("5dfc8ac5d3fa12967b8888ec").generation_time.astimezone(None)
# output: datetime.datetime(2019, 12, 20, 16, 48, 5, tzinfo=datetime.timezone(datetime.timedelta(seconds=28800), 'CST'))
```

可以看到，现在输出的时间信息，跟之前的输出相差了8个小时。调用`astimezone`传入**None**的时候，就会默认转化为我们当前所在的时区（代码运行系统所在的时区，东8）

可能我们不想要看到输出这么一长串的信息，展示出来的时候去掉时区信息，我们可以调用 `replace` 方法：

```python
ObjectId("5dfc8ac5d3fa12967b8888ec").generation_time.astimezone(None).replace(tzinfo=None)
# output: datetime.datetime(2019, 12, 20, 16, 48, 5)
```

又或许，我们需要的只是一个整型的时间戳，可以这样做：

```python
import struct
from bson import ObjectId

oid = ObjectId("5dfc8ac5d3fa12967b8888ec")
timestamp = struct.unpack(">I", oid.binary[0:4])[0]
# timestamp = 1576831685
```
