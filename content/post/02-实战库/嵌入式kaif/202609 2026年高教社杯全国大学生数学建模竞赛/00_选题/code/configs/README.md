# configs

`default.json` 是主运行配置。

主要可调项：

- `paths.data_dir`：附件1~4所在目录；
- `run.start_date/end_date`：全年模拟范围；
- `run.save_from_date`：正式结果开始日期，默认2025-02-01；
- `run.initial_energy_kwh`：2025-01-01 0:00初始储电量；
- `q2`：问题2场景规模、CVaR和随机种子；
- `q3.update_combination`：问题3滚动更新时间，固定模型索引0/36/72/108；
- `result_writer`：结果文件写出参数。
