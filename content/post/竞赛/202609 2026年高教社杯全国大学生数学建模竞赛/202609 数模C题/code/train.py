# -*- coding: utf-8 -*-
"""
train.py
预测模块回测入口。

本题没有必须训练的黑箱机器学习模型，因此这里的“train”承担：
1. Q2日前负荷预测回测；
2. Q2日前光伏预测回测；
3. 输出MAE/RMSE/WMAPE等指标；
4. 检查每个预测日严格只使用过去信息。

不运行Gurobi。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def load_cfg(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def wmape(actual: np.ndarray, forecast: np.ndarray) -> float:
    denom = float(np.abs(actual).sum())
    if denom <= 1e-12:
        return float("nan")
    return float(np.abs(actual - forecast).sum() / denom)


def main():
    parser = argparse.ArgumentParser(
        description="Q2因果日前预测回测"
    )
    parser.add_argument(
        "--config",
        default="configs/default.json",
    )
    parser.add_argument(
        "--start-date",
        default="2025-02-01",
    )
    parser.add_argument(
        "--end-date",
        default="2025-12-31",
    )
    args = parser.parse_args()

    cfg = load_cfg(args.config)

    from config import ProjectConfig
    from data_loader import load_attachment2
    from forecast_model import build_q2_day_ahead_forecast

    data_dir = PROJECT_ROOT / cfg["paths"]["data_dir"]
    project_config = ProjectConfig(data_dir=data_dir)
    attachment2 = load_attachment2(project_config)

    dates = pd.date_range(
        args.start_date,
        args.end_date,
        freq="D",
    )

    rows = []

    for d in dates:
        forecast = build_q2_day_ahead_forecast(
            attachment2,
            d,
            config=project_config,
        )

        if (
            forecast.history_end_date is not None
            and forecast.history_end_date >= d
        ):
            raise AssertionError(
                f"{d.date()}预测发生未来信息泄露。"
            )

        actual_load = attachment2.load_kw.loc[d].to_numpy(
            dtype=float
        )
        actual_pv = attachment2.pv_kw.loc[d].to_numpy(
            dtype=float
        )

        load_fc = forecast.load_kw.to_numpy(dtype=float)
        pv_fc = forecast.pv_kw.to_numpy(dtype=float)

        rows.append(
            {
                "date": d,
                "history_end_date": forecast.history_end_date,
                "load_mae_kw": float(
                    np.mean(np.abs(actual_load - load_fc))
                ),
                "load_rmse_kw": float(
                    np.sqrt(
                        np.mean((actual_load - load_fc) ** 2)
                    )
                ),
                "load_wmape": wmape(actual_load, load_fc),
                "pv_mae_kw": float(
                    np.mean(np.abs(actual_pv - pv_fc))
                ),
                "pv_rmse_kw": float(
                    np.sqrt(
                        np.mean((actual_pv - pv_fc) ** 2)
                    )
                ),
                "pv_wmape": wmape(actual_pv, pv_fc),
            }
        )

    daily = pd.DataFrame(rows)

    output_dir = (
        PROJECT_ROOT
        / cfg["paths"]["output_dir"]
        / "tables"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    daily_path = (
        output_dir / "q2_forecast_backtest_daily.csv"
    )
    daily.to_csv(
        daily_path,
        index=False,
        encoding="utf-8-sig",
    )

    summary = pd.DataFrame(
        [
            {
                "metric": "load_mae_kw",
                "value": daily["load_mae_kw"].mean(),
            },
            {
                "metric": "load_rmse_kw",
                "value": np.sqrt(
                    np.mean(
                        daily["load_rmse_kw"].to_numpy() ** 2
                    )
                ),
            },
            {
                "metric": "load_wmape",
                "value": daily["load_wmape"].mean(),
            },
            {
                "metric": "pv_mae_kw",
                "value": daily["pv_mae_kw"].mean(),
            },
            {
                "metric": "pv_rmse_kw",
                "value": np.sqrt(
                    np.mean(
                        daily["pv_rmse_kw"].to_numpy() ** 2
                    )
                ),
            },
            {
                "metric": "pv_wmape",
                "value": daily["pv_wmape"].mean(),
            },
        ]
    )

    summary_path = (
        output_dir / "q2_forecast_backtest_summary.csv"
    )
    summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    print("[TRAIN] 因果预测回测完成。")
    print(summary.to_string(index=False))
    print(f"[TRAIN] Daily: {daily_path}")
    print(f"[TRAIN] Summary: {summary_path}")


if __name__ == "__main__":
    main()
