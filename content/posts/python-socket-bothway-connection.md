---
title: "使用python socket实现双向的tcp通信"
date: 2022-04-22T13:53:32+08:00
tags: [socket]
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

很久之前玩过的python socket，今天用来做个双向的通信程序。

### 服务端代码：

server.py
```python
# coding: utf-8
# tcp stream server
import socket
import logging
import time
import datetime as dt
from threading import Thread, currentThread
# 配置logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(process)s %(threadName)s |%(message)s",
)


class Server:
    """ socket 服务端 """
    def __init__(self, host='localhost', port=8099):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind((host, port))
        self.msg = None

    def read(self, conn: socket.socket = None):
        """ 从tcp连接里面读取数据 """
        while True:
            try:
                data = conn.recv(1024).decode()
            except Exception as e:
                logging.info("recv failed: %s", e)
                return
            logging.info("[R %s]<< %s", currentThread().getName(), data)
            self.msg = data
            time.sleep(1)

    def write(self, conn: socket.socket = None):
        """ 向tcp连接里面写入数据 """
        while True:
            msg = f"{dt.datetime.now()} - {self.msg}"
            logging.info("[W %s]>> %s", currentThread().getName(), msg)
            try:
                conn.send(msg.encode())
            except Exception as e:
                logging.info("send failed: %s", e)
                return
            time.sleep(1)

    def serve(self):
        """ 开启服务 """
        self._sock.listen()
        logging.info("Serving...")
        while True:
            logging.info("Waiting for connection...")
            conn, addr = self._sock.accept()
            logging.info("Recived new conn: %s from %s", conn, addr)
            # 开启读写线程处理当前连接
            Thread(target=self.read, args=(conn, )).start()
            Thread(target=self.write, args=(conn, )).start()


if __name__ == '__main__':
    s = Server()
    s.serve()

```

以上就是服务端代码，简单的开启了一个socket服务器，接受连接，然后开启两个线程，每隔一秒，同时向连接中读写数据。

当然，这个读写可能不是同时发生的。


### 客户端代码

client.py
```python
# coding: utf-8
# tcp stream client
import socket
import logging
import time
import os
from threading import Thread, currentThread

# 配置logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(process)s %(threadName)s |%(message)s",
)


class Client:
    """ socket 客户端 """
    def __init__(self, host='localhost', port=8099):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._addr = (host, port)

    def read(self):
        """ 向连接中接受数据 """
        while True:
            try:
                data = self._sock.recv(1024).decode()
            except Exception as e:
                logging.info("recv failed: %s", e)
                return
            logging.info("[R %s]<< %s", currentThread().getName(), data)
            time.sleep(1)

    def write(self):
        """ 向连接中发送随机数 """
        while True:
            msg = os.urandom(4).hex()
            logging.info("[W %s]>> %s", currentThread().getName(), msg)
            try:
                self._sock.send(msg.encode())
            except Exception as e:
                logging.info("send failed: %s", e)
                return
            time.sleep(1)

    def run(self):
        """ 开启连接 """
        self._sock.connect(self._addr)
        logging.info("New connection: %s", self._sock)
        r = Thread(target=self.read)
        r.start()
        w = Thread(target=self.write)
        w.start()
        r.join()
        w.join()


if __name__ == '__main__':
    client = Client()
    client.run()

```

客户端同服务端是一样的，向服务端发起一个连接，然后启用两个线程，每隔一秒向连接中发送/接受数据


### 运行

运行server和client，就可以看到了正常的输出：

服务端输出
```
$ python server.py
2022-04-22 14:22:11,901 INFO 76227 MainThread |Serving...
2022-04-22 14:22:11,901 INFO 76227 MainThread |Waiting for connection...
2022-04-22 14:22:20,788 INFO 76227 MainThread |Recived new conn: <socket.socket fd=6, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 8099), raddr=('127.0.0.1', 56814)> from ('127.0.0.1', 56814)
2022-04-22 14:22:20,789 INFO 76227 Thread-2 |[W Thread-2]>> 2022-04-22 14:22:20.789066 - None
2022-04-22 14:22:20,789 INFO 76227 MainThread |Waiting for connection...
2022-04-22 14:22:20,789 INFO 76227 Thread-1 |[R Thread-1]<< 8903a9aa
2022-04-22 14:22:21,793 INFO 76227 Thread-2 |[W Thread-2]>> 2022-04-22 14:22:21.793070 - 8903a9aa
```

客户端输出
```
$ python client.py
2022-04-22 14:22:20,788 INFO 76320 MainThread |New connection: <socket.socket fd=3, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 56814), raddr=('127.0.0.1', 8099)>
2022-04-22 14:22:20,789 INFO 76320 Thread-3 |[W Thread-3]>> 8903a9aa
2022-04-22 14:22:20,789 INFO 76320 Thread-2 |[R Thread-2]<< 2022-04-22 14:22:20.789066 - None
2022-04-22 14:22:21,793 INFO 76320 Thread-3 |[W Thread-3]>> 5606048f
2022-04-22 14:22:21,793 INFO 76320 Thread-2 |[R Thread-2]<< 2022-04-22 14:22:21.793070 - 8903a9aa
```

工作正常，看起来是没有问题的。 


### 优化

#### 线程化客户端

将每个客户端作为一个线程，然后同时开启多个

client.py
```python
class Client(Thread):
    pass

if __name__ == '__main__':
    cs = [Client() for _ in range(3)]
    for c in cs:
        c.start()
    for c in cs:
        c.join()
```

#### 优化服务端

服务端，有个`msg`变量是线程冲突的，存在资源抢夺问题，我们使用信息池，不同连接的信息独立存储

server.py
```python
class Server:
    def __init__(self, host='localhost', port=8099):
        # ...
        self.msg = {}

    def read(self, conn: socket.socket = None):
        # ...
        self.msg[conn.fileno()] = data

    def write(self, conn: socket.socket = None):
        # ...
        msg = f"{dt.datetime.now()} - {self.msg.get(conn.fileno())}"

    def serve(self):
        # ...
        while True:
            # ...
            conn, addr = self._sock.accept()
            self.msg[conn.fileno()] = ''
            # ...
```


### 搞个聊天服务程序

想要干什么？

搞一个类似微信聊天服务器一样的东西，主要用作消息的中转，客户端通过服务端，发现其他用户，并向其他用户发送消息。

就像这样：

```mermaid
graph LR

client1 --> server --> client2
client2 --> server --> client1
```

需要解决哪些问题：

- 怎么存储一个连接
- 制定用户的在线机制（连接超时）
- 用户认证？（没必要搞这么复杂）

其他。。。。待续。
