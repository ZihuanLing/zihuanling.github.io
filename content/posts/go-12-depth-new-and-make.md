---
title: "12.go深入：new、make和内存分配"
date: 2022-03-13T23:35:38+08:00
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


Go语言程序所管理的虚拟内存空间会被分为两部分：堆内存和栈内存。栈内存主要由Go语言来管理，开发者无法干涉太多，堆内存则有开发者进行分配。

## 变量

一个数据类型，在声明之后，会被赋值给一个变量，变量存储了程序所需的数据。

### 变量的声明

单纯的声明变量，可以使用`var`关键字，如：

```go
var s string		// 声明一个[字符串]变量，初始值为零值""
var sp *string		// 声明一个[字符串指针]变量，初始值为 nil
```

### 变量的初始化

有3种方法

- 声明的时候直接初始化： `var name string = "mike"`
- 声明之后再进行赋值初始化： `name = "mike"`,此前 `name` 变量已经声明
- 直接使用 `:=` 进行初始化： `name := "mike"`

### 值变量和指针变量初始化的区别

我们使用值初始化的时候，可以简单的这样写：

```go
var name string
name = "mike"
```

但是，当我们使用指针初始化的时候：

```go
var nameP *string   // 声明一个字符串指针
*nameP = "mike"		// 给nameP指向的地址赋值初始化
```

这时候，由于 `nameP` 指向的是一个空地址 `nil`，我们对这个空地址进行赋值初始化的时候，会报以下错误：

```
panic: runtime error: invalid memory address or nil pointer dereference
```

显而易见，我们无法对一个空地址赋值。

因此，**如果要对一个变量赋值，这个变量必须有对应的分配好的内存，这样才可以对这块内存操作，完成赋值的目的。**不止是赋值操作，针对指针变量，如果没有分配内存，对其进行取值时一样会报 `nil异常`，因为没有可以操作的内存。

## new函数

声明指针变量的时候，是默认没有分配内存的，因此，我们可以使用 `new` 函数来进行内存的分配：

```go
var nameP *string
nameP = new(string) 	// 分配一块string类型的内存
*nameP := "mike"
fmt.Println(*nameP)
```

这样，我们的nameP变量指向的就不是一个 `nil` 空地址了，而是指向了一块具体的字符串的内存。因此可以对其进行赋值操作。

### new函数源码

```go
// The new built-in function allocates memory. The first argument is a type,
// not a value, and the value returned is a pointer to a newly
// allocated zero value of that type.
func new(Type) *Type
```

所以 `new`就是根据传入的类型，申请一块内存，然后返回指向这块内存的指针，该块内存初始化的数据就是该类型的零值。

## make函数

make函数是map、slice、chan的工厂函数，可以同时用于三种类型的初始化。

## 总结

new函数只用于分配内存，并且把内存清零，也就是返回一个指向对应类型的零值的指针。new函数一般用于需要显式地返回指针的情况，不常用。

make函数只用于slice、chan、map三种内置类型的创建和初始化，因为这三种类型的结构比较复杂，如 `slice` 要提前初始化好内部元素的类型，slice的长度和容量等，这样才能更好地使用它们。