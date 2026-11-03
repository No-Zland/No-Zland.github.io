---
title: 算法竞赛 · 总舵
tags: [MOC, 导航]
---

# 🧭 算法竞赛 · 总舵

> 结构约定：文件夹只管"形态"（导航 / 知识 / 实战），知识点交给标签，一道题只有一份、永远在 `02-实战库/刷题/`。
> 新建笔记前先看 [[模板/题目复盘模板]]，不要手动起名字。

## 一、进度概览

- 题目总数：`$= dv.pages('"02-实战库/刷题"').length`
- 待复盘：`$= dv.pages('"02-实战库/刷题"').where(p => p.file.tags.includes("#状态/待复盘")).length`
- 复习中：`$= dv.pages('"02-实战库/刷题"').where(p => p.file.tags.includes("#状态/复习中")).length`
- 已掌握：`$= dv.pages('"02-实战库/刷题"').where(p => p.file.tags.includes("#状态/已掌握")).length`
- 理论卡片：`$= dv.pages('"01-知识库/算法"').length`

## 二、复习队列（搁置越久越靠前）

```dataview
TABLE WITHOUT ID
  file.link AS "题目",
  difficulty AS "难度",
  map(filter(file.tags, (t) => startswith(t, "#算法/")), (t) => replace(t, "#算法/", "")) AS "考点",
  reviewed AS "上次复盘",
  (date(today) - reviewed).days AS "搁置(天)"
FROM "02-实战库/刷题"
WHERE (contains(file.tags, "#状态/待复盘") OR contains(file.tags, "#状态/需重做")) AND reviewed
SORT reviewed ASC
LIMIT 20
```

> `AND reviewed` 是必要的：没有复盘日期的行会被排除，否则天数会算成负数。

## 三、最近 7 天动过的题

```dataview
TABLE WITHOUT ID file.link AS "题目", file.mtime AS "修改时间", difficulty AS "难度"
FROM "02-实战库/刷题"
WHERE file.mtime >= date(today) - dur(7 days)
SORT file.mtime DESC
LIMIT 15
```

## 四、领域覆盖度（哪块还是空的，一眼看见）

```dataview
TABLE WITHOUT ID domain AS "领域", length(rows) AS "题数"
FROM "02-实战库/刷题"
FLATTEN file.tags AS tag
FLATTEN split(tag, "/")[1] AS domain
WHERE startswith(tag, "#算法/")
GROUP BY domain
SORT length(rows) DESC
```

## 五、导航入口

| MOC | 说明 |
|---|---|
| [[MOC-算法总览]] | 全库视角：领域 / 平台 / 难度 / 体检 |
| [[MOC-动态规划]] | 单知识点范本，复制后改标签即可 |
| [[MOC-20天速通LeetCode]] | 刷题路线（外部题单） |

## 六、库体检

```dataview
TABLE WITHOUT ID file.link AS "缺 #算法/ 标签"
FROM "02-实战库/刷题"
WHERE length(filter(file.tags, (t) => startswith(t, "#算法/"))) = 0
```

```dataview
TABLE WITHOUT ID file.link AS "没有复盘日期"
FROM "02-实战库/刷题"
WHERE !reviewed
```
