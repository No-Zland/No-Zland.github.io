# -*- coding: utf-8 -*-
"""
forecast_parser.py
问题3附件3解析与“整点预测 -> 10分钟物理区间电量”转换。

严格沿用前文：
- Attachment3Data.raw 保留原始宽表，不修改；
- Attachment3Data.release_index 提供每条原始记录的 issue_datetime；
- 物理时间仍由 time_index.py 统一管理；
- 不根据结果模板文字推断模型k。

附件3规则
---------
[FP-01]
    target_datetime = issue_datetime + lead_hour

[FP-02]
    F0 = 当前决策时刻已经观测到的光伏功率

[FP-03]
    对相邻整点锚点线性插值：
        P(t) = (1-a)F_h + a F_{h+1}

[FP-04]
    每个10分钟物理区间用梯形积分：
        G_m = (P_m + P_{m+1})/2 * (1/6)  kWh

重要：
- F0必须由调用者传入，解析器绝不读取未来实际光伏；
- 预报1小时~预报24小时均先转成绝对target_datetime；
- 2025-12-31 18:00 + 24h -> 2026-01-01 18:00，不能截断。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from config import DEFAULT_CONFIG, ProjectConfig
from data_loader import Attachment3Data


@dataclass
class ParsedForecastVersion:
    """一个附件3发布版本的完整24小时10分钟化结果。"""

    issue_datetime: pd.Timestamp
    issue_date: pd.Timestamp
    issue_hour: int

    # 25个小时锚点：F0 + F1..F24
    hourly_anchors: pd.DataFrame

    # 145个10分钟边界功率
    boundary_power_kw: pd.DataFrame

    # 144个10分钟物理区间
    interval_forecast: pd.DataFrame

    @property
    def forecast_kwh(self) -> pd.Series:
        series = self.interval_forecast["forecast_kwh"].copy()
        series.index = range(len(series))
        series.name = "forecast_kwh"
        return series


def _normalize_issue_datetime(value) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.second != 0 or ts.microsecond != 0:
        raise ValueError("issue_datetime必须对齐到整点发布时刻。")
    if ts.minute != 0:
        raise ValueError("附件3发布时间必须为整点。")
    if ts.hour not in {0, 6, 12, 18}:
        raise ValueError("附件3发布时间只能为0/6/12/18点。")
    return ts


def _find_release_row(
    attachment3: Attachment3Data,
    issue_datetime: pd.Timestamp,
) -> int:
    """
    通过release_index中的绝对issue_datetime定位原始行。
    不按“每4行一天”硬编码。
    """
    rel = attachment3.release_index

    matches = rel.loc[
        pd.to_datetime(rel["issue_datetime"]) == issue_datetime
    ]

    if len(matches) != 1:
        raise KeyError(
            f"附件3中issue_datetime={issue_datetime}应且只能匹配1行，"
            f"实际匹配{len(matches)}行。"
        )

    return int(matches.iloc[0]["raw_row_position"])


def parse_forecast_version(
    attachment3: Attachment3Data,
    issue_datetime,
    *,
    current_observed_pv_kw: float,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> ParsedForecastVersion:
    """
    解析附件3某一发布版本并转换成未来24小时144个10分钟区间电量。

    参数
    ----
    attachment3:
        data_loader.load_attachment3()结果。
    issue_datetime:
        0/6/12/18点的绝对发布时间。
    current_observed_pv_kw:
        [FP-02] 发布时刻已经观测到的当前光伏功率F0。
        必须由外部因果运行层传入，本函数不读取附件2未来值。
    """
    issue = _normalize_issue_datetime(issue_datetime)

    if pd.isna(current_observed_pv_kw):
        raise ValueError("current_observed_pv_kw不能缺失。")
    if float(current_observed_pv_kw) < -1e-12:
        raise ValueError("当前观测光伏功率不能为负。")

    raw_position = _find_release_row(
        attachment3,
        issue,
    )
    row = attachment3.raw.iloc[raw_position]

    anchor_rows = [
        {
            "lead_hour": 0,
            "target_datetime": issue,
            "forecast_kw": max(
                0.0,
                float(current_observed_pv_kw),
            ),
            "source": "current_observation_F0",
        }
    ]

    # [FP-01] 显式构造绝对目标时间
    for h in range(1, config.forecast_horizons + 1):
        column = f"预报{h}小时"
        if column not in attachment3.raw.columns:
            raise ValueError(f"附件3缺少字段{column}。")

        value = pd.to_numeric(
            pd.Series([row[column]]),
            errors="raise",
        ).iloc[0]

        if pd.isna(value):
            raise ValueError(
                f"{issue}发布版本的{column}存在缺失值。"
            )

        value = float(value)
        if value < -1e-12:
            raise ValueError(
                f"{issue}发布版本的{column}出现负光伏预测。"
            )

        target_datetime = issue + pd.Timedelta(hours=h)

        anchor_rows.append(
            {
                "lead_hour": h,
                "target_datetime": target_datetime,
                "forecast_kw": max(0.0, value),
                "source": column,
            }
        )

    anchors = pd.DataFrame(anchor_rows)

    expected_targets = pd.date_range(
        issue,
        issue + pd.Timedelta(hours=24),
        freq="1h",
    )
    if not pd.DatetimeIndex(
        anchors["target_datetime"]
    ).equals(expected_targets):
        raise AssertionError(
            "附件3 target_datetime 映射错误。"
        )

    # ------------------------------------------------------------------
    # [FP-03] 25个整点锚点 -> 145个10分钟边界功率
    # ------------------------------------------------------------------
    boundary_times = pd.date_range(
        issue,
        issue + pd.Timedelta(hours=24),
        freq="10min",
    )

    anchor_ns = pd.DatetimeIndex(
        anchors["target_datetime"]
    ).asi8.astype(float)
    boundary_ns = boundary_times.asi8.astype(float)

    anchor_power = anchors["forecast_kw"].to_numpy(
        dtype=float
    )

    interpolated = np.interp(
        boundary_ns,
        anchor_ns,
        anchor_power,
    )

    boundary_power = pd.DataFrame(
        {
            "boundary_datetime": boundary_times,
            "forecast_kw": interpolated,
        }
    )

    # ------------------------------------------------------------------
    # [FP-04] 145边界功率 -> 144物理区间梯形积分
    # ------------------------------------------------------------------
    interval_rows = []
    dt_hours = config.dt_minutes / 60.0

    for m in range(config.intervals_per_day):
        start_dt = boundary_times[m]
        end_dt = boundary_times[m + 1]
        p_start = float(interpolated[m])
        p_end = float(interpolated[m + 1])
        p_avg = 0.5 * (p_start + p_end)
        energy = p_avg * dt_hours

        interval_rows.append(
            {
                "m": m,
                "interval_start_datetime": start_dt,
                "interval_end_datetime": end_dt,
                "forecast_kw_start": p_start,
                "forecast_kw_end": p_end,
                "forecast_kw_avg": p_avg,
                "forecast_kwh": energy,
            }
        )

    intervals = pd.DataFrame(interval_rows)

    if len(intervals) != config.intervals_per_day:
        raise AssertionError(
            "附件3每个发布版本必须转换成144个10分钟物理区间。"
        )

    return ParsedForecastVersion(
        issue_datetime=issue,
        issue_date=issue.normalize(),
        issue_hour=int(issue.hour),
        hourly_anchors=anchors,
        boundary_power_kw=boundary_power,
        interval_forecast=intervals,
    )


def extract_current_day_model_kwh(
    parsed: ParsedForecastVersion,
    model_date,
    *,
    start_k: int,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.Series:
    """
    从一个24小时发布版本中抽取“当前自然日尚未执行区间”的光伏预测。

    输出index严格为：
        start_k,...,143

    定位依据是绝对物理interval_start_datetime，
    不是附件3列号或Excel时间字符串。
    """
    d = pd.Timestamp(model_date).normalize()

    if not (0 <= start_k < config.intervals_per_day):
        raise ValueError("start_k必须位于0~143。")

    target_start = d + pd.Timedelta(
        minutes=start_k * config.dt_minutes
    )
    target_end = d + pd.Timedelta(days=1)

    frame = parsed.interval_forecast

    selected = frame.loc[
        (frame["interval_start_datetime"] >= target_start)
        & (frame["interval_end_datetime"] <= target_end)
    ].copy()

    expected_len = config.intervals_per_day - start_k
    if len(selected) != expected_len:
        raise ValueError(
            f"当前发布版本无法完整覆盖当天k={start_k}~143。"
            f"实际{len(selected)}个区间，期望{expected_len}。"
        )

    result = pd.Series(
        selected["forecast_kwh"].to_numpy(dtype=float),
        index=list(
            range(start_k, config.intervals_per_day)
        ),
        name="pv_forecast_kwh",
        dtype=float,
    )

    return result


def extract_preview_after_midnight(
    parsed: ParsedForecastVersion,
    model_date,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """
    提取当前发布版本中跨过当天24:00之后的预览部分。

    该部分只用于MPC评价当前日末SOC的未来价值，
    不能写成次日正式购电计划。
    """
    d = pd.Timestamp(model_date).normalize()
    midnight_next = d + pd.Timedelta(days=1)

    frame = parsed.interval_forecast.copy()

    preview = frame.loc[
        frame["interval_start_datetime"] >= midnight_next
    ].copy()

    preview.reset_index(drop=True, inplace=True)
    return preview
