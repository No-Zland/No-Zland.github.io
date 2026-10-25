# -*- coding: utf-8 -*-
"""
data_checker.py
C题附件1-4公共数据审计模块。

本模块只做：
- 数据长度检查
- 日期连续性检查
- 缺失值检查
- 时间索引/右端点映射检查
- 附件3结构检查

不删除、不插值、不修补原始数据，不做预测、不做优化。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd

from config import DEFAULT_CONFIG, ProjectConfig
from data_loader import (
    Attachment1Data,
    Attachment2Data,
    Attachment3Data,
    Attachment4Data,
    DataBundle,
    load_all,
)
from time_index import validate_time_map


@dataclass
class CheckItem:
    category: str
    item: str
    passed: bool
    detail: str


def _item(
    category: str,
    item: str,
    passed: bool,
    detail: str,
) -> CheckItem:
    return CheckItem(category, item, bool(passed), detail)


def _expected_dates(config: ProjectConfig) -> pd.DatetimeIndex:
    return pd.date_range(
        config.start_date,
        config.end_date,
        freq="D",
    )


def _check_date_index(
    index: pd.Index,
    source_name: str,
    config: ProjectConfig,
) -> list[CheckItem]:
    items = []

    idx = pd.DatetimeIndex(index).normalize()
    expected = _expected_dates(config)

    items.append(
        _item(
            "日期",
            f"{source_name}-日期数量",
            len(idx) == len(expected),
            f"实际{len(idx)}日，期望{len(expected)}日。",
        )
    )

    items.append(
        _item(
            "日期",
            f"{source_name}-日期唯一",
            idx.is_unique,
            f"重复日期数={int(idx.duplicated().sum())}",
        )
    )

    same = len(idx) == len(expected) and idx.equals(expected)
    items.append(
        _item(
            "日期",
            f"{source_name}-2025全年连续",
            same,
            (
                f"实际范围={idx.min().date() if len(idx) else None}"
                f"~{idx.max().date() if len(idx) else None}；"
                f"期望={config.start_date}~{config.end_date}"
            ),
        )
    )

    return items


def check_time_map(
    bundle: DataBundle,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> list[CheckItem]:
    items = []
    try:
        validate_time_map(bundle.time_map, config)
        passed = True
        detail = "144行映射及k=0/36/60/143关键断言全部通过。"
    except Exception as exc:
        passed = False
        detail = repr(exc)

    items.append(
        _item(
            "时间索引",
            "唯一time_map",
            passed,
            detail,
        )
    )

    tm = bundle.time_map.set_index("k")

    expected = {
        0: ("0:00", "0:10", "0:10"),
        36: ("6:00", "6:10", "6:10"),
        60: ("10:00", "10:10", "10:10"),
        143: ("23:50", "24:00", "0:00+1"),
    }

    for k, triple in expected.items():
        got = (
            tm.loc[k, "interval_start"],
            tm.loc[k, "interval_end"],
            tm.loc[k, "source_right_endpoint_label"],
        )
        items.append(
            _item(
                "时间索引",
                f"k={k}关键映射",
                got == triple,
                f"实际={got}；期望={triple}",
            )
        )

    template_ok = bundle.time_map["template_slot"].tolist() == list(
        range(config.intervals_per_day)
    )
    items.append(
        _item(
            "时间索引",
            "template_slot仅按顺序映射",
            template_ok,
            "要求template_slot[k]=k；模板显示文字不参与k推断。",
        )
    )

    return items


def check_attachment1(
    data: Attachment1Data,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> list[CheckItem]:
    items = []

    items.append(
        _item(
            "附件1",
            "数据行数",
            len(data.raw) == 144,
            f"实际{len(data.raw)}行，期望144行。",
        )
    )

    numeric_cols = [
        "price_yuan_per_kwh",
        "load_kw",
        "pv_forecast_kw",
    ]

    for col in numeric_cols:
        n_missing = int(data.aligned[col].isna().sum())
        items.append(
            _item(
                "附件1",
                f"{col}-缺失值",
                n_missing == 0,
                f"缺失值数量={n_missing}",
            )
        )

    source_labels_ok = (
        data.aligned["source_right_endpoint_label"].iloc[0] == "0:10"
        and data.aligned["source_right_endpoint_label"].iloc[-1] == "0:00+1"
    )
    items.append(
        _item(
            "附件1",
            "右端点标签首尾",
            source_labels_ok,
            (
                f"首={data.aligned['source_right_endpoint_label'].iloc[0]}, "
                f"尾={data.aligned['source_right_endpoint_label'].iloc[-1]}"
            ),
        )
    )

    return items


def check_attachment2(
    data: Attachment2Data,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> list[CheckItem]:
    items = []

    for name, frame in [
        ("负荷", data.load_kw),
        ("光伏", data.pv_kw),
    ]:
        items.extend(_check_date_index(frame.index, f"附件2-{name}", config))

        shape_ok = frame.shape == (365, 144)
        items.append(
            _item(
                "附件2",
                f"{name}-模型网格维度",
                shape_ok,
                f"实际={frame.shape}，期望=(365, 144)",
            )
        )

        n_missing = int(frame.isna().sum().sum())
        items.append(
            _item(
                "附件2",
                f"{name}-缺失值",
                n_missing == 0,
                f"缺失值数量={n_missing}",
            )
        )

    same_index = data.load_kw.index.equals(data.pv_kw.index)
    items.append(
        _item(
            "附件2",
            "负荷与光伏日期完全一致",
            same_index,
            "两个sheet必须共享同一2025日期索引。",
        )
    )

    return items


def check_attachment3(
    data: Attachment3Data,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> list[CheckItem]:
    items = []

    raw = data.raw
    rel = data.release_index

    items.append(
        _item(
            "附件3",
            "原始数据行数",
            len(raw) == config.expected_attachment3_rows,
            (
                f"实际{len(raw)}行，"
                f"期望{config.expected_attachment3_rows}=365×4。"
            ),
        )
    )

    expected_cols = 2 + config.forecast_horizons
    items.append(
        _item(
            "附件3",
            "原始列数",
            raw.shape[1] == expected_cols,
            f"实际{raw.shape[1]}列，期望{expected_cols}列。",
        )
    )

    # 日期列允许非0点行存在空/共享字符串空标记，因此单独报告。
    date_col = config.attachment3_date_col
    raw_date_missing = int(raw[date_col].isna().sum())
    items.append(
        _item(
            "附件3",
            "日期列原始空值仅报告不修补",
            True,
            (
                f"pandas直接识别的空值数量={raw_date_missing}；"
                "另外部分读取链路可能将共享字符串空标记显示为'28'。"
                "raw保持原样，release_index负责解释。"
            ),
        )
    )

    forecast_cols = list(config.attachment3_forecast_columns)
    forecast_missing = int(raw[forecast_cols].isna().sum().sum())
    items.append(
        _item(
            "附件3",
            "24小时预测字段缺失值",
            forecast_missing == 0,
            f"预测字段缺失总数={forecast_missing}",
        )
    )

    # 每天四个发布时间
    expected_issue_times = {"0:00", "6:00", "12:00", "18:00"}
    grouped = rel.groupby("issue_date")["issue_time"].agg(list)

    day_count_ok = len(grouped) == 365
    items.append(
        _item(
            "附件3",
            "自然日数量",
            day_count_ok,
            f"实际{len(grouped)}日，期望365日。",
        )
    )

    bad_days = []
    for d, times in grouped.items():
        if len(times) != 4 or set(times) != expected_issue_times:
            bad_days.append((d, times))

    items.append(
        _item(
            "附件3",
            "每天0/6/12/18四次发布",
            len(bad_days) == 0,
            (
                "全部通过。"
                if not bad_days
                else f"异常日期前5个={bad_days[:5]}"
            ),
        )
    )

    items.extend(_check_date_index(grouped.index, "附件3-发布日期", config))

    return items


def check_attachment4(
    data: Attachment4Data,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> list[CheckItem]:
    items = []

    items.extend(_check_date_index(data.price.index, "附件4-价格", config))

    items.append(
        _item(
            "附件4",
            "模型网格维度",
            data.price.shape == (365, 144),
            f"实际={data.price.shape}，期望=(365, 144)",
        )
    )

    n_missing = int(data.price.isna().sum().sum())
    items.append(
        _item(
            "附件4",
            "价格缺失值",
            n_missing == 0,
            f"缺失值数量={n_missing}",
        )
    )

    return items


def build_check_report(
    bundle: DataBundle,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """返回完整审计报告DataFrame。"""
    items: List[CheckItem] = []

    items.extend(check_time_map(bundle, config))
    items.extend(check_attachment1(bundle.attachment1, config))
    items.extend(check_attachment2(bundle.attachment2, config))
    items.extend(check_attachment3(bundle.attachment3, config))
    items.extend(check_attachment4(bundle.attachment4, config))

    report = pd.DataFrame(
        [
            {
                "category": x.category,
                "item": x.item,
                "passed": x.passed,
                "detail": x.detail,
            }
            for x in items
        ]
    )

    return report


def assert_all_passed(report: pd.DataFrame) -> None:
    """
    若存在失败项，抛出异常。
    说明性项目（例如附件3日期列原始空值报告）本身标记passed=True。
    """
    failed = report.loc[~report["passed"]]
    if not failed.empty:
        text = "\n".join(
            f"[{row.category}] {row.item}: {row.detail}"
            for row in failed.itertuples(index=False)
        )
        raise AssertionError("数据审计未通过：\n" + text)


def run_all_checks(
    config: ProjectConfig = DEFAULT_CONFIG,
    raise_on_error: bool = True,
) -> tuple[DataBundle, pd.DataFrame]:
    """
    读取附件1-4并执行全部公共检查。

    返回：
        bundle: 后续模块可直接复用的数据对象
        report: 审计报告

    不提供 __main__ 入口，避免在本阶段写主程序。
    """
    bundle = load_all(config)
    report = build_check_report(bundle, config)

    if raise_on_error:
        assert_all_passed(report)

    return bundle, report
