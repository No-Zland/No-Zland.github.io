---
title: MOC · 算法总览
tags: [MOC, 算法/总览]
---

# 🗺️ 算法总览

> 这一页 90% 的内容是 Dataview 生成的，**不需要手动维护题目清单**。只要题目打了 `#算法/领域/考点`，它就会出现在对应的分组里。
> 手写区只写"看代码看不出来的东西"：学习顺序、选型、易错点。

## 一、领域分布

```dataview
TABLE WITHOUT ID domain AS "领域", length(rows) AS "题数"
FROM "02-实战库/刷题"
FLATTEN file.tags AS tag
FLATTEN split(tag, "/")[1] AS domain
WHERE startswith(tag, "#算法/")
GROUP BY domain
SORT length(rows) DESC
```

## 二、考点分布（三级标签）

```dataview
TABLE WITHOUT ID topic AS "考点", length(rows) AS "题数", rows.file.link AS "题目"
FROM "02-实战库/刷题"
FLATTEN filter(file.tags, (t) => startswith(t, "#算法/") AND length(split(t, "/")) = 3) AS tag
FLATTEN split(tag, "/")[2] AS topic
GROUP BY topic
SORT length(rows) DESC
```

> `length(split(t, "/")) = 3` 只保留 `#算法/领域/考点` 这种三级标签，避免把 `#算法/动态规划` 这种两级标签也塞进考点表里。

## 三、按平台

```dataview
TABLE WITHOUT ID plat AS "平台", length(rows) AS "题数", rows.file.link AS "题目"
FROM "02-实战库/刷题"
FLATTEN filter(file.tags, (t) => startswith(t, "#平台/")) AS tag
FLATTEN split(tag, "/")[1] AS plat
GROUP BY plat
```

## 四、全部题目（按难度、题号）

```dataview
TABLE WITHOUT ID
  file.link AS "题目",
  difficulty AS "难度",
  map(filter(file.tags, (t) => startswith(t, "#算法/")), (t) => replace(t, "#算法/", "")) AS "考点",
  reviewed AS "上次复盘"
FROM "02-实战库/刷题"
SORT choice(difficulty = "入门", 1, choice(difficulty = "普及", 2, choice(difficulty = "提高", 3, choice(difficulty = "省选", 4, 5)))) ASC, pid ASC
```

## 五、一题多解（同时挂多个考点的题，最值得回看）

```dataview
TABLE WITHOUT ID
  file.link AS "题目",
  length(filter(file.tags, (t) => startswith(t, "#算法/"))) AS "考点数",
  map(filter(file.tags, (t) => startswith(t, "#算法/")), (t) => replace(t, "#算法/", "")) AS "考点"
FROM "02-实战库/刷题"
WHERE length(filter(file.tags, (t) => startswith(t, "#算法/"))) > 1
SORT length(filter(file.tags, (t) => startswith(t, "#算法/"))) DESC
```

## 六、理论卡片索引

```dataview
TABLE WITHOUT ID file.link AS "卡片", level AS "类型", file.mtime AS "更新"
FROM "01-知识库/算法"
SORT file.mtime DESC
LIMIT 30
```

---

## ✍️ 手工区（只写 Dataview 生成不了的内容）

### 建议学习顺序

1. 基础（枚举 / 模拟 / 排序 / 二分 / 双指针 / 前缀和）
2. 数据结构（并查集 / 堆 / 树状数组 / 线段树）
3. 动态规划（线性 → 背包 → 区间 → 树形 → 状压 → 数位）
4. 数论 / 图论 / 字符串并行推进，各刷 10 题打底
5. 搜索进阶、几何、博弈按比赛需要补

### 选型速查

| 场景 | 首选 | 备选 |
|---|---|---|
| 区间查询 + 单点改 | 树状数组 | 线段树 |
| 区间改 + 区间查 | 线段树（懒标记） | 分块 |
| 最短路，非负权 | Dijkstra + 堆 | — |
| 最短路，有负权 | SPFA（慎用） | Bellman-Ford |
| 多模式串匹配 | AC 自动机 | 字符串哈希 |
