---
title: "15.go深入：SliceHeader，高效的slice"
date: 2022-03-18T14:34:12+08:00
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

## 数组

数组由两部分组成：**数组的大小和数组内部的元素类型**。

```go
// 伪代码表示
array {
  len
  item type
}
```

看以下两个数组的定义：

```go
a1 := [1]string{"mike"}
a2 := [2]string{"mike"}
```

上述定义的两个变量，a1的类型为 `[1]string`，a2的类型为 `[2]string`，所以说，数组的大小也属于数组类型的一部分。

### 数组的两个限制

- **一旦一个数组被声明，它的大小和内部的类型就不能改变，**我们将不能随意向其中追加任意多的元素。

- 另外，当我们使用数组存储大量数据，然后将数组作为函数的参数进行传值时，由于函数之间是**值传递**的，因此，数组的拷贝将会**耗费巨大的内存**。

## slice 切片

我们可以将切片理解为**动态的数组**。

**切片是对数组的封装，它的底层是一个数组存储了所有的元素，但是它可以动态地添加元素，容量不足时可以自动扩容。**

### 动态扩容

使用内置的`append`方法，向切片中追加元素，**返回一个新的切片**。

同时，当容量不足的时候，`append`**会自动对切片进行扩容。**

```go
func main(){
    ss := []string{"mike"} // 定义切片ss
    fmt.Printf("slice before append: %s, length=%d, cap=%d\n", ss, len(ss), cap(ss))    
    ss = append(ss, "lucy", "john") // append 追加元素
    fmt.Printf("slice after append: %s, length=%d, cap=%d\n", ss, len(ss), cap(ss))
}
```

输出：

```
slice before append: [mike], length=1, cap=1
slice after append: [mike lucy john], length=3, cap=3
```



### 数据结构

切片在go语言中是一个数据结构：

```go
type SliceHeader struct {
	Data uintptr	// 指向存储切片元素的数组
	Len int			// 切片长度
	Cap int			// 切片容量
}
```

示例证明：

```go
func main(){
    arr := [4]string{"mike", "lucy", "john", "trump"}
	s1 := arr[0:1]
	s2 := arr[:]
	s3 := arr[1:]
	s4 := s2[1:]
	s5 := append(s1, "amy")
	fmt.Println((*reflect.SliceHeader)(unsafe.Pointer(&s1)).Data)
	fmt.Println((*reflect.SliceHeader)(unsafe.Pointer(&s2)).Data)
	fmt.Println((*reflect.SliceHeader)(unsafe.Pointer(&s3)).Data)
	fmt.Println((*reflect.SliceHeader)(unsafe.Pointer(&s4)).Data)
	fmt.Println((*reflect.SliceHeader)(unsafe.Pointer(&s5)).Data)
	fmt.Println(
		unsafe.Sizeof(arr),
		unsafe.Sizeof(s1),
		unsafe.Sizeof(s2),
		unsafe.Sizeof(s3),
		unsafe.Sizeof(s4),
		unsafe.Sizeof(s5),
		)
}
```

输出：

```
824634801872
824634801872
824634801888
824634801888
824634801872
64 24 24 24 24 24
```

上述代码中，我们定义了一个数组`arr`，然后用不同的方法创建了5个数组切片 `s1~s5`，我们用 `unsafe.Pointer` 获取到 `SliceHeader`切片里面指向的`Data`，可以发现：

- s1 和 s2 `Data`指向的内存是一样的，因为他们都是从 `arr`切片下来的，且都是从头部开始切
- s2 和 s3 `Data`指向的内存是不一样的，因为 `s3`是从arr第2个元素开始切的，它的 `Data`的初始位置是arr的第二个元素
- s4 的`Data`指向，和s3的是相同的，虽然s4是从s2第1个元素切出来的，但是s2的Data开始地址跟arr一致，因此效果等同于从arr的第二个元素开始切，因此Data指向跟s3一致
- s5 是使用`append(s1, "amy")`得到，但是返回了新的切片之后，其`Data`指向的地址仍然和s1是相同的
- 最后，打印出arr和各个slice的Size，可以看到，数组占用的Size是较大的，而无论slice里面的数据有多少，其都只占用 **24字节** 大小的内存，符合其 `SliceHeader` 的定义

### 高效的原因

一方面，从集合类型的方面考虑，数组、切片和map都是集合类型，他们都可以存放元素，但是数组和切片是连续的内存操作，通过索引就可以快速地找到元素存储的地址，因此取值和赋值要更加高效。

另一方面，使用切片之所以高效，是因为我们在函数中进行参数传递的时候，传递的只是一份24个字节的`SliceHeader`数据，实际访问数据时，使用的是同一个底层数组，因此避免了耗费大量内存去拷贝数据，提高了效率。

### 需要注意的

使用切片作为函数传值虽然高效，但由于使用的底层数据是相同的，修改切片里面的数据时，其他切片的数据也可能会被修改，一个例子：

```go
// 打印切片信息
func info(s []string) {
	head := (*reflect.SliceHeader)(unsafe.Pointer(&s))
	addr := (*string)(unsafe.Pointer(head.Data))
	fmt.Printf("data: %v, address: %v, len: %d, cap: %d \n", head.Data, addr, len(s), cap(s))
	for i, _ := range s {
		fmt.Printf("%p %v\n", &s[i], s[i])
	}
	fmt.Println("======")
}

func main(){
    arr := [2]string{"mike", "lucy"}
	s1 := arr[0:1]
	s2 := append(s1, "amy")  // 往切片s1追加元素，返回新切片给s2
	s1[0] = "Lisa"			// 修改切片s1第一个元素为 Lisa
	info(s1)
	info(s2)
	info(arr[:])
}
```

输出：

```
data: 824634229888, address: 0xc00007c480, len: 1, cap: 3 
0xc00007c480 Lisa
======
data: 824634229888, address: 0xc00007c480, len: 2, cap: 3 
0xc00007c480 Lisa
0xc00007c490 amy
======
data: 824634229888, address: 0xc00007c480, len: 3, cap: 3 
0xc00007c480 Lisa
0xc00007c490 amy
0xc00007c4a0 trump
======
```

从上面的输出可以看到，我们从原始数组`arr`切出了一个切片s1，s1里面只有一个元素，但是，在打印信息的时候，显示它的容量 `cap=3`，等于原始数组的长度。

我们往s1里面追加了一个元素 `amy`，返回一个新的切片s2，然后，将s1的第一个元素改成`Lisa`，随后的输出结果可以看到，原始数组arr、切片s1、s2的第一个元素都变成了`Lisa`，而我们往s1追加元素的时候，修改的是原数组的第二个元素， `lucy -> amy`。且三者的各个数据的地址都是一样的，说明切片和原始数组共用一个底层数组。

**但是**，有意思的是，我们使用append往切片中追加元素，当追加的元素超过了当前的slice的容量时，返回的切片指向的就是底层数组就是一块新的内存了。

我们将上述代码中的 `append` 语句改成：

```go
s2 := append(s1, "amy", "panda", "python", "java")  // 往切片s1追加元素，返回新切片给s2
```

输出：

```
data: 824634229888, address: 0xc00007c480, len: 1, cap: 3 
0xc00007c480 Lisa
======
data: 824634048608, address: 0xc000050060, len: 5, cap: 6 
0xc000050060 mike
0xc000050070 amy
0xc000050080 panda
0xc000050090 python
0xc0000500a0 java
======
data: 824634229888, address: 0xc00007c480, len: 3, cap: 3 
0xc00007c480 Lisa
0xc00007c490 lucy
0xc00007c4a0 trump
======
```

可以看到有4个变化：

- s2的容量 cap 跟其他两个不同了，自动扩容到了 5
- s1和arr的对应元素地址是一样的，说明两者用的底层相同，s2的元素地址跟其他两个不同，说明新申请了一块内存空间来存储s2切片内容
- 修改s1的第一个元素，没有影响到s2的数据
- 往s1中追加多个元素，没有影响到原始数组arr的数据

**所以，多个切片使用到同一个底层数组的情况下，应该考虑到数据之间的冲突问题。**go提供一个 `copy` 内部函数，让我们可以实现切片拷贝，修改拷贝数据，不会影响到原始数据。



## []byte和string 转换

一般情况下，我们字符串`string`和`[]byte`可以这样转换：

```go
var s string = "Hello world."
// string -> []byte
b := []byte(s)
// []byte -> string
bs := string(b)
```

slice类型有SliceHeader， 同样的，string类型也有 StringHeader，它的结构体如下：

```go
type StringHeader struct {
    Data uintptr
    Len int
}
```

但是跟 `SliceHeader` 的区别是，`StringHeader`少了一个`Cap`字段用以存储容量。

回到string 和 []byte 转换的例子，go语言是通过分配内存然后在复制内容的方式，去实现`[]byte和string`的互相转换的。我们用 `SliceHeader、StringHeader`看下转换后的 Data指向地址

```go
func main(){
	var s string = "Hello world."
	// string -> []byte
	b := []byte(s)
	// []byte -> string
	bs := string(b)
	fmt.Printf("addr of s: %v\n", (*reflect.StringHeader)(unsafe.Pointer(&s)).Data)
	fmt.Printf("addr of b: %v\n", (*reflect.SliceHeader)(unsafe.Pointer(&b)).Data)
	fmt.Printf("addr of bs: %v\n", (*reflect.StringHeader)(unsafe.Pointer(&bs)).Data)
}
```

输出：

```
addr of s: 10646786
addr of b: 824634580712
addr of bs: 824634580680
```

由此可见，直接的 `string <-> []byte`互转是通过拷贝原始值来实现的。

#### 转换优化

StringHeader 比 SliceHeader 少了一个Cap字段，我们可以通过 unsafe.Pointer 将 SliceHeader 直接转换成 StringHeader，但是返回来却是行不通的，我们还需要手动补充上一个 Cap字段。

为了在string 和 []byte 互转的时候节省内存，实现**零值拷贝**，我们在转换的时候，使用对应的`Header结构体` + `unsafe.Pointer`进行转换。

将上述例子改变如下：

```go
func main(){
	var s string = "Hello world."
	// string -> []byte
	sliceHeader := (*reflect.SliceHeader)(unsafe.Pointer(&s))
	sliceHeader.Cap = sliceHeader.Len
	b := *(*[]byte)(unsafe.Pointer(sliceHeader))
	// []byte -> string
	stringHeader := (*reflect.StringHeader)(unsafe.Pointer(&b))
	bs := *(*string)(unsafe.Pointer(stringHeader))
	
	fmt.Printf("%s, addr of s: %v\n", s, (*reflect.StringHeader)(unsafe.Pointer(&s)).Data)
	fmt.Printf("%s, addr of b: %v\n", b, (*reflect.SliceHeader)(unsafe.Pointer(&b)).Data)
	fmt.Printf("%s, addr of bs: %v\n", bs, (*reflect.StringHeader)(unsafe.Pointer(&bs)).Data)
}
```

输出：

```
Hello world., addr of s: 9860354
Hello world., addr of b: 9860354
Hello world., addr of bs: 9860354
```

可以看到，修改之后，对应的`Header`中Data指向的是同一个地址。

需要注意的是，通过 `unsafe.Pointer`将stirng转换为 []byte的时候，不可以通过索引对 []byte修改，否则会导致程序崩溃，因为go语言中，string内存是只读的。

go语言标准库中， `strings.Builder` 也使用了零值拷贝提升新能：

```go
// String returns the accumulated string.
func (b *Builder) String() string {
   return *(*string)(unsafe.Pointer(&b.buf))
}
```

