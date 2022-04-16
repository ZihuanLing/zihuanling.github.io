---
title: "go: grpc和protobuf"
date: 2022-04-16T22:34:33+08:00
tags: [go, grpc, protobuf]
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

# gRPC

一个高性能、开源的通用RPC框架。

gPPC是一个现代的开源高性能的远程过程调用框架，并且可以运行在任何环境中。它可以有效地连接数据中心内和跨数据中心的服务，支持负载均衡、跟踪、健康检查和身份验证。它也适用于分布式计算的最后一英里，将设备、移动应用程序和浏览器连接到后端服务。

> gRPC is a modern open source high performance Remote Procedure Call (RPC) framework that can run in any environment. It can efficiently connect services in and across data centers with pluggable support for load balancing, tracing, health checking and authentication. It is also applicable in last mile of distributed computing to connect devices, mobile applications and browsers to backend services.

github 地址： https://github.com/grpc/grpc

原来是用 `C++` 写的，后来也有了go语言版本：https://github.com/grpc/grpc-go

# gRPC 和 go

gPPC支持多个语言和平台，包括GO、Python、C++、Nodejs等，我们接下来学习的是使用go来体验一下gRPC的功能。

学习地址：https://www.grpc.io/docs/languages/go/quickstart/

## 前期准备：

### golang安装

### protobuf 编译器，`protoc`，第三个版本

之前已经简单体验过了protobuf： [文章：go-proto](http://lingzihuan.icu/posts/go-proto/)

### 安装支持go语言的protoc编译器插件

```bash
$ go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28
$ go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2
```



ok，至此，前期的环境准备就绪，我们可以开始体验golang版本的gRPC了。

我们接下来使用上次写的protobuf学习例子，修改一下，让其可以用上gRPC。



## 上手体验

#### 编译命令

```bash
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-gprc_opt=paths=source_relative proto/media.proto
```

相比上次的单纯编译protobuf，我们这次添加对grpc的支持，主要是新增了两个flag：`--go-grpc_out=. --go-grpc_opt=paths=source_relative`

运行上面的编译命令，我们发现，当前的路径下并没有生成别的东西，这是因为，我们的proto中没有定义grpc相关的服务。



#### 定义gRPC服务

我们可以在proto文件中这样写：

proto/media.proto

```protobuf
// 上传的请求体
message UploadRequest {
  Picture pic = 1;
}
// 上传图片的响应体
message UploadReply {
  int32 status = 1;
  string msg = 2;
}

// 定义一个rpc多媒体服务
service Media {
  rpc UploadPicture(UploadRequest) returns (UploadReply) {}
}
```

我们上次定义了一个名为 `Picture` 的message，用来表示图片消息，这次，我们新增了两个消息，`UploadRequest`和`UploadReply`，分别表示上传的消息内容和返回的上传结果。

另外定义了一个服务：`Media`，里面有一个方法 `UploadPicture`，用于上传图片。

重新运行`protoc`编译命令，就会看到，proto目录下，生成了一个 `media_grpc.pb.go`文件，里面实现了我们在proto文件中定义的gRPC服务。



#### 实现rpc服务的逻辑

我们在proto文件中定义了相关的协议，以及服务。同时编译也生成了对应的服务代码，但是，生成的代码只是我们服务的一个抽象，而具体的业务处理逻辑，还需要我们自己去实现。

server/server_main.go

```go
// 实现媒体服务
type server struct {
	proto.UnimplementedMediaServer
}

// UploadPicture 实现上传图片接口
func (s *server) UploadPicture(ctx context.Context, req *proto.UploadRequest) (*proto.UploadReply, error) {
	log.Println("Processing upload picture request.")
	picture := req.GetPic()
	log.Printf("Got picture: %v\n", picture)
	return &proto.UploadReply{
		Status: 1,
		Msg:    "Good job.",
	}, nil
}

func main() {
	l, _ := net.Listen("tcp", ":8099")
	s := grpc.NewServer()
	proto.RegisterMediaServer(s, &server{})
	log.Printf("Server listening at: %v\n", l.Addr())
	if err := s.Serve(l); err != nil {
		log.Fatalf("server error: %v\n", err)
	}
}
```

上述代码中，我们通过组合 `proto.UnimplementedMediaServer`，来实现抽象的MediaServer接口，然后再实现 `UploadPicture`这个方法，方法很简单，我们从请求体中获取对应的数据，打印出来，然后给客户端返回一句 “good job”。

然后是开启服务，这里的关键句是 `s := grpc.NewServer` 来实例化一个grpc服务，然后调用 `proto.RegisterMediaServer` 来向这个grpc服务中注册我们定义的媒体服务。最后，`s.Serve`开启服务。

#### 实现客户端调用

客户端的调用相对来说简单，不需要再去实现什么接口，只要简单的向连接中发送请求即可

```go
func main() {
	conn, err := grpc.Dial("localhost:8099", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("gRPC failed to dial, error: %v", err)
	}
	defer conn.Close()
	client := proto.NewMediaClient(conn)
	pic := &proto.Picture{
		Name: "pandas",
		Type: proto.Picture_JPG,
		Data: []byte{1, 2, 3, 4, 5, 6, 7},
	}
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	req := proto.UploadRequest{Pic: pic}
	resp, err := client.UploadPicture(ctx, &req)
	if err != nil {
		log.Fatalf("client call grpc service error: %v", err)
	}
	log.Printf("rpc response message: %v\n", resp.GetMsg())
}
```

客户端中，我们这次使用 `grpc.Dial`来向服务端发起一个连接，然后第二个参数是 `grpc.WithTransportCredentials(insecure.NewCredentials())`，意味着向服务端发起请求需要进行一定的验证。（？）

然后直接调用 `proto.UploadPicture`，即可向服务端中发送上传图片请求。

#### 运行

运行上述代码

服务端输出：

```
2022/04/17 00:00:25 Server listening at: [::]:8099
2022/04/17 00:10:07 Processing upload picture request.
2022/04/17 00:10:07 Got picture: name:"pandas"  type:JPG  data:"\x01\x02\x03\x04\x05\x06\x07"
```

客户端输出：

```
2022/04/17 00:10:07 rpc response message: Good job.
```

可以看到，表现符合预期。



## 总结

想要在go上使用grpc，有以下几个主要步骤：

1. 前期准备，golang、protobuf编译器（protoc）、两个go语言的protobuf插件：protoc-gen-go、protoc-gen-go-grpc
2. 编写服务的protobuf代码，需要使用`service`关键字，去定义一个grpc服务
3. 使用protoc编译proto文件，生成go代码，编译参数为：`protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative`
4. 服务端实现对应的服务逻辑，并开启grpc服务。生成的只是简单的服务代码，以及服务接口，我们在proto中定义的rpc服务具体业务逻辑并没有被实现，还需要我们手动实现具体的服务接口，然后，使用 `proto.RegisterMediaServer`来向对应的grpc服务中注册我们自己实现的服务
5. 客户端发起连接，需要使用`grpc.Dial`，并且第二个参数传 `grpc.WithTransportCredentials(insecure.NewCredentials())`，否则会报错。

 