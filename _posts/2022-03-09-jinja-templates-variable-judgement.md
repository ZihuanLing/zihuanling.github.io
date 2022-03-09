---
layout: post
title: "Jinja2: 判断变量是否为空、存在等"
date: 2022-03-09
tags: [jinja2]
comments: false
author: ZihuanLing
---

在 Jinja2 模板中，我们经常需要判断一个变量是否存在，里面的值是否为空等等。

<!-- more -->

### 检查变量是否存在，或者是否被定义

```jinja
{% raw %}
{% if variable is defined %}
    variable is defined
{% else %}
    variable is not defined
{% endif %}
{% endraw %}
```

### 检查数据的长度是否为空

对于列表类型的变量，我们可能需要知道这个列表是否为空的

```jinja
{% raw %}
{% if variable | length %}
    variable is not empty
{% else %}
    variable is empty
{% endif %}
{% endraw %}
```

需要注意的是，如果这个变量为非列表类型，模板渲染的时候会报错

### 检查变量值是否为True

```jinja
{% raw %}
{% if variable is sameas true %}
    variable is true
{% else %}
    variable is not true
{% endif %}
{% endraw %}
```

### 同样，我们也可以用关键字`and`来实现多个判断

#### 判断变量存在且不为空（列表型变量）

```jinja
{% raw %}
{% if variable is defined and variable | length %}
    variable is defined and is not empty
{% else %}
    variable is not defined or empty
{% endif %}
{% endraw %}
```

#### 判断变量存在且为true（布尔型变量）

```jinja
{% raw %}
{% if variable is defined and is sameas true %}
    variable is defined and is true
{% else %}
    variable is not defined or not true
{% endif %}
{% endraw %}
```
