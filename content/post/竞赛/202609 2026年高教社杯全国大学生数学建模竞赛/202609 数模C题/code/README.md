# 2026 国赛 C 题：微网与外部电网电力调控策略

本仓库按照比赛工程形式组织，根目录结构与常见算法项目保持一致，同时保留本题已经冻结的时间索引、因果信息边界、Q1-Q4求解器、结果写出和阶段24可视化。

---

## 1. 目录结构

```text
C题_服务器工程/
├─ configs/
│  ├─ default.json
│  └─ README.md
│
├─ data/
│  ├─ 附件1.xlsx
│  ├─ 附件2.xlsx
│  ├─ 附件3.xlsx
│  ├─ 附件4.xlsx
│  └─ README.md
│
├─ models/
│  ├─ 问题1_最终统一版.md
│  ├─ 问题2_最终统一版.md
│  ├─ 问题3_最终统一版.md
│  ├─ 问题4_动态电价模型_完整.md
│  ├─ README.md
│  └─ *.pkl                  # 运行后生成的结果缓存
│
├─ scripts/
│  ├─ check_env.py
│  ├─ run_server.sh
│  └─ README.md
│
├─ src/
│  ├─ config.py
│  ├─ time_index.py
│  ├─ data_loader.py
│  ├─ data_checker.py
│  ├─ model_base.py
│  ├─ question1_solver.py
│  ├─ forecast_model.py
│  ├─ scenario_tree.py
│  ├─ question2_solver.py
│  ├─ forecast_parser.py
│  ├─ rolling_scheduler.py
│  ├─ question3_solver.py
│  ├─ question4_solver.py
│  ├─ result_writer.py
│  ├─ visualize.py
│  └─ __init__.py
│
├─ tests/
│  ├─ conftest.py
│  ├─ test_time_index.py
│  ├─ test_causality.py
│  ├─ test_settlement.py
│  └─ test_result_writer.py
│
├─ output/
│  ├─ results/               # result1.xlsx ~ result4-3.xlsx
│  ├─ figures/               # 阶段24正文图片
│  ├─ tables/                # 检查报告、回测、实验CSV
│  └─ logs/                  # 服务器运行日志
│
├─ .gitignore
├─ evaluate.py
├─ experiments.py
├─ README.md
├─ requirements.txt
├─ run.py
└─ train.py
```

---

## 2. 环境要求

建议 Linux 服务器使用：

- Python 3.10+
- Gurobi 11+，并已配置可用许可证
- 足够的内存和运行时间

Python依赖见：

```bash
requirements.txt
```

### 创建虚拟环境

```bash
cd C题_服务器工程

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Gurobi许可证

安装 `gurobipy` 只代表Python可以导入Gurobi，不代表许可证可用。

运行：

```bash
python scripts/check_env.py --require-gurobi
```

若输出：

```text
Gurobi license: OK
```

才说明服务器可以正式求解。

如果服务器使用学术许可证、WLS或Token Server，请先按服务器实际环境完成Gurobi授权。

---

## 3. 数据放置

默认附件放在：

```text
data/
├─ 附件1.xlsx
├─ 附件2.xlsx
├─ 附件3.xlsx
└─ 附件4.xlsx
```

默认配置文件：

```text
configs/default.json
```

如果数据目录改变，只修改：

```json
{
  "paths": {
    "data_dir": "data"
  }
}
```

不要修改 `time_index.py` 去适配路径。

---

## 4. 最重要的时间规则

全工程唯一物理索引：

```text
k = 0,...,143
```

其中：

```text
k=0   -> 0:00-0:10   -> source 0:10
k=36  -> 6:00-6:10   -> source 6:10
k=60  -> 10:00-10:10 -> source 10:10
k=143 -> 23:50-24:00 -> source 0:00+1
```

附件1、2、4中的时间标签是**区间右端点**。

结果模板只使用：

```text
model k -> time_map.template_slot -> Excel业务槽位
```

严禁根据Excel模板显示字符串反向决定模型 `k`。

---

## 5. 因果实时运行规则

当前代码已经修复“提前知道当前10分钟完整实际负荷/PV”的问题。

在第 `k` 个物理区间开始时：

```text
tau_k
```

储能决策只能使用：

```text
actual j < k
当前真实SOC E[k]
历史预测误差分布
```

不能使用：

```text
actual load[k]
actual PV[k]
```

完整的 `actual[k]` 只有在区间结束后才进入信息集。

因此：

```text
6:00 决策 k=36
```

只能看到：

```text
k=0,...,35
```

不能提前读取附件2中右端点为 `6:10` 的实际值。

---

## 6. 第一次运行：先做检查

推荐先执行：

```bash
python run.py --stage check
```

或服务器统一入口：

```bash
bash scripts/run_server.sh check
```

检查内容包括：

- 附件1~4是否存在；
- 日期是否连续；
- 缺失值；
- 144个物理时间区间；
- `k=0/36/60/143`关键映射；
- `template_slot`顺序；
- 单元测试。

数据检查报告输出到：

```text
output/tables/data_check_report.csv
```

---

## 7. 分问题运行

### 问题1

```bash
python run.py --stage q1
```

服务器：

```bash
bash scripts/run_server.sh q1
```

输出：

```text
output/results/result1.xlsx
models/q1_result.pkl
output/figures/fig1_typical_day_profiles.png
output/figures/fig2_q1_operation.png
```

### 问题2

```bash
bash scripts/run_server.sh q2
```

输出：

```text
output/results/result2.xlsx
models/q2_period.pkl
output/figures/fig3_q2_forecast_vs_actual.png
output/figures/fig4_emergency_distribution.png
```

### 问题3

```bash
bash scripts/run_server.sh q3
```

输出：

```text
output/results/result3.xlsx
models/q3_period.pkl
output/figures/fig5_q3_pv_update_progression.png
```

### 问题4-2

```bash
bash scripts/run_server.sh q4-2
```

输出：

```text
output/results/result4-2.xlsx
models/q4_2_period.pkl
```

### 问题4-3

```bash
bash scripts/run_server.sh q4-3
```

输出：

```text
output/results/result4-3.xlsx
models/q4_3_period.pkl
output/figures/fig7_q4_dynamic_price_response.png
```

---

## 8. 一次运行全部问题

服务器推荐：

```bash
bash scripts/run_server.sh all
```

直接Python：

```bash
python run.py --stage all
```

由于Q2/Q3/Q4包含全年144时段滚动求解和场景树，**全量计算可能耗时较长**。

建议第一次先：

```bash
bash scripts/run_server.sh check
bash scripts/run_server.sh q1
```

确认数据、环境和Gurobi都正常以后再运行：

```bash
bash scripts/run_server.sh all
```

---

## 9. 断点重跑 / 缓存复用

求解后的结构化结果会缓存到：

```text
models/*.pkl
```

如果服务器任务中断，但已有某些缓存，可使用：

```bash
bash scripts/run_server.sh all --reuse-cache
```

已有的 `pkl` 会直接复用，避免重复求解。

如果只想重新画图：

```bash
bash scripts/run_server.sh figures
```

它会读取：

```text
models/*.pkl
```

而不重新运行Gurobi。

---

## 10. 后台运行

### nohup

```bash
nohup bash scripts/run_server.sh all \
  > output/logs/nohup_all.log 2>&1 &
```

查看进程：

```bash
ps -ef | grep run.py
```

查看日志：

```bash
tail -f output/logs/nohup_all.log
```

`run_server.sh` 自身也会生成：

```text
output/logs/run_all_YYYYMMDD_HHMMSS.log
```

### tmux

更推荐长时间求解使用：

```bash
tmux new -s c2026
bash scripts/run_server.sh all
```

退出但不终止：

```text
Ctrl+B
D
```

重新进入：

```bash
tmux attach -t c2026
```

---

## 11. 预测回测

`train.py` 不训练神经网络，而是做Q2因果日前预测回测。

运行：

```bash
python train.py
```

输出：

```text
output/tables/q2_forecast_backtest_daily.csv
output/tables/q2_forecast_backtest_summary.csv
```

预测每一天 `d` 时只允许使用：

```text
date < d
```

的数据。

---

## 12. 结果汇总

运行：

```bash
python evaluate.py
```

程序会读取：

```text
models/*.pkl
```

汇总：

- 正式日期数量；
- 总成本；
- 日均成本；
- 紧急购电费用；
- 年末SOC。

输出：

```text
output/tables/model_cost_summary.csv
```

---

## 13. 问题3消融实验

先确保已经有：

```text
models/q3_period.pkl
```

然后：

```bash
python experiments.py q3-ablation --date 2025-03-20
```

比较：

```text
00_only
00_06
00_06_12
00_06_12_18
```

输出：

```text
output/tables/q3_ablation_20250320.csv
output/figures/fig6_strategy_cost_comparison.png
```

四种策略使用同一个该日真实初始SOC进行比较。

---

## 14. 敏感性分析图

准备CSV，例如：

```csv
lambda,total_cost_yuan
0.0,100000
0.1,101200
0.2,103500
```

运行：

```bash
python experiments.py sensitivity-plot \
  --csv output/tables/sensitivity.csv \
  --x-col lambda \
  --y-col total_cost_yuan \
  --xlabel "Risk weight" \
  --ylabel "Total cost (CNY)"
```

输出：

```text
output/figures/fig8_sensitivity_analysis.png
```

---

## 15. 阶段24正文重点图

`src/visualize.py` 包含：

```text
Figure 1  Typical day: load, PV, price
Figure 2  Q1 purchase/charge/discharge/battery energy
Figure 3  Q2 forecast vs actual
Figure 4  Emergency purchase time distribution
Figure 5  Q3 PV forecast updates at 0/6/12/18
Figure 6  Cost comparison among update strategies
Figure 7  Q4 storage response under dynamic price
Figure 8  Sensitivity analysis
```

统一规范：

- `matplotlib`
- 每张图单独绘制
- 英文图题和坐标轴
- 功率：kW
- 区间电量：kWh per 10-min interval
- 储电量：kWh
- 电价：CNY/kWh
- 成本：CNY

---

## 16. 结果Excel

正式结果保存到：

```text
output/results/
```

包括：

```text
result1.xlsx
result2.xlsx
result3.xlsx
result4-2.xlsx
result4-3.xlsx
```

`result_writer.py` 在写出以后会再次读取Excel检查：

- Sheet名称；
- 正式日期范围；
- 每天144个槽位；
- `k=0`没有漏写；
- 最后槽位是 `k=143`，不是第二天 `k=144`；
- 全天购电量等于 `sum(k=0...143)`；
- SOC为0:00和24:00；
- 紧急购电连续物理区间自动合并；
- 论文10:00-10:10固定来自 `k=60`。

---

## 17. 单元测试

运行：

```bash
pytest -q tests
```

目前覆盖：

- 时间索引；
- 实时因果信息边界；
- Q3结算；
- 紧急购电物理时间合并；
- 论文指定模型索引。

`run_server.sh` 在正式运行前会自动执行测试。

---

## 18. 常用命令速查

```bash
# 环境/数据检查
bash scripts/run_server.sh check

# Q1
bash scripts/run_server.sh q1

# Q2
bash scripts/run_server.sh q2

# Q3
bash scripts/run_server.sh q3

# Q4-2
bash scripts/run_server.sh q4-2

# Q4-3
bash scripts/run_server.sh q4-3

# 全部问题
bash scripts/run_server.sh all

# 复用已有缓存
bash scripts/run_server.sh all --reuse-cache

# 只重画图
bash scripts/run_server.sh figures

# 预测回测
python train.py

# 结果汇总
python evaluate.py

# Q3消融
python experiments.py q3-ablation --date 2025-03-20

# 单元测试
pytest -q tests
```

---

## 19. 服务器运行前最终检查

正式跑全年以前确认：

```text
[ ] data/附件1.xlsx ~ 附件4.xlsx 都存在
[ ] pip install -r requirements.txt 成功
[ ] python scripts/check_env.py --require-gurobi 通过
[ ] pytest -q tests 通过
[ ] python run.py --stage check 通过
[ ] Gurobi许可证有效
[ ] output/和models/有写权限
```

之后再执行：

```bash
bash scripts/run_server.sh all
```
