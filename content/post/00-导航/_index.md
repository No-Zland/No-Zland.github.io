---
title: 知识库总览
tags: [MOC, 导航]
---

# 🏠 知识库总览

> 三级形态：`00-导航`（入口）/ `01-知识库`（可复用知识）/ `02-实战库`（一次性记录）。
> 知识点靠嵌套标签组织，题目只有一份，永远在 `02-实战库/刷题/`。

## 快速入口

| 区域 | 内容 | 入口 |
|---|---|---|
| 01-知识库 / 算法 | 理论卡片、MOC、比赛与培训整理 | [[算法/_index\|算法总舵]] |
| 01-知识库 / 课程 | C语言、C++、计组、汇编、数电、编译原理、计算机网络、Linux | — |
| 01-知识库 / 语言与工具 | Python、通信协议、IT 素养、AI | — |
| 01-知识库 / 科研 · 阅读 · 个人 | 参考文献、书籍资料、随笔与实验总结 | — |
| 02-实战库 / 刷题 | 所有题目（扁平） | [[MOC-算法总览]] |
| 02-实战库 / 竞赛 · 项目 | 数模、光电、机器人、安卓、网安… | — |

## 全库统计

- 笔记总数：`$= dv.pages('"01-知识库"').length + dv.pages('"02-实战库"').length`
- 题目数：`$= dv.pages('"02-实战库/刷题"').length`
- 待复盘：`$= dv.pages('"02-实战库/刷题"').where(p => p.file.tags.includes("#状态/待复盘")).length`
- 课程笔记：`$= dv.pages('"01-知识库/课程"').length`

## 最近改动的 15 篇

```dataview
TABLE WITHOUT ID file.link AS "笔记", file.folder AS "位置", file.mtime AS "修改时间"
FROM "01-知识库" OR "02-实战库"
SORT file.mtime DESC
LIMIT 15
```

## 待复盘队列

```dataview
TABLE WITHOUT ID file.link AS "题目", reviewed AS "上次复盘", (date(today) - reviewed).days AS "搁置(天)"
FROM "02-实战库/刷题"
WHERE contains(file.tags, "#状态/待复盘") AND reviewed
SORT reviewed ASC
LIMIT 10
```

## 标签体检（没有挂算法标签的题目）

```dataview
TABLE WITHOUT ID file.link AS "缺标签"
FROM "02-实战库/刷题"
WHERE length(filter(file.tags, (t) => startswith(t, "#算法/"))) = 0
```
