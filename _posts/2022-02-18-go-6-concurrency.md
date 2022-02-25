---
layout: post
title: "6. go并发：Goroutines和Channels的声明和使用"
date: 2022-02-18
tags: [go]
comments: false
author: ZihuanLing
---

并发，就是让程序在同一时刻做多件事情。

go语言天生自带并发属性，使得并发编程**十！分！方！便！**，我们只需要 `go 函数名()` 即可！`\(^o^)/`

<!-- more -->

## 进程和线程

### 进程
程序启动时，系统会为其创建一个进程

### 线程
是进程的执行空间，一个进程可以包含多个线程，线程被操作系统调度执行
一个程序启动，对应的进程会被创建，同时也会创建一个线程（主线程），主线程结束，整个程序也就退出了。
我们可以从主线程创建其他的子线程，这就是多线程并发

### 协程 Goroutine
goroutine比线程更加轻盈，被Go runtime调度。
启动协程： `go function()`

```go
// 这里启动了两个goroutine， 一个是用go关键字触发的，另一个是 main goroutine（主线程）
func main(){
  go fmt.Println("Hello goroutine.")
  fmt.Println("Main goroutine.")
  time.Sleep(time.Second)
}
```

## Channel

多个goroutine之间，使用 channel进行通信

### 声明一个channel
```go
// 直接使用 make 创建一个channel，接受的数据类型是string
ch := make(chan string)
// 一个channel的操作只有两种：
// - 发送，向chan中发送值： chan<-
// - 接受，从chan中获取值： <-chan
```

demo

```go
func main(){
  ch := make(chan string)
  go func(){
    fmt.Println("Message in goroutine")
    ch <- "goroutine finished."	// send message to channel.
  }()
  fmt.Println("Main goroutine.")
  v := <-ch		// receive message from channel
  fmt.Println("Message from channel: ", v)
}
```

> 在上面的示例中，我们在新启动的 goroutine 中向 chan 类型的变量 ch 发送值；在 main goroutine 中，从变量 ch 接收值；如果 ch 中没有值，则**阻塞**等待到 ch 中有值可以接收为止。
>
> 通过 make 创建的 chan 中没有值，而 main goroutine 又想从 chan 中获取值，获取不到就一直等待，等到另一个 goroutine 向 chan 发送值为止。
>
> channel 有点像在两个 goroutine 之间架设的管道，一个 goroutine 可以往这个管道里发送数据，另外一个可以从这个管道里取数据，有点类似于我们说的队列。

### 无缓冲channel

上述的channel就是一个无缓冲的channel，容量为0，无法存储数据，只能传输。
它的发送和接受操作是同时的，可以称为**同步channel**

### 有缓冲channel

类似一个可阻塞的队列，内部的元素先进先出，通过make第二个参数指定channel容量大小：
```go
ch := make(chan int, 5)  // 创建一个容量为5的channel
```

上述创建一个容量为5的channel，可以存放最多5个int类型的元素，其具备以下特点：
- 有缓冲channel内部有一个缓冲队列
- 发送操作是向队尾插入元素，如果队列已满，则阻塞等待，直到另一个goroutine执行接收操作，释放channel的空间
- 接收操作是从队头获取一个元素，如果队列已空，阻塞等待，直到有goroutine插入新的元素 

### 关闭channel

使用内置的close函数关闭：

```go
close(ch)
```

如果一个channel被关闭了，就不能向里面发送数据了，继续发送会引发panic异常。

但是可以接受已关闭channel里面的数据，无数据则接受的是元素类型的零值。

### 单向channel

只能发送不能接收，或者只能接收不能发送的channel，成为单向channel

```go
onlySend := make(chan<- int)			// 单发
onlyReceive := make(<-chan int)		// 单收
```

这样的channel一般在函数或者方法的参数声明中使用：

```go
func counter(sendCh chan<- int){
  // 只能往sendCh中发送数据
  // num := <-sendCh  // 不能从单发channel中接受数据，编译会不通过
}
```

### select + channel 示例

```go
// 结构示例
select {
  case i1 = <-ch1:
  	// todo
  case ch2 <- i2:
  	// todo
  default:
  	// default process
}
```

整体结构与switch很像，有case和default，但是select的case是一个个可以操作的channel

```go
// select 下载例子
func main() {
  firstCh := make(chan string)
  secondCh := make(chan string)
  thirdCh := make(chan string)
  
  go func() { firstCh <- downloadFile("firstCh") }()
  go func() { secondCh <- downloadFile("secondCh") }()
  go func() { thirdCh <- downloadFile("thirdCh") }()
  
  // select 多路复用，哪个channel最先获取到值，
  // 就说明当前channel下载好了
  select {
  case filePath := <-firstCh:
    	fmt.Println(filePath)
  case filePath := <-secondCh:
    	fmt.Println(filePath)
  case filePath := <-thirdCh:
    fmt.Println(filePath)
  }
}

func downloadFile(filename string) string {
  time.Sleep(time.Second)
  return "filepath:" + filename
}
```

> 如果这些 case 中有一个可以执行，select 语句会选择该 case 执行，如果同时有多个 case 可以被执行，则随机选择一个，这样每个 case 都有平等的被执行的机会。如果一个 select 没有任何 case，那么它会一直等待下去。

在 Go 语言中，提倡通过通信来共享内存，而不是通过共享内存来通信，其实就是提倡通过 channel 发送接收消息的方式进行数据传递，而不是通过修改同一个变量。**所以在数据流动、传递的场景中要优先使用 channel，它是并发安全的，性能也不错。**(因为channel内部带有同步互斥锁)

