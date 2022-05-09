---
title: "HTML a标签下载json数据"
date: 2022-05-09T20:52:39+08:00
tags: [HTML]
categories: [daily]
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

假如我们有一个json文件：`example.json`，我们想要将这个文件的连接放到网站上提供下载。

在HTML中这样写：

```html
<a href="http://lingzihuan.icu/leetcode-submissions.json">点击下载</a>
```

{{< raw >}}

<a href="http://lingzihuan.icu/leetcode-submissions.json">点击下载</a>

{{< /raw >}}

当我们点击链接的时候，chrome浏览器会自动打开一个页面，然后将json文件的内容加载进来，但是，当我们想要将文件下载到本地的时候，还得自己右键点击，然后选择”另存为“。

看过 Stack Overflow 上的提示，看到可以给其设定 `download`属性：

```html
<a href="http://lingzihuan.icu/leetcode-submissions.json" download>点击下载</a>
```

然并卵，没有用，我们要给a标签的`href`属性的url前面加入 `data:`才可解决：

```html
<a href="data:http://lingzihuan.icu/leetcode-submissions.json" download>点击下载</a>
```

{{< raw >}}

<a href="data:http://lingzihuan.icu/leetcode-submissions.json" download>点击下载</a>

{{< /raw >}}