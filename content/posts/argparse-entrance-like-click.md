---
title: "Argparse Entrance Like Click"
date: 2022-09-19T00:30:54+08:00
tags: []
categories: []
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

# 使用python argparse实现简单的click



[python3 argparse 文档](https://docs.python.org/zh-cn/3/library/argparse.html#module-argparse)

[python3 ArgParse教程](https://docs.python.org/zh-cn/3/howto/argparse.html#id1)

## 需求

实现一个类似click command的类，支持将函数作为命令注册进去，调用这个类的时候，解析命令行参数，执行对应的注册函数。

可以用装饰器的方法进行函数注册以及参数添加

类名： Entrance

方法：

- 注册： Entrance.register
- 参数：Entrance.option

## 实现

**entrance.py**

```python
# encoding: utf-8
"""the only entrance for the program"""
import argparse


class EntranceConflict(Exception):
    pass


class Entrance:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.sub_parser = self.parser.add_subparsers()
        self.entrances = {}

    def register(self, name=None):
        """ 注册一个函数作为入口
        可以指定name，否则默认使用函数的名字
        """
        def decorator(f):
            entrance_name = name or f.__name__
            if entrance_name in self.entrances:
                raise EntranceConflict(f"entrance {entrance_name} already registered.")
            # make parser
            _parser = self.sub_parser.add_parser(name=entrance_name)
            _params = f.__entrance_params__
            for _args, _kwargs in _params:
                _parser.add_argument(*_args, **_kwargs)
            _parser.set_defaults(processor=f)
            # add parser to entrances
            self.entrances[entrance_name] = _parser

            return f

        return decorator

    def option(self, *args, **kwargs):
        """ 注册一个函数的参数
        参数格式参考 argparse.ArgumentParser.add_argument
        """
        def decorator(f):
            # set tmp attrs for f
            if not hasattr(f, '__entrance_params__'):
                f.__entrance_params__ = []
            f.__entrance_params__.append((args, kwargs))
            return f

        return decorator

    def __call__(self, *args, **kwargs):
        args = self.parser.parse_args()
        # extrac args
        params = vars(args)
        processor = params.get('processor')
        if processor:
            del params['processor']
            return processor(**params)
        else:
            print('un processable entrance: {}'.format(args))
            self.parser.print_help()


entrance = Entrance()

```



## 调用

写一个简单的调用demo

**main.py**

```python
from entrance import entrance 


@entrance.register()
@entrance.option('--user-name', required=True)
@entrance.option('--age')
def add_user(user_name, age):
    print("Added user: {}, age={}".format(user_name, age))
    
    
@entrance.register()
@entrance.option('--user-id', required=True)
def del_user(user_id):
    print("deleted user whose id = {}".format(user_id))
    

if __name__ == '__main__':
    entrance()
```



运行

```bash
$ python main.py add_user --user-name Mike --age 19
Added user: Mike, age=19

$ python main.py del_user --user-id 10   
deleted user whose id = 10

```

