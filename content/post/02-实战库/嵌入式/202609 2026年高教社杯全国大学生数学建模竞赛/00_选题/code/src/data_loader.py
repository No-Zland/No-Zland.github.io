# -*- coding: utf-8 -*-
"""
data_loader.py
附件1-4公共数据读取模块。

原则：
1. 使用pandas读取，不写回原始附件；
2. 原始DataFrame始终保留；
3. 附件1/2/4只能通过time_map将右端点标签映射到模型k；
4. 附件3保留原始宽表，不在此模块做插值、预测或10分钟化；
5. 日期统一为 pandas.Timestamp(normalized)。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from numbers import Real
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from config import DEFAULT_CONFIG, ProjectConfig
from time_index import (
    build_time_map,
    canonical_source_label,
    expected_source_labels,
)


@dataclass
class Attachment1Data:
    raw: pd.DataFrame
    aligned: pd.DataFrame


@dataclass
class Attachment2Data:
    load_raw: pd.DataFrame
    pv_raw: pd.DataFrame
    load_kw: pd.DataFrame
    pv_kw: pd.DataFrame


@dataclass
class Attachment3Data:
    raw: pd.DataFrame
    release_index: pd.DataFrame


@dataclass
class Attachment4Data:
    raw: pd.DataFrame
    price: pd.DataFrame


@dataclass
class DataBundle:
    time_map: pd.DataFrame
    attachment1: Attachment1Data
    attachment2: Attachment2Data
    attachment3: Attachment3Data
    attachment4: Attachment4Data


def _ensure_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"未找到附件：{path}")


def _parse_excel_date_value(value) -> pd.Timestamp:
    """
    解析附件2/4等日期单元格。

    支持：
    - Excel日期序列号
    - datetime/date/Timestamp
    - 日期字符串
    """
    if pd.isna(value):
        return pd.NaT

    if isinstance(value, pd.Timestamp):
        return value.normalize()

    if isinstance(value, datetime):
        return pd.Timestamp(value).normalize()

    if isinstance(value, date):
        return pd.Timestamp(value).normalize()

    if isinstance(value, Real):
        # Excel 1900 date system，pandas/openpyxl常用兼容原点
        return (
            pd.Timestamp("1899-12-30")
            + pd.to_timedelta(float(value), unit="D")
        ).normalize()

    s = str(value).strip()
    if not s:
        return pd.NaT

    return pd.to_datetime(s, errors="raise").normalize()


def _parse_date_series(series: pd.Series) -> pd.Series:
    parsed = series.map(_parse_excel_date_value)
    return pd.to_datetime(parsed).dt.normalize()


def _validate_source_label_order(
    labels,
    config: ProjectConfig,
    source_name: str,
) -> None:
    canonical = [canonical_source_label(x) for x in labels]
    expected = expected_source_labels(config)

    if len(canonical) != config.intervals_per_day:
        raise ValueError(
            f"{source_name}时间标签数量应为{config.intervals_per_day}，"
            f"实际为{len(canonical)}。"
        )

    if canonical != expected:
        mismatches = [
            (i, got, exp)
            for i, (got, exp) in enumerate(zip(canonical, expected))
            if got != exp
        ]
        preview = mismatches[:10]
        raise ValueError(
            f"{source_name}时间标签未按统一右端点顺序排列。"
            f"前若干差异={preview}"
        )


def load_attachment1(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> Attachment1Data:
    """
    读取附件1。

    aligned 为144行模型时段表：
        k
        interval_start/end
        source_right_endpoint_label
        price_yuan_per_kwh
        load_kw
        pv_forecast_kw
    """
    path = config.attachment1_path
    _ensure_file(path)

    raw = pd.read_excel(
        path,
        sheet_name=config.attachment1_sheet,
        dtype=None,
    )

    required = [
        config.attachment1_time_col,
        config.attachment1_price_col,
        config.attachment1_load_col,
        config.attachment1_pv_forecast_col,
    ]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(f"附件1缺少字段：{missing}")

    if len(raw) != config.intervals_per_day:
        raise ValueError(
            f"附件1数据行数应为144，实际为{len(raw)}。"
        )

    _validate_source_label_order(
        raw[config.attachment1_time_col].tolist(),
        config,
        "附件1",
    )

    time_map = build_time_map(config)
    aligned = time_map.copy()

    aligned["price_yuan_per_kwh"] = pd.to_numeric(
        raw[config.attachment1_price_col], errors="raise"
    ).to_numpy()
    aligned["load_kw"] = pd.to_numeric(
        raw[config.attachment1_load_col], errors="raise"
    ).to_numpy()
    aligned["pv_forecast_kw"] = pd.to_numeric(
        raw[config.attachment1_pv_forecast_col], errors="raise"
    ).to_numpy()

    return Attachment1Data(raw=raw, aligned=aligned)


def _load_daily_wide_sheet(
    path: Path,
    sheet_name: str,
    config: ProjectConfig,
    source_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    读取“日期 + 144个右端点时间列”的宽表。

    返回：
        raw: 原始宽表
        model_grid: index=date, columns=0..143 的模型网格
    """
    _ensure_file(path)

    raw = pd.read_excel(path, sheet_name=sheet_name, dtype=None)

    if raw.shape[1] != config.intervals_per_day + 1:
        raise ValueError(
            f"{source_name}应有145列（日期+144时段），实际{raw.shape[1]}列。"
        )

    date_col = raw.columns[0]
    if str(date_col) != config.wide_date_col:
        # 不静默改表头，但允许Excel读取后出现等价字符串差异。
        if str(date_col).strip() != config.wide_date_col.strip():
            raise ValueError(
                f"{source_name}首列应为{config.wide_date_col!r}，"
                f"实际为{date_col!r}。"
            )

    time_columns = list(raw.columns[1:])
    _validate_source_label_order(time_columns, config, source_name)

    dates = _parse_date_series(raw.iloc[:, 0])
    values = raw.iloc[:, 1:].copy()
    values = values.apply(pd.to_numeric, errors="raise")

    model_grid = values.copy()
    model_grid.index = dates
    model_grid.index.name = "date"
    model_grid.columns = list(range(config.intervals_per_day))

    return raw, model_grid


def load_attachment2(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> Attachment2Data:
    """
    读取附件2两个sheet。

    输出 load_kw / pv_kw:
        index: 统一日期 Timestamp
        columns: k=0..143
        values: kW
    """
    load_raw, load_kw = _load_daily_wide_sheet(
        config.attachment2_path,
        config.attachment2_load_sheet,
        config,
        "附件2-小区负载",
    )

    pv_raw, pv_kw = _load_daily_wide_sheet(
        config.attachment2_path,
        config.attachment2_pv_sheet,
        config,
        "附件2-光伏发电实际功率",
    )

    if not load_kw.index.equals(pv_kw.index):
        raise ValueError("附件2负荷与光伏日期索引不一致。")

    return Attachment2Data(
        load_raw=load_raw,
        pv_raw=pv_raw,
        load_kw=load_kw,
        pv_kw=pv_kw,
    )


def _canonical_issue_time(value) -> str:
    """将附件3预报时刻统一成 H:MM。"""
    if pd.isna(value):
        raise ValueError("附件3发现空预报时刻。")

    if isinstance(value, time):
        return f"{value.hour}:{value.minute:02d}"

    if isinstance(value, (pd.Timestamp, datetime)):
        return f"{value.hour}:{value.minute:02d}"

    if isinstance(value, Real):
        minute = int(round(float(value) * 24 * 60)) % (24 * 60)
        h, m = divmod(minute, 60)
        return f"{h}:{m:02d}"

    s = str(value).strip()
    parts = s.split(":")
    if len(parts) >= 2:
        h = int(parts[0])
        m = int("".join(ch for ch in parts[1] if ch.isdigit())[:2] or 0)
        return f"{h}:{m:02d}"

    raise ValueError(f"无法解析附件3预报时刻：{value!r}")


def _is_attachment3_blank_date_marker(value) -> bool:
    """
    附件3中6/12/18时的日期原始单元格可能是：
    - NaN / 空字符串
    - 某些读取链路下暴露为shared-string索引文本 '28'

    '28' 仅在非0:00行作为已知空日期标记处理。
    原始DataFrame不会被修改。
    """
    if pd.isna(value):
        return True

    s = str(value).strip()
    return s == "" or s == "28"


def _build_attachment3_release_index(
    raw: pd.DataFrame,
    config: ProjectConfig,
) -> pd.DataFrame:
    """
    仅建立附件3发布记录索引，不改动raw，不生成预测目标时刻，不插值。
    """
    date_col = config.attachment3_date_col
    time_col = config.attachment3_issue_time_col

    required = [date_col, time_col, *config.attachment3_forecast_columns]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(f"附件3缺少字段：{missing}")

    records = []
    current_date: Optional[pd.Timestamp] = None

    for pos, (_, row) in enumerate(raw.iterrows()):
        issue_time = _canonical_issue_time(row[time_col])
        raw_date = row[date_col]

        if issue_time == "0:00":
            if _is_attachment3_blank_date_marker(raw_date):
                raise ValueError(
                    f"附件3第{pos + 2}行是0:00发布记录，但日期为空/异常。"
                )
            current_date = _parse_excel_date_value(raw_date)
        else:
            if not _is_attachment3_blank_date_marker(raw_date):
                # 若非0点行显式写了日期，也按其实际日期解析并校验。
                explicit_date = _parse_excel_date_value(raw_date)
                if current_date is not None and explicit_date != current_date:
                    raise ValueError(
                        f"附件3第{pos + 2}行日期与当前自然日不一致："
                        f"{explicit_date} != {current_date}"
                    )
                current_date = explicit_date

        if current_date is None or pd.isna(current_date):
            raise ValueError(
                f"附件3第{pos + 2}行无法确定所属自然日。"
            )

        hour = int(issue_time.split(":")[0])
        issue_datetime = current_date + pd.Timedelta(hours=hour)

        records.append(
            {
                "raw_row_position": pos,
                "issue_date": current_date,
                "issue_time": issue_time,
                "issue_hour": hour,
                "issue_datetime": issue_datetime,
            }
        )

    release_index = pd.DataFrame(records)
    release_index["issue_date"] = pd.to_datetime(
        release_index["issue_date"]
    ).dt.normalize()

    return release_index


def load_attachment3(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> Attachment3Data:
    """
    读取附件3并保留原始宽表结构。

    raw:
        原始 1460×26 数据区，不做ffill、不插值、不转成长表。

    release_index:
        仅提供每一原始行对应的自然日/发布时间，用于后续解析和校验。
    """
    path = config.attachment3_path
    _ensure_file(path)

    raw = pd.read_excel(
        path,
        sheet_name=config.attachment3_sheet,
        dtype=object,
    )

    release_index = _build_attachment3_release_index(raw, config)

    return Attachment3Data(
        raw=raw,
        release_index=release_index,
    )


def load_attachment4(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> Attachment4Data:
    """
    读取附件4。

    price:
        index: 统一日期 Timestamp
        columns: k=0..143
        values: 元/kWh

    注意：这里只做数据对齐，不代表未来价格在决策时可知。
    信息可用性由后续问题4模块控制。
    """
    raw, price = _load_daily_wide_sheet(
        config.attachment4_path,
        config.attachment4_sheet,
        config,
        "附件4-实时电价",
    )

    return Attachment4Data(raw=raw, price=price)


def load_all(
    config: ProjectConfig = DEFAULT_CONFIG,
) -> DataBundle:
    """一次性读取附件1-4，供后续模块复用。"""
    time_map = build_time_map(config)

    return DataBundle(
        time_map=time_map,
        attachment1=load_attachment1(config),
        attachment2=load_attachment2(config),
        attachment3=load_attachment3(config),
        attachment4=load_attachment4(config),
    )
