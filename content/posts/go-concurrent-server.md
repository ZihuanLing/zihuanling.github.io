---
title: "go：简简单单的并发网络连接"
date: 2022-04-06T20:45:19+08:00
tags: [go]
categories: [go]
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

go 是天生支持并发的，我们只要 使用 `go func()` 就可以快速实现并发。在网络服务的处理中，实现并发可以大大提高服务的吞吐量，我们来研究一下。

## 简单的TCP服务器

我们先来实现一个简单的tcp服务，监听8989端口，从连接中读取一段数据，这段数据表示的是当前请求的id，然后返回一段话。

### 服务器

server/main.go

```go
package main

import (
	"fmt"
	"log"
	"net"
)

func main() {
	// 启动tcp连接，监听8989端口
	l, err := net.Listen("tcp", ":8989")
	if err != nil {
		log.Fatalf("Server listening error: %s\n", err)
	}
	for {
		conn, err := l.Accept()
		if err != nil {
			log.Printf("Accept error: %s\n", err)
			continue
		}
		// 接收连接,调用handleConn处理当前连接
		handleConn(conn)
	}
}

func handleConn(conn net.Conn) {
	defer conn.Close()		// 优雅关闭连接
	data := make([]byte, 4)
	conn.Read(data)
	log.Printf("Recieved connection from %s, ID[%s]\n", conn.RemoteAddr(), data)
	// 向客户端返回一句 Hello World
	if n, err := conn.Write([]byte(fmt.Sprintf("Hello world! -> ID[%s]", data))); err != nil {
		log.Printf("Write error: %s | %s\n", err, conn.RemoteAddr())
	} else {
		log.Printf("%d bytes wrote for ID[%s]", n, data)
	}
}
```

服务器简单，直接启动一个tcp服务，监听8989端口，然后接收到客户端连接的时候，从连接中获取当前请求的ID，然后向当前客户端返回一句 `Hello World`

### 客户端

client/main.go

```go
func main() {
	reqTCP(2)
}

func reqTCP(id int) {
	conn, err := net.Dial("tcp", "localhost:8989")
	if err != nil {
		log.Printf("Dial tcp error: %s\n", err)
		return
	}
	// 写入当前请求ID
	if _, err := conn.Write([]byte(strconv.Itoa(id))); err != nil {
		log.Printf("Conn write error: %s\n", err)
		return
	}
	data := make([]byte, 100) // 返回的内容应该不会超过100字节
	if _, err := conn.Read(data); err != nil {
		log.Printf("Conn read error: %s\n", err)
		return
	}
	log.Printf("Recieved from server: %s\n", data)
}
```

客户端要做的事情，就是向服务端拨号，然后发送一个请求ID，最后从服务端获取返回的数据，并打印出来。

### 运行

运行 `server/main.go`

```bash
go run server/main.go
```

运行 `client/main.go`

```bash
go run client/main.go
```

**客户端**输出：

```
2022/04/06 21:13:50 Recieved from server: Hello world! -> ID[2]
```

**服务端**输出：

```
2022/04/06 21:13:50 Recieved connection from [::1]:64088, ID[2]
2022/04/06 21:13:50 24 bytes wrote for ID[2]
```

客户看到，一个简单的TCP服务器就实现了。

## 并发的请求

一般情况下，服务器并不会仅处理一个请求，而是多个请求一起处理，这就要求我们的服务器有很好的并发处理能力。

改动 `client/main.go`，让其进行并发请求：

```go
func main() {
	nReq := 10 // 10个并发请求
	var wg sync.WaitGroup
	wg.Add(nReq)
	for i := 0; i < nReq; i++ {
		go func(n int) {
			defer wg.Done()
			reqTCP(n)
		}(i)
	}
	wg.Wait()
}
// 省略其他代码...
```

此时直接运行的话，可以看到输出：

```
客户端输出：
----
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[7]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[8]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[9]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[6]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[5]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[2]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[0]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[3]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[1]
2022/04/06 21:30:10 Recieved from server: Hello world! -> ID[4]

服务端输出：
----
2022/04/06 21:30:10 Recieved connection from [::1]:56405, ID[7]
2022/04/06 21:30:10 24 bytes wrote for ID[7]
2022/04/06 21:30:10 Recieved connection from [::1]:56406, ID[8]
2022/04/06 21:30:10 24 bytes wrote for ID[8]
2022/04/06 21:30:10 Recieved connection from [::1]:56408, ID[9]
2022/04/06 21:30:10 24 bytes wrote for ID[9]
2022/04/06 21:30:10 Recieved connection from [::1]:56409, ID[6]
2022/04/06 21:30:10 24 bytes wrote for ID[6]
2022/04/06 21:30:10 Recieved connection from [::1]:56407, ID[5]
2022/04/06 21:30:10 24 bytes wrote for ID[5]
2022/04/06 21:30:10 Recieved connection from [::1]:56404, ID[2]
2022/04/06 21:30:10 24 bytes wrote for ID[2]
2022/04/06 21:30:10 Recieved connection from [::1]:56412, ID[0]
2022/04/06 21:30:10 24 bytes wrote for ID[0]
2022/04/06 21:30:10 Recieved connection from [::1]:56411, ID[3]
2022/04/06 21:30:10 24 bytes wrote for ID[3]
2022/04/06 21:30:10 Recieved connection from [::1]:56410, ID[1]
2022/04/06 21:30:10 24 bytes wrote for ID[1]
2022/04/06 21:30:10 Recieved connection from [::1]:56413, ID[4]
2022/04/06 21:30:10 24 bytes wrote for ID[4]
```

从输出可以看到，我们并发发起了10个请求，这些请求的时间间隔可能很小很小，可以看做是同时发起的，服务器接收到请求和返回数据的顺序和客户端打印的结果是一致的。但是由于程序处理太快，所有请求都在一瞬间处理完成了，不能体现出某些较耗时的操作情况下，客户端的等待情况。

改造服务端，让其返回数据前 Sleep 一秒

`server/main.go`

```go
func handleConn(conn net.Conn) {
	defer conn.Close() // 优雅关闭连接
	data := make([]byte, 4)
	conn.Read(data)
	log.Printf("Recieved connection from %s, ID[%s]\n", conn.RemoteAddr(), data)
	time.Sleep(time.Second)		// 返回前 Sleep 1秒
	// 向客户端返回一句 Hello World
	if n, err := conn.Write([]byte(fmt.Sprintf("Hello world! -> ID[%s]", data))); err != nil {
		log.Printf("Write error: %s | %s\n", err, conn.RemoteAddr())
	} else {
		log.Printf("%d bytes wrote for ID[%s]", n, data)
	}
}
```

重新运行，客户端输出：

```
2022/04/06 21:36:21 Recieved from server: Hello world! -> ID[9]
2022/04/06 21:36:22 Recieved from server: Hello world! -> ID[2]
2022/04/06 21:36:23 Recieved from server: Hello world! -> ID[4]
2022/04/06 21:36:24 Recieved from server: Hello world! -> ID[5]
2022/04/06 21:36:25 Recieved from server: Hello world! -> ID[7]
2022/04/06 21:36:27 Recieved from server: Hello world! -> ID[8]
2022/04/06 21:36:28 Recieved from server: Hello world! -> ID[6]
2022/04/06 21:36:29 Recieved from server: Hello world! -> ID[0]
2022/04/06 21:36:30 Recieved from server: Hello world! -> ID[1]
2022/04/06 21:36:31 Recieved from server: Hello world! -> ID[3]
```

可以看到，客户端是每间隔**1秒**打印一条记录，说明此时服务端对请求的处理是串行的，一次只处理一个连接。

## 并发的服务

接下来，我们对服务器进行改造，让其实现一次性处理多个连接

`server/main.go`

```go
func main() {
	// 启动tcp连接，监听8989端口
	l, err := net.Listen("tcp", ":8989")
	if err != nil {
		log.Fatalf("Server listening error: %s\n", err)
	}
	for {
		conn, err := l.Accept()
		if err != nil {
			log.Printf("Accept error: %s\n", err)
			continue
		}
		// 接收连接,调用handleConn处理当前连接
		// 使用go关键字，直接并发处理
		go handleConn(conn)
	}
}
// 省略其他...
```

服务端的并发非常简单！直接使用  `go handleConn(conn)` 即可让程序对当前连接的处理进入并发。

重新运行服务端、客户端

客户端输出：

```
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[6]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[5]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[1]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[3]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[9]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[7]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[2]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[4]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[0]
2022/04/06 21:42:38 Recieved from server: Hello world! -> ID[8]
```

服务端输出：

```
2022/04/06 21:42:37 Recieved connection from [::1]:56841, ID[3]
2022/04/06 21:42:37 Recieved connection from [::1]:56839, ID[7]
2022/04/06 21:42:37 Recieved connection from [::1]:56844, ID[1]
2022/04/06 21:42:37 Recieved connection from [::1]:56843, ID[9]
2022/04/06 21:42:37 Recieved connection from [::1]:56840, ID[4]
2022/04/06 21:42:37 Recieved connection from [::1]:56842, ID[2]
2022/04/06 21:42:37 Recieved connection from [::1]:56847, ID[5]
2022/04/06 21:42:37 Recieved connection from [::1]:56845, ID[0]
2022/04/06 21:42:37 Recieved connection from [::1]:56846, ID[8]
2022/04/06 21:42:37 Recieved connection from [::1]:56848, ID[6]
2022/04/06 21:42:38 24 bytes wrote for ID[1]
2022/04/06 21:42:38 24 bytes wrote for ID[6]
2022/04/06 21:42:38 24 bytes wrote for ID[0]
2022/04/06 21:42:38 24 bytes wrote for ID[7]
2022/04/06 21:42:38 24 bytes wrote for ID[2]
2022/04/06 21:42:38 24 bytes wrote for ID[4]
2022/04/06 21:42:38 24 bytes wrote for ID[9]
2022/04/06 21:42:38 24 bytes wrote for ID[5]
2022/04/06 21:42:38 24 bytes wrote for ID[3]
2022/04/06 21:42:38 24 bytes wrote for ID[8]
```

可以看到，服务端是在同一时间接收到了所有请求，而且也在同一时间进入到了 `handleConn`函数，进行处理，在**1秒**后，所有连接都返回了对应的内容。非常简单的实现了并发！

## 并发的HTTP

`server/main.go`

```go
func main() {
	// 启动tcp连接，监听8989端口
	l, err := net.Listen("tcp", ":8989")
	if err != nil {
		log.Fatalf("Server listening error: %s\n", err)
	}
	http.HandleFunc("/hello", httpHandler)
	http.Serve(l, nil)
}

func httpHandler(resp http.ResponseWriter, req *http.Request) {
	id := req.URL.Query().Get("id")
	log.Printf("Request from %s, method[%s], ID[%s]\n", req.RemoteAddr, req.Method, id)
	time.Sleep(time.Second)
	fmt.Fprintf(resp, fmt.Sprintf("Hello http -> ID[%s]", id))
	log.Printf("Done ID[%s]", id)
}
```

`client/main.go`

```go

func main() {
	nReq := 10 // 10个并发请求
	var wg sync.WaitGroup
	wg.Add(nReq)
	for i := 0; i < nReq; i++ {
		go func(n int) {
			defer wg.Done()
			reqHTTP(n)
		}(i)
	}
	wg.Wait()
}

func reqHTTP(id int) {
    // 简单的http Get
	resp, err := http.Get("http://localhost:8989/hello?id=" + strconv.Itoa(id))
	if err != nil {
		log.Printf("Http request error: %s\n", err)
		return
	}
	data := make([]byte, resp.ContentLength)
	resp.Body.Read(data)
	log.Printf("Http response: %s\n", data)
}
```

运行 服务端和客户端，输出：

```
客户端：
----
2022/04/06 22:12:45 Http response: Hello http -> ID[4]
2022/04/06 22:12:45 Http response: Hello http -> ID[2]
2022/04/06 22:12:45 Http response: Hello http -> ID[3]
2022/04/06 22:12:45 Http response: Hello http -> ID[1]
2022/04/06 22:12:45 Http response: Hello http -> ID[5]
2022/04/06 22:12:45 Http response: Hello http -> ID[0]
2022/04/06 22:12:45 Http response: Hello http -> ID[9]
2022/04/06 22:12:45 Http response: Hello http -> ID[8]
2022/04/06 22:12:45 Http response: Hello http -> ID[6]
2022/04/06 22:12:45 Http response: Hello http -> ID[7]

服务端：
----
2022/04/06 22:12:44 Request from [::1]:59686, method[GET], ID[9]
2022/04/06 22:12:44 Request from [::1]:59684, method[GET], ID[1]
2022/04/06 22:12:44 Request from [::1]:59685, method[GET], ID[8]
2022/04/06 22:12:44 Request from [::1]:59680, method[GET], ID[6]
2022/04/06 22:12:44 Request from [::1]:59688, method[GET], ID[4]
2022/04/06 22:12:44 Request from [::1]:59683, method[GET], ID[2]
2022/04/06 22:12:44 Request from [::1]:59687, method[GET], ID[3]
2022/04/06 22:12:44 Request from [::1]:59681, method[GET], ID[0]
2022/04/06 22:12:44 Request from [::1]:59682, method[GET], ID[5]
2022/04/06 22:12:44 Request from [::1]:59689, method[GET], ID[7]
2022/04/06 22:12:45 Done ID[4]
2022/04/06 22:12:45 Done ID[2]
2022/04/06 22:12:45 Done ID[3]
2022/04/06 22:12:45 Done ID[1]
2022/04/06 22:12:45 Done ID[5]
2022/04/06 22:12:45 Done ID[0]
2022/04/06 22:12:45 Done ID[9]
2022/04/06 22:12:45 Done ID[8]
2022/04/06 22:12:45 Done ID[6]
2022/04/06 22:12:45 Done ID[7]
```

可以看到，go http是天然并发的。

