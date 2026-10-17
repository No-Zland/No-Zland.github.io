# -*- coding: utf-8 -*-
"""
evaluate.py
结果汇总、合法性报告汇总与费用统计。

优先读取 models/*.pkl 缓存，不重新求解Gurobi。
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def load_cfg(path):
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def summarize_period(name: str, period) -> dict:
    formal = period.formal_results

    if name == "q2":
        values = [
            float(day.total_cost_yuan)
            for day in formal.values()
        ]
        emergency = [
            float(day.emergency_cost_yuan)
            for day in formal.values()
        ]
    elif name == "q3":
        values = [
            float(day.C_total_yuan)
            for day in formal.values()
        ]
        emergency = [
            float(day.C_emg_yuan)
            for day in formal.values()
        ]
    elif name in {"q4-2", "q4-3"}:
        values = [
            float(day.C_total_yuan)
            for day in formal.values()
        ]
        emergency = [
            float(day.C_emg_yuan)
            for day in formal.values()
        ]
    else:
        raise ValueError(name)

    return {
        "model": name,
        "formal_days": len(formal),
        "total_cost_yuan": sum(values),
        "mean_daily_cost_yuan": (
            sum(values) / len(values)
            if values
            else float("nan")
        ),
        "total_emergency_cost_yuan": sum(emergency),
        "final_energy_kwh": float(
            period.final_energy_kwh
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="汇总已求解的C题结果"
    )
    parser.add_argument(
        "--config",
        default="configs/default.json",
    )
    args = parser.parse_args()

    cfg = load_cfg(args.config)

    from config import ProjectConfig
    from data_checker import run_all_checks

    data_dir = PROJECT_ROOT / cfg["paths"]["data_dir"]
    project_config = ProjectConfig(data_dir=data_dir)

    _, data_report = run_all_checks(
        project_config,
        raise_on_error=True,
    )

    output_tables = (
        PROJECT_ROOT
        / cfg["paths"]["output_dir"]
        / "tables"
    )
    output_tables.mkdir(parents=True, exist_ok=True)

    data_report.to_csv(
        output_tables / "evaluate_data_check.csv",
        index=False,
        encoding="utf-8-sig",
    )

    model_dir = PROJECT_ROOT / cfg["paths"]["model_dir"]

    cache_map = {
        "q2": model_dir / "q2_period.pkl",
        "q3": model_dir / "q3_period.pkl",
        "q4-2": model_dir / "q4_2_period.pkl",
        "q4-3": model_dir / "q4_3_period.pkl",
    }

    rows = []

    q1_path = model_dir / "q1_result.pkl"
    if q1_path.exists():
        q1 = load_pickle(q1_path)
        rows.append(
            {
                "model": "q1",
                "formal_days": 1,
                "total_cost_yuan": float(
                    q1.total_cost_yuan
                ),
                "mean_daily_cost_yuan": float(
                    q1.total_cost_yuan
                ),
                "total_emergency_cost_yuan": 0.0,
                "final_energy_kwh": float(
                    q1.energy_kwh.loc[144]
                ),
            }
        )

    for name, path in cache_map.items():
        if path.exists():
            period = load_pickle(path)
            rows.append(
                summarize_period(name, period)
            )

    summary = pd.DataFrame(rows)

    summary_path = output_tables / "model_cost_summary.csv"
    summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    print("[EVALUATE] 数据检查通过。")
    if summary.empty:
        print(
            "[EVALUATE] 尚未找到models/*.pkl结果缓存，"
            "请先运行run.py。"
        )
    else:
        print(summary.to_string(index=False))
        print(f"[EVALUATE] Summary: {summary_path}")


if __name__ == "__main__":
    main()
