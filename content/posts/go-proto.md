---
title: "go 和 protobuf"
date: 2022-04-14T21:14:52+08:00
tags: [go, protobuf]
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



# Google protocol buffers

简称`protobuf`，它是谷歌提供的跨语言，跨平台的，可扩展的用来将结构化的数据进行序列化的一种机制。就像**XML**，但是更加精简、快速和简单。我们可以先预先定义我们的协议（写到一个 `.proto` 文件里面），里面声明了我们需要怎么去将数据结构化，然后，我们可以使用这份proto，去生成我们指定的语言源代码文件，我们就能够很方便地从各种数据流中读取结构化数据，或者是写入结构化数据。并且是跨语言的。

> Protocol buffers are Google's language-neutral, platform-neutral, extensible mechanism for serializing structured data – think XML, but smaller, faster, and simpler. You define how you want your data to be structured once, then you can use special generated source code to easily write and read your structured data to and from a variety of data streams and using a variety of languages.



# 安装protoc编译器

`.proto`文件只是我们定义的协议文件，一般来讲，编程语言是不能直接使用这份文件的（除非是自己针对proto写一个自定义的解析逻辑，但是没人会这么闲），我们想要的，应该是简单高效的开发，可以即写即用那种。

因此，我们使用特定的编程语言编写服务时，需要将我们定义的 `.proto` 文件翻译（编译）成为对应的语言文件，这时，google 给我们提供了 protoc。

### 下载

我们可以在这个地方下载： [protobuf v3.20.0](https://github.com/protocolbuffers/protobuf/releases/tag/v3.20.0) ，里面有很多的版本，我们可以找到对应的平台。

### 安装

将其解压之后，我们得到一个 `bin`目录，里面有一个 `protoc`的可执行文件，我们将其添加到环境变量中的`Path`中去，这样，我们就可以在终端中运行`protoc`命令了。

### 验证安装

我们添加完环境变量后，打开一个新的终端，我们输入以下命令来验证一下安装是否成功：

```
>protoc --version
libprotoc 3.20.0
```



# 编写自己的protobuf协议

我想要实现一个协议，可以传输多媒体数据，且后端是用go写的。

首先创建一个项目，名为 `learnProto`，表示这是我用来学习`protobuf`的练手项目。然后创建一个`proto`文件夹，用来存放我们的`proto`文件。

```protobuf
// learnProto/proto/media.proto
syntax = "proto3";

message Picture {
  string name = 1;  // 图片的名称
  enum PicTypes {
    PNG = 0;
    JPG = 1;
    JPEG = 2;
    BMQ = 3;
  }
  PicTypes type = 2;  // 图片类型
  bytes data = 3;     // 图片数据
}
```

首先我们需要在文件的开始位置，写上 `syntax = "proto3"`，说明这个proto是用的proto3版本。

上述proto文件中，我们定义了一个消息的结构：图片

这个消息的结构有3个字段：

- 名称：使用的是string类型
- 类型：我们自定义了一个枚举类型，用来表示允许进行传输的图片格式
- 数据：图片的数据应该是字节类型的

这样，我们就写好了自己的proto协议，我们将要使用这个协议来进行图片文件的传输。

## 编译协议

**重要：**我们需要使用go来实现后端，然后使用编写的proto来实现数据的传输，这样，我们就需要给proto文件加上两行声明：

- 第一行：告诉protoc编译器，这个proto文件编译成go文件之后，将要属于哪个包： `package proto`
- 第二行：告诉protoc编译器，这个proto文件当前的位置： `option go_package="learnProto/proto"`

proto文件改成了：

```protobuf
syntax = "proto3";

package proto;
option go_package="learnProto/proto";
// ... 省略 
```

目前，我们的项目结构是长这样的：

```
learnProto/
  proto/
    media.proto
  go.mod
```

接下来我们使用**protoc**进行编译：

```bash
protoc --proto_path=. --go_out=. --go_opt=paths=source_relative proto/media.proto
```

命令运行之后，将会在 proto 文件夹下生成一个 `media.pb.go` 的文件，这个，就是我们通过 protoc 将 proto文件编译成的go文件。



# 使用protobuf

## 编写go服务端

```go
// learnProto/server/server_main.go
package main

import (
	bf "google.golang.org/protobuf/proto"
	"learnProto/proto"
	"log"
	"net"
)

func main() {
	l, _ := net.Listen("tcp", ":8099")
	for {
		conn, _ := l.Accept()
		log.Println("Received on connection.")
		// read all from connection
		_data := make([]byte, 1024)
		if n, err := conn.Read(_data); err != nil {
			log.Fatalf("Read error: %s", err)
		} else {
			log.Printf("%d bytes read\n", n)
		}
		message := &proto.Picture{}
		bf.Unmarshal(_data, message)
		log.Printf("data: %v", message)
	}
}

```

服务端的代码简单，我们定义一个TCP服务端，监听8099端口，从里面获取数据，通过proto将其转化成为对应的结构体。

由于是简单的使用proto，我们暂时不考虑里面传输的数据长度，直接构建一个1024长度的byte切片，从连接里面读取数据。然后使用 `bf.Unmarshal` 将里面的字节码数据反序列化为 `proto.Picture`结构体

后续可以优化这块，比如约定开始传送的是一个长度为 `HEADER_SIZE` 的数据，里面声明了我们本次传输的内容是图片还是视频，然后接下来的数据有多大，等。



## 编写go客户端

```go
// learnProto/client/client_main.go
package main

import (
	bf "google.golang.org/protobuf/proto"
	"learnProto/proto"
	"log"
	"net"
	"time"
)

func main() {
	conn, _ := net.Dial("tcp", "localhost:8099")
	message := &proto.Picture{
		Name: "pandas",
		Type: proto.Picture_JPG,
		Data: []byte{1, 2, 3, 4, 5, 6, 7},
	}
	msg, _ := bf.Marshal(message)
	n, err := conn.Write(msg)
	if err != nil {
		log.Fatalf("Error write to connectin: %s", err)
	}
	log.Printf("%d bytes wrote.", n)
	time.Sleep(time.Second)
}
```

客户端，我们使用 `net.Dial` 向服务端发起连接，然后构造一个假的 `Picture`消息，图片的名称为 **pandas**，图片的类型是 **JPG**，然后内容是随便给几个字节。

然后，使用 `bf.Marshal`，将结构体数据序列化成为字节 `[]byte`,通过tcp连接发送到客户端。

随后休眠一秒，防止连接提前终端而导致服务端数据读取失败。

## 运行

运行上述代码

客户端输出：

```
2022/04/14 23:42:00 19 bytes wrote.
```

服务端输出：

```
2022/04/14 23:42:00 Received on connection.
2022/04/14 23:42:00 19 bytes read
2022/04/14 23:42:00 data: name:"pandas"  type:JPG  data:"\x01\x02\x03\x04\x05\x06\x07"
```

可以看到，服务端收到了客户端发送的message，并且正确地将其序列化成为了 `proto.Picture`对象。

## 改进

### 服务端可做改进：

考虑新增消息类型的时候，可以通过使用约定 **HEADER** 的方式，来确定接下来发送的消息属于什么类型，以及消息的长度等。

接收到媒体信息的时候，将数据保存起来。

使用 goroutine改造，支持并发处理多个请求。



### 客户端可做改进：

图片的数据可以直接从文件或者数据库读取

自动解析图片的名称、格式等