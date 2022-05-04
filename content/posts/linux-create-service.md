---
title: "Linux创建简单的systemd服务"
date: 2022-05-04T22:38:12+08:00
tags: [linux, linux-service]
categories: [linux]
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

参考地址：

- https://linuxconfig.org/how-to-write-a-simple-systemd-service

- https://www.freedesktop.org/software/systemd/man/systemd.service.html

# 前言

`systemd`是系统的服务和进程的管理工具，在linux系统下，我们使用 `ps aux | head`，我们可以看到，系统启动的第一个进程就是systemd。

有时候，我们想要让程序运行在后台，而不是一直在前台，开一个终端挂着。（使用nohup可以实现这个）

有时候，想要在开机的时候就自动启动某个服务，比如redis、mysql、nginx这些，这时候，我们就可以将这些程序的启动编写成为一个服务，这样，在系统启动的时候，systemd会自动加载服务配置，然后启动这些服务。

现在，我想要创建一个**python jupyter notebook**服务。

# 创建文件

systemd services存在路径 `/etc/systemd/system` 下，我们在这路径下创建的 `.service` 文件，都可以作为系统服务运行。

我们创建一个 `notebook.service`

```bash
vi notebook.service
```

文件创建完毕后，我们开始编写里面的内容，一个 `.service`文件里面包含三个关键部分： `Unit, Service, Install`

## Unit

对于一个简单服务来说，我们在 `[Unit]` 这个块只要写上服务描述就可以了，字段为Description。

```ini
[Unit]
Description=Jupyter notebook service at port[8080]
```

## Serivce

`[Service]` 块是服务配置的集合，这里面的配置声明了该如何去运行这个服务。

```ini
[Service]
Type=simple
ExecStart=/usr/bin/env /root/miniconda3/bin/jupyter notebook
Restart=on-failure
User=root
WorkingDirectory=/tmp/notebook
```

在Serivce声明中，我们首先要说明这个服务的类型 `Type=simple`

然后，是最重要的部分，我们需要告诉系统应该去执行什么东西： `ExecStart=/usr/bin/env /root/miniconda3/bin/jupyter notebook`， 这里，我们指定了执行 jupyter notebook 这个命令，前面加载了用户的环境变量。

随后指定这个服务的重启策略：`Restart=on-failure`， 我要求的是启动失败后重启

最后，这个服务运行的角色：`User=root`，以及运行时所在路径： `WorkingDirectory=/tmp/notebook`

## Install

`[Install]` 块声明了当前服务应该应该怎样启用，常用的就是 `WantedBy=multi-user.target`

```ini
[Install]
WantedBy=multi-user.target
```

# 启动服务

服务写完了，我们需要将其启动起来：

```bash
# 启用
systemctl enable notebook
# 启动
systemctl start notebook
```



ok，至此，一个简单的 `notebook.service` 就创建并启动完成了。

还有更多高级的用法，可以参考：https://www.freedesktop.org/software/systemd/man/init.html#