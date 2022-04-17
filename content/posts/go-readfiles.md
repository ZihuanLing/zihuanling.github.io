---
title: "go: 读取文件"
date: 2022-04-18T00:05:28+08:00
tags: [go, daily]
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

学习网站： https://gobyexample.com/reading-files

可以直接读取文件里面的所有内容到内存里面：

```go
data, err := os.ReadFile("/tmp/data")
fmt.Println(string(data))
```

有时候想要自定义一些操作，比如读取文件里面的某些内容，从某个位置开始读取等，这时候，我们可以用 `os.Open` 打开一个文件，返回一个 `os.File` 对象。

```go
f, err := os.Open("/tmp/data")
```

我们可以定义一个缓存（5个字节的[]byte类型），然后从文件中读取内容，读取的内容大小上限为5：

```go
b1 := make([]byte, 5)
n1, err := f.Read(b1)
fmt.Printf("%d bytes read from file: %s\n", n1, string(b1))
```

调用 `f.Read`来读取文件，返回两个结果，第一个为实际读取的内容长度，第二个为`error`。我们定义了一个长度为5的 b1 来存储文件内容，但是文件里面的内容长度可能只有3，因此，n1不一定等于5，它是实际读取的长度。

同样，我们还能用 `os.Seek`，来查找文件的位置，第一个参数为 `offset`，意味着偏移量，第二个参数为 `whence`，

- 0表示从文件的开始位置进行偏移查找
- 1表示从文件的当前位置开始偏移，如果之前已经设置过偏移，再次设置则从当前位置开始偏移
- 2表示从文件的末尾开始偏移

```go
o2, err := f.Seek(6, 0)
b2 := make([]byte, 2)
n2, err := f.Read(b2)
fmt.Printf("%d bytes read at %d\n", n2, o2)
fmt.Printf("Value is : %s\n", string(b2[:n2]))
```

golang 的 `io`包提供了一些有用的函数，帮助我们高效读取。比如 `io.ReadAtLeast`，可以更健壮地实现上的读取操作：

```go
o3, err := f.Seek(6, 0)
b3 := make([]byte, 2)
n3, err := io.ReadAtLeast(f, b3, 2)
fmt.Printf("%d bytes @ %d: %s\n", n3, o3, string(b3))
```

如果想要将文件指针倒回到最初的位置，没有内置的函数，但是使用 `f.Seek(0, 0)` 可以实现同样的效果：

```go
_, err := f.Seek(0, 0)
```

golang的 `bufio` 包提供了 **缓冲读取器**，它提供和额外的读取方法，对于少量的读取很有用：

```go
r4 := bufio.NewReader(f)
b4, err := r4.Peek(5)
fmt.Printf("5 bytes: %s\n", string(b4))
```

最后，我们应该在结束的时候关闭文件：

```go
f.Close()
```

但是一般来说，我们应该在打开文件之后，使用 `defer f.Close()` 来进行优雅的关闭文件：

```go
f, err := os.Open("/tmp/data")
defer f.Close()
```



完整代码：

```go

func check(err error) {
	if err != nil {
		panic(err)
	}
}

func main() {
	// ReadFile
	data, err := os.ReadFile("/tmp/data")
	check(err)
	fmt.Printf("data: %s\n", string(data))

	// Open file
	f, err := os.Open("/tmp/data")
	check(err)
	b1 := make([]byte, 5)
	n1, err := f.Read(b1)
	check(err)
	fmt.Printf("%d size of data read: %s\n", n1, string(b1))

	// Seek
	o1, err := f.Seek(6, 0)
	check(err)
	b2 := make([]byte, 2)
	n2, err := f.Read(b2)
	check(err)
	fmt.Printf("%d bytes read @ %d: %s\n", n2, o1, string(b2))

	// io.ReadAtLeast
	o3, err := f.Seek(6, 0)
	b3 := make([]byte, 2)
	n3, err := io.ReadAtLeast(f, b3, 2)
	check(err)
	fmt.Printf("io.ReadAtLeast, %d bytes read @ %d: %s\n", n3, o3, string(b3))

	// rewind
	_, err = f.Seek(0, 0)
	check(err)

	// bufio
	r4 := bufio.NewReader(f)
	b4, err := r4.Peek(5)
	check(err)
	fmt.Printf("5 bytes read from bufio: %s\n", string(b4))

	// close file
	f.Close()
}
```

