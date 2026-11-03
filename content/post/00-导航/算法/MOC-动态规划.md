---
title: MOC · 动态规划
tags: [MOC, 算法/动态规划]
---

# 🧩 动态规划

> **这是"单个知识点 MOC"的范本**：复制此文件 → 改文件名 → 把下面所有 `#算法/动态规划` 换成你的领域（如 `#算法/图论`），就是一页新 MOC。
> 不要在这一页手写题目清单，Dataview 会自动把它长出来。

## 一、本域考点分布

```dataview
TABLE WITHOUT ID topic AS "考点", length(rows) AS "题数", rows.file.link AS "题目"
FROM "02-实战库/刷题"
FLATTEN filter(file.tags, (t) => startswith(t, "#算法/动态规划/") AND length(split(t, "/")) = 3) AS tag
FLATTEN split(tag, "/")[2] AS topic
GROUP BY topic
SORT length(rows) DESC
```

## 二、全部 DP 题（跨域题也会在这里出现）

```dataview
TABLE WITHOUT ID
  file.link AS "题目",
  map(filter(file.tags, (t) => startswith(t, "#算法/动态规划/")), (t) => replace(t, "#算法/动态规划/", "")) AS "DP 考点",
  difficulty AS "难度",
  reviewed AS "上次复盘"
FROM "02-实战库/刷题"
WHERE any(map(file.tags, (t) => startswith(t, "#算法/动态规划")))
SORT reviewed DESC
```

## 三、待复盘

```dataview
TABLE WITHOUT ID file.link AS "题目", reviewed AS "上次复盘", (date(today) - reviewed).days AS "搁置(天)"
FROM "02-实战库/刷题"
WHERE any(map(file.tags, (t) => startswith(t, "#算法/动态规划")))
  AND (contains(file.tags, "#状态/待复盘") OR contains(file.tags, "#状态/需重做"))
  AND reviewed
SORT reviewed ASC
```

## 四、相关的理论卡片

```dataview
TABLE WITHOUT ID file.link AS "卡片", level AS "类型"
FROM "01-知识库/算法"
WHERE any(map(file.tags, (t) => startswith(t, "#算法/动态规划")))
```

---

## ✍️ 手工区

### 状态设计五步

1. **问"什么在变"** —— 变化的量就是维度，不要一上来就写 `dp[i][j]`。
2. **问"决策是什么"** —— 每个转移对应一个选择，选择集合决定复杂度。
3. **问"边界在哪"** —— 空集、长度 1、`i = 0` 要先写死。
4. **问"答案在哪个状态"** —— 是 `dp[n]` 还是 `max(dp[...])`，先定终点再写递推。
5. **问"能不能砍一维"** —— 滚动数组 / 前缀和 / 单调队列，先跑通再优化。

### 常见坑

- 数位 DP 的 `limit` 与 `lead`（前导零）必须一起记，漏一个就多算。
- 01 背包倒序、完全背包正序；写反了答案会偏大而不是偏小，很难一眼看出。
- 区间 DP：先枚举区间长度再枚举左端点，顺序反了会用到未初始化状态。
- 期望 DP：正推期望、倒推概率，混用会得到"看起来对但差一点"的结果。
