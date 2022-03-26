---
title: "17.go: 代码检查和性能优化"
date: 2022-03-26T20:01:10+08:00
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

对我们的代码进行检查，有助于提高代码质量，确保代码更加符合规范。

## 使用 golangci-lint 进行代码检查

go语言代码分析的工具有很多，如 `golint、gofmt、misspell`等，我们一般使用 **集成工具** `golangci-lint`，而不是单独使用他们。

### 安装

```bash
go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.32.2
```

### 查看版本

```bash
golangci-lint version
```

输出：

```
golangci-lint has version v1.32.2 ...
```

### 运行检查：

```bash
golangci-lint run quality/
```

这里的 `quality`是一个包，里面有一个 `main.go` 文件，内容如下：

quality/main.go

```go
package main

import "os"

func main(){
	os.Mkdir("/tmp", 0666)
}
```

运行检查后，输出如下：

```
quality\main.go:6:10: Error return value of `os.Mkdir` is not checked (errcheck)
        os.Mkdir("/tmp", 0666)
```

因为 `os.Mkdir` 返回一个 error，但是我们没有处理这个 error，因此提示了这个错误。

### golangci-lint 配置

golangci-lint是一个集成工具，里面有很多linters，我们可以用 `golangci-lint linters` 查看有哪些linters，以及他们的作用、启用情况，默认启用的linters如下：

```
deadcode - 死代码检查
errcheck - 返回错误是否使用检查
gosimple - 检查代码是否可以简化
govet - 代码可疑检查，比如格式化字符串和类型不一致
ineffassign - 检查是否有未使用的代码
staticcheck - 静态分析检查
structcheck - 查找未使用的结构体字段
typecheck - 类型检查
unused - 未使用代码检查
varcheck - 未使用的全局变量和常量检查
```

我们可以通过一个 `.golangci.yml` 来对 golangci-lint 进行自定义的配置：

.golangci.yml

```yaml
# 假设我们的代码检查仅启用 unused
linters:
  disable-all: true
  enable:
    - unused
```

配置 golangci-lint 使用固定版本，在 `.golangci.yml` 里面添加：

```yaml
service:
  golangci-lint-version: 1.32.2  # 使用固定版本的golangci-lint
```

针对每个启用的 linter 使用单独的配置，如设置拼写检测语言为US：

```yaml
linters-settings:
  misspell:
    locale: US
```

更多配置参考： [官方文档](https://golangci-lint.run/usage/configuration/)



## 性能优化

**写正确的代码是性能优化的前提**

性能优化的目的是让程序更好、更快地运行，但这不是必要的。

### 堆分配还是栈

go语言的内存空间分为两部分：栈内存和堆内存

- 栈内存：由编译器自动分配和释放，开发者无法控制。一般存储函数中的局部变量、参数等，函数创建的时候，这些内存会被自动创建；函数返回的时候，这些内存会被自动释放。
- 栈内存：生命周期比栈内存要长，如果函数返回的值还会在其他地方使用，那么这个值就会被编译器自动分配到堆上。相比栈内存来说，不能自动被编译器释放，只能通过垃圾回收器才能释放，所以效率相对低。

### 逃逸分析

在 `main.go` 写入以下代码：

```go
func newString() *string {
    s := new(string)
    *s = "mike"
    return s
}
```

查看逃逸分析：

```bash
go build -gcflags="-m -l" ./quality/main.go
# -m 打印出逃逸分析信息
# -l 禁止内联，方便更好观察逃逸
```

输出：

```
quality\main.go:4:10: new(string) escapes to heap
```

上述结果说明：**指针作为函数返回值的时候，一定会发生逃逸**

修改函数，让其返回 `string` 而不是 `*string`

```go
func newString() string {
	s := new(string)
	*s = "Mike"
	return *s
}
```

再次运行逃逸分析，输出：

```
quality\main.go:4:10: new(string) does not escape
```

可以看到没有发生逃逸了，因为我们没有在函数中返回指针。

**并不是说不使用指针作为函数返回就不会发生逃逸，被已经逃逸的指针变量引用的变量，也会发生逃逸**

如：

```go
fmt.Println("Hello world.")
```

```
>go build -gcflags="-m -l" ./quality/main.go
# let_go/quality
quality\main.go:6:13: ... argument does not escape
quality\main.go:6:14: "Hello world." escapes to heap
```

引用代码如下：

```go
func (p *pp) printArg(arg interface{}, verb rune) {
   p.arg = arg
   //省略其他无关代码
}
```

被 slice、map、chan 三种类型引用的指针也会发生逃逸：

```go
m := map[int]*string{}
s := "Mike"
m[0] = &s
```

逃逸分析结果：

```
quality\main.go:5:2: moved to heap: s
quality\main.go:4:22: map[int]*string{} does not escape
```

可以看到被变量 m 引用的 变量s 逃逸到了 堆上。

### 优化技巧

1. 尽可能避免逃逸，因为栈内存效率更高，小对象传参时，array比slice效果要更好
2. 对于频繁的内存申请操作，我们应该学会重用内存，比如 `sync.Pool`
3. 选用合适的算法达到高性能的目的，如 **空间换时间**

其他：

尽可能避免使用锁、并发加锁的范围要尽可能小、使用 `StringBuilder`做`string`和 `[]byte` 之间的转换、defer嵌套不要太多，等。



### go 性能剖析工具： pprof

