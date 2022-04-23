---
title: "Go与Hdf5，数据读写实践"
date: 2022-04-23T22:10:10+08:00
tags: [go,hdf5]
categories: [go]
showToc: true
TocOpen: false
draft: true
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

然后我们初始化一个项目，名为 `h5`，用于编写go、hdf5 的简单测试用例

```bash
mkdir -p ~/go/src/h5
cd ~/go/src/h5
go mod init
# 安装
go get -v gonum.org/v1/hdf5
```

