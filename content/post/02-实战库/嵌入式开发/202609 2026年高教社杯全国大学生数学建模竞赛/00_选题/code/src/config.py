# -*- coding: utf-8 -*-
"""
config.py
C题公共配置模块。

职责：
1. 统一附件路径、sheet名称、字段名称；
2. 统一2025年日期范围与10分钟时间尺度；
3. 仅保存配置，不读取数据、不做预测、不建立优化模型。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class ProjectConfig:
    """C题公共配置。"""

    # 数据目录：比赛工程中可改成 Path("data") 等。
    data_dir: Path = Path(".")

    # 原始附件文件名
    attachment1_name: str = "附件1.xlsx"
    attachment2_name: str = "附件2.xlsx"
    attachment3_name: str = "附件3.xlsx"
    attachment4_name: str = "附件4.xlsx"

    # Sheet 名称
    attachment1_sheet: str = "Sheet1"
    attachment2_load_sheet: str = "小区负载"
    attachment2_pv_sheet: str = "光伏发电实际功率"
    attachment3_sheet: str = "Sheet1"
    attachment4_sheet: str = "Sheet1"

    # 原始字段名称
    attachment1_time_col: str = "时间"
    attachment1_price_col: str = "电价"
    attachment1_load_col: str = "小区负载"
    attachment1_pv_forecast_col: str = "光伏发电预测功率"

    wide_date_col: str = "日期\\时间"

    attachment3_date_col: str = "日期"
    attachment3_issue_time_col: str = "预报时刻"

    # 时间与日期
    year: int = 2025
    start_date: str = "2025-01-01"
    end_date: str = "2025-12-31"
    dt_minutes: int = 10
    intervals_per_day: int = 144
    state_nodes_per_day: int = 145

    # 附件3
    issue_hours: Tuple[int, ...] = (0, 6, 12, 18)
    forecast_horizons: int = 24
    expected_attachment3_rows: int = 365 * 4

    @property
    def attachment1_path(self) -> Path:
        return self.data_dir / self.attachment1_name

    @property
    def attachment2_path(self) -> Path:
        return self.data_dir / self.attachment2_name

    @property
    def attachment3_path(self) -> Path:
        return self.data_dir / self.attachment3_name

    @property
    def attachment4_path(self) -> Path:
        return self.data_dir / self.attachment4_name

    @property
    def attachment3_forecast_columns(self) -> Tuple[str, ...]:
        return tuple(f"预报{i}小时" for i in range(1, self.forecast_horizons + 1))


DEFAULT_CONFIG = ProjectConfig()
