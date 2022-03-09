---
layout: post
title: "使用 getopts 获取命令行中的参数"
date: 2022-02-24
tags: [bash,linux]
comments: false
categories: [linux]
---

在某些场景中，我们写的bash脚本需要获取命令行中指定的某些参数，用以判断某些条件，或者设置某些变量等。

getopts可以让我们通过指定 `-a 1` 的方式指定对应的参数名称和参数值。

<!-- more -->

### 一个更详细的小教程，可以看这里： [getopts_tutorial](https://wiki.bash-hackers.org/howto/getopts_tutorial)

### 使用

可以使用 `while getopts ":a:p:" opt; do...` 的方式，将参数名称读取到 `opt` 变量中，然后，在循环体中，使用 `$OPTARG` 获取到具体的参数值。

一个小栗子，用于快捷创建新的 gihub pages 博客模板：
```bash
#!/usr/bin/env bash

# 用于快捷创建新博客
# 命令： ./new.sh -t 标签1,标签2 -n 文章标题 -l layout -c 1

layout="post"
title="new-post"
now=$(date +%Y-%m-%d)
can_comment="false"
author="ZihuanLing"

while getopts ":l:t:c:n:" opt; do
  case $opt in 
    l)
      layout="$OPTARG"
      ;;
    t) 
      tags="[$OPTARG]"
      ;;
    c)
      can_comment="true"
      ;;
    n)
      title=$(echo "$OPTARG" | sed "s/ /\-/g")
      ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac 
done

if [ -z $tags ]; then
  tags="[]"
fi

filename="_posts/${now}-${title}.md"

read -r -d '' content << EOM
---
layout: ${layout}
title: "${title}"
date: ${now}
tags: ${tags}
comments: ${can_comment}
author: ${author}
---

<!-- more -->

EOM

echo "$filename"
echo "$content"
echo "$content" > $filename
```
