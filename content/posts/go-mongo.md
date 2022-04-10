---
title: "Go 使用mongodb"
date: 2022-04-10T16:06:40+08:00
tags: [go, mongo]
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

# 安装

```bash
mkdir go-mongo
go mod init go-mongo
go get go.mongodb.org/mongo-driver/mongo
```

# 使用

数据库里面有一条这样的数据：

```json
{
  "_id": {
    "$oid": "6252912ec4495f97bccf41aa"
  },
  "title": "My Mongo Post",
  "create_time": {
    "$date": "2022-04-10T10:33:45.149Z"
  },
  "viewer": 201
}
```

## 连接数据库

```go
// 关键代码
const MONGO_URI = "mongodb://localhost:27017/test"
client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(MONGO_URI))

// 优雅关闭连接
defer client.Disconnect(context.TODO())
```

## 数据查询

首先获取到对应的`database`以及`collection`

```go
coll := client.Database("test").Collection("post")
```

然后查询：

```go
coll := client.Database("test").Collection("post")
var result bson.M	// 需要一个bson.M 对象，用于存储查询回来的数据
// FindOne 接受2个参数，一个context，一个filter，filter 为 bson.D类型
err = coll.FindOne(context.TODO(), bson.D{}).Decode(&result)
if err == mongo.ErrNoDocuments {
    fmt.Printf("No document found.\n")
    return
} else if err != nil {
    panic(err)
}
fmt.Printf("Found document result: %s\n", result)
```

数据查询注意点：

- 需要一个 `bson.M` 对象，用于存储返回的数据
- `Collection.FindOne` 接受3个参数，ctx、filter和opts，返回的是一个 `SingleResult` 对象
  - ctx可以为nil，如果为nil的话，默认会创建一个 `context.Backgroud`的context
  - `filter`为查询条件，为 `bson.D` 类型，上面代码默认为空，意味着查询任意一条数据。也可以指定特定的条件，如 `bson.d{{"title", "first post"}}`，意味着查询 tile 为 first post 的文档。
  - opts：类型为 `options.FindOneOptions` 类型，查询的额外条件，比如限定返回的具体字段：`&options.FindOneOptions{Projection: map[string]int{"_id": 0}}`，这个options禁止返回`_id`字段。
- 使用 `SingleResult.Decode`方法将返回的`SingleResult`反序列化为 `bson.M` 对象，`SingleResult.Decode(&result)`

上述查询输出：

```
Found document result: map[_id:ObjectID("6252912ec4495f97bccf41aa") create_time:%!s(primitive.DateTime=1649548800000) title:My Mongo Post viewer:%!s(int32=201)]
```

### bson数据转struct

通过 `SingleResult.Decode` 转化而来的是一个bson.M对象，实际的应用场景中，这种格式的对象是很难用的，因此，我们需要将其Unmarshal一下，反序列化成为一个结构体。

我们的post有几个字段：title、viewer、create_time，因此，我们定义一个 `Post`结构体，将这些字段映射到结构体里面：

```go
type Post struct {
	Title      string    `bson:"title"`
	Viewer     int32     `bson:"viewer"`
	CreateTime time.Time `bson:"create_Time"`
}

func (p Post) String() string {
	return fmt.Sprintf("Title: %s\nCreated at: %s\nViewers: %d\n", p.Title, p.CreateTime, p.Viewer)
}
```

同时，我们给这个结构体实现了 `Stringer` 接口，打印出特定的数据格式。

接下来，我们将前面步骤取回的 `result` 转化成为 `Post` 结构体：

```go
doc, err := bson.Marshal(result)
if err != nil {
    fmt.Printf("bson.Marshal error: %s", err)
    return
}
err = bson.Unmarshal(doc, &post)
if err != nil {
    fmt.Printf("bson.Unmarshal error: %s", err)
    return
}
fmt.Println(post)
```

一共是两个步骤：

1. 将`bson.M`对象使用`bson.Marshal`序列化成为一个**bson字符串**
2. 使用 `bson.Unmarshal` 转化成struct结构体对象

重新运行上述代码，输出：

```
Title: My Mongo Post
Created at: 2022-04-10 10:33:45.149 +0000 UTC
Viewers: 201
```

可以看到，正常输出了内容，但是 `Datetime` 字段有些异常，primitive.Datetime 没能很好地转化成为 `Time` 对象。我们后续再研究下。

## 数据插入

数据插入可以支持直接的结构体插入：

```go
func insert(coll *mongo.Collection) {
	rand.Seed(time.Now().Unix())
	num := rand.Uint32()

	post := Post{
		Title:      "New post - " + strconv.Itoa(int(num)),
		Viewer:     num,
		CreateTime: time.Now(),
	}
	r, err := coll.InsertOne(nil, &post)
	if err != nil {
		fmt.Printf("Insert post error： %s\n", err)
		return
	}
	fmt.Printf("Data inserted: %s， \n%s", r.InsertedID, post)
}
```

运行后，数据库中多了一条数据：

```json
{
  "_id": {
    "$oid": "6252b289dfed1f0d342af950"
  },
  "title": "New post - 2596996162",
  "viewer": 2596996162,
  "create_Time": {
    "$date": "2022-04-10T10:33:45.149Z"
  }
}
```

可以看到数据是成功插入了的，但是时间 `create_time` 有点问题，跟实际时间不符，应该是时区的设置问题。

## 数据删除

```go
func delete(coll *mongo.Collection) {
	r, err := coll.DeleteOne(nil, bson.D{{"viewer", 1170169558}})
	if err != nil {
		fmt.Printf("Delete error: %s\n", err)
		return
	}
	fmt.Printf("Delete result: %d deleted", r.DeletedCount)
}
```

## 数据修改

```go
func update(coll *mongo.Collection) {
	r, err := coll.UpdateOne(
		nil,
		bson.D{{"title", "New post - 2596996162"}},
		bson.D{{"$set", bson.D{{"updated", true}}}},
	)
	if err != nil {
		fmt.Printf("update error: %s\n", err)
		return
	}
	fmt.Printf("Update result: %d updated.\n", r.ModifiedCount)
}
```

