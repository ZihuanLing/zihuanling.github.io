---
layout: post
title: "让github page支持mermaid语法"
date: 2022-03-04
tags: [daily]
comments: false
author: ZihuanLing
---

目前，github page 会将 markdown里面的 `mermaid` 块渲染成为一个 `div.language-mermaid` 的 html 代码块，但是，mermaid-js仅支持渲染 `div.mermaid` 的html代码块，因此，我们需要做一点处理。

<!-- more -->

我们只需要在文章模板的末尾，添加如下转化代码即可：
```markdown
文件：_layouts/post.html
{% raw %}
{%- if content contains 'mermaid' -%}
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
const config = {
    startOnLoad:true,
    theme: 'forest',
    flowchart: {
        useMaxWidth:false,
        htmlLabels:true
        }
};
mermaid.initialize(config);
window.mermaid.init(undefined, document.querySelectorAll('.language-mermaid'));
</script>
{% endif %}
{% endraw %}
```

上述代码手动将 `div.language-mermaid` 添加到 mermaid引擎的渲染中。

#### 引用

在文章里面指定文章layout，即可引用，并且渲染mermaid！
```markdown
---
layout: post
---
```

#### 其他方法

当然也可以在 `_config.yml` 配置kramdown, 让其可以将 `mermaid` 块渲染成 `div.mermaid` 这样的html的代码块，但是实现起来有点复杂。

参考： [Issue https://github.com/gettalong/kramdown/issues/637](https://github.com/gettalong/kramdown/issues/637)
