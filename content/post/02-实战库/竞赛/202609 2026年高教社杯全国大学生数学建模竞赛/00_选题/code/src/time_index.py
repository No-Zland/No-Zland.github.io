# -*- coding: utf-8 -*-
"""
time_index.py
全题唯一时间索引模块。

核心原则：
    k -> [tau_k, tau_{k+1}) -> source_right_endpoint_label=tau_{k+1}

附件1/2/4的 0:10, 0:20, ..., 0:00+1
统一解释为10分钟物理区间的右端点标签。

注意：
- paper_label 表示真实物理区间；
- template_display_label 仅表示当前已知结果模板的显示槽位文字；
- template_display_label 永远不能反向决定模型 k。
"""

from __future__ import annotations

from datetime import time, datetime
from numbers import Real
from typing import Any

import pandas as pd

from config import DEFAULT_CONFIG, ProjectConfig


def _clock_label_from_minutes(total_minutes: int, plus_one_style: bool = False) -> str:
    """
    将从当天0:00起累计分钟数转换为显示标签。

    total_minutes:
        0~1439 -> 当天时刻
        1440及以上 -> 次日时刻，plus_one_style=True 时输出 0:00+1 形式
    """
    day_offset, minute_in_day = divmod(int(total_minutes), 24 * 60)
    hour, minute = divmod(minute_in_day, 60)

    if plus_one_style and day_offset > 0:
        return f"{hour}:{minute:02d}+{day_offset}"

    if day_offset == 0:
        return f"{hour}:{minute:02d}"

    # 物理区间端点用于 paper_label 时，1440 分钟写成 24:00 更直观。
    if total_minutes == 24 * 60:
        return "24:00"

    return f"{24 * day_offset + hour}:{minute:02d}"


def _template_clock_label(total_minutes: int) -> str:
    """结果模板显示时刻：跨日后使用 0:00+1、0:10+1 形式。"""
    day_offset, minute_in_day = divmod(int(total_minutes), 24 * 60)
    hour, minute = divmod(minute_in_day, 60)
    if day_offset == 0:
        return f"{hour}:{minute:02d}"
    return f"{hour}:{minute:02d}+{day_offset}"


def build_time_map(config: ProjectConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    """
    建立全题唯一144行 time_map。

    至少包含：
        k
        interval_start
        interval_end
        source_right_endpoint_label
        paper_label
        template_slot
        template_display_label

    同时附加 start_minute/end_minute，便于后续程序计算。
    """
    if config.dt_minutes != 10:
        raise ValueError("当前赛题固定采用10分钟时间步，不允许在time_map中静默改变。")
    if config.intervals_per_day != 144:
        raise ValueError("当前赛题每天必须恰好144个10分钟物理区间。")

    rows = []
    for k in range(config.intervals_per_day):
        start_minute = k * config.dt_minutes
        end_minute = (k + 1) * config.dt_minutes

        interval_start = _clock_label_from_minutes(start_minute)
        interval_end = _clock_label_from_minutes(end_minute)

        source_label = (
            "0:00+1"
            if end_minute == 24 * 60
            else _clock_label_from_minutes(end_minute)
        )

        # 论文/模型物理区间标签
        paper_label = f"{interval_start}-{interval_end}"

        # 当前已知结果模板业务槽位显示文字与模型物理区间相差10 min。
        # 这里只保留显示映射，绝不使用该文字反推模型 k。
        template_start = start_minute + config.dt_minutes
        template_end = end_minute + config.dt_minutes
        template_display_label = (
            f"{_template_clock_label(template_start)}-"
            f"{_template_clock_label(template_end)}"
        )

        rows.append(
            {
                "k": k,
                "start_minute": start_minute,
                "end_minute": end_minute,
                "interval_start": interval_start,
                "interval_end": interval_end,
                "source_right_endpoint_label": source_label,
                "paper_label": paper_label,
                "template_slot": k,
                "template_display_label": template_display_label,
            }
        )

    time_map = pd.DataFrame(rows)

    validate_time_map(time_map, config)
    return time_map


def validate_time_map(
    time_map: pd.DataFrame,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> None:
    """对唯一时间映射执行强制单元测试。"""
    if len(time_map) != config.intervals_per_day:
        raise AssertionError(
            f"time_map必须为{config.intervals_per_day}行，实际{len(time_map)}行。"
        )

    if list(time_map["k"]) != list(range(config.intervals_per_day)):
        raise AssertionError("time_map.k 必须严格为0~143且顺序唯一。")

    if time_map["template_slot"].tolist() != time_map["k"].tolist():
        raise AssertionError("必须满足 template_slot[k] = k。")

    expected = {
        0: ("0:00", "0:10", "0:10"),
        36: ("6:00", "6:10", "6:10"),
        60: ("10:00", "10:10", "10:10"),
        143: ("23:50", "24:00", "0:00+1"),
    }

    for k, (start, end, source) in expected.items():
        row = time_map.loc[time_map["k"] == k].iloc[0]
        assert row["interval_start"] == start, (
            f"k={k} interval_start错误：{row['interval_start']} != {start}"
        )
        assert row["interval_end"] == end, (
            f"k={k} interval_end错误：{row['interval_end']} != {end}"
        )
        assert row["source_right_endpoint_label"] == source, (
            f"k={k} source错误："
            f"{row['source_right_endpoint_label']} != {source}"
        )


def canonical_source_label(value: Any) -> str:
    """
    将 pandas 从Excel读出的时间表头/时间单元格统一成：
        0:10, 6:00, 10:00, ..., 0:00+1

    支持：
    - Excel时间小数（如 10min = 0.00694444）
    - datetime.time / Timestamp / datetime
    - '0:10' / '00:10:00'
    - 特殊末端字符串 '0:00+1'
    """
    if pd.isna(value):
        raise ValueError("发现空时间标签。")

    if isinstance(value, str):
        s = value.strip()
        if not s:
            raise ValueError("发现空字符串时间标签。")

        # 次日特殊标签
        normalized = s.replace("＋", "+")
        if normalized in {"0:00+1", "00:00+1", "0:00:00+1", "00:00:00+1"}:
            return "0:00+1"

        # 纯时刻字符串
        parts = normalized.split(":")
        if len(parts) >= 2 and parts[0].isdigit():
            hour = int(parts[0])
            minute_text = "".join(ch for ch in parts[1] if ch.isdigit())
            if minute_text:
                minute = int(minute_text[:2])
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return f"{hour}:{minute:02d}"

        # pandas解析兜底
        try:
            parsed = pd.to_datetime(s, errors="raise")
            return f"{parsed.hour}:{parsed.minute:02d}"
        except Exception as exc:
            raise ValueError(f"无法识别时间标签：{value!r}") from exc

    if isinstance(value, time):
        return f"{value.hour}:{value.minute:02d}"

    if isinstance(value, (pd.Timestamp, datetime)):
        return f"{value.hour}:{value.minute:02d}"

    if isinstance(value, Real):
        # Excel时间为一天的小数。使用四舍五入规避浮点误差。
        minute = int(round(float(value) * 24 * 60))
        minute %= 24 * 60
        hour, minute_in_hour = divmod(minute, 60)
        return f"{hour}:{minute_in_hour:02d}"

    raise TypeError(f"不支持的时间标签类型：{type(value)!r}, value={value!r}")


def expected_source_labels(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> list[str]:
    """返回144个附件右端点标签的标准顺序。"""
    return build_time_map(config)["source_right_endpoint_label"].tolist()


TIME_MAP = build_time_map(DEFAULT_CONFIG)
