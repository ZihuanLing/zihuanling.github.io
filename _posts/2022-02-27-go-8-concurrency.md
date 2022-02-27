---
layout: post
title: "8. go并发：Context-多线程并发控制神器"
date: 2022-02-27
tags: [go]
comments: false
author: ZihuanLing
---


## 协程如何退出

一般来说，我们执行协程，需要等到协程执行完毕，才能够退出。但是，当我们想要让协程提前退出，就需要一种机制，去控制协程的退出。

以下例子使用`select + channel`的方式，控制协程的退出

```go

func main() {
	ch := make(chan bool)
	var wg sync.WaitGroup
	go func() {
		defer wg.Done()
        // 开启looper协程
		looper(ch)
	}()
	wg.Add(1)
    // 5秒后发送中断信号
	time.Sleep(time.Second * 5)
	fmt.Println("Signal to goroutine exit...")
	ch <- true
	fmt.Println("Signal sent.")
	wg.Wait()  // 等待协程完全退出
	fmt.Println("Exit.")
}

func looper(ch <-chan bool){
	for {
		select {
		case <-ch:
			fmt.Println("go break signal")
			return
		default:
			fmt.Println("looper is running...")
			time.Sleep(time.Second * 1)
		}
	}
}

```

上述例子通过一个`ch` channel 发送信号，让协程收到信号后终止循环。
