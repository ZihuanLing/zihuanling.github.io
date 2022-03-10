---
title: "11. go深入：值、指针以及引用类型"
date: 2022-03-10T14:44:08+08:00
tags: []
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

## 值类型

假设我们有一个这样的结构体：

```go
type person struct {
    name string
    age uint
}
```

然后我们试图定义一个函数，修改这个结构体实例的值：

```go
func modify(argP person){
    argP.name = "Nobody"
    argP.age = 10
}

// 我们实际运行一下这个函数
func main(){
    p := person{name: "mike", age: 19}
    fmt.Println(p)
    modify(p)
    fmt.Println(p)
}
```

上述的例子中，我们期望在经过了`modify`函数修改后，打印出来的结果是 `{Nobody, 10}`，然而实际上，输出的仍然是初始化的值： `{mike, 19}`

为啥会这样呢，因为上面定义的变量 `p` 是**值类型**，而通过`modify`函数传入的变量值`argP`只是**原始值变量p的一份值拷贝**，而不是原来的数据本身。

其实，我们只要在`modify`函数内部和外部打印出变量p和argP的地址，就可以发现他们的不同之处。

```go
func modify(argP person){
    fmt.Printf("address of arg p: %p\n", &argP)
    // ... 
}

func main(){
    // ...
    fmt.Printf("address of p: %p\n", &p)
    modify(p)
    // ...
}
```

输出为： 

```
address of p: 0xc0002905a0
address of arg p: 0xc0000d01b0
```

可以看到，在函数内部和外部，变量的地址是不一样的。

**实际上，在go语言中，函数的传参都是值传递，也就是原来数据的一份拷贝，而不是数据本身。以上述的`modify`函数来说，参数`argP`就是原始变量`p`的一份值拷贝。除了struct之外，还有浮点型、整形、字符串、布尔、数组等，这些都是值类型**


## 指针类型

回到最初的期望，我们想要修改 person 的值，只需要修改`modify`函数的参数为指针类型（\*person），然后在对应的函数体中修改原始数据的值：

```go
func modify(argP *person) {
    fmt.Printf("address of arg p: %p\n", argP)
    argP.name = "Nobody"
    argP.age = 10
}
```

这样，就Ok了。

看到输出： 

```
address of p: 0xc000290450
{Mike 19}
address of arg p: 0xc000290450
{Nobody 10}
```


## 引用类型

引用类型，包括 map 跟 chan

### map

同样是上述的例子，我们不试用自定义结构体 person，而是使用map来达到修改的目的：

```go
func main(){
    m := make(map[string]int)
    m["age"] = 19
    fmt.println(m)
    modify(m)
    fmt.Println(m)
}

func modify(p map[string]int){
    p["age"] = 10
}
```

可以看到输出如下：

```
map[age:19]
map[age:10]
```

同样达到了我们**修改值**这个期望，因为 `map` 是一个引用类型，在go语言中，无论是通过字面量还是make函数创建的map，go语言编译器都会自动帮我们转化成为对 `runtime.makemap` 的调用，`rumtime.makemap`的定义如下：

```go
// makemap implements Go map creation for make(map[k]v, hint).
func makemap(t *maptype, hint int, h *hmap) *hmap{
  //省略无关代码
}
```

可以看到，这个函数最终返回的是 `*hmap` 类型，而他本质上就是一个指针。因此，我们才可以通过在函数内修改map的值，达到修改原始数据的目的。

需要注意的是，map在这里被理解为**引用类型**，但是它的**本质上就是一个指针**。


### chan

作为goroutine中的通信桥梁，**channel也是可以被理解为引用类型，本质上也是一个指针**

同map一样，go语言也会帮我们自动调用 `runtime.makechan`函数，创建一个channal：

```go
func makechan(t *chantype, size int64) *hchan {
    //省略无关代码
}
```

可以看到，返回的是一个 `*hchan`，本质上也是一个指针，同map一样。

**严格来说，GO语言没有引用类型**，将map、chan成为引用类型是为了便于理解。此外，go语言中的**函数、接口、slice切片、指针类型等**，也可以成为引用类型。


## 类型的零值

在go中，定义变量要么通过声明，要么通过make和new函数，不一样的是**make和new函数属于显式声明并初始化**，如果我们声明的变量没有显式声明初始化，则该变量的默认值就是对应类型的零值：

|类型|零值|
|----|----|
|数值类型（int、float等）| 0|
|bool|false|
|string|""（空字符串）|
|struct|内部字段的零值|
|slice、map、指针、函数、chan、interface|nil|


## 总结

在go语言中，**函数的参数传递只有值传递**，而且传递的实参都是原始数据的一份拷贝。
- 如果拷贝的内容都是值类型的，那么在函数中就无法修改原始数据
- 如果拷贝内容是指针，则可以在函数中修改原始数据

