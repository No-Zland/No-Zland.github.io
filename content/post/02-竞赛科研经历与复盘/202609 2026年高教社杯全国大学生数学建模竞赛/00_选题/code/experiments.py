# -*- coding: utf-8 -*-
"""
experiments.py
消融实验与敏感性分析入口。

目前提供：
1. q3-ablation：
   比较00_only / 00_06 / 00_06_12 / 00_06_12_18；
2. sensitivity-plot：
   从CSV的两列直接生成Figure 8。
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


def load_pickle(path):
    with Path(path).open("rb") as f:
        return pickle.load(f)


def run_q3_ablation(cfg: dict, date: str):
    from config import ProjectConfig
    from data_loader import load_all
    from question2_solver import Question2Settings
    from question3_solver import (
        Question3Settings,
        Question3Solver,
    )
    from visualize import (
        plot_figure6_strategy_cost_comparison,
    )

    data_dir = PROJECT_ROOT / cfg["paths"]["data_dir"]
    project_config = ProjectConfig(data_dir=data_dir)
    bundle = load_all(project_config)

    q2_cfg = dict(cfg.get("q2", {}))
    q2_cfg["solver_output"] = bool(
        cfg["run"].get("solver_output", False)
    )
    q2_settings = Question2Settings(**q2_cfg)

    q3_cfg = cfg.get("q3", {})
    q3_settings = Question3Settings(
        update_combination=tuple(
            q3_cfg.get(
                "update_combination",
                [0, 36, 72, 108],
            )
        ),
        rolling_horizon_intervals=int(
            q3_cfg.get("rolling_horizon_intervals", 144)
        ),
        q2_runtime_settings=q2_settings,
        solver_output=bool(
            cfg["run"].get("solver_output", False)
        ),
        enforce_charge_discharge_exclusivity=bool(
            q3_cfg.get(
                "enforce_charge_discharge_exclusivity",
                False,
            )
        ),
    )

    d = pd.Timestamp(date).normalize()

    # 为公平比较，优先使用全年主策略缓存中该日真实初始SOC。
    q3_cache = (
        PROJECT_ROOT
        / cfg["paths"]["model_dir"]
        / "q3_period.pkl"
    )

    if not q3_cache.exists():
        raise FileNotFoundError(
            "Q3消融需要先运行主策略生成models/q3_period.pkl，"
            "这样四个方案能从该日同一个真实初始SOC开始。"
        )

    baseline_period = load_pickle(q3_cache)
    if d not in baseline_period.formal_results:
        raise KeyError(f"Q3缓存中不存在日期{d.date()}。")

    initial_energy = float(
        baseline_period.formal_results[
            d
        ].initial_energy_kwh
    )

    solver = Question3Solver(
        attachment1=bundle.attachment1,
        attachment2=bundle.attachment2,
        attachment3=bundle.attachment3,
        settings=q3_settings,
        config=project_config,
    )

    results = solver.run_ablation_day(
        d,
        initial_energy_kwh=initial_energy,
        check_legality=True,
    )

    cost_df = pd.DataFrame(
        [
            {
                "strategy": name,
                "total_cost_yuan": float(
                    result.C_total_yuan
                ),
                "plan_cost_yuan": float(
                    result.C_plan_yuan
                ),
                "adjustment_cost_yuan": float(
                    result.C_adj_yuan
                ),
                "emergency_cost_yuan": float(
                    result.C_emg_yuan
                ),
            }
            for name, result in results.items()
        ]
    )

    tables = (
        PROJECT_ROOT
        / cfg["paths"]["output_dir"]
        / "tables"
    )
    figures = (
        PROJECT_ROOT
        / cfg["paths"]["output_dir"]
        / "figures"
    )
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    csv_path = (
        tables
        / f"q3_ablation_{d.strftime('%Y%m%d')}.csv"
    )
    cost_df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig",
    )

    fig_path = (
        figures
        / "fig6_strategy_cost_comparison.png"
    )
    fig, _ = plot_figure6_strategy_cost_comparison(
        cost_df,
        output_path=fig_path,
    )

    import matplotlib.pyplot as plt
    plt.close(fig)

    print(cost_df.to_string(index=False))
    print(f"[EXPERIMENT] CSV: {csv_path}")
    print(f"[EXPERIMENT] Figure 6: {fig_path}")


def run_sensitivity_plot(
    cfg: dict,
    csv_path: str,
    x_col: str,
    y_col: str,
    xlabel: str,
    ylabel: str,
):
    from visualize import plot_figure8_sensitivity_analysis

    csv_path = Path(csv_path)
    if not csv_path.is_absolute():
        csv_path = PROJECT_ROOT / csv_path

    df = pd.read_csv(csv_path)

    if x_col not in df.columns or y_col not in df.columns:
        raise ValueError(
            f"CSV必须包含{x_col}和{y_col}两列。"
        )

    figures = (
        PROJECT_ROOT
        / cfg["paths"]["output_dir"]
        / "figures"
    )
    figures.mkdir(parents=True, exist_ok=True)

    fig_path = (
        figures / "fig8_sensitivity_analysis.png"
    )

    fig, _ = plot_figure8_sensitivity_analysis(
        df[x_col].to_numpy(),
        df[y_col].to_numpy(),
        xlabel=xlabel,
        ylabel=ylabel,
        output_path=fig_path,
    )

    import matplotlib.pyplot as plt
    plt.close(fig)

    print(f"[EXPERIMENT] Figure 8: {fig_path}")


def main():
    parser = argparse.ArgumentParser(
        description="C题消融/敏感性实验"
    )
    parser.add_argument(
        "--config",
        default="configs/default.json",
    )

    sub = parser.add_subparsers(
        dest="experiment",
        required=True,
    )

    p1 = sub.add_parser("q3-ablation")
    p1.add_argument(
        "--date",
        default="2025-03-20",
    )

    p2 = sub.add_parser("sensitivity-plot")
    p2.add_argument("--csv", required=True)
    p2.add_argument("--x-col", required=True)
    p2.add_argument("--y-col", required=True)
    p2.add_argument("--xlabel", required=True)
    p2.add_argument("--ylabel", required=True)

    args = parser.parse_args()
    cfg = load_cfg(args.config)

    if args.experiment == "q3-ablation":
        run_q3_ablation(cfg, args.date)
    elif args.experiment == "sensitivity-plot":
        run_sensitivity_plot(
            cfg,
            args.csv,
            args.x_col,
            args.y_col,
            args.xlabel,
            args.ylabel,
        )


if __name__ == "__main__":
    main()
