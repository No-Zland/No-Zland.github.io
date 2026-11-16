# -*- coding: utf-8 -*-
"""
forecast_model.py
问题2日前负荷/光伏预测与严格因果历史残差库。

只实现问题2需要的预测功能，不包含：
- 问题3附件3预测更新；
- 问题4动态电价预测；
- 任何优化模型。

核心信息规则
------------
对目标日期 d 在 0:00 作预测时，只允许使用日期 s<d 的附件2实际数据。
禁止读取 d 当天未来实际负荷/光伏参与：
1. 当天0:00预测；
2. 当天0:00场景生成；
3. 历史残差模型参数计算。

时间接口
--------
附件2已经由 data_loader.py 按唯一 time_map 对齐为：
    index = date
    columns = k=0,...,143

本文件只使用 columns 中的模型k，不解析Excel时间字符串。

主预测方法
----------
负荷：
    优先使用上周同日同物理时段值（lag-7）；
    历史不足7天时使用此前可用日期同物理时段均值。

光伏：
    使用最近7个已实现历史日同物理时段均值。

这与前面已经确定的简单、可解释、严格因果基线保持一致。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from config import DEFAULT_CONFIG, ProjectConfig
from data_loader import Attachment2Data
from time_index import build_time_map, validate_time_map


@dataclass
class AvailableHistory:
    """目标日0:00时真正可用的历史信息。"""

    target_date: pd.Timestamp
    load_kw: pd.DataFrame
    pv_kw: pd.DataFrame

    @property
    def history_days(self) -> int:
        return len(self.load_kw)

    @property
    def last_available_date(self) -> Optional[pd.Timestamp]:
        if self.history_days == 0:
            return None
        return pd.Timestamp(self.load_kw.index.max()).normalize()


@dataclass
class DayAheadForecast:
    """问题2某日0:00生成的144区间日前预测。"""

    target_date: pd.Timestamp

    # 功率，kW
    load_kw: pd.Series
    pv_kw: pd.Series

    # 10 min区间电量，kWh
    load_kwh: pd.Series
    pv_kwh: pd.Series

    history_days: int
    history_end_date: Optional[pd.Timestamp]

    load_method: str
    pv_method: str


@dataclass
class ResidualLibrary:
    """
    严格因果历史残差库。

    每一历史日 s 的残差都来自：
        actual(s) - forecast(s | 仅使用 t<s 的数据)

    因此不存在用全年拟合后残差回填历史的未来泄露。
    """

    target_date: pd.Timestamp

    load_residual_kw: pd.DataFrame
    pv_residual_kw: pd.DataFrame

    load_residual_kwh: pd.DataFrame
    pv_residual_kwh: pd.DataFrame

    @property
    def dates(self) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(self.load_residual_kw.index)

    @property
    def n_days(self) -> int:
        return len(self.load_residual_kw)


def _normalize_date(value) -> pd.Timestamp:
    return pd.Timestamp(value).normalize()


def _validate_attachment2(
    attachment2: Attachment2Data,
    config: ProjectConfig,
) -> None:
    if not isinstance(attachment2, Attachment2Data):
        raise TypeError(
            "attachment2必须是data_loader.load_attachment2()返回的"
            "Attachment2Data。"
        )

    expected_columns = list(range(config.intervals_per_day))

    for name, frame in [
        ("load_kw", attachment2.load_kw),
        ("pv_kw", attachment2.pv_kw),
    ]:
        if list(frame.columns) != expected_columns:
            raise ValueError(
                f"attachment2.{name}列必须严格为模型k=0~143。"
            )

        if not isinstance(frame.index, pd.DatetimeIndex):
            raise TypeError(
                f"attachment2.{name}.index必须为DatetimeIndex。"
            )

        if frame.index.has_duplicates:
            raise ValueError(f"attachment2.{name}存在重复日期。")

        if frame.isna().any().any():
            raise ValueError(f"attachment2.{name}存在缺失值。")


def _validate_series_k(
    series: pd.Series,
    config: ProjectConfig,
    name: str,
) -> pd.Series:
    expected = list(range(config.intervals_per_day))
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name}必须为pandas.Series。")
    if list(series.index) != expected:
        raise ValueError(f"{name}.index必须严格为模型k=0~143。")

    result = pd.to_numeric(series, errors="raise").astype(float)
    if result.isna().any():
        raise ValueError(f"{name}存在缺失值。")
    return result


def build_available_history(
    attachment2: Attachment2Data,
    target_date,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> AvailableHistory:
    """
    构造目标日 d 在0:00真正可用的附件2历史信息。

    强制：
        history.index < target_date

    不允许把target_date当天任何真实值放入历史集。
    """
    _validate_attachment2(attachment2, config)

    d = _normalize_date(target_date)

    load_history = attachment2.load_kw.loc[
        attachment2.load_kw.index < d
    ].copy()
    pv_history = attachment2.pv_kw.loc[
        attachment2.pv_kw.index < d
    ].copy()

    if not load_history.index.equals(pv_history.index):
        raise ValueError("历史负荷与光伏日期索引不一致。")

    if len(load_history) > 0:
        if not (load_history.index < d).all():
            raise AssertionError("历史信息中混入目标日或未来日期。")

    return AvailableHistory(
        target_date=d,
        load_kw=load_history,
        pv_kw=pv_history,
    )


def forecast_load_day_ahead(
    history: AvailableHistory,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.Series:
    """
    生成当天144个物理区间的负荷功率预测(kW)。

    主规则：
    1. 若 d-7 已经存在，使用上周同日同k：
           P^L_hat[d,k] = P^L[d-7,k]
    2. 若历史不足7天，则使用所有可用历史日同k均值；
    3. 若完全没有历史（仅可能出现在1月1日暖启动），返回全0基线。
       实际运行仍由当前信息下的因果紧急购电/储能补救保证可行，
       且1月份不保存正式结果。
    """
    d = history.target_date
    expected_k = list(range(config.intervals_per_day))

    if history.history_days == 0:
        return pd.Series(
            np.zeros(config.intervals_per_day),
            index=expected_k,
            dtype=float,
            name="load_forecast_kw",
        )

    lag7_date = d - pd.Timedelta(days=7)

    if lag7_date in history.load_kw.index:
        result = history.load_kw.loc[lag7_date].astype(float).copy()
    else:
        result = history.load_kw.mean(axis=0).astype(float)

    result.index = expected_k
    result = result.clip(lower=0.0)
    result.name = "load_forecast_kw"
    return result


def forecast_pv_day_ahead(
    history: AvailableHistory,
    *,
    recent_days: int = 7,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.Series:
    """
    生成当天144个物理区间的光伏功率预测(kW)。

    使用最近 min(7, 可用历史天数) 个历史日同k平均。
    完全无历史时返回全0暖启动基线。
    """
    expected_k = list(range(config.intervals_per_day))

    if history.history_days == 0:
        return pd.Series(
            np.zeros(config.intervals_per_day),
            index=expected_k,
            dtype=float,
            name="pv_forecast_kw",
        )

    if recent_days <= 0:
        raise ValueError("recent_days必须为正整数。")

    recent = history.pv_kw.tail(min(recent_days, history.history_days))
    result = recent.mean(axis=0).astype(float)
    result.index = expected_k
    result = result.clip(lower=0.0)
    result.name = "pv_forecast_kw"
    return result


def build_q2_day_ahead_forecast(
    attachment2: Attachment2Data,
    target_date,
    *,
    pv_recent_days: int = 7,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> DayAheadForecast:
    """
    问题2统一日前预测入口。

    对target_date的预测严格只使用 target_date 之前的数据。
    输出144个模型物理区间预测，不读取Excel时间字符串。
    """
    time_map = build_time_map(config)
    validate_time_map(time_map, config)

    history = build_available_history(
        attachment2,
        target_date,
        config=config,
    )

    load_kw = forecast_load_day_ahead(
        history,
        config=config,
    )
    pv_kw = forecast_pv_day_ahead(
        history,
        recent_days=pv_recent_days,
        config=config,
    )

    dt_hours = config.dt_minutes / 60.0
    load_kwh = load_kw * dt_hours
    pv_kwh = pv_kw * dt_hours
    load_kwh.name = "load_forecast_kwh"
    pv_kwh.name = "pv_forecast_kwh"

    if history.last_available_date is not None:
        if not history.last_available_date < history.target_date:
            raise AssertionError("日前预测使用了目标日或未来数据。")

    return DayAheadForecast(
        target_date=history.target_date,
        load_kw=load_kw,
        pv_kw=pv_kw,
        load_kwh=load_kwh,
        pv_kwh=pv_kwh,
        history_days=history.history_days,
        history_end_date=history.last_available_date,
        load_method="lag7_else_expanding_same_slot_mean",
        pv_method=f"recent_{pv_recent_days}_days_same_slot_mean",
    )


def build_causal_residual_library(
    attachment2: Attachment2Data,
    target_date,
    *,
    max_residual_days: Optional[int] = 60,
    pv_recent_days: int = 7,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> ResidualLibrary:
    """
    构造target_date在0:00可用的历史样本外残差库。

    对每个历史日期 s<target_date：
        1. 用 s 之前的数据生成 forecast(s)；
        2. 再用 actual(s)-forecast(s) 形成残差。

    这样每一条残差轨迹都是严格因果的，不存在全年度参数回看。

    参数
    ----
    max_residual_days:
        只保留最近若干历史残差日以控制场景生成规模。
        None 表示保留全部因果残差。
    """
    _validate_attachment2(attachment2, config)
    d = _normalize_date(target_date)

    candidate_dates = pd.DatetimeIndex(
        attachment2.load_kw.index[
            attachment2.load_kw.index < d
        ]
    )

    # 至少需要一个更早历史日才能形成真正的样本外残差；
    # 因此历史第一天不进入残差库。
    if len(candidate_dates) <= 1:
        empty = pd.DataFrame(
            columns=list(range(config.intervals_per_day)),
            dtype=float,
        )
        empty.index = pd.DatetimeIndex([], name="date")
        return ResidualLibrary(
            target_date=d,
            load_residual_kw=empty.copy(),
            pv_residual_kw=empty.copy(),
            load_residual_kwh=empty.copy(),
            pv_residual_kwh=empty.copy(),
        )

    residual_dates = candidate_dates[1:]

    if max_residual_days is not None:
        if max_residual_days <= 0:
            raise ValueError("max_residual_days必须为正整数或None。")
        residual_dates = residual_dates[-max_residual_days:]

    load_rows = []
    pv_rows = []
    kept_dates = []

    for s in residual_dates:
        # 关键：forecast(s)内部只读取 t<s。
        forecast_s = build_q2_day_ahead_forecast(
            attachment2,
            s,
            pv_recent_days=pv_recent_days,
            config=config,
        )

        if forecast_s.history_end_date is not None:
            if not forecast_s.history_end_date < s:
                raise AssertionError(
                    f"构造{s.date()}残差时发生未来信息泄露。"
                )

        actual_load = attachment2.load_kw.loc[s].astype(float)
        actual_pv = attachment2.pv_kw.loc[s].astype(float)

        load_rows.append(
            (actual_load - forecast_s.load_kw).to_numpy(dtype=float)
        )
        pv_rows.append(
            (actual_pv - forecast_s.pv_kw).to_numpy(dtype=float)
        )
        kept_dates.append(s)

    columns = list(range(config.intervals_per_day))
    index = pd.DatetimeIndex(kept_dates, name="date")

    load_residual_kw = pd.DataFrame(
        load_rows,
        index=index,
        columns=columns,
        dtype=float,
    )
    pv_residual_kw = pd.DataFrame(
        pv_rows,
        index=index,
        columns=columns,
        dtype=float,
    )

    dt_hours = config.dt_minutes / 60.0

    load_residual_kwh = load_residual_kw * dt_hours
    pv_residual_kwh = pv_residual_kw * dt_hours

    if len(index) > 0 and not (index < d).all():
        raise AssertionError("残差库混入目标日或未来日期。")

    return ResidualLibrary(
        target_date=d,
        load_residual_kw=load_residual_kw,
        pv_residual_kw=pv_residual_kw,
        load_residual_kwh=load_residual_kwh,
        pv_residual_kwh=pv_residual_kwh,
    )



def validate_observed_prefix(
    observed_load_kwh: pd.Series,
    observed_pv_kwh: pd.Series,
    current_k: int,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> tuple[pd.Series, pd.Series]:
    """
    校验实时因果补救在区间k开始时可读取的真实前缀。

    严格时序：
        当前要决定物理区间
            I_k = [tau_k, tau_{k+1})
        的储能动作时，附件2中第k个区间的完整实际负荷/光伏
        尚未实现。

    因此在tau_k只能使用：
        index = 0,...,k-1

    特别地：
        k=0  -> 真实前缀必须为空；
        k=36 -> 6:00决策时只允许0..35；
        k=72 -> 12:00决策时只允许0..71；
        k=108-> 18:00决策时只允许0..107。

    明确禁止把current_k及其之后的真实值传入当前储能决策。
    当前区间真实值只能在动作决定以后用于事后能量平衡、
    紧急购电、弃光和计划富余结算。
    """
    if not (0 <= current_k < config.intervals_per_day):
        raise ValueError("current_k必须位于0~143。")

    expected_index = list(range(current_k))

    for name, series in [
        ("observed_load_kwh", observed_load_kwh),
        ("observed_pv_kwh", observed_pv_kwh),
    ]:
        if not isinstance(series, pd.Series):
            raise TypeError(f"{name}必须为pandas.Series。")

        if list(series.index) != expected_index:
            raise ValueError(
                f"{name}在决定k={current_k}动作前只能包含已完成区间，"
                f"index必须严格为0~{current_k - 1 if current_k > 0 else '空'}；"
                "禁止包含current_k实际值。"
            )

        if series.isna().any():
            raise ValueError(f"{name}存在缺失值。")

    return (
        observed_load_kwh.astype(float).copy(),
        observed_pv_kwh.astype(float).copy(),
    )
