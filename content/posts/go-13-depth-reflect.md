---
title: "13.go深入：reflect 运行时反射"
date: 2022-03-14T00:33:13+08:00
tags: []
categories: []
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
ShowPostNavLinks: true# 
---



## 啥是反射

go语言中，反射为我们提供了一种可以在运行时操作任意类型对象的能力，比如，查看一个接口变量的具体类型、看一个结构体有多少字段、修改某个字段的值等。

比如 `fmt.Println`：

```go
func Println(a ...interface{}) (n int, err error) {
    return Fprintln(os.Stdout, a...)
}
```

函数定义中有一个可变参数 `a ...interface{}`，我们在调用的时候，可以传1个到多个参数进去。

## reflect.Value 和 reflect.Type

go语言的反射定义中，任何接口都有两个部分组成：**接口的具体类型，以及具体类型对应的值**。如 `var i in = 3`，由于 `interface{}`可以表示任何类型，因此**i**可以转化为 `interface{}`，将其当做一个接口，此时它在go反射中就表示成 `<Value, Type>`，其中Value为3，Type为int。

go反射中，标准库为我们提供了两种类型 `reflect.Value`和 `reflect.Type`分别表示变量的值和类型，并且可以用函数 `reflect.ValueOf`和 `reflect.TypeOf`分别获取**任意对象** Value和Type。

```go
func main(){
    var i int = 3
    iv := reflect.ValueOf(i)
    it := reflect.TypeOf(i)
    fmt.Println(iv, it)
}
```

### reflect.Value

#### 结构体定义

reflect.Value 可以通过 `reflect.ValueOf`获得，其结构体定义如下

```go
type Value struct {
    typ *rtype
    ptr unsafe.Pointer
    flag
}
```

其里面的变量都是私有的，意味着我们只能使用它的方法，它的常用方法有：

```go
//针对具体类型的系列方法
//以下是用于获取对应的值
Bool
Bytes
Complex
Float
Int
String
Uint
CanSet //是否可以修改对应的值
// 以下是用于修改对应的值
Set
SetBool
SetBytes
SetComplex
SetFloat
SetInt
SetString
Elem //获取指针指向的值，一般用于修改对应的值
//以下Field系列方法用于获取struct类型中的字段
Field
FieldByIndex
FieldByName
FieldByNameFunc
Interface //获取对应的原始类型
IsNil //值是否为nil
IsZero //值是否是零值
Kind //获取对应的类型类别，比如Array、Slice、Map等
//获取对应的方法
Method
MethodByName
NumField //获取struct类型中字段的数量
NumMethod//类型上方法集的数量
Type//获取对应的reflect.Type
```

可以总结为3类：

1. 用户获取和修改对应的值

2. 和struct类型的字段有关

3. 和类型上的方法集有关，用于获取对应的方法

#### 获取原始类型

我们使用 `reflect.ValueOf` 将任意类型的对象转为 `reflect.Value`，也可以通过 `reflect.Interface`进行逆转换

```go
func main(){
    var i int = 3
    // int to reflect.Value
    iv := reflect.ValueOf(i)
    // reflect.Value to int
    i1 := iv.Interface().(int)
    fmt.Println(iv, i1)
}
```

#### 修改对应的值 

已经定义的变量可以通过反射，在运行时修改，如下所示：

```go
func main() {
    i := 3
    ipv := reflect.ValueOf(&i)
    ipv.Elem().SetInt(4)
    fmt.Println(i)
}
```

需要注意的是， `reflect.ValueOf` 返回的是一个**值的拷贝**，因此，我们想要修改原始值，就需要传入**指针变量**。

因为传入的是**指针变量**，所以需要调用 `Elem()`方法，找到这个指针指向的值，然后才能调用 `Set...` 方法进行修改。

所以，使用运行时修改变量值的关键点在于：

传递指针（可寻址），通过 `Elem`方法获取指向的值，才可以保证值可以被修改。`reflect.Value`为我们提供了 `CanSet`方法，判断是否可修改该变量。

修改struct结构体中的值，也是同理：

- 传递strcut结构体指针，获取 `reflect.ValueOf`
- 通过 `Elem`方法获取指针指向的值
- 通过 `Field`方法获取需要修改的字段
- 通过 `Set`系列方法，修改成对应的值

```go
type person struct {
	Name string
	Age uint
}

func main(){
    p := person{Name: "mike", Age: 10}
	fmt.Println("Original person is : ", p)
	ppv := reflect.ValueOf(&p)
	ppv.Elem().FieldByName("Age").SetUint(20)	// set age to 20
    // ppv.Elem().Field(1).SetUint(20)	// 也可
	fmt.Println("person changed: ", p)
}
```

输出：

```
Original person is :  {mike 10}
person changed:  {mike 20}
```

小总结，通过反射修改一个值的规则：

- 可被寻址，即需要向 `reflect.ValueOf` 传递一个指针作为参数
- 如果想修改struct结构体的字段值，则对应的字段必须是**可导出的**，即**该字段的首字母是大写的**
- 需要使用 `Elem` 方法获得指针指向的值，才能通过 `Set` 系列方法进行修改

#### 获取对应的底层类型

可以使用 `Kind` 方法获取对应的底层类型：

```go
func main(){
    p := person{"Mike", 20}
    ppv := reflect.ValueOf(&p)
    pv := reflect.ValueOf(p)
    fmt.Println(ppv.Kind(), pv.Kind())	// ptr, struct
}
```

`Kind`返回的值可以为：

```go
type Kind uint
const (
   Invalid Kind = iota
   Bool
   Int
   Int8
   Int16
   Int32
   Int64
   Uint
   Uint8
   Uint16
   Uint32
   Uint64
   Uintptr
   Float32
   Float64
   Complex64
   Complex128
   Array
   Chan
   Func
   Interface
   Map
   Ptr
   Slice
   String
   Struct
   UnsafePointer
)
```



### reflect.Type

我们使用 `reflect.TypeOf` 获取一个 `reflect.Type`。

reflect.Value 用于于值有关的操作中，而如果是和变量类型本身有关的操作，则最好使用reflectType，如：获取结构体对应的字段名称或方法。

#### 接口定义

`reflect.Value`是一个结构体，而 `reflect.Type`是一个接口，大部分常用方法同 `reflect.Value`是相同的，如下：

```go
type Type interface {
    Implements(u Type) bool
    AssignableTo(u Type) bool
    ConvertibleTo(u Type) bool
    Comparable() bool
    
    // 同 reflect.Value功能相同
    Kind() Kind
    Method(int) Method
    MethodByName(string) (Method, bool)
    NumMethod() int
    Elem() Type
    Field(i int) StructField
    FieldByIndex(index []int) StructField
    FieldByName(name string) (StructField, bool)
    FieldByNameFunc(match func(string) bool) (StructField, bool)
    NumField() int
}
```

特有的方法：

1. `Implements`：用于判断是否实现了该接口
2. `AssignableTo`：用于判断是否可以赋值给类型u，即使用`=`进行赋值
3. `ConvertibleTo`：用于判断是否可以转换为类型u
4. `Comparable`：用于判断该类型是否可比较，使用关系运算符进行比较

#### 遍历结构体的字段和方法

```go
// 实现String方法
func (p person) String() string {
	return fmt.Sprintf("This person name is %s, age = %d", p.Name, p.Age)
}

func main(){
    p := person{"Mike", 20}
    pt := reflect.TypeOf(p)
    // 遍历字段
    for i := 0; i < pt.NumField(); i++ {
    	fmt.Printf("Field %d: %s\n", i+1, pt.Field(i).Name)
	}
	// 遍历方法
	for i := 0; i < pt.NumMethod(); i++ {
		fmt.Printf("Method %d: %s\n", i+1, pt.Method(i).Name)
	}
}
```

输出：

```
Field 1: Name
Field 2: Age
Method 1: String
```

#### 是否实现某接口

下面检查person是否实现 `fmt.Stringer` 和 `io.Writer` 接口：

```go
func main(){
    p := person{"Mike", 20}
    pt := reflect.TypeOf(p)
    stringerType := reflect.TypeOf((*fmt.Stringer)(nil)).Elem()
    writerType := reflect.TypeOf((*io.Writer)(nil)).Elem()
    fmt.Println("person implement stringer: ", pt.Implements(stringerType))
    fmt.Println("person implement writer: ", pt.Implements(writerType))
}
```

输出：

```
person implement stringer:  true
person implement writer:  false
```

由于 `fmt.Stringer` 是一个接口，而传入 `reflect.TypeOf` 里面的必须是一个**值**，因此需要转化一下，传入一个空接口指针 `(*fmt.Stringer)(nil)`，然后取其对应的 `Elem` 进行判断。

这样的做法很少，我们一般使用断言进行判断，而不是反射，以下写法更简单：

```go
func main(){
    p := person{"Mike", 20}
    pt := reflect.TypeOf(p)
    _, ok := pt.(fmt.Stringer)
    fmt.Println("Stringer implemented by person: ", ok)
}
```



## 字符串和结构体互换

字符串和结构体互转，最多是Json和Struct互相转换，这样的转换相当于python里面将字典序列化成为json字符串或者反序列化。

### Json和Struct互转

go语言提供了一个json包，可以让我们实现json字符串和struct结构体的互转：

```go
func main() {
    p := person{Name: "Mike", Age: 10}
    // struct 转换成字符串
    pJson, err := json.Marshal(p)
    if err == nil {
    	fmt.Printf("pJson string : %s\n", pJson)
	}
	// Json 字符串转化为struct结构体
	jsonString := "{\"Name\": \"Jack\", \"Age\": 20}"
	if err := json.Unmarshal([]byte(jsonString), &p); err == nil {
		fmt.Printf("Unmarshaled struct: %s\n", p)
	} else {
		fmt.Printf("Error unmarshal: %e\n", err)
	}
}
```

输出：

```
pJson string : {"Name":"Mike","Age":10}
Unmarshaled struct: This person name is Jack, age = 20
```

- 通过 `json.Marshal` 将struct转化成 字符串（返回的是 []byte）
- 通过 `json.Unmarshal` 将json字符串（[]byte）转化成 strcut结构体

需要注意的是，如果 `person` 的定义中，含有私有成员变量（小写开头），那么在json序列化和反序列化的过程中，将不会解析/赋值该字段。

### Struct Tag

`Struct Tag`是struct结构体字段的标签，用其辅助完成一些额外的操作，如果 json和struct 互转，使用tag让json化的字段变成小写：

```go
type person struct {
	Name string `json:"name"`
	Age uint	`json:"age"`
}

func main() {
    p := person{Name: "Mike", Age: 10}
    // struct 转换成字符串
    pJson, err := json.Marshal(p)
    if err == nil {
    	fmt.Printf("pJson string : %s\n", pJson)
	}
	// Json 字符串转化为struct结构体
    jsonString := "{\"name\": \"Jack\", \"age\": 20}"
	if err := json.Unmarshal([]byte(jsonString), &p); err == nil {
		fmt.Printf("Unmarshaled struct: %s\n", p)
	}
}
```

输出：

```
pJson string : {"name":"Mike","age":10}
Unmarshaled struct: This person name is Jack, age = 20
```

需要注意的是，`json.Unmarshal`传入的字符串，如果存在 `"{\"age\": 10, \"Age\": 20}"` 两个字段，那么在反序列化之后，得到的结构体对应的值是最后一个，即20。

我们通过**反射**获取结构体的tag，通过 `Field`方法返回一个`StructField`，然后取`Tag.Get` 获取对应的tag

```go
func main() {
    p := person{Name: "Mike", Age: 10}
    pt := reflect.TypeOf(p)
    for i := 0; i < pt.NumField(); i++ {
    	f := pt.Field(i)
    	fmt.Println(f.Tag.Get("json"))
	}
}
```

同一个结构体可以定义多个tag：

```go
type person struct {
    Name string `json:"name" bson:"b_name"`
    Age uint `json:"age" bson:"b_age"`
}
```

### 实现Struct转Json

```go
func StructToJson(i interface{}) string {
	builder := strings.Builder{}
	builder.WriteString("{")
	iv := reflect.ValueOf(i)
	it := reflect.TypeOf(i)
	numFields := it.NumField()
	for i := 0; i < numFields; i++ {
		f := it.Field(i)
		jTag := f.Tag.Get("json")
		builder.WriteString("\"" + jTag + "\":")
		builder.WriteString(fmt.Sprintf("\"%v\"", iv.Field(i)))
		if i < numFields - 1 {
			builder.WriteString(",")
		}
	}
	builder.WriteString("}")
	return fmt.Sprintf("%s", builder.String())
}

func main() {
    p := person{Name: "Mike", Age: 10}
    s := StructToJson(p)
    fmt.Println(s)
}
```

输出：

```
{"name":Mike,"age":10}
```

## 反射定律

反射是计算机语言中程序检视自身结构的一种方法，灵活、强大，可以绕过编译器的很多静态检查，过多使用会造成混乱。

1. 任何接口值 `interface{}`都可以反射出反射对象，即 `reflect.Value和reflect.Type`，通过函数 `reflect.ValueOf和reflect.TypeOf`获得
2. 反射对象也可以还原为 `interface{}`变量，即定律1 的可逆性，通过 `reflect.Value`的 `Interface`方法获得
3. 要修改反射的对象，该值必须可设置（传入指针）

## 总结

在反射中，获取变量的值、修改变量的值等，优先使用 `reflect.Value`；获取结构体内的字段、类型拥有的方法集等，优先使用 `reflect.Type`