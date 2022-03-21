---
title: "16.go: 单元测试和基准测试"
date: 2022-03-21T22:23:25+08:00
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

# 单元测试

单元测试就是对单元进行测试（听起来是一句废话），单元可以是一个函数、一个模块等，我们最小的单元是一个函数。

以**斐波那契数列**为例，实现一个测试用例

test/main.go

```go
package main

// 斐波那契数列
func Fibonacci(n int) int {
	if n <= 0 {
		return 0
	} else if n == 1 {
		return 1
	}
	return Fibonacci(n-1) + Fibonacci(n-2)
}
```

我们在 main.go 里面写了一个 **Fibonacci**函数，用于计算对应的斐波那契值。

我们接下来写一个测试用例，测试的文件名应该是以 `_test.go` 结尾的，前面的名称最好是需要测试的文件名称，比如要测试 `main.go`，则测试文件命名为 `main_test.go`，而在 测试文件里面，需要一个以 `Test`开头的函数，后面接需要测试的函数名称，如 `TestFibonacci`，这个函数接受一个 `*Testing.T`指针，且不返回任何值

test/main_test.go

```go
func TestFibonacci(t *testing.T) {
	result := map[int]int{
		1: 1, 2: 1, 3: 2, 4: 3, 5: 5,
		6: 8, 7: 13, 8: 21,
	}
	for n, expect := range result {
		got := Fibonacci(n)
		if expect != got{
			t.Fatalf("Test Fibonacci failed: expect %d, got %d", expect, got)
		} else {
			fmt.Printf("ok, Fibonacci(%d) = %d\n", n, got)
		}
	}
}
```

在代码所在目录下，运行测试用例（所有）

```bash
go test -v .
```

输出：

```
=== RUN   TestFibonacci
ok, Fibonacci(5) = 5
ok, Fibonacci(6) = 8
ok, Fibonacci(7) = 13
ok, Fibonacci(8) = 21
ok, Fibonacci(1) = 1
ok, Fibonacci(2) = 1
ok, Fibonacci(3) = 2
ok, Fibonacci(4) = 3
--- PASS: TestFibonacci (0.00s)
PASS
ok      let_go/test     1.434s
```



## 单元测试覆盖率

通过一个 flag `--coverprofile` 来获得一个单元测试覆盖率文件：

```bash
go test -v --coverprofile=test.cover .
```

输出最后的内容是：

```
PASS
coverage: 100.0% of statements
ok      let_go/test     18.222s coverage: 100.0% of statements
```

可以看到，输出了覆盖率数据，我们的测试用例的覆盖率是 100%。

当前路径下，生成了一个 `test.cover`文件，我们可以使用 `go tool` 从其中得到一个html的覆盖率测试报告：

```bash
go tool cover -html=test.cover -o=test-cover.html
```

打开生成的 `test-cover.html`文件，我们就可以看到对应的覆盖率情况。



# 基准测试

基准测试用于评估代码的性能。

测试文件的命名跟单元测试是一样的，都是 `_test.go`结尾，不同的是基准测试的函数名是 `Benchmark`开头，后接被测试函数名，如 `BenchmarkFibonacci`，同时接收一个 `*testing.B`指针参数。

main_test.go

```go
func BenchmarkFibonacci(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Fibonacci(10)
	}
}
```

`b.N`是框架提供的，表示循环运行次数。

运行测试用例，同样是使用 `go test`，不过要加上 `-bench`参数，后接 `.` 表示所有，也可以接具体的函数名称。

```bash
go test -bench=. .
# go test -bench=Fibonacci .
```

输出：

```
goos: windows
goarch: amd64
pkg: let_go/test
cpu: Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz
BenchmarkFibonacci-8     3076749               354.4 ns/op
PASS
ok      let_go/test     2.838s
```

`BenchmarkFibonacci-8`：这里的 `-8` 表示运行基准测试对应的 GOMAXPROCS 的值。

`3076749`：表示一共for循环了 3076749次

`354.4 ns/op`：表示每次循环耗时 `354.4 ns`

基准测试默认是 **1秒**，因此上述结果是1秒内运行了`3076749`次，每次耗时`354.4 ns`。我们同样可以指定运行时长，使用 `-benchtime` 参数：

```bash
go test -bench=. -benchtime=3s .
```



## 计时方法

基准测试之前，我们可能需要准备数据，我们的基准测试应该把这部分时间排除在外，这是，我们可以使用 `ResetTimer`方法：

```go
func BenchmarkFibonacci(b *testing.B) {
	n := 10		// 前期准备
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Fibonacci(n)
	}
}
```

此外，还有 `StartTimer`和 `StopTimer`，可以灵活控制计时时间。



## 内存统计

通过 `ReportAllocs` 方法开启内存统计：

```go
func BenchmarkFibonacci(b *testing.B) {
	n := 10
	b.ReportAllocs()	// 报告内存统计
	b.ResetTimer()		// 重置计时器
	for i := 0; i < b.N; i++ {
		Fibonacci(n)
	}
}
```

输出：

```
BenchmarkFibonacci-8     3320989               374.9 ns/op             0 B/op          0 allocs/op
PASS
ok      let_go/test     21.393s
```

发现多了 `0 B/op          0 allocs/op` 这段输出，前者表示每次分配了多少字节的内存，后者表示每次操作分配内存的次数。

除了 `b.ReportAllocs`外，还可以在命令行中使用 `-benchmem`参数，可以达到同样的效果。

## 并发基准测试

主要用以测试 在多个goroutine 下的代码性能，使用 `runParallel` 方法，传入一个函数作为参数：

```go
func BenchmarkFibonacci(b *testing.B) {
	n := 10
	b.RunParallel(func(pb *testing.PB){
		for pb.Next() {
			Fibonacci(n)
		}
	})
}
```

运行：

```bash
go test -bench=. .
```

输出：

```
BenchmarkFibonacci-8    13952709               114.2 ns/op
```

可以看到，并行测试的情况下，函数被运行了 13952709 次。

## 优化

可以看到上述基准测试的内存统计中，并没有发生内存申请，也就是说，内存并不是影响函数性能的原因。

下面我们使用缓存来优化 `Fibonacci`函数

main.go

```go
// 斐波那契数列
func Fibonacci(n int) int {
	if n <= 0 {
		return 0
	} else if n == 1 {
		return 1
	}
	v, ok := cache[n]
	if !ok {
		v = Fibonacci(n-1) + Fibonacci(n-2)
		cache[n] = v
	}
	return v
}
```

再次运行基准测试，输出：

```
BenchmarkFibonacci-8    261475790                4.585 ns/op
```

可以看到，每次循环的时间从 `114.2 ns -> 4.585 ns`，性能提高了约25倍。

