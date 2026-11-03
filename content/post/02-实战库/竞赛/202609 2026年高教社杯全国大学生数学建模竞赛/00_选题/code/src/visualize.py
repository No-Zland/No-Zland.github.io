# -*- coding: utf-8 -*-
"""
visualize.py
阶段24：可视化模块

设计目标
--------
1. 严格复用已经确定的变量命名、时间索引和单位；
2. 图题、坐标轴和图例统一使用英文，避免中文字体依赖；
3. 每张图单独成图，不使用seaborn，不使用subplot；
4. 所有时间轴均基于model k=0,...,143，不允许用Excel表头字符串反推；
5. 默认输出到 output/figures 目录；
6. 量纲明确：负荷/光伏可显示为kW，购电/充放电可显示为kWh per interval，
   电价为CNY/kWh，储电量为kWh。

推荐正文重点图
--------------
Figure 1: Typical day profiles (load, PV, price)
Figure 2: Q1 operation (purchase, charge, discharge, energy)
Figure 3: Q2 forecast vs actual
Figure 4: Emergency purchase time distribution
Figure 5: Q3 PV forecast updates approaching actual PV
Figure 6: Total cost comparison among update strategies
Figure 7: Q4 storage response under dynamic price
Figure 8: Sensitivity analysis
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import DEFAULT_CONFIG, ProjectConfig
from time_index import build_time_map, validate_time_map


# ============================================================================
# 路径与公共工具
# ============================================================================


@dataclass
class VisualizationPaths:
    project_root: Path
    output_root: Path
    figure_root: Path
    table_root: Path
    result_root: Path
    log_root: Path


def ensure_project_output_dirs(
    project_root: str | Path = ".",
) -> VisualizationPaths:
    """
    创建并返回标准输出目录。

    目录结构：
        project_root/
            output/
                figures/
                tables/
                results/
                logs/
    """
    project_root = Path(project_root)
    output_root = project_root / "output"
    figure_root = output_root / "figures"
    table_root = output_root / "tables"
    result_root = output_root / "results"
    log_root = output_root / "logs"

    for p in [
        output_root,
        figure_root,
        table_root,
        result_root,
        log_root,
    ]:
        p.mkdir(parents=True, exist_ok=True)

    return VisualizationPaths(
        project_root=project_root,
        output_root=output_root,
        figure_root=figure_root,
        table_root=table_root,
        result_root=result_root,
        log_root=log_root,
    )


def _ordered_time_map(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    tm = build_time_map(config)
    validate_time_map(tm, config)
    tm = tm.sort_values("k").reset_index(drop=True)
    return tm


def _midpoint_hours(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> np.ndarray:
    """
    144个物理10分钟区间的中点小时坐标：
        x_k = (k + 0.5) * 10 / 60
    """
    return (
        np.arange(config.intervals_per_day, dtype=float) + 0.5
    ) * (config.dt_minutes / 60.0)


def _boundary_hours(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> np.ndarray:
    """
    145个状态边界的小时坐标：
        x_j = j * 10 / 60
    """
    return np.arange(
        config.state_nodes_per_day, dtype=float
    ) * (config.dt_minutes / 60.0)


def _series_144(
    series: pd.Series,
    *,
    name: str,
    config: ProjectConfig,
) -> pd.Series:
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name}必须为pandas.Series。")
    expected = list(range(config.intervals_per_day))
    if list(series.index) != expected:
        raise ValueError(
            f"{name}.index必须严格为model k=0~143。"
        )
    values = pd.to_numeric(series, errors="raise").astype(float)
    if values.isna().any():
        raise ValueError(f"{name}存在缺失值。")
    return values


def _series_145(
    series: pd.Series,
    *,
    name: str,
    config: ProjectConfig,
) -> pd.Series:
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name}必须为pandas.Series。")
    expected = list(range(config.state_nodes_per_day))
    if list(series.index) != expected:
        raise ValueError(
            f"{name}.index必须严格为state j=0~144。"
        )
    values = pd.to_numeric(series, errors="raise").astype(float)
    if values.isna().any():
        raise ValueError(f"{name}存在缺失值。")
    return values


def interval_kwh_to_kw(
    series_kwh: pd.Series,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.Series:
    """
    10分钟区间电量(kWh) -> 区间平均功率(kW)
    """
    s = _series_144(
        series_kwh,
        name="series_kwh",
        config=config,
    )
    return s / (config.dt_minutes / 60.0)


def get_actual_day_load_kwh(
    attachment2,
    date,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.Series:
    d = pd.Timestamp(date).normalize()
    s = (
        attachment2.load_kw.loc[d]
        .astype(float)
        .copy()
        * (config.dt_minutes / 60.0)
    )
    s.index = list(range(config.intervals_per_day))
    return _series_144(s, name="actual_load_kwh", config=config)


def get_actual_day_pv_kwh(
    attachment2,
    date,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.Series:
    d = pd.Timestamp(date).normalize()
    s = (
        attachment2.pv_kw.loc[d]
        .astype(float)
        .copy()
        * (config.dt_minutes / 60.0)
    )
    s.index = list(range(config.intervals_per_day))
    return _series_144(s, name="actual_pv_kwh", config=config)


def get_actual_day_price(
    attachment4,
    date,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.Series:
    d = pd.Timestamp(date).normalize()
    s = attachment4.price.loc[d].astype(float).copy()
    s.index = list(range(config.intervals_per_day))
    return _series_144(s, name="actual_price", config=config)


def _save_figure(
    fig,
    output_path: str | Path | None,
) -> Optional[Path]:
    if output_path is None:
        return None
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )
    return output_path


# ============================================================================
# Figure 1：典型日负荷-光伏-电价
# ============================================================================


def plot_figure1_typical_day_profiles(
    *,
    date,
    load_kwh: pd.Series,
    pv_kwh: pd.Series,
    price_yuan_per_kwh: pd.Series,
    output_path: str | Path | None = None,
    config: ProjectConfig = DEFAULT_CONFIG,
):
    """
    Figure 1
    Typical day:
        load, PV, and electricity price.

    负荷/光伏用区间平均功率(kW)；
    电价用CNY/kWh，采用右轴。
    """
    d = pd.Timestamp(date).normalize()
    load_kwh = _series_144(load_kwh, name="load_kwh", config=config)
    pv_kwh = _series_144(pv_kwh, name="pv_kwh", config=config)
    price = _series_144(
        price_yuan_per_kwh,
        name="price_yuan_per_kwh",
        config=config,
    )

    x = _midpoint_hours(config)
    load_kw = interval_kwh_to_kw(load_kwh, config=config)
    pv_kw = interval_kwh_to_kw(pv_kwh, config=config)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(x, load_kw.to_numpy(), label="Load power")
    ax1.plot(x, pv_kw.to_numpy(), label="PV power")
    ax1.set_xlabel("Time of day (hour)")
    ax1.set_ylabel("Power (kW)")
    ax1.set_title(
        f"Figure 1. Typical Day Profiles - {d.date()}"
    )
    ax1.set_xlim(0, 24)
    ax1.grid(True, alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(
        x,
        price.to_numpy(),
        label="Electricity price",
    )
    ax2.set_ylabel("Price (CNY/kWh)")

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="upper right",
    )

    fig.tight_layout()
    _save_figure(fig, output_path)
    return fig, ax1, ax2


# ============================================================================
# Figure 2：问题1购电-充放电-SOC
# ============================================================================


def plot_figure2_q1_operation(
    result1,
    *,
    output_path: str | Path | None = None,
    config: ProjectConfig = DEFAULT_CONFIG,
):
    """
    Figure 2
    Q1 operation:
        purchase, charge, discharge, and battery energy.
    """
    purchase = _series_144(
        result1.plan_purchase_kwh,
        name="result1.plan_purchase_kwh",
        config=config,
    )
    charge = _series_144(
        result1.charge_kwh,
        name="result1.charge_kwh",
        config=config,
    )
    discharge = _series_144(
        result1.discharge_kwh,
        name="result1.discharge_kwh",
        config=config,
    )
    energy = _series_145(
        result1.energy_kwh,
        name="result1.energy_kwh",
        config=config,
    )

    x = _midpoint_hours(config)
    x_state = _boundary_hours(config)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(x, purchase.to_numpy(), label="Grid purchase")
    ax1.plot(x, charge.to_numpy(), label="Charge")
    ax1.plot(x, discharge.to_numpy(), label="Discharge")
    ax1.set_xlabel("Time of day (hour)")
    ax1.set_ylabel("Energy per 10-min interval (kWh)")
    ax1.set_title("Figure 2. Q1 Purchase-Charge-Discharge Schedule")
    ax1.set_xlim(0, 24)
    ax1.grid(True, alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(x_state, energy.to_numpy(), label="Battery energy")
    ax2.set_ylabel("Battery energy (kWh)")

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="upper right",
    )

    fig.tight_layout()
    _save_figure(fig, output_path)
    return fig, ax1, ax2


# ============================================================================
# Figure 3：问题2预测 vs 实际
# ============================================================================


def plot_figure3_q2_forecast_vs_actual(
    q2_day_result,
    *,
    actual_load_kwh: pd.Series,
    actual_pv_kwh: pd.Series,
    output_path: str | Path | None = None,
    config: ProjectConfig = DEFAULT_CONFIG,
):
    """
    Figure 3
    Q2:
        day-ahead forecast vs actual values.

    同一张图中绘制：
        load forecast / actual
        PV forecast / actual
    单位统一为每10分钟电量(kWh)。
    """
    load_fc = _series_144(
        q2_day_result.load_forecast_kwh,
        name="q2_day_result.load_forecast_kwh",
        config=config,
    )
    pv_fc = _series_144(
        q2_day_result.pv_forecast_kwh,
        name="q2_day_result.pv_forecast_kwh",
        config=config,
    )
    actual_load_kwh = _series_144(
        actual_load_kwh,
        name="actual_load_kwh",
        config=config,
    )
    actual_pv_kwh = _series_144(
        actual_pv_kwh,
        name="actual_pv_kwh",
        config=config,
    )

    x = _midpoint_hours(config)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, load_fc.to_numpy(), label="Load forecast")
    ax.plot(x, actual_load_kwh.to_numpy(), label="Load actual")
    ax.plot(x, pv_fc.to_numpy(), label="PV forecast")
    ax.plot(x, actual_pv_kwh.to_numpy(), label="PV actual")

    ax.set_xlabel("Time of day (hour)")
    ax.set_ylabel("Energy per 10-min interval (kWh)")
    ax.set_title(
        f"Figure 3. Q2 Forecast vs Actual - "
        f"{pd.Timestamp(q2_day_result.date).date()}"
    )
    ax.set_xlim(0, 24)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right")

    fig.tight_layout()
    _save_figure(fig, output_path)
    return fig, ax


# ============================================================================
# Figure 4：紧急购电时间分布
# ============================================================================


def plot_figure4_emergency_distribution(
    period_result,
    *,
    output_path: str | Path | None = None,
    config: ProjectConfig = DEFAULT_CONFIG,
):
    """
    Figure 4
    Emergency purchase time distribution.

    统计所有正式日期(2025-02-01~2025-12-31)在每个model k上的
    紧急购电量总和，展示其日内时段分布。
    """
    if not hasattr(period_result, "formal_results"):
        raise TypeError("period_result必须具有formal_results。")

    total = pd.Series(
        np.zeros(config.intervals_per_day, dtype=float),
        index=list(range(config.intervals_per_day)),
        dtype=float,
    )

    for _, day_result in period_result.formal_results.items():
        base = getattr(day_result, "base_result", day_result)
        s = _series_144(
            base.actual_emergency_kwh,
            name="actual_emergency_kwh",
            config=config,
        )
        total = total + s

    x = _midpoint_hours(config)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, total.to_numpy(), width=(config.dt_minutes / 60.0) * 0.9)
    ax.set_xlabel("Time of day (hour)")
    ax.set_ylabel("Total emergency purchase (kWh)")
    ax.set_title("Figure 4. Emergency Purchase Time Distribution")
    ax.set_xlim(0, 24)
    ax.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    _save_figure(fig, output_path)
    return fig, ax


# ============================================================================
# Figure 5：问题3 0/6/12/18预测逐步逼近实际
# ============================================================================


def _extract_q3_parser_forecast_kw(
    update_record,
    *,
    target_date,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.Series:
    """
    从MPCUpdateRecord.parser_audit重建当前自然日未来10分钟PV预测平均功率(kW)。

    当前question3_solver保存的parser_audit来自附件3整点锚点：
        lead_hour
        target_datetime
        forecast_kw
        source

    因此这里不把整点锚点直接当作10分钟区间值，而是与正式模型保持一致：

    1. 以整点锚点做线性插值；
    2. 对每个10分钟物理区间取两个边界预测功率的平均值；
    3. 只返回该发布时刻以后、仍属于target_date的model k。

    该函数只服务可视化，不改变任何优化结果。
    """
    if not hasattr(update_record, "parser_audit"):
        raise AttributeError("update_record缺少parser_audit。")

    audit = update_record.parser_audit.copy()
    required = {"target_datetime", "forecast_kw"}

    if audit.empty:
        return pd.Series(dtype=float)

    if not required.issubset(audit.columns):
        raise ValueError(
            "parser_audit必须至少包含target_datetime和forecast_kw。"
        )

    audit["target_datetime"] = pd.to_datetime(
        audit["target_datetime"]
    )
    audit["forecast_kw"] = pd.to_numeric(
        audit["forecast_kw"],
        errors="raise",
    ).astype(float)

    audit = audit.sort_values("target_datetime")
    anchor_t = pd.DatetimeIndex(
        audit["target_datetime"]
    )
    anchor_y = audit["forecast_kw"].to_numpy(dtype=float)

    if len(anchor_t) < 2:
        raise ValueError("附件3可视化至少需要两个预测锚点。")

    d = pd.Timestamp(target_date).normalize()
    issue = pd.Timestamp(update_record.issue_datetime)

    start_k = int(
        (
            issue - d
        ).total_seconds()
        // (config.dt_minutes * 60)
    )
    start_k = max(0, min(config.intervals_per_day, start_k))

    anchor_ns = anchor_t.asi8.astype(float)

    result = {}

    for k in range(start_k, config.intervals_per_day):
        t0 = d + pd.Timedelta(
            minutes=k * config.dt_minutes
        )
        t1 = t0 + pd.Timedelta(
            minutes=config.dt_minutes
        )

        # 发布版本必须覆盖该区间两个边界。
        if t0 < anchor_t[0] or t1 > anchor_t[-1]:
            continue

        b = np.array(
            [
                pd.Timestamp(t0).value,
                pd.Timestamp(t1).value,
            ],
            dtype=float,
        )

        p0, p1 = np.interp(
            b,
            anchor_ns,
            anchor_y,
        )

        result[k] = 0.5 * (
            float(p0) + float(p1)
        )

    return pd.Series(
        result,
        dtype=float,
        name="pv_forecast_kw",
    ).sort_index()


def plot_figure5_q3_pv_update_progression(
    q3_day_result,
    *,
    actual_pv_kwh: pd.Series,
    output_path: str | Path | None = None,
    config: ProjectConfig = DEFAULT_CONFIG,
):
    """
    Figure 5
    Q3:
        PV forecasts issued at 0:00, 6:00, 12:00, 18:00
        progressively approach actual PV.

    实际值使用actual_pv_kwh，并转换为kW显示。
    预测曲线从对应更新时间r开始绘制；r之前置为NaN。
    """
    actual_pv_kwh = _series_144(
        actual_pv_kwh,
        name="actual_pv_kwh",
        config=config,
    )
    actual_pv_kw = interval_kwh_to_kw(
        actual_pv_kwh,
        config=config,
    )

    x = _midpoint_hours(config)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, actual_pv_kw.to_numpy(), label="Actual PV")

    update_records = getattr(
        q3_day_result,
        "update_records",
        {},
    )
    if not isinstance(update_records, Mapping):
        raise TypeError("q3_day_result.update_records必须为映射。")

    for r in sorted(update_records):
        record = update_records[r]
        forecast_kw = _extract_q3_parser_forecast_kw(
            record,
            target_date=q3_day_result.date,
            config=config,
        )

        values = np.full(
            config.intervals_per_day,
            np.nan,
            dtype=float,
        )
        for k, v in forecast_kw.items():
            if 0 <= int(k) <= 143:
                values[int(k)] = float(v)

        label = f"Forecast issued at {int(r/6):02d}:00"
        ax.plot(x, values, label=label)

    ax.set_xlabel("Time of day (hour)")
    ax.set_ylabel("PV power (kW)")
    ax.set_title(
        f"Figure 5. Q3 PV Forecast Update Progression - "
        f"{pd.Timestamp(q3_day_result.date).date()}"
    )
    ax.set_xlim(0, 24)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right")

    fig.tight_layout()
    _save_figure(fig, output_path)
    return fig, ax


# ============================================================================
# Figure 6：不同更新策略总成本比较
# ============================================================================


def plot_figure6_strategy_cost_comparison(
    strategy_cost,
    *,
    strategy_col: str = "strategy",
    cost_col: str = "total_cost_yuan",
    output_path: str | Path | None = None,
):
    """
    Figure 6
    Total cost comparison under different update strategies.

    输入可以是：
    1. DataFrame，包含strategy_col和cost_col；
    2. dict[str, float]
    """
    if isinstance(strategy_cost, dict):
        df = pd.DataFrame(
            {
                strategy_col: list(strategy_cost.keys()),
                cost_col: list(strategy_cost.values()),
            }
        )
    else:
        df = pd.DataFrame(strategy_cost).copy()

    if strategy_col not in df.columns or cost_col not in df.columns:
        raise ValueError(
            f"输入必须包含列{strategy_col}和{cost_col}。"
        )

    labels = df[strategy_col].astype(str).tolist()
    values = pd.to_numeric(
        df[cost_col],
        errors="raise",
    ).astype(float)

    x = np.arange(len(df), dtype=float)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x, values.to_numpy())
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Update strategy")
    ax.set_ylabel("Total cost (CNY)")
    ax.set_title(
        "Figure 6. Total Cost Comparison among Update Strategies"
    )
    ax.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    _save_figure(fig, output_path)
    return fig, ax


# ============================================================================
# Figure 7：问题4 动态电价下低价充高价放
# ============================================================================


def plot_figure7_q4_dynamic_price_response(
    q4_day_result,
    *,
    output_path: str | Path | None = None,
    config: ProjectConfig = DEFAULT_CONFIG,
):
    """
    Figure 7
    Q4:
        storage response under dynamic electricity price.

    左轴：
        actual charge / actual discharge (kWh per interval)
    右轴：
        actual real-time electricity price (CNY/kWh)
    """
    base = getattr(q4_day_result, "base_result", q4_day_result)

    charge = _series_144(
        base.actual_charge_kwh,
        name="actual_charge_kwh",
        config=config,
    )
    discharge = _series_144(
        base.actual_discharge_kwh,
        name="actual_discharge_kwh",
        config=config,
    )

    if not hasattr(q4_day_result, "actual_price_yuan_per_kwh"):
        raise AttributeError(
            "q4_day_result必须包含actual_price_yuan_per_kwh。"
        )

    price = _series_144(
        q4_day_result.actual_price_yuan_per_kwh,
        name="actual_price_yuan_per_kwh",
        config=config,
    )

    x = _midpoint_hours(config)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(x, charge.to_numpy(), label="Charge")
    ax1.plot(x, discharge.to_numpy(), label="Discharge")
    ax1.set_xlabel("Time of day (hour)")
    ax1.set_ylabel("Energy per 10-min interval (kWh)")
    ax1.set_title(
        f"Figure 7. Q4 Storage Response under Dynamic Price - "
        f"{pd.Timestamp(q4_day_result.date).date()}"
    )
    ax1.set_xlim(0, 24)
    ax1.grid(True, alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(
        x,
        price.to_numpy(),
        label="Real-time price",
    )
    ax2.set_ylabel("Price (CNY/kWh)")

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="upper right",
    )

    fig.tight_layout()
    _save_figure(fig, output_path)
    return fig, ax1, ax2


# ============================================================================
# Figure 8：敏感性分析
# ============================================================================


def plot_figure8_sensitivity_analysis(
    x_values,
    y_values,
    *,
    xlabel: str,
    ylabel: str,
    title: str = "Figure 8. Sensitivity Analysis",
    output_path: str | Path | None = None,
):
    """
    Figure 8
    Generic one-factor sensitivity analysis.
    """
    x = np.asarray(x_values, dtype=float)
    y = np.asarray(y_values, dtype=float)

    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
        raise ValueError("x_values与y_values必须为等长一维数组。")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, y, marker="o")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    _save_figure(fig, output_path)
    return fig, ax


# ============================================================================
# 批量生成包装器
# ============================================================================


def generate_phase24_figures(
    *,
    project_root: str | Path = ".",
    typical_day_date=None,
    typical_day_load_kwh: Optional[pd.Series] = None,
    typical_day_pv_kwh: Optional[pd.Series] = None,
    typical_day_price_yuan_per_kwh: Optional[pd.Series] = None,
    q1_result=None,
    q2_day_result=None,
    q2_actual_load_kwh: Optional[pd.Series] = None,
    q2_actual_pv_kwh: Optional[pd.Series] = None,
    q2_or_q3_or_q4_period_result=None,
    q3_day_result=None,
    q3_actual_pv_kwh: Optional[pd.Series] = None,
    strategy_cost=None,
    q4_day_result=None,
    sensitivity_x=None,
    sensitivity_y=None,
    sensitivity_xlabel: str = "Parameter",
    sensitivity_ylabel: str = "Response",
    sensitivity_title: str = "Figure 8. Sensitivity Analysis",
    config: ProjectConfig = DEFAULT_CONFIG,
) -> Dict[str, Path]:
    """
    按可用输入批量生成阶段24正文重点图。

    返回：
        {figure_name: saved_path}
    """
    paths = ensure_project_output_dirs(project_root)
    saved: Dict[str, Path] = {}

    if (
        typical_day_date is not None
        and typical_day_load_kwh is not None
        and typical_day_pv_kwh is not None
        and typical_day_price_yuan_per_kwh is not None
    ):
        p = paths.figure_root / "fig1_typical_day_profiles.png"
        plot_figure1_typical_day_profiles(
            date=typical_day_date,
            load_kwh=typical_day_load_kwh,
            pv_kwh=typical_day_pv_kwh,
            price_yuan_per_kwh=typical_day_price_yuan_per_kwh,
            output_path=p,
            config=config,
        )
        saved["figure1"] = p

    if q1_result is not None:
        p = paths.figure_root / "fig2_q1_operation.png"
        plot_figure2_q1_operation(
            q1_result,
            output_path=p,
            config=config,
        )
        saved["figure2"] = p

    if (
        q2_day_result is not None
        and q2_actual_load_kwh is not None
        and q2_actual_pv_kwh is not None
    ):
        p = paths.figure_root / "fig3_q2_forecast_vs_actual.png"
        plot_figure3_q2_forecast_vs_actual(
            q2_day_result,
            actual_load_kwh=q2_actual_load_kwh,
            actual_pv_kwh=q2_actual_pv_kwh,
            output_path=p,
            config=config,
        )
        saved["figure3"] = p

    if q2_or_q3_or_q4_period_result is not None:
        p = paths.figure_root / "fig4_emergency_distribution.png"
        plot_figure4_emergency_distribution(
            q2_or_q3_or_q4_period_result,
            output_path=p,
            config=config,
        )
        saved["figure4"] = p

    if q3_day_result is not None and q3_actual_pv_kwh is not None:
        p = paths.figure_root / "fig5_q3_pv_update_progression.png"
        plot_figure5_q3_pv_update_progression(
            q3_day_result,
            actual_pv_kwh=q3_actual_pv_kwh,
            output_path=p,
            config=config,
        )
        saved["figure5"] = p

    if strategy_cost is not None:
        p = paths.figure_root / "fig6_strategy_cost_comparison.png"
        plot_figure6_strategy_cost_comparison(
            strategy_cost,
            output_path=p,
        )
        saved["figure6"] = p

    if q4_day_result is not None:
        p = paths.figure_root / "fig7_q4_dynamic_price_response.png"
        plot_figure7_q4_dynamic_price_response(
            q4_day_result,
            output_path=p,
            config=config,
        )
        saved["figure7"] = p

    if sensitivity_x is not None and sensitivity_y is not None:
        p = paths.figure_root / "fig8_sensitivity_analysis.png"
        plot_figure8_sensitivity_analysis(
            sensitivity_x,
            sensitivity_y,
            xlabel=sensitivity_xlabel,
            ylabel=sensitivity_ylabel,
            title=sensitivity_title,
            output_path=p,
        )
        saved["figure8"] = p

    return saved
