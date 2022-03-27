---
title: "Go：简单的http服务以及Restful Api"
date: 2022-03-27T15:27:00+08:00
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

## 简易 http 服务

使用 go 自带的 http 模块实现一个简单的 http 服务器，对请求者说一句 `Hello, go http!`

```go
func main(){
	http.HandleFunc("/hello", sayHello)
	http.ListenAndServe(":8080", nil)
}

func sayHello(resp http.ResponseWriter, req *http.Request) {
	log.Println("In say hello")
	resp.WriteHeader(http.StatusOK)
	resp.Write([]byte("Hello, go http!"))
}

```

运行上述代码，在终端使用 curl 访问该地址，返回正常：

```
>curl http://localhost:8080/hello
Hello, go http!
```

且程序使用 `log` 打印了一句： `2022/03/27 15:32:48 In say hello`

但是，我们的http方法有很多， GET/POST/PUT/PATCH/DELETE 等，我们使用任意一个方法，访问上述地址，都能得到 `Hello, go http!` 这句返回，如 `POST`:

```
>curl -X POST http://localhost:8080/hello
Hello, go http!
```

`http.Request` 这个结构体中，包含了一个 `Method` 字段，让我们可以根据不同的方法，决定不同的处理方式，我们将 `sayHello` 方法改造如下：

```go
func sayHello(resp http.ResponseWriter, req *http.Request) {
	log.Println("In say hello")
	switch req.Method {
	case "GET":
		fmt.Fprintln(resp, "GET: Hello, go http!")
	case "POST":
		fmt.Fprintln(resp, "POST: Hello, go http!")
	default:
		resp.WriteHeader(http.StatusNotFound)
		fmt.Fprintln(resp, "Not found")
	}
}
```

请求输出：

```
>curl http://localhost:8080/hello
GET: Hello, go http!

>curl -X POST http://localhost:8080/hello
POST: Hello, go http!

>curl -X PUT http://localhost:8080/hello
Not found
```



## 基于 gin 框架的 RESTFUL API 服务

虽然go自带的net/http包可以方便的创建HTTP服务，但是其包含以下不足：

- 不能单独地对请求方法（POST/GET等）注册特定的处理函数
- 不支持 path 变量参数
- 不能自动对 path 进行校准
- 性能一般
- 扩展性不足
- 。。。

**gin**是 github 上开源的一个 go web 框架，它是一个包，我们可以通过 go.mod 进行引入

接下来，我们使用gin框架实现一个简单的用户查询系统

### 引入 gin框架

安装命令：

```bash
go get github.com/gin-gonic/gin
```

引入：

```go
import "github.com/gin-gonic/gin"
```

### 使用gin框架

使用gin框架，我们可以简单的这样写：

```go
func main(){
    engine := gin.Default()
    engine.Run(":8080")
}
```

`gin.Default()`方法会返回一个 gin `Engine` 实例，我们调用这个 实例的 `Run`方法，传入监听的地址，就可以实现一个简单的gin服务。

处理具体路径的请求，我们可以使用 `engine.Handle`方法

#### 定义 User 结构体：

```go
type User struct {
	ID uint			`json:"id"`
	Age uint		`json:"age"`
	Name string		`json:"name"`
}

// 初始用户列表
var userList []User = []User{ {1, 19, "Mike"}, {2, 20, "Jack"} }
```

上述代码，我们定义了一个用户User的基本接口，包含字段 ID, Age, Name， 然后定义了 json struct tag，让gin返回的json字段小写。

#### 获取用户列表

我们接下来实现一个 `GET` 方法，这个方法请求路径 `/users`，返回所有的用户列表：

```go
// 获取用户列表
func getAllUsers(c *gin.Context) {
	log.Println("Getting user list")
	c.JSON(http.StatusOK, userList)
}
```

非常简单，`getAllUsers` 是一个Handler， 接收一个 `*gin.Contest`类型的参数，在这个Handler里面，我们直接将用户列表`userList`返回，使用 `c.JSON`方法，这个方法接收两个参数：

- 第一个是 http状态码
- 第二个是要返回的对象

这个方法会自动将返回对象序列化成为Json字符串

完成了一个Handler，我们接下来在gin中注册这个Handler

main.go

```go
func main(){
	engine := gin.Default()
	engine.Handle(http.MethodGet, "/users", getAllUsers)
	engine.Run(":8080")
}
```

运行上述程序，然后在终端测试：

```
>curl http://localhost:8080/users
[{"id":1,"age":19,"name":"Mike"},{"id":2,"age":20,"name":"Jack"}]
```

可以看到，正常返回了用户列表

#### 查询具体用户

```go
// 查询用户
func queryUser(c *gin.Context) {
	id := c.Param("id")
	log.Printf("Querying user with id = %s", id)
	for _, u := range userList {
		if strings.EqualFold(id, strconv.Itoa(int(u.ID))) {
			log.Printf("Found user: %v", u)
			c.JSON(http.StatusOK, u)
			return
		}
	}
	log.Printf("User %s not found", id)
	c.JSON(http.StatusNotFound, gin.H{
		"message": "user not found.",
	})
}
```

我们实现了一个 `queryUser` handler，这个handler处理的方法是 GET，请求的api是 `/users/:id` 里面的 **id** 是路径参数，在gin中，我们通过 `c.Param()` 方法，获取路径参数，这个方法返回的是一个 `string`类型的变量，我们用定义的 `ID`字段是 uint 类型的，因此，我们需要使用 `strconv.Itoa` 对其进行一个转换，然后通过对比查找对应的用户。

找到对应的用户之后，我们通过 `c.JSON` 返回用户，否则，我们返回一个 `404 Not Found`

里面用到的 `gin.H` 本质是一个 `map[string]interface{}` 类型，用来方便返回一些信息

在 `main`中注册新的Handler：

```go
func main(){
    //...
    engine.Handle(http.MethodGet, "/users/:id", queryUser)
    //...
}
```

运行程序后，测试：

```
>curl http://localhost:8080/users/1
{"id":1,"age":19,"name":"Mike"}				# 查询到id为1的用户
>curl http://localhost:8080/users/3			# id为3的用户不存在
{"message":"user not found."}
```

可以看到，在用户存在或不存在的情况下，都可以正常返回

#### 创建新用户

```go
// 创建用户
func createUser(c *gin.Context) {
	var name string
	var age uint

	if name_, ok := c.GetPostForm("name"); !ok {
		msg := "[name] field missed."
		log.Println(msg)
		c.JSON(http.StatusBadRequest, gin.H{"message": msg})
		return
	} else {
		name = name_
	}
	if age_, ok := c.GetPostForm("age"); !ok {
		msg := "[age] field missed."
		log.Println(msg)
		c.JSON(http.StatusBadRequest, gin.H{"message": msg})
		return
	} else {
		_age, err := strconv.Atoi(age_)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid age: " + age_})
			return
		}
		age = uint(_age)
	}
	// find last ID
	var lastID uint = userList[len(userList) - 1].ID
	// create user
	newUser := User{ID: lastID+1, Age: age, Name: name}
	userList = append(userList, newUser)
	c.JSON(http.StatusOK, gin.H{"message": "ok, new user id : " + strconv.Itoa(int(newUser.ID))})
	log.Printf("New user created, id = %d", newUser.ID)
}
```

创建用户，我们通过 `POST`方法，请求 `/users` ，传入的参数有两个字段： name，age。

gin框架中，我们通过 `c.GetPostForm` 方法，获取`POST`方法里面的内容，返回 `string, bool`，我们可以通过返回的flag，判断用户是否传了对应的值，以实现特定的逻辑。当然，我们也可以通过 `c.DefaultPostForm`, 在获取不到指定值的情况下，返回一个空字符串。

然后通过取到最后一个用户的ID，生成下一个用户的ID，实现自增。（其实这样有很大的缺陷，比如我们删除了最后一个用户之后，新建的用户ID可能会跟刚刚删除的用户ID一样，导致冲突。）

注册Handler：

```go
func main(){
    //...
    engine.Handle(http.MethodPost, "/users", createUser)
    //...
}
```

运行、测试：

```
>curl -X POST  http://localhost:8080/users
{"message":"[name] field missed."}		# 错误：不带name参数
>curl -X POST  http://localhost:8080/users -d "name=Jack"
{"message":"[age] field missed."}		# 错误：不带age参数
>curl -X POST  http://localhost:8080/users -d "name=Jack" -d "age=aa"
{"message":"Invalid age: aa"}			# 错误的 age 参数
>curl -X POST  http://localhost:8080/users -d "name=Jack" -d "age=29"
{"message":"ok, new user id : 3"}		# 创建成功，新用户ID 为 3
>curl http://localhost:8080/users		# 查看用户列表，新用户成功创建
[{"id":1,"age":19,"name":"Mike"},{"id":2,"age":20,"name":"Jack"},{"id":3,"age":29,"name":"Jack"}]
```

#### 修改用户

```go
// 修改用户
func modifyUser(c *gin.Context) {
	id := c.Param("id")
	var age int
	name := c.DefaultPostForm("name", "")
	_age := c.DefaultPostForm("age", "")
    // 两个必传参数
	if name == "" || _age == "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": "[name] and [age] is required."})
		return
	}
	// string to int
	age, err := strconv.Atoi(_age)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid age: " + _age})
		return
	}
	log.Printf("Modify user with id = %s", id)
    // 查找用户进行修改
	for idx, u := range userList {
		if strings.EqualFold(id, strconv.Itoa(int(u.ID))) {
			log.Printf("Found user: %v", u)
			u.Name = name
			u.Age = uint(age)
			userList[idx] = u
			log.Printf("User modified to: %v", u)
			c.JSON(http.StatusOK, gin.H{"message": "ok"})
			return
		}
	}
	log.Printf("User %s not found", id)
	c.JSON(http.StatusNotFound, gin.H{"message": "user not found."})
}
```

逻辑简单，直接从post方法传过来的数据中，获取name和age字段，然后查找对应的用户，对其进行修改，当用户不存在的情况下，返回 `404 Not Found`

注册 Handler：

```go
func main(){
    //...
    engine.Handle(http.MethodPut, "/users/:id", modifyUser)
    //...
}
```

运行，测试：

```
>curl http://localhost:8080/users		# 当前的用户列表
[{"id":1,"age":19,"name":"Mike"},{"id":2,"age":20,"name":"Jack"}]
>curl -X PUT http://localhost:8080/users/4 -d "name=Amy"				# 参数缺失
{"message":"[name] and [age] is required."}
>curl -X PUT http://localhost:8080/users/4 -d "name=Amy" -d "age=10"	# id=4的用户不存在
{"message":"user not found."}
>curl -X PUT http://localhost:8080/users/2 -d "name=Amy" -d "age=10"	# 修改成功
{"message":"ok"}
>curl http://localhost:8080/users
[{"id":1,"age":19,"name":"Mike"},{"id":2,"age":10,"name":"Amy"}]		# 修改成功后的用户列表
```

可以看到，表现符合预期。

#### 删除用户

```go
// 删除用户
func deleteUser(c *gin.Context) {
	id := c.Param("id")
	log.Printf("Querying user with id = %s", id)
	for idx, u := range userList {
		if strings.EqualFold(id, strconv.Itoa(int(u.ID))) {
			log.Printf("Deleting user: %v", u)
			for ; idx < len(userList) - 1; idx++ {
				userList[idx] = userList[idx+1]
			}
			userList = userList[:len(userList) - 1]
			c.JSON(http.StatusOK, gin.H{"message": "ok"})
			return
		}
	}
	log.Printf("User %s not found", id)
	c.JSON(http.StatusNotFound, gin.H{
		"message": "user not found.",
	})
}
```

这里删除用户的逻辑也是很简单的：从传入的用户id里面找到当前用户的位置，然后从数组里面将该用户删除掉即可。

这里使用的是数据覆盖，实际业务逻辑中，我们可以使用Mongo、MySQL等数据引擎，实现CRUD操作。

```go
func main(){
    //...
    engine.Handle(http.MethodDelete, "/users/:id", deleteUser)
    //...
}
```

运行、调试：

```
>curl http://localhost:8080/users
[{"id":1,"age":19,"name":"Mike"},{"id":2,"age":20,"name":"Jack"}]	# 当前的所有用户
>curl -X DELETE http://localhost:8080/users/2	# 删除第二个用户
{"message":"ok"}
>curl http://localhost:8080/users
[{"id":1,"age":19,"name":"Mike"}]		# 剩下一个用户
```

<hr>

附代码：

```go
package main

import (
	"github.com/gin-gonic/gin"
	"log"
	"net/http"
	"strconv"
	"strings"
)


func main(){
	engine := gin.Default()
	engine.Handle(http.MethodGet, "/users", getAllUsers)
	engine.Handle(http.MethodPost, "/users", createUser)
	engine.Handle(http.MethodGet, "/users/:id", queryUser)
	engine.Handle(http.MethodPut, "/users/:id", modifyUser)
	engine.Handle(http.MethodDelete, "/users/:id", deleteUser)
	engine.Run(":8080")
}

type User struct {
	ID uint			`json:"id"`
	Age uint		`json:"age"`
	Name string		`json:"name"`
}

// 初始用户列表
var userList []User = []User{ {1, 19, "Mike"}, {2, 20, "Jack"} }

// 获取用户列表
func getAllUsers(c *gin.Context) {
	log.Println("Getting user list")
	c.JSON(http.StatusOK, userList)
}

// 查询用户
func queryUser(c *gin.Context) {
	id := c.Param("id")
	log.Printf("Querying user with id = %s", id)
	for _, u := range userList {
		if strings.EqualFold(id, strconv.Itoa(int(u.ID))) {
			log.Printf("Found user: %v", u)
			c.JSON(http.StatusOK, u)
			return
		}
	}
	log.Printf("User %s not found", id)
	c.JSON(http.StatusNotFound, gin.H{
		"message": "user not found.",
	})
}

// 创建用户
func createUser(c *gin.Context) {
	var name string
	var age uint

	if name_, ok := c.GetPostForm("name"); !ok {
		msg := "[name] field missed."
		log.Println(msg)
		c.JSON(http.StatusBadRequest, gin.H{"message": msg})
		return
	} else {
		name = name_
	}
	if age_, ok := c.GetPostForm("age"); !ok {
		msg := "[age] field missed."
		log.Println(msg)
		c.JSON(http.StatusBadRequest, gin.H{"message": msg})
		return
	} else {
		_age, err := strconv.Atoi(age_)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid age: " + age_})
			return
		}
		age = uint(_age)
	}
	// find last ID
	var lastID uint = userList[len(userList) - 1].ID
	// create user
	newUser := User{ID: lastID+1, Age: age, Name: name}
	userList = append(userList, newUser)
	c.JSON(http.StatusOK, gin.H{"message": "ok, new user id : " + strconv.Itoa(int(newUser.ID))})
	log.Printf("New user created, id = %d", newUser.ID)
}

// 修改用户
func modifyUser(c *gin.Context) {
	id := c.Param("id")
	var age int
	name := c.DefaultPostForm("name", "")
	_age := c.DefaultPostForm("age", "")
	if name == "" || _age == "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": "[name] and [age] is required."})
		return
	}
	// string to int
	age, err := strconv.Atoi(_age)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid age: " + _age})
		return
	}
	log.Printf("Modify user with id = %s", id)
	for idx, u := range userList {
		if strings.EqualFold(id, strconv.Itoa(int(u.ID))) {
			log.Printf("Found user: %v", u)
			u.Name = name
			u.Age = uint(age)
			userList[idx] = u
			log.Printf("User modified to: %v", u)
			c.JSON(http.StatusOK, gin.H{"message": "ok"})
			return
		}
	}
	log.Printf("User %s not found", id)
	c.JSON(http.StatusNotFound, gin.H{
		"message": "user not found.",
	})
}

// 删除用户
func deleteUser(c *gin.Context) {
	id := c.Param("id")
	log.Printf("Querying user with id = %s", id)
	for idx, u := range userList {
		if strings.EqualFold(id, strconv.Itoa(int(u.ID))) {
			log.Printf("Deleting user: %v", u)
			for ; idx < len(userList) - 1; idx++ {
				userList[idx] = userList[idx+1]
			}
			userList = userList[:len(userList) - 1]
			c.JSON(http.StatusOK, gin.H{"message": "ok"})
			return
		}
	}
	log.Printf("User %s not found", id)
	c.JSON(http.StatusNotFound, gin.H{
		"message": "user not found.",
	})
}
```

