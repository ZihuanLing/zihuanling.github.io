---
title: "Go与Hdf5，数据读写实践"
date: 2022-04-23T22:10:10+08:00
tags: [go,hdf5]
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

# 前言

HDF5 (Hierarchical Data Format) 是由美国伊利诺伊大学厄巴纳-香槟分校，是一种跨平台传输的文件格式，存储图像和数据

## 优势

- 通用数据模型，可以通过无限多种数据类型表示非常复杂、异构的数据对象和各种各样的元数据
- 高速原始数据采集
- 可移植和可扩展，文件大小没有限制
- 自描述的，不需要外部信息应用程序来解释文件的结构和内容
- 拥有用于管理、操作、查看和分析数据的开源工具和应用程序软件生态系统
- 在各种计算平台和编程语言（包括C、C++、Fortran90和Java）上运行的软件库。

参考文章链接： [大数据存储 hdf5简介](https://cloud.tencent.com/developer/article/1786168)

# 实践

## 环境安装

对于go语言，hdf5已经有了支持的库： [gonum/hdf5](https://github.com/gonum/hdf5)，我们可以直接安装这个包，并且使用。

需要注意的是，这个包使用了 `cgo`，依赖了hdf5的C语言库，因此，需要我们自己预先安装，使用centos系统，可以很方便安装，直接使用命令： 

```bash
yum install -y hdf5 hdf5-devel
```

当然，如果系统没有软件源的话，hdf5也提供了源码安装，下载 [hdf5-1.12.1](https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.1/src/hdf5-1.12.1.tar.bz2)，解压后，执行安装：

```bash
cd hdf5-1.12.1
./configure --prefix /usr/local
make -j 2 && make install
```

然后我们初始化一个项目，名为 `h5`，用于编写go、hdf5 的简单测试用例

```bash
mkdir -p ~/go/src/h5
cd ~/go/src/h5
go mod init
# 安装
go get -v gonum.org/v1/hdf5
```

## 使用

### 创建文件
```go
func main() {
	// 创建hdf5文件
	f, err := hdf5.CreateFile("data.h5", hdf5.F_ACC_TRUNC)
	if err != nil {
		panic(fmt.Errorf("failed to create hdf5 file: %e", err))
	}
	defer f.Close()
    fmt.Println("File created.")
}
```

创建文件的代码就一行： `hdf5.CreateFile("data.h5", hdf5.F_ACC_TRUNC)`，其中 data.h5 为文件的名称，使用flag为`hdf5.F_ACC_TRUNC`，如果文件已存在的话，会清除原始文件里面的内容。


### 写入数据

```go
func write() {
	var f *hdf5.File
	var err error
	if f, err = hdf5.OpenFile("data.h5", hdf5.F_ACC_RDWR); err != nil {
		panic(fmt.Errorf("failed to create hdf5 file: %e", err))
	}
	defer f.Close()
	// 写入 10x10 矩阵
	data := [10][10]int32{}
	for i := 0; i < 10; i ++ {
		for j := 0; j < 10; j++ {
			data[i][j] = int32((i * 10) + (j + 1))
		}
	}
	// 创建datatype
	dtype, err := hdf5.NewDataTypeFromType(reflect.TypeOf(data[0][0]))
	if err != nil { panic(fmt.Errorf("failed to create datatype: %s", err))}
	// 创建dataspace
	dims := []uint{10, 10}
	dspace, err := hdf5.CreateSimpleDataspace(dims, dims)
	if err != nil { panic(fmt.Errorf("failed to create datasapce: %s", err))}
	// 创建dataset
	ds, err := f.CreateDataset("data", dtype, dspace)
	if err != nil {	panic(fmt.Errorf("failed to create dataset: %s", err)) }
	// 写入数据
	if err = ds.Write(&data); err != nil {
		panic(fmt.Errorf("write dataset error: %s", err))
	}
}
```

写入的过程，可以分为以下几个步骤：

- `hdf5.OpenFile` 打开一个hdf5文件
- 准备好需要写入的数据`data`
- `hdf5.NewDataTypeFromType` 从数据创建DataType，表明当前dataset存储的数据类型
- `hdf5.CreateSimpleDataspace` 创建DataSpace，表明当前dataset的数据存储space，有数据的形状是怎样的
- `hdf5.CreateDataset` 创建dataset，使用前两个步骤创建的 datatype和dataspace，这是存储数据的主空间
- 最后，调用`dataset.Write` 将数据写入dataset中

写入完成后，我们使用 `hdf5` 工具 `h5ls` 查看数据的内容：

```
$ h5ls -d data.h5/data
data                     Dataset {10, 10}
    Data:
         1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
         36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
         69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100
```

命令 `h5ls -d data.h5/data` 查看文件 **data.h5**里面名为**data**的dataset，参数 `-d` 要求打印出里面的数据内容

从内容可以表明，这是一个 **10x10**的数据集合。而从输出表明，数据在hdf5 里面是线性存储的。


### 读取数据

```go
func read() {
	var f *hdf5.File
	var err error
	if f, err = hdf5.OpenFile("data.h5", hdf5.F_ACC_RDWR); err != nil {
		panic(fmt.Errorf("failed to create hdf5 file: %e", err))
	}
	defer f.Close()
	// 读取 10x10 矩阵
	data := [10][10]int32{}
	ds, err := f.OpenDataset("data")
	if err != nil { panic(fmt.Errorf("failed to open dataset: %s", err))}
	ds.Read(&data)
	fmt.Printf("data: %v\n", data)
}
```

读取比较简单，这里是读取所有数据
- `hdf5.OpenFile` 打开文件
- `file.OpenDataset` 打开dataset
- `ds.Read` 将dataset中的数据读取到 data 中

运行结果
```
$ go run main.go 
data: [[1 2 3 4 5 6 7 8 9 10] [11 12 13 14 15 16 17 18 19 20] [21 22 23 24 25 26 27 28 29 30] [31 32 33 34 35 36 37 38 39 40] [41 42 43 44 45 46 47 48 49 50] [51 52 53 54 55 56 57 58 59 60] [61 62 63 64 65 66 67 68 69 70] [71 72 73 74 75 76 77 78 79 80] [81 82 83 84 85 86 87 88 89 90] [91 92 93 94 95 96 97 98 99 100]]
```

定义的 data 是 10x10 的，dataset中的数据也是 10x10 的，刚好可以容纳所有的数据。

如果定义的data不足10x10，则只会读取 `m x n` 的数据量存储于 data 中，比如data为 3x3 矩阵，则只会读取 1,2,3,4,5,6,7,8,9 这几个数值

如果定义的data超过 10x10，则会按照顺序存储到data中，比如 10 x 11, 则第一行为 1...11 , 第二行 12...22 ... 以此类推。这也说明了h5文件中的数据是线性存储的。 需要注意的是，如果data大小超过了dataspace，则data的剩下的空间为对应的零值。


### end

更多测试用例例子，见：https://github.com/gonum/hdf5/blob/master/h5d_dataset_test.go

