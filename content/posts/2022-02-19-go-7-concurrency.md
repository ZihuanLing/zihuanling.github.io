---
layout: post
title: "7. go并发：同步原语，用sycn包控制并发"
date: 2022-02-19
tags: [go]
comments: false
categories: [go]
---

go在并发的时候，可能会出现多个协程同时访问一个资源的时候，这就出现了资源竞争。也可能出现协程还在运行，但是主程序却退出了的情况，这是缺少控制导致的。

用sync包，可以方便的控制资源的访问，也可以方便实现阻塞等待，让协程执行完毕再退出程序，或者执行下一步。

<!-- more -->

## 资源竞争

在同一个goroutine中，如果分配的内存没有被其他的goroutine访问，只在该goroutine中使用，则不存在资源竞争问题

如果同一块内存被多个goroutine同时访问，就会产生不知道谁先访问，也无法预料最后结果的情况，这就是资源竞争：

```go
// 共享的资源
var sum = 0
func main(){
  for i := 0; i < 100; i++ {
    go add(10)
  }
  // goroutine 不会阻塞下面的代码，此处Sleep一下，防止main goroutine直接退出
  // 而导致未完成的goroutine也被终止
  time.Sleep(time.Second * 2)
  fmt.Println("Sum is:", sum)
}

func add(i int) {
  sum += i
}
```

上述例子中，sum变量为共享的资源，程序运行的过程中会发生资源竞争。

> 使用 go build、go run、go test 这些 Go 语言工具链提供的命令时，添加 -race 标识可以帮你检查 Go 语言代码是否存在资源竞争

## 同步原语

### sync.Mutex

互斥锁，同一个时刻，只有一个goroutine能执行某段代码，其他协程需要等待该协程执行完毕后才能继续执行。

```go
var (
	sum int
  mutex sync.Mutex
)

func add(i int) {
  mutex.Lock()
  // defer mutex.Unlock()		// 使用defer，关闭更加优雅
  sum += i
  mutex.Unlock()
}
```

### sync.RWMutex

读写锁

有几种情况：

- 写的时候不能同时读，这个时候读取的话可能读到脏数据
- 读的时候不能同时写，也可能产生不可预料的结果
- 读的时候可以同时读，因为数据不会改变。

```go

// 共享的资源
var (
	sum = 0
	mutex sync.RWMutex
)
func main(){
  for i := 0; i < 100; i++ {
    go add(10)
  }
  for i := 0; i < 10; i++ {
  	go fmt.Println("sum is:", readSum())
  }
  time.Sleep(time.Second)
}

func readSum() int {
  // 读取的时候使用RLock（读锁）
	mutex.RLock()
	defer mutex.RUnlock()
	d := sum
	return d
}

func add(i int) {
	mutex.Lock()
	defer mutex.Unlock()
	sum += i
}
```


### sync.WaitGroup

上述代码中，我们用到了 time.Sleep 来防止goroutine执行完毕之前，主程序退出。

由于不知道多个协程执行完毕需要多少时间，因此设置了一个固定的值，调用Sleep

我们可以使用sync.WaitGroup来监听协程的运行情况：

```go
func main(){
  wg := sync.WaitGroup
  wg.Add(110) // 监听 110 个goroutine
  for i := 0; i < 100; i++ {
    go func(){
      defer wg.Done()	// wg计数器减一
      add(10)
    }()
  }
  for i := 0; i < 10; i++ {
    go func(){
      defer wg.Done()
      fmt.Println("sum is : ", readSum())
    }()
  }
  // 一直等待（阻塞），直到计数器为0
  wg.Wait()
}
```

`sync.WaitGroup` 的使用步骤:

1. 声明一个WaitGroup，`wg := sync.WaitGroup`,然后调用`wg.Add`方法，设置需要跟踪的协程数量
2. 在每个协程执行完毕时调用 `wg.Done`，让计数器值减一，告诉sync.WaitGroup，该协程执行完毕
3. 在需要阻塞的地方，调用`wg.Wait`方法，知道计数器值为0



### sync.Once

```go
func main() {
  var once sync.Once
	var wg sync.WaitGroup
	wg.Add(10)
	onceBody := func() {
	  fmt.Println("only once.")
	}
	//启动10个协程执行once.Do(onceBody)
	for i := 0; i < 10; i++ {
		go func() {
			defer wg.Done()
       //把要执行的函数(方法)作为参数传给once.Do方法即可
			once.Do(onceBody)
		}()
	}
	wg.Wait()
}	
```

**sync.Once 适用于创建某个对象的单例、只加载一次的资源等只执行一次的场景**



### sync.Cond

sync.Cond 可以一声令下让所有协程都开始执行，*关键点在于协程开始的时候是等待的，要等待 sync.Cond 唤醒才能执行*

sync.Cond 可以用于控制协程的阻塞和唤醒。

```go
func main() {
	cond := sync.NewCond(&sync.Mutex{})
	var wg sync.WaitGroup
	wg.Add(11)
  // 10 个人赛跑
	for i := 1; i <= 10; i++ {
		go func(num int) {
			defer wg.Done()
			fmt.Printf("%-2d is ready.\n", num)
			cond.L.Lock()
      defer cond.L.Unlock()
      cond.Wait()		// 进入等待，直到 cond.Signal() 或者 cond.Broadcast()
			fmt.Printf("%-2d is running...\n", num)
		}(i)
	}
	time.Sleep(time.Second)
  // 1 个裁判发号施令
	go func() {
		defer wg.Done()
		fmt.Println("judgement is ready.")
		fmt.Println("Run!")
		cond.Broadcast()  // Broadcast 让所有的协程开始运行
	}()
	wg.Wait()
}
```

sync.Cond 的三个方法：

1. Wait：阻塞当前协程，知道被其他协程调用Broadcast或者Signal方法唤醒，**使用的时候需要加锁**，直接使用sync.Cond中的锁即可（L字段）
2. Signal：唤醒一个等待时间最长的协程
3. Broadcast：唤醒所有等待的协程

> 在调用 cond.Signal 或者 cond.Broadcast 之前，要确保目标协程处于Wait阻塞状态，否则会有死锁问题。

### sync.Map

方法：

1. Store：存储一堆key-value值
2. Load：根据key获取对应的value值，且可判断key是否存在
3. LoadOrStore：如果key对应的value存在，则返回value；否则，存储对应的value
4. Delete：删除一个key-value键值对
5. Range：循环迭代sync.Map，效果与for-range一样

```go

func main() {
	var mp sync.Map
	var wg sync.WaitGroup
	wg.Add(10)
	for i := 0; i < 10; i++ {
		go func(id int) {
			defer wg.Done()
			if _, loaded := mp.LoadOrStore("initialized", id); !loaded {
				fmt.Println(id, "mapper not initialized, init now.")
				return
			}
			value, loaded := mp.LoadOrStore(id, id)
			if loaded {
				fmt.Println(id, "Loaded value ", value)
				if value != id {
					fmt.Println(id, "Insert from other goroutine, delete it")
					mp.Delete(id)
				}
			} else {
				fmt.Println(id, "Store value ", id)
			}
			mp.Store(id + 1, id)
		}(i)
	}
	wg.Wait()
	wg.Add(1)
	go func() {
		defer wg.Done()
		mp.Range(func(key, value interface{}) bool {
			fmt.Printf("range for k = %v, value = %v\n", key, value)
			return true
		})
	}()
	wg.Wait()
}
```

