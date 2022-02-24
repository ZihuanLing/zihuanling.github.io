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