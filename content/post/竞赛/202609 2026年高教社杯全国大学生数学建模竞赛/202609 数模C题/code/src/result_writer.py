# -*- coding: utf-8 -*-
"""
result_writer.py
C题 result1.xlsx / result2.xlsx / result3.xlsx /
result4-2.xlsx / result4-3.xlsx 统一结果写出器。

重要说明
--------
当前没有官方附件5原始空白xlsx，只掌握题目/模板结构说明，因此本模块
按已知工作表名称和字段结构“重建兼容格式”。

最重要的时间原则：
    模型物理时间：
        k -> [tau_k, tau_{k+1})
    输出模板槽位：
        template_slot[k] = k
    模板显示文字：
        只用于Excel表头展示，绝不能反向推断模型k。

因此即使模板第一个显示槽位是：
    0:10-0:20
写入其中的仍然是：
    model k=0 -> physical 0:00-0:10

同理模板最后一个显示槽位：
    0:00+1-0:10+1
写入的是：
    model k=143 -> physical 23:50-24:00

绝不存在模型k=144，也不会把第二天0:00-0:10错误并入当天。

本模块使用 artifact_tool 写Excel，并在导出后重新读取Excel执行结构校验。
不使用openpyxl，也不从Excel表头文字反向确定模型时间。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

import numpy as np
import pandas as pd

from _excel_backend import Blob, SpreadsheetFile, Workbook

from config import DEFAULT_CONFIG, ProjectConfig
from time_index import build_time_map, validate_time_map


# ============================================================================
# 模板固定结构
# ============================================================================

SHEET_PLAN = "计划购电量"
SHEET_ADJUST = "调整购电量"
SHEET_STORAGE = "充放电量"
SHEET_EMERGENCY = "紧急购电量"

RESULT_SHEETS: Dict[str, tuple[str, ...]] = {
    "result1.xlsx": (
        SHEET_PLAN,
        SHEET_STORAGE,
    ),
    "result2.xlsx": (
        SHEET_PLAN,
        SHEET_STORAGE,
        SHEET_EMERGENCY,
    ),
    "result3.xlsx": (
        SHEET_PLAN,
        SHEET_ADJUST,
        SHEET_STORAGE,
        SHEET_EMERGENCY,
    ),
    "result4-2.xlsx": (
        SHEET_PLAN,
        SHEET_STORAGE,
        SHEET_EMERGENCY,
    ),
    "result4-3.xlsx": (
        SHEET_PLAN,
        SHEET_ADJUST,
        SHEET_STORAGE,
        SHEET_EMERGENCY,
    ),
}

FORMAL_START_DATE = pd.Timestamp("2025-02-01")
FORMAL_END_DATE = pd.Timestamp("2025-12-31")
FORMAL_DATES = pd.date_range(
    FORMAL_START_DATE,
    FORMAL_END_DATE,
    freq="D",
)
FORMAL_DAY_COUNT = len(FORMAL_DATES)  # 334

REPORT_DATES: tuple[pd.Timestamp, ...] = (
    pd.Timestamp("2025-03-20"),
    pd.Timestamp("2025-06-21"),
    pd.Timestamp("2025-09-23"),
    pd.Timestamp("2025-12-21"),
)

# 论文表1必须只按模型k提取，不能搜索模板显示文字。
REPORT_INTERVAL_INDEX: tuple[int, ...] = (
    60,   # 10:00-10:10
    72,   # 12:00-12:10
    84,   # 14:00-14:10
    96,   # 16:00-16:10
    108,  # 18:00-18:10
    120,  # 20:00-20:10
)

FOUR_HOUR_BLOCKS: tuple[tuple[int, int, str], ...] = (
    (0, 24, "0:00-4:00"),
    (24, 48, "4:00-8:00"),
    (48, 72, "8:00-12:00"),
    (72, 96, "12:00-16:00"),
    (96, 120, "16:00-20:00"),
    (120, 144, "20:00-24:00"),
)



def _excel_col_name(index0: int) -> str:
    """0-based列号转Excel列名。"""
    if index0 < 0:
        raise ValueError("index0必须非负。")
    n = index0 + 1
    letters = []
    while n:
        n, rem = divmod(n - 1, 26)
        letters.append(chr(65 + rem))
    return "".join(reversed(letters))


def _range(sheet: Any, start_row0: int, start_col0: int, row_count: int, col_count: int):
    """artifact_tool稳定A1范围适配器，避免依赖get_range_by_indexes实现差异。"""
    if row_count <= 0 or col_count <= 0:
        raise ValueError("row_count/col_count必须为正。")
    start = f"{_excel_col_name(start_col0)}{start_row0 + 1}"
    end = (
        f"{_excel_col_name(start_col0 + col_count - 1)}"
        f"{start_row0 + row_count}"
    )
    return sheet.get_range(f"{start}:{end}")


# ============================================================================
# 公共检查 / 数据访问
# ============================================================================


class ResultWriterError(RuntimeError):
    """结果结构或输出模板不合法。"""


def _normalize_date(value) -> pd.Timestamp:
    return pd.Timestamp(value).normalize()


def _as_python_datetime(ts: pd.Timestamp) -> datetime:
    ts = pd.Timestamp(ts).normalize()
    return datetime(ts.year, ts.month, ts.day)


def _validate_series_144(
    series: pd.Series,
    *,
    name: str,
    config: ProjectConfig,
) -> pd.Series:
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name}必须为pandas.Series。")

    expected = list(range(config.intervals_per_day))

    if list(series.index) != expected:
        raise ResultWriterError(
            f"{name}.index必须严格为模型k=0~143。"
            "禁止通过Excel表头字符串重新定位。"
        )

    values = pd.to_numeric(series, errors="raise").astype(float)

    if values.isna().any():
        raise ResultWriterError(f"{name}存在缺失值。")

    return values


def _validate_energy_145(
    series: pd.Series,
    *,
    name: str,
    config: ProjectConfig,
) -> pd.Series:
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name}必须为pandas.Series。")

    expected = list(range(config.state_nodes_per_day))

    if list(series.index) != expected:
        raise ResultWriterError(
            f"{name}.index必须严格为状态节点j=0~144。"
        )

    values = pd.to_numeric(series, errors="raise").astype(float)

    if values.isna().any():
        raise ResultWriterError(f"{name}存在缺失值。")

    return values


def _get_formal_results(period_result: Any) -> Mapping[pd.Timestamp, Any]:
    if not hasattr(period_result, "formal_results"):
        raise TypeError(
            "多日结果必须提供formal_results属性。"
        )

    raw = period_result.formal_results
    if not isinstance(raw, Mapping):
        raise TypeError("formal_results必须为日期->单日结果映射。")

    normalized = {
        _normalize_date(d): result
        for d, result in raw.items()
    }

    actual_dates = pd.DatetimeIndex(sorted(normalized))
    expected_dates = FORMAL_DATES

    if not actual_dates.equals(expected_dates):
        missing = expected_dates.difference(actual_dates)
        extra = actual_dates.difference(expected_dates)
        raise ResultWriterError(
            "正式结果日期必须恰好为2025-02-01~2025-12-31 "
            f"共{FORMAL_DAY_COUNT}天。"
            f"缺失={list(missing[:10])}；"
            f"额外={list(extra[:10])}"
        )

    for required_date in REPORT_DATES:
        if required_date not in normalized:
            raise ResultWriterError(
                f"缺少论文指定日期{required_date.date()}。"
            )

    return normalized


def _unwrap_q4_base(day_result: Any) -> Any:
    """Q4单日结果外层包含base_result；Q1-Q3直接返回自身。"""
    return getattr(day_result, "base_result", day_result)


def _get_plan_series(
    day_result: Any,
    *,
    mode: str,
    config: ProjectConfig,
) -> pd.Series:
    base = _unwrap_q4_base(day_result)

    if mode in {"q2", "q4-2"}:
        series = base.plan_purchase_kwh
    elif mode in {"q3", "q4-3"}:
        series = base.original_plan_kwh
    else:
        raise ValueError(f"未知mode={mode}")

    return _validate_series_144(
        series,
        name=f"{mode}.plan_purchase_kwh",
        config=config,
    )


def _get_adjusted_series(
    day_result: Any,
    *,
    mode: str,
    config: ProjectConfig,
) -> pd.Series:
    if mode not in {"q3", "q4-3"}:
        raise ValueError("只有Q3/Q4-3存在调整购电量。")

    base = _unwrap_q4_base(day_result)

    # 模板“调整购电量”写最终生效正常购电量GF，
    # 而不是dG_plus-dG_minus。
    return _validate_series_144(
        base.final_effective_plan_kwh,
        name=f"{mode}.final_effective_plan_kwh",
        config=config,
    )


def _get_charge_discharge_energy(
    day_result: Any,
    *,
    config: ProjectConfig,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    base = _unwrap_q4_base(day_result)

    charge = _validate_series_144(
        base.actual_charge_kwh,
        name="actual_charge_kwh",
        config=config,
    )
    discharge = _validate_series_144(
        base.actual_discharge_kwh,
        name="actual_discharge_kwh",
        config=config,
    )
    energy = _validate_energy_145(
        base.energy_kwh,
        name="energy_kwh",
        config=config,
    )

    return charge, discharge, energy


def _get_emergency_series(
    day_result: Any,
    *,
    config: ProjectConfig,
) -> pd.Series:
    base = _unwrap_q4_base(day_result)
    return _validate_series_144(
        base.actual_emergency_kwh,
        name="actual_emergency_kwh",
        config=config,
    )


def _get_plan_cost(day_result: Any, *, mode: str) -> float:
    if mode == "q2":
        return float(day_result.plan_cost_yuan)
    if mode == "q3":
        return float(day_result.C_plan_yuan)
    if mode in {"q4-2", "q4-3"}:
        return float(day_result.C_plan_yuan)
    raise ValueError(f"未知mode={mode}")


def _get_regular_cost(day_result: Any, *, mode: str) -> float:
    """
    调整购电量sheet中的“全天购电费”：
    - Q3/Q4-3使用最终正常购电及调整结算C_reg；
    - 不包含紧急购电费用。
    """
    if mode in {"q3", "q4-3"}:
        return float(day_result.C_reg_yuan)
    raise ValueError("只有Q3/Q4-3存在C_reg。")


# ============================================================================
# time_map / paper table / emergency interval
# ============================================================================


def _ordered_time_map(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    time_map = build_time_map(config)
    validate_time_map(time_map, config)

    ordered = time_map.sort_values(
        "template_slot"
    ).reset_index(drop=True)

    if ordered["template_slot"].tolist() != list(range(144)):
        raise ResultWriterError(
            "template_slot必须严格为0~143。"
        )

    if ordered["k"].tolist() != list(range(144)):
        raise ResultWriterError(
            "template_slot顺序必须与模型k顺序一一对应。"
        )

    # 强制关键物理映射。
    checks = {
        0: ("0:00", "0:10", "0:10"),
        36: ("6:00", "6:10", "6:10"),
        60: ("10:00", "10:10", "10:10"),
        143: ("23:50", "24:00", "0:00+1"),
    }

    by_k = ordered.set_index("k")
    for k, expected in checks.items():
        got = (
            by_k.loc[k, "interval_start"],
            by_k.loc[k, "interval_end"],
            by_k.loc[k, "source_right_endpoint_label"],
        )
        if got != expected:
            raise ResultWriterError(
                f"time_map关键映射错误：k={k}, "
                f"actual={got}, expected={expected}"
            )

    return ordered


def _series_in_template_slot_order(
    series: pd.Series,
    *,
    config: ProjectConfig,
) -> list[float]:
    """
    唯一合法的模板写入顺序。

    不是：
        根据template_display_label搜索时间。

    而是：
        model k
        -> time_map.template_slot
        -> 顺序写入Excel业务槽位。
    """
    values = _validate_series_144(
        series,
        name="template_series",
        config=config,
    )

    tm = _ordered_time_map(config)

    ordered = [
        float(values.loc[int(k)])
        for k in tm["k"]
    ]

    if len(ordered) != 144:
        raise AssertionError("每天必须恰好写入144个10分钟值。")

    # 额外防错：第一个值必须是model k=0。
    if not np.isclose(ordered[0], float(values.loc[0])):
        raise AssertionError("model k=0在写入时发生丢失/错位。")

    # 最后一个值必须是model k=143，而不是不存在的k=144。
    if not np.isclose(ordered[-1], float(values.loc[143])):
        raise AssertionError("最后槽位不是model k=143。")

    return ordered


def extract_paper_table1(
    day_result: Any,
    *,
    mode: str,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """
    论文表1提取器。

    只使用：
        REPORT_INTERVAL_INDEX
        time_map.paper_label

    绝不使用template_display_label搜索时间。
    """
    tm = _ordered_time_map(config).set_index("k")

    if mode in {"q2", "q4-2"}:
        series = _get_plan_series(
            day_result,
            mode=mode,
            config=config,
        )
    elif mode in {"q3", "q4-3"}:
        # 论文若展示最终生效购电，可改为_get_adjusted_series；
        # 当前按“计划购电量”表1默认提取0:00原计划G0。
        series = _get_plan_series(
            day_result,
            mode=mode,
            config=config,
        )
    else:
        raise ValueError(f"未知mode={mode}")

    rows = []
    for k in REPORT_INTERVAL_INDEX:
        rows.append(
            {
                "k": k,
                "paper_label": tm.loc[k, "paper_label"],
                "purchase_kwh": float(series.loc[k]),
            }
        )

    frame = pd.DataFrame(rows)

    if frame.loc[frame["k"] == 60, "paper_label"].iloc[0] != "10:00-10:10":
        raise ResultWriterError(
            "论文10:00-10:10必须来自model k=60。"
        )

    return frame


def merge_emergency_intervals(
    emergency_kwh: pd.Series,
    *,
    tolerance_kwh: float = 1e-8,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> list[dict]:
    """
    把相邻的紧急购电物理区间自动合并。

    例如：
        k=78,79,80
    -> 13:00-13:30

    时间标签由time_map.interval_start/end生成，
    不使用模板显示标签。
    """
    q = _validate_series_144(
        emergency_kwh,
        name="emergency_kwh",
        config=config,
    )

    active = [
        k for k in range(config.intervals_per_day)
        if float(q.loc[k]) > tolerance_kwh
    ]

    if not active:
        return []

    runs: list[tuple[int, int]] = []
    start = active[0]
    prev = active[0]

    for k in active[1:]:
        if k == prev + 1:
            prev = k
            continue

        runs.append((start, prev))
        start = k
        prev = k

    runs.append((start, prev))

    tm = _ordered_time_map(config).set_index("k")

    events = []
    for start_k, end_k in runs:
        label = (
            f"{tm.loc[start_k, 'interval_start']}-"
            f"{tm.loc[end_k, 'interval_end']}"
        )

        amount = float(
            q.loc[start_k:end_k].sum()
        )

        events.append(
            {
                "start_k": start_k,
                "end_k": end_k,
                "paper_interval": label,
                "emergency_kwh": amount,
            }
        )

    return events


# ============================================================================
# artifact_tool workbook helpers
# ============================================================================


_HEADER_FORMAT = {
    "fill": "#D9EAF7",
    "font": {"bold": True},
    "horizontal_alignment": "center",
    "vertical_alignment": "center",
    "wrap_text": True,
}

_SUBHEADER_FORMAT = {
    "fill": "#EEF5FA",
    "font": {"bold": True},
    "horizontal_alignment": "center",
    "vertical_alignment": "center",
}


def _style_header(sheet: Any, row_count: int, col_count: int) -> None:
    header = _range(sheet, 
        0, 0, 1, col_count
    )
    header.format = _HEADER_FORMAT

    body = _range(sheet, 
        0, 0, row_count, col_count
    )
    body.format.vertical_alignment = "center"


def _create_plan_matrix_sheet(
    workbook: Workbook,
    *,
    sheet_name: str,
    formal_results: Mapping[pd.Timestamp, Any],
    mode: str,
    adjusted: bool,
    config: ProjectConfig,
) -> None:
    """
    result2/3/4的全时段矩阵版计划/调整购电量。

    列：
        A 日期\时间
        B~? 144个template_slot
        最后两列 全天购电量 / 全天购电费
    """
    tm = _ordered_time_map(config)
    display_headers = tm["template_display_label"].tolist()

    header = (
        ["日期\\时间"]
        + display_headers
        + ["全天购电量", "全天购电费"]
    )

    rows = [header]

    for d in FORMAL_DATES:
        day = formal_results[d]

        if adjusted:
            series = _get_adjusted_series(
                day,
                mode=mode,
                config=config,
            )
            total_fee = _get_regular_cost(
                day,
                mode=mode,
            )
        else:
            series = _get_plan_series(
                day,
                mode=mode,
                config=config,
            )
            total_fee = _get_plan_cost(
                day,
                mode=mode,
            )

        slot_values = _series_in_template_slot_order(
            series,
            config=config,
        )

        total_purchase = float(series.sum())

        # 全天购电量必须严格等于sum(k=0..143)
        if abs(total_purchase - sum(slot_values)) > 1e-8:
            raise ResultWriterError(
                f"{d.date()}全天购电量与144个k求和不一致。"
            )

        rows.append(
            [_as_python_datetime(d)]
            + slot_values
            + [total_purchase, float(total_fee)]
        )

    sheet = workbook.worksheets.add(sheet_name)
    _range(sheet, 
        0, 0, len(rows), len(header)
    ).values = rows

    _style_header(
        sheet,
        row_count=len(rows),
        col_count=len(header),
    )

    sheet.freeze_panes.freeze_rows(1)
    sheet.freeze_panes.freeze_columns(1)

    _range(sheet, 
        1, 0, FORMAL_DAY_COUNT, 1
    ).format.number_format = "yyyy-mm-dd"

    # 适度列宽，避免144列自动扩展失控。
    _range(sheet, 
        0, 0, len(rows), 1
    ).format.column_width = 14

    _range(sheet, 
        0, 1, len(rows), 144
    ).format.column_width = 12

    _range(sheet, 
        0, 145, len(rows), 2
    ).format.column_width = 14


def _create_result1_plan_sheet(
    workbook: Workbook,
    *,
    result1: Any,
    config: ProjectConfig,
) -> None:
    tm = _ordered_time_map(config)
    q = _validate_series_144(
        result1.plan_purchase_kwh,
        name="result1.plan_purchase_kwh",
        config=config,
    )

    slot_values = _series_in_template_slot_order(
        q,
        config=config,
    )

    rows = [["时间段", "购电量"]]

    for slot, value in enumerate(slot_values):
        # 只用template_slot顺序；显示文字不参与定位。
        rows.append(
            [
                tm.loc[slot, "template_display_label"],
                float(value),
            ]
        )

    sheet = workbook.worksheets.add(SHEET_PLAN)
    _range(sheet, 
        0, 0, len(rows), 2
    ).values = rows

    _style_header(sheet, len(rows), 2)
    sheet.freeze_panes.freeze_rows(1)
    sheet.get_range("A1:A145").format.column_width = 20
    sheet.get_range("B1:B145").format.column_width = 14


def _aggregate_four_hour_blocks(
    charge: pd.Series,
    discharge: pd.Series,
) -> list[tuple[str, float, float]]:
    rows = []

    for start_k, end_k_exclusive, label in FOUR_HOUR_BLOCKS:
        charge_sum = float(
            charge.loc[
                start_k:end_k_exclusive - 1
            ].sum()
        )
        discharge_sum = float(
            discharge.loc[
                start_k:end_k_exclusive - 1
            ].sum()
        )
        rows.append(
            (label, charge_sum, discharge_sum)
        )

    return rows


def _create_result1_storage_sheet(
    workbook: Workbook,
    *,
    result1: Any,
    config: ProjectConfig,
) -> None:
    charge = _validate_series_144(
        result1.charge_kwh,
        name="result1.charge_kwh",
        config=config,
    )
    discharge = _validate_series_144(
        result1.discharge_kwh,
        name="result1.discharge_kwh",
        config=config,
    )
    energy = _validate_energy_145(
        result1.energy_kwh,
        name="result1.energy_kwh",
        config=config,
    )

    blocks = _aggregate_four_hour_blocks(
        charge,
        discharge,
    )

    rows = [[
        "时间段",
        "充电量",
        "放电量",
        "时刻",
        "储电量",
    ]]

    for i, (label, ch, dis) in enumerate(blocks):
        if i == 0:
            time_label = "0:00"
            e = float(energy.loc[0])
        elif i == 1:
            time_label = "24:00"
            e = float(energy.loc[144])
        else:
            time_label = None
            e = None

        rows.append(
            [label, ch, dis, time_label, e]
        )

    sheet = workbook.worksheets.add(SHEET_STORAGE)
    _range(sheet, 
        0, 0, len(rows), 5
    ).values = rows

    _style_header(sheet, len(rows), 5)
    sheet.get_range("A1:A7").format.column_width = 18
    sheet.get_range("B1:C7").format.column_width = 14
    sheet.get_range("D1:E7").format.column_width = 14


def _create_storage_sheet_multi(
    workbook: Workbook,
    *,
    formal_results: Mapping[pd.Timestamp, Any],
    config: ProjectConfig,
) -> None:
    rows = [[
        "日期",
        "时间段",
        "充电量",
        "放电量",
        "时刻",
        "储电量",
    ]]

    for d in FORMAL_DATES:
        day = formal_results[d]
        charge, discharge, energy = (
            _get_charge_discharge_energy(
                day,
                config=config,
            )
        )
        blocks = _aggregate_four_hour_blocks(
            charge,
            discharge,
        )

        for i, (label, ch, dis) in enumerate(blocks):
            date_value = (
                _as_python_datetime(d)
                if i == 0
                else None
            )

            if i == 0:
                state_time = "0:00"
                state_energy = float(energy.loc[0])
            elif i == 1:
                state_time = "24:00"
                state_energy = float(energy.loc[144])
            else:
                state_time = None
                state_energy = None

            rows.append(
                [
                    date_value,
                    label,
                    ch,
                    dis,
                    state_time,
                    state_energy,
                ]
            )

    sheet = workbook.worksheets.add(SHEET_STORAGE)
    _range(sheet, 
        0, 0, len(rows), 6
    ).values = rows

    _style_header(sheet, len(rows), 6)
    sheet.freeze_panes.freeze_rows(1)

    _range(sheet, 
        1, 0, FORMAL_DAY_COUNT * 6, 1
    ).format.number_format = "yyyy-mm-dd"

    _range(sheet, 0, 0, len(rows), 1).format.column_width = 14
    _range(sheet, 0, 1, len(rows), 1).format.column_width = 18
    _range(sheet, 0, 2, len(rows), 2).format.column_width = 14
    _range(sheet, 0, 4, len(rows), 2).format.column_width = 14


def _create_emergency_sheet(
    workbook: Workbook,
    *,
    formal_results: Mapping[pd.Timestamp, Any],
    config: ProjectConfig,
    strict_max_three_events: bool,
    tolerance_kwh: float,
) -> None:
    """
    模板说明中每个日期预留3行。

    默认strict_max_three_events=True：
    - <=3个合并后事件：补空到3行；
    - >3个事件：直接报错，绝不静默截断。

    如正式求解发现某日确有>3个独立紧急区间，可显式关闭strict，
    此时writer会扩展行数以保存全部事件。
    """
    rows = [["日期", "购电时间段", "购电量"]]

    for d in FORMAL_DATES:
        day = formal_results[d]

        emergency = _get_emergency_series(
            day,
            config=config,
        )

        events = merge_emergency_intervals(
            emergency,
            tolerance_kwh=tolerance_kwh,
            config=config,
        )

        if strict_max_three_events and len(events) > 3:
            raise ResultWriterError(
                f"{d.date()}合并后有{len(events)}个紧急购电区间，"
                "超过模板每天预留3行。"
                "为避免静默丢失，请检查模型或显式设置"
                "strict_max_three_events=False。"
            )

        n_rows = (
            max(3, len(events))
            if strict_max_three_events
            else max(1, len(events))
        )

        for i in range(n_rows):
            date_value = (
                _as_python_datetime(d)
                if i == 0
                else None
            )

            if i < len(events):
                interval_label = events[i][
                    "paper_interval"
                ]
                amount = float(
                    events[i]["emergency_kwh"]
                )
            else:
                interval_label = None
                amount = None

            rows.append(
                [date_value, interval_label, amount]
            )

    sheet = workbook.worksheets.add(SHEET_EMERGENCY)
    _range(sheet, 
        0, 0, len(rows), 3
    ).values = rows

    _style_header(sheet, len(rows), 3)
    sheet.freeze_panes.freeze_rows(1)

    _range(sheet, 
        1, 0, len(rows) - 1, 1
    ).format.number_format = "yyyy-mm-dd"

    _range(sheet, 0, 0, len(rows), 1).format.column_width = 14
    _range(sheet, 0, 1, len(rows), 1).format.column_width = 22
    _range(sheet, 0, 2, len(rows), 1).format.column_width = 14


# ============================================================================
# 写出后重新读取校验
# ============================================================================


def _sheet_names_from_imported_workbook(
    workbook: Any,
) -> list[str]:
    inspected = workbook.inspect(
        {
            "kind": "sheet",
            "include": "id,name",
        }
    ).ndjson

    names = []
    for line in inspected.splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        names.append(record["name"])

    return names


def _validate_plan_sheet_after_reload(
    workbook: Any,
    *,
    sheet_name: str,
    formal_results: Optional[
        Mapping[pd.Timestamp, Any]
    ],
    result1: Optional[Any],
    mode: Optional[str],
    adjusted: bool,
    config: ProjectConfig,
) -> list[dict]:
    checks = []
    tm = _ordered_time_map(config)

    sheet = workbook.worksheets.get_item(sheet_name)

    if result1 is not None:
        values = _range(sheet, 
            0, 0, 145, 2
        ).values

        checks.append(
            {
                "item": f"{sheet_name}:result1_row_count",
                "passed": len(values) == 145,
                "detail": f"rows={len(values)}",
            }
        )

        # 144显示标签严格来自template_slot顺序。
        headers = [row[0] for row in values[1:]]
        expected_headers = (
            tm["template_display_label"].tolist()
        )
        checks.append(
            {
                "item": f"{sheet_name}:template_slot_headers",
                "passed": headers == expected_headers,
                "detail": "显示标签仅按template_slot顺序输出。",
            }
        )

        expected_q = _validate_series_144(
            result1.plan_purchase_kwh,
            name="result1.plan_purchase_kwh",
            config=config,
        )

        written_q = [
            float(row[1]) for row in values[1:]
        ]

        checks.append(
            {
                "item": f"{sheet_name}:k0_not_missing",
                "passed": np.isclose(
                    written_q[0],
                    float(expected_q.loc[0]),
                ),
                "detail": (
                    "第一业务槽位必须写model k=0，"
                    "不能从k=1开始。"
                ),
            }
        )

        checks.append(
            {
                "item": f"{sheet_name}:last_is_k143",
                "passed": np.isclose(
                    written_q[-1],
                    float(expected_q.loc[143]),
                ),
                "detail": (
                    "最后业务槽位必须写model k=143，"
                    "不能写不存在的次日k=144。"
                ),
            }
        )

        return checks

    if formal_results is None or mode is None:
        raise ValueError("多日计划表校验缺少formal_results/mode。")

    # Header + 334 dates, 147 columns.
    values = _range(sheet, 
        0, 0, FORMAL_DAY_COUNT + 1, 147
    ).values

    checks.append(
        {
            "item": f"{sheet_name}:shape",
            "passed": (
                len(values) == FORMAL_DAY_COUNT + 1
                and all(len(row) == 147 for row in values)
            ),
            "detail": (
                f"expected=335x147; "
                f"actual_rows={len(values)}"
            ),
        }
    )

    header = values[0]
    expected_slot_headers = (
        tm["template_display_label"].tolist()
    )

    checks.append(
        {
            "item": f"{sheet_name}:slot_header_order",
            "passed": (
                header[1:145] == expected_slot_headers
            ),
            "detail": (
                "Excel显示表头只验证template_slot顺序，"
                "不参与模型k定位。"
            ),
        }
    )

    first_day = formal_results[FORMAL_DATES[0]]

    if adjusted:
        expected_first_series = _get_adjusted_series(
            first_day,
            mode=mode,
            config=config,
        )
    else:
        expected_first_series = _get_plan_series(
            first_day,
            mode=mode,
            config=config,
        )

    # B列对应template_slot=0 -> model k=0
    written_first_k0 = float(values[1][1])
    checks.append(
        {
            "item": f"{sheet_name}:k0_not_missing",
            "passed": np.isclose(
                written_first_k0,
                float(expected_first_series.loc[0]),
            ),
            "detail": (
                "首个业务单元格必须是model k=0 "
                "(physical 0:00-0:10)。"
            ),
        }
    )

    # 第144个槽位对应k=143，不是下一天0:00-0:10。
    written_first_k143 = float(values[1][144])
    checks.append(
        {
            "item": f"{sheet_name}:no_next_day_k144",
            "passed": np.isclose(
                written_first_k143,
                float(expected_first_series.loc[143]),
            ),
            "detail": (
                "最后槽位显示虽为0:00+1-0:10+1，"
                "但写入值必须是model k=143 "
                "(physical 23:50-24:00)。"
            ),
        }
    )

    # 全量检查每天全天购电量=144个槽位之和。
    total_ok = True
    max_residual = 0.0

    for row_index, d in enumerate(FORMAL_DATES, start=1):
        slot_values = np.array(
            [
                float(x)
                for x in values[row_index][1:145]
            ],
            dtype=float,
        )
        stored_total = float(values[row_index][145])
        residual = abs(
            stored_total - float(slot_values.sum())
        )
        max_residual = max(max_residual, residual)
        if residual > 1e-7:
            total_ok = False
            break

    checks.append(
        {
            "item": f"{sheet_name}:daily_total_equals_sum_k0_143",
            "passed": total_ok,
            "detail": (
                f"max_residual={max_residual:.12g} kWh"
            ),
        }
    )

    return checks


def validate_written_result(
    path: str | Path,
    *,
    filename: str,
    config: ProjectConfig = DEFAULT_CONFIG,
    formal_results: Optional[
        Mapping[pd.Timestamp, Any]
    ] = None,
    result1: Optional[Any] = None,
    mode: Optional[str] = None,
) -> pd.DataFrame:
    """
    导出后重新读取xlsx，执行结构校验。

    校验包括：
    - sheet名称与数量；
    - 日期范围/数量；
    - 144个template_slot；
    - k=0未漏；
    - 最后槽位为k=143而非次日k=144；
    - 每日总购电量=sum(k=0..143)；
    - 充放电表的0:00/24:00 SOC结构；
    - 紧急购电表结构；
    - 论文k=60物理标签为10:00-10:10。
    """
    path = Path(path)

    if filename not in RESULT_SHEETS:
        raise ValueError(f"未知结果文件名：{filename}")

    workbook = SpreadsheetFile.import_xlsx(
        Blob.load(str(path))
    )

    rows = []

    actual_sheet_names = (
        _sheet_names_from_imported_workbook(workbook)
    )
    expected_sheet_names = list(
        RESULT_SHEETS[filename]
    )

    rows.append(
        {
            "item": "sheet_names",
            "passed": actual_sheet_names
            == expected_sheet_names,
            "detail": (
                f"actual={actual_sheet_names}; "
                f"expected={expected_sheet_names}"
            ),
        }
    )

    # time_map本体防错
    tm = _ordered_time_map(config).set_index("k")

    rows.append(
        {
            "item": "paper_k60",
            "passed": (
                tm.loc[60, "paper_label"]
                == "10:00-10:10"
            ),
            "detail": (
                "论文10:00-10:10必须来自model k=60。"
            ),
        }
    )

    rows.append(
        {
            "item": "physical_k0",
            "passed": (
                tm.loc[0, "paper_label"] == "0:00-0:10"
                and tm.loc[
                    0, "source_right_endpoint_label"
                ] == "0:10"
            ),
            "detail": "k=0物理区间/右端点映射。",
        }
    )

    rows.append(
        {
            "item": "physical_k143",
            "passed": (
                tm.loc[143, "paper_label"]
                == "23:50-24:00"
                and tm.loc[
                    143, "source_right_endpoint_label"
                ] == "0:00+1"
            ),
            "detail": "k=143为当天最后物理区间。",
        }
    )

    if filename == "result1.xlsx":
        rows.extend(
            _validate_plan_sheet_after_reload(
                workbook,
                sheet_name=SHEET_PLAN,
                formal_results=None,
                result1=result1,
                mode=None,
                adjusted=False,
                config=config,
            )
        )

        storage = workbook.worksheets.get_item(
            SHEET_STORAGE
        )
        storage_values = _range(storage, 
            0, 0, 7, 5
        ).values

        rows.append(
            {
                "item": "result1_storage_rows",
                "passed": len(storage_values) == 7,
                "detail": "header+6个4小时区间。",
            }
        )

        rows.append(
            {
                "item": "result1_soc_0_24",
                "passed": (
                    storage_values[1][3] == "0:00"
                    and storage_values[2][3] == "24:00"
                ),
                "detail": "只在模板指定位置写0:00/24:00储电量。",
            }
        )
    else:
        adjusted = filename in {
            "result3.xlsx",
            "result4-3.xlsx",
        }

        rows.extend(
            _validate_plan_sheet_after_reload(
                workbook,
                sheet_name=SHEET_PLAN,
                formal_results=formal_results,
                result1=None,
                mode=mode,
                adjusted=False,
                config=config,
            )
        )

        if adjusted:
            rows.extend(
                _validate_plan_sheet_after_reload(
                    workbook,
                    sheet_name=SHEET_ADJUST,
                    formal_results=formal_results,
                    result1=None,
                    mode=mode,
                    adjusted=True,
                    config=config,
                )
            )

        storage = workbook.worksheets.get_item(
            SHEET_STORAGE
        )

        expected_storage_rows = (
            1 + FORMAL_DAY_COUNT * 6
        )

        storage_values = _range(storage, 
            0, 0, expected_storage_rows, 6
        ).values

        rows.append(
            {
                "item": "storage_row_count",
                "passed": (
                    len(storage_values)
                    == expected_storage_rows
                ),
                "detail": (
                    f"header+{FORMAL_DAY_COUNT}*6="
                    f"{expected_storage_rows}"
                ),
            }
        )

        # 每天第1/2行必须分别对应0:00/24:00。
        soc_format_ok = True
        for day_i in range(FORMAL_DAY_COUNT):
            base_row = 1 + day_i * 6
            if (
                storage_values[base_row][4] != "0:00"
                or storage_values[base_row + 1][4]
                != "24:00"
            ):
                soc_format_ok = False
                break

        rows.append(
            {
                "item": "storage_soc_0_24_format",
                "passed": soc_format_ok,
                "detail": "每个日期只写0:00和24:00储电量。",
            }
        )

        emergency = workbook.worksheets.get_item(
            SHEET_EMERGENCY
        )

        emergency_header = emergency.get_range(
            "A1:C1"
        ).values[0]

        rows.append(
            {
                "item": "emergency_header",
                "passed": emergency_header
                == ["日期", "购电时间段", "购电量"],
                "detail": f"header={emergency_header}",
            }
        )

    report = pd.DataFrame(rows)

    failed = report.loc[~report["passed"]]
    if not failed.empty:
        raise ResultWriterError(
            f"{filename}写出后结构校验失败：\n"
            + failed.to_string(index=False)
        )

    return report


# ============================================================================
# 五个文件写出
# ============================================================================


def write_result1(
    result1: Any,
    output_dir: str | Path,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> tuple[Path, pd.DataFrame]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    workbook = Workbook.create()

    _create_result1_plan_sheet(
        workbook,
        result1=result1,
        config=config,
    )
    _create_result1_storage_sheet(
        workbook,
        result1=result1,
        config=config,
    )

    path = output_dir / "result1.xlsx"
    SpreadsheetFile.export_xlsx(workbook).save(
        str(path)
    )

    report = validate_written_result(
        path,
        filename="result1.xlsx",
        result1=result1,
        config=config,
    )

    return path, report


def _write_multi_day_result(
    *,
    filename: str,
    period_result: Any,
    mode: str,
    output_dir: str | Path,
    include_adjustment: bool,
    strict_max_three_events: bool,
    emergency_tolerance_kwh: float,
    config: ProjectConfig,
) -> tuple[Path, pd.DataFrame]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    formal_results = _get_formal_results(
        period_result
    )

    workbook = Workbook.create()

    _create_plan_matrix_sheet(
        workbook,
        sheet_name=SHEET_PLAN,
        formal_results=formal_results,
        mode=mode,
        adjusted=False,
        config=config,
    )

    if include_adjustment:
        _create_plan_matrix_sheet(
            workbook,
            sheet_name=SHEET_ADJUST,
            formal_results=formal_results,
            mode=mode,
            adjusted=True,
            config=config,
        )

    _create_storage_sheet_multi(
        workbook,
        formal_results=formal_results,
        config=config,
    )

    _create_emergency_sheet(
        workbook,
        formal_results=formal_results,
        config=config,
        strict_max_three_events=(
            strict_max_three_events
        ),
        tolerance_kwh=emergency_tolerance_kwh,
    )

    path = output_dir / filename
    SpreadsheetFile.export_xlsx(workbook).save(
        str(path)
    )

    report = validate_written_result(
        path,
        filename=filename,
        formal_results=formal_results,
        mode=mode,
        config=config,
    )

    return path, report


def write_result2(
    period_result: Any,
    output_dir: str | Path,
    *,
    strict_max_three_events: bool = True,
    emergency_tolerance_kwh: float = 1e-8,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> tuple[Path, pd.DataFrame]:
    return _write_multi_day_result(
        filename="result2.xlsx",
        period_result=period_result,
        mode="q2",
        output_dir=output_dir,
        include_adjustment=False,
        strict_max_three_events=(
            strict_max_three_events
        ),
        emergency_tolerance_kwh=(
            emergency_tolerance_kwh
        ),
        config=config,
    )


def write_result3(
    period_result: Any,
    output_dir: str | Path,
    *,
    strict_max_three_events: bool = True,
    emergency_tolerance_kwh: float = 1e-8,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> tuple[Path, pd.DataFrame]:
    return _write_multi_day_result(
        filename="result3.xlsx",
        period_result=period_result,
        mode="q3",
        output_dir=output_dir,
        include_adjustment=True,
        strict_max_three_events=(
            strict_max_three_events
        ),
        emergency_tolerance_kwh=(
            emergency_tolerance_kwh
        ),
        config=config,
    )


def write_result4_2(
    period_result: Any,
    output_dir: str | Path,
    *,
    strict_max_three_events: bool = True,
    emergency_tolerance_kwh: float = 1e-8,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> tuple[Path, pd.DataFrame]:
    return _write_multi_day_result(
        filename="result4-2.xlsx",
        period_result=period_result,
        mode="q4-2",
        output_dir=output_dir,
        include_adjustment=False,
        strict_max_three_events=(
            strict_max_three_events
        ),
        emergency_tolerance_kwh=(
            emergency_tolerance_kwh
        ),
        config=config,
    )


def write_result4_3(
    period_result: Any,
    output_dir: str | Path,
    *,
    strict_max_three_events: bool = True,
    emergency_tolerance_kwh: float = 1e-8,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> tuple[Path, pd.DataFrame]:
    return _write_multi_day_result(
        filename="result4-3.xlsx",
        period_result=period_result,
        mode="q4-3",
        output_dir=output_dir,
        include_adjustment=True,
        strict_max_three_events=(
            strict_max_three_events
        ),
        emergency_tolerance_kwh=(
            emergency_tolerance_kwh
        ),
        config=config,
    )


def write_all_results(
    *,
    result1: Any,
    result2_period: Any,
    result3_period: Any,
    result4_2_period: Any,
    result4_3_period: Any,
    output_dir: str | Path,
    strict_max_three_events: bool = True,
    emergency_tolerance_kwh: float = 1e-8,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> Dict[str, tuple[Path, pd.DataFrame]]:
    """
    一次写出五个题目要求的结果文件，并全部执行导出后回读校验。
    """
    outputs: Dict[
        str,
        tuple[Path, pd.DataFrame],
    ] = {}

    outputs["result1.xlsx"] = write_result1(
        result1,
        output_dir,
        config=config,
    )

    outputs["result2.xlsx"] = write_result2(
        result2_period,
        output_dir,
        strict_max_three_events=(
            strict_max_three_events
        ),
        emergency_tolerance_kwh=(
            emergency_tolerance_kwh
        ),
        config=config,
    )

    outputs["result3.xlsx"] = write_result3(
        result3_period,
        output_dir,
        strict_max_three_events=(
            strict_max_three_events
        ),
        emergency_tolerance_kwh=(
            emergency_tolerance_kwh
        ),
        config=config,
    )

    outputs["result4-2.xlsx"] = write_result4_2(
        result4_2_period,
        output_dir,
        strict_max_three_events=(
            strict_max_three_events
        ),
        emergency_tolerance_kwh=(
            emergency_tolerance_kwh
        ),
        config=config,
    )

    outputs["result4-3.xlsx"] = write_result4_3(
        result4_3_period,
        output_dir,
        strict_max_three_events=(
            strict_max_three_events
        ),
        emergency_tolerance_kwh=(
            emergency_tolerance_kwh
        ),
        config=config,
    )

    return outputs
