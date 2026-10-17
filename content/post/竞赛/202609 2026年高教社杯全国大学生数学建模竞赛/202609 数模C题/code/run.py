# -*- coding: utf-8 -*-
"""
run.py
C题统一运行入口。

支持阶段：
    check
    q1
    q2
    q3
    q4-2
    q4-3
    figures
    all

默认使用：
    configs/default.json

所有源码从：
    src/

所有结果输出到：
    output/results/
    output/figures/
    output/tables/
    output/logs/

所有中间结果缓存到：
    models/
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any, Dict

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def load_json_config(path: str | Path) -> dict:
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        raise FileNotFoundError(f"未找到配置文件：{path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_project_path(value: str | Path) -> Path:
    p = Path(value)
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def ensure_output_dirs(cfg: dict) -> Dict[str, Path]:
    output_root = resolve_project_path(
        cfg["paths"].get("output_dir", "output")
    )
    model_root = resolve_project_path(
        cfg["paths"].get("model_dir", "models")
    )

    paths = {
        "output": output_root,
        "results": output_root / "results",
        "figures": output_root / "figures",
        "tables": output_root / "tables",
        "logs": output_root / "logs",
        "models": model_root,
    }

    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)

    return paths


def save_pickle(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)


def build_project_config(cfg: dict):
    from config import ProjectConfig

    data_dir = resolve_project_path(
        cfg["paths"].get("data_dir", "data")
    )

    return ProjectConfig(data_dir=data_dir)


def build_q2_settings(cfg: dict):
    from question2_solver import Question2Settings

    q2_cfg = dict(cfg.get("q2", {}))
    q2_cfg["solver_output"] = bool(
        cfg["run"].get("solver_output", False)
    )

    return Question2Settings(**q2_cfg)


def build_q3_settings(cfg: dict, q2_settings):
    from question3_solver import Question3Settings

    q3_cfg = cfg.get("q3", {})

    return Question3Settings(
        update_combination=tuple(
            int(x)
            for x in q3_cfg.get(
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


def load_and_check_data(project_config, paths):
    from data_checker import run_all_checks

    bundle, report = run_all_checks(
        project_config,
        raise_on_error=True,
    )

    report_path = paths["tables"] / "data_check_report.csv"
    report.to_csv(
        report_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"[CHECK] 数据检查通过："
        f"{int(report['passed'].sum())}/{len(report)}"
    )
    print(f"[CHECK] 报告：{report_path}")

    return bundle, report


def generate_figure1(bundle, cfg, paths):
    from visualize import (
        get_actual_day_load_kwh,
        get_actual_day_pv_kwh,
        get_actual_day_price,
        plot_figure1_typical_day_profiles,
    )

    date = pd.Timestamp(
        cfg["run"].get("typical_day", "2025-03-20")
    ).normalize()

    load_kwh = get_actual_day_load_kwh(
        bundle.attachment2,
        date,
    )
    pv_kwh = get_actual_day_pv_kwh(
        bundle.attachment2,
        date,
    )
    price = get_actual_day_price(
        bundle.attachment4,
        date,
    )

    path = (
        paths["figures"]
        / "fig1_typical_day_profiles.png"
    )

    fig, *_ = plot_figure1_typical_day_profiles(
        date=date,
        load_kwh=load_kwh,
        pv_kwh=pv_kwh,
        price_yuan_per_kwh=price,
        output_path=path,
    )

    import matplotlib.pyplot as plt
    plt.close(fig)

    print(f"[FIG] {path}")


def run_q1(bundle, cfg, project_config, paths, reuse_cache=False):
    cache = paths["models"] / "q1_result.pkl"

    if reuse_cache and cache.exists():
        result = load_pickle(cache)
        print(f"[Q1] 复用缓存：{cache}")
    else:
        from question1_solver import Question1Solver

        solver = Question1Solver(
            attachment1=bundle.attachment1,
            initial_energy_kwh=float(
                cfg["run"].get(
                    "initial_energy_kwh",
                    6000.0,
                )
            ),
            config=project_config,
            solver_output=bool(
                cfg["run"].get("solver_output", False)
            ),
        )
        result = solver.solve(check_legality=True)
        save_pickle(result, cache)
        print(f"[Q1] 缓存：{cache}")

    from result_writer import write_result1

    xlsx_path, report = write_result1(
        result,
        paths["results"],
        config=project_config,
    )
    report.to_csv(
        paths["tables"] / "result1_writer_check.csv",
        index=False,
        encoding="utf-8-sig",
    )

    if cfg["run"].get("generate_figures", True):
        from visualize import plot_figure2_q1_operation
        import matplotlib.pyplot as plt

        fig, *_ = plot_figure2_q1_operation(
            result,
            output_path=(
                paths["figures"]
                / "fig2_q1_operation.png"
            ),
            config=project_config,
        )
        plt.close(fig)

    print(f"[Q1] Excel：{xlsx_path}")
    return result


def run_q2(bundle, cfg, project_config, paths, q2_settings, reuse_cache=False, visualize=None):
    cache = paths["models"] / "q2_period.pkl"

    if reuse_cache and cache.exists():
        period = load_pickle(cache)
        print(f"[Q2] 复用缓存：{cache}")
    else:
        from question2_solver import Question2Solver

        solver = Question2Solver(
            attachment1=bundle.attachment1,
            attachment2=bundle.attachment2,
            settings=q2_settings,
            config=project_config,
        )

        period = solver.solve_period(
            start_date=cfg["run"]["start_date"],
            end_date=cfg["run"]["end_date"],
            initial_energy_kwh=float(
                cfg["run"].get(
                    "initial_energy_kwh",
                    6000.0,
                )
            ),
            save_from_date=cfg["run"]["save_from_date"],
            check_legality=bool(
                cfg["run"].get(
                    "check_legality",
                    True,
                )
            ),
        )

        save_pickle(period, cache)
        print(f"[Q2] 缓存：{cache}")

    from result_writer import write_result2

    writer_cfg = cfg.get("result_writer", {})
    xlsx_path, report = write_result2(
        period,
        paths["results"],
        strict_max_three_events=bool(
            writer_cfg.get(
                "strict_max_three_events",
                True,
            )
        ),
        emergency_tolerance_kwh=float(
            writer_cfg.get(
                "emergency_tolerance_kwh",
                1e-8,
            )
        ),
        config=project_config,
    )
    report.to_csv(
        paths["tables"] / "result2_writer_check.csv",
        index=False,
        encoding="utf-8-sig",
    )

    if cfg["run"].get("generate_figures", True):
        from visualize import (
            get_actual_day_load_kwh,
            get_actual_day_pv_kwh,
            plot_figure3_q2_forecast_vs_actual,
            plot_figure4_emergency_distribution,
        )
        import matplotlib.pyplot as plt

        date = pd.Timestamp(
            cfg["run"].get(
                "typical_day",
                "2025-03-20",
            )
        ).normalize()

        day = period.formal_results[date]

        fig, *_ = plot_figure3_q2_forecast_vs_actual(
            day,
            actual_load_kwh=get_actual_day_load_kwh(
                bundle.attachment2,
                date,
                config=project_config,
            ),
            actual_pv_kwh=get_actual_day_pv_kwh(
                bundle.attachment2,
                date,
                config=project_config,
            ),
            output_path=(
                paths["figures"]
                / "fig3_q2_forecast_vs_actual.png"
            ),
            config=project_config,
        )
        plt.close(fig)

        fig, *_ = plot_figure4_emergency_distribution(
            period,
            output_path=(
                paths["figures"]
                / "fig4_emergency_distribution.png"
            ),
            config=project_config,
        )
        plt.close(fig)

    print(f"[Q2] Excel：{xlsx_path}")
    return period


def run_q3(bundle, cfg, project_config, paths, q3_settings, reuse_cache=False):
    cache = paths["models"] / "q3_period.pkl"

    if reuse_cache and cache.exists():
        period = load_pickle(cache)
        print(f"[Q3] 复用缓存：{cache}")
    else:
        from question3_solver import Question3Solver

        solver = Question3Solver(
            attachment1=bundle.attachment1,
            attachment2=bundle.attachment2,
            attachment3=bundle.attachment3,
            settings=q3_settings,
            config=project_config,
        )

        period = solver.solve_period(
            start_date=cfg["run"]["start_date"],
            end_date=cfg["run"]["end_date"],
            initial_energy_kwh=float(
                cfg["run"].get(
                    "initial_energy_kwh",
                    6000.0,
                )
            ),
            save_from_date=cfg["run"]["save_from_date"],
            check_legality=bool(
                cfg["run"].get(
                    "check_legality",
                    True,
                )
            ),
        )

        save_pickle(period, cache)
        print(f"[Q3] 缓存：{cache}")

    from result_writer import write_result3

    writer_cfg = cfg.get("result_writer", {})
    xlsx_path, report = write_result3(
        period,
        paths["results"],
        strict_max_three_events=bool(
            writer_cfg.get(
                "strict_max_three_events",
                True,
            )
        ),
        emergency_tolerance_kwh=float(
            writer_cfg.get(
                "emergency_tolerance_kwh",
                1e-8,
            )
        ),
        config=project_config,
    )
    report.to_csv(
        paths["tables"] / "result3_writer_check.csv",
        index=False,
        encoding="utf-8-sig",
    )

    if cfg["run"].get("generate_figures", True):
        from visualize import (
            get_actual_day_pv_kwh,
            plot_figure5_q3_pv_update_progression,
        )
        import matplotlib.pyplot as plt

        date = pd.Timestamp(
            cfg["run"].get(
                "typical_day",
                "2025-03-20",
            )
        ).normalize()

        day = period.formal_results[date]
        fig, *_ = plot_figure5_q3_pv_update_progression(
            day,
            actual_pv_kwh=get_actual_day_pv_kwh(
                bundle.attachment2,
                date,
                config=project_config,
            ),
            output_path=(
                paths["figures"]
                / "fig5_q3_pv_update_progression.png"
            ),
            config=project_config,
        )
        plt.close(fig)

    print(f"[Q3] Excel：{xlsx_path}")
    return period


def build_q4_solver(bundle, project_config, q2_settings, q3_settings):
    from question4_solver import Question4Solver

    return Question4Solver(
        attachment1=bundle.attachment1,
        attachment2=bundle.attachment2,
        attachment3=bundle.attachment3,
        attachment4=bundle.attachment4,
        q2_settings=q2_settings,
        q3_settings=q3_settings,
        config=project_config,
    )


def run_q4_2(bundle, cfg, project_config, paths, q2_settings, q3_settings, reuse_cache=False):
    cache = paths["models"] / "q4_2_period.pkl"

    if reuse_cache and cache.exists():
        period = load_pickle(cache)
        print(f"[Q4-2] 复用缓存：{cache}")
    else:
        solver = build_q4_solver(
            bundle,
            project_config,
            q2_settings,
            q3_settings,
        )

        period = solver.solve_q4_2_period(
            start_date=cfg["run"]["start_date"],
            end_date=cfg["run"]["end_date"],
            initial_energy_kwh=float(
                cfg["run"].get(
                    "initial_energy_kwh",
                    6000.0,
                )
            ),
            save_from_date=cfg["run"]["save_from_date"],
            use_oracle=bool(
                cfg["run"].get(
                    "use_oracle_price",
                    False,
                )
            ),
            check_legality=bool(
                cfg["run"].get(
                    "check_legality",
                    True,
                )
            ),
        )
        save_pickle(period, cache)
        print(f"[Q4-2] 缓存：{cache}")

    from result_writer import write_result4_2

    writer_cfg = cfg.get("result_writer", {})
    xlsx_path, report = write_result4_2(
        period,
        paths["results"],
        strict_max_three_events=bool(
            writer_cfg.get(
                "strict_max_three_events",
                True,
            )
        ),
        emergency_tolerance_kwh=float(
            writer_cfg.get(
                "emergency_tolerance_kwh",
                1e-8,
            )
        ),
        config=project_config,
    )
    report.to_csv(
        paths["tables"] / "result4_2_writer_check.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print(f"[Q4-2] Excel：{xlsx_path}")
    return period


def run_q4_3(bundle, cfg, project_config, paths, q2_settings, q3_settings, reuse_cache=False):
    cache = paths["models"] / "q4_3_period.pkl"

    if reuse_cache and cache.exists():
        period = load_pickle(cache)
        print(f"[Q4-3] 复用缓存：{cache}")
    else:
        solver = build_q4_solver(
            bundle,
            project_config,
            q2_settings,
            q3_settings,
        )

        period = solver.solve_q4_3_period(
            start_date=cfg["run"]["start_date"],
            end_date=cfg["run"]["end_date"],
            initial_energy_kwh=float(
                cfg["run"].get(
                    "initial_energy_kwh",
                    6000.0,
                )
            ),
            save_from_date=cfg["run"]["save_from_date"],
            use_oracle=bool(
                cfg["run"].get(
                    "use_oracle_price",
                    False,
                )
            ),
            check_legality=bool(
                cfg["run"].get(
                    "check_legality",
                    True,
                )
            ),
        )
        save_pickle(period, cache)
        print(f"[Q4-3] 缓存：{cache}")

    from result_writer import write_result4_3

    writer_cfg = cfg.get("result_writer", {})
    xlsx_path, report = write_result4_3(
        period,
        paths["results"],
        strict_max_three_events=bool(
            writer_cfg.get(
                "strict_max_three_events",
                True,
            )
        ),
        emergency_tolerance_kwh=float(
            writer_cfg.get(
                "emergency_tolerance_kwh",
                1e-8,
            )
        ),
        config=project_config,
    )
    report.to_csv(
        paths["tables"] / "result4_3_writer_check.csv",
        index=False,
        encoding="utf-8-sig",
    )

    if cfg["run"].get("generate_figures", True):
        from visualize import plot_figure7_q4_dynamic_price_response
        import matplotlib.pyplot as plt

        date = pd.Timestamp(
            cfg["run"].get(
                "typical_day",
                "2025-03-20",
            )
        ).normalize()

        day = period.formal_results[date]
        fig, *_ = plot_figure7_q4_dynamic_price_response(
            day,
            output_path=(
                paths["figures"]
                / "fig7_q4_dynamic_price_response.png"
            ),
            config=project_config,
        )
        plt.close(fig)

    print(f"[Q4-3] Excel：{xlsx_path}")
    return period


def regenerate_cached_figures(bundle, cfg, project_config, paths):
    """
    从models/*.pkl复用已求解结果，不重新跑Gurobi。
    """
    import matplotlib.pyplot as plt

    generate_figure1(bundle, cfg, paths)

    q1_cache = paths["models"] / "q1_result.pkl"
    if q1_cache.exists():
        from visualize import plot_figure2_q1_operation
        result = load_pickle(q1_cache)
        fig, *_ = plot_figure2_q1_operation(
            result,
            output_path=paths["figures"] / "fig2_q1_operation.png",
            config=project_config,
        )
        plt.close(fig)

    q2_cache = paths["models"] / "q2_period.pkl"
    if q2_cache.exists():
        from visualize import (
            get_actual_day_load_kwh,
            get_actual_day_pv_kwh,
            plot_figure3_q2_forecast_vs_actual,
            plot_figure4_emergency_distribution,
        )
        period = load_pickle(q2_cache)
        date = pd.Timestamp(cfg["run"]["typical_day"]).normalize()
        day = period.formal_results[date]

        fig, *_ = plot_figure3_q2_forecast_vs_actual(
            day,
            actual_load_kwh=get_actual_day_load_kwh(
                bundle.attachment2,
                date,
                config=project_config,
            ),
            actual_pv_kwh=get_actual_day_pv_kwh(
                bundle.attachment2,
                date,
                config=project_config,
            ),
            output_path=paths["figures"] / "fig3_q2_forecast_vs_actual.png",
            config=project_config,
        )
        plt.close(fig)

        fig, *_ = plot_figure4_emergency_distribution(
            period,
            output_path=paths["figures"] / "fig4_emergency_distribution.png",
            config=project_config,
        )
        plt.close(fig)

    q3_cache = paths["models"] / "q3_period.pkl"
    if q3_cache.exists():
        from visualize import (
            get_actual_day_pv_kwh,
            plot_figure5_q3_pv_update_progression,
        )
        period = load_pickle(q3_cache)
        date = pd.Timestamp(cfg["run"]["typical_day"]).normalize()
        day = period.formal_results[date]

        fig, *_ = plot_figure5_q3_pv_update_progression(
            day,
            actual_pv_kwh=get_actual_day_pv_kwh(
                bundle.attachment2,
                date,
                config=project_config,
            ),
            output_path=paths["figures"] / "fig5_q3_pv_update_progression.png",
            config=project_config,
        )
        plt.close(fig)

    q43_cache = paths["models"] / "q4_3_period.pkl"
    if q43_cache.exists():
        from visualize import plot_figure7_q4_dynamic_price_response
        period = load_pickle(q43_cache)
        date = pd.Timestamp(cfg["run"]["typical_day"]).normalize()
        day = period.formal_results[date]

        fig, *_ = plot_figure7_q4_dynamic_price_response(
            day,
            output_path=paths["figures"] / "fig7_q4_dynamic_price_response.png",
            config=project_config,
        )
        plt.close(fig)

    print(f"[FIG] 已从缓存重建可用图像：{paths['figures']}")


def main():
    parser = argparse.ArgumentParser(
        description="2026国赛C题统一运行入口"
    )
    parser.add_argument(
        "--stage",
        choices=[
            "check",
            "q1",
            "q2",
            "q3",
            "q4-2",
            "q4-3",
            "figures",
            "all",
        ],
        default="all",
        help="运行阶段",
    )
    parser.add_argument(
        "--config",
        default="configs/default.json",
        help="配置文件路径",
    )
    parser.add_argument(
        "--reuse-cache",
        action="store_true",
        help="若models中已有pkl则复用，避免重复求解",
    )
    parser.add_argument(
        "--no-figures",
        action="store_true",
        help="本次运行不自动绘图",
    )

    args = parser.parse_args()

    cfg = load_json_config(args.config)
    if args.no_figures:
        cfg["run"]["generate_figures"] = False

    paths = ensure_output_dirs(cfg)
    project_config = build_project_config(cfg)

    bundle, _ = load_and_check_data(
        project_config,
        paths,
    )

    if (
        cfg["run"].get("generate_figures", True)
        and args.stage != "check"
    ):
        generate_figure1(bundle, cfg, paths)

    if args.stage == "check":
        return

    if args.stage == "figures":
        regenerate_cached_figures(
            bundle,
            cfg,
            project_config,
            paths,
        )
        return

    # 只有实际求解阶段才导入Gurobi相关settings。
    q2_settings = build_q2_settings(cfg)
    q3_settings = build_q3_settings(
        cfg,
        q2_settings,
    )

    if args.stage in {"q1", "all"}:
        run_q1(
            bundle,
            cfg,
            project_config,
            paths,
            reuse_cache=args.reuse_cache,
        )

    if args.stage in {"q2", "all"}:
        run_q2(
            bundle,
            cfg,
            project_config,
            paths,
            q2_settings,
            reuse_cache=args.reuse_cache,
        )

    if args.stage in {"q3", "all"}:
        run_q3(
            bundle,
            cfg,
            project_config,
            paths,
            q3_settings,
            reuse_cache=args.reuse_cache,
        )

    if args.stage in {"q4-2", "all"}:
        run_q4_2(
            bundle,
            cfg,
            project_config,
            paths,
            q2_settings,
            q3_settings,
            reuse_cache=args.reuse_cache,
        )

    if args.stage in {"q4-3", "all"}:
        run_q4_3(
            bundle,
            cfg,
            project_config,
            paths,
            q2_settings,
            q3_settings,
            reuse_cache=args.reuse_cache,
        )

    print("[DONE] 运行完成。")
    print(f"[DONE] Excel：{paths['results']}")
    print(f"[DONE] Figures：{paths['figures']}")
    print(f"[DONE] Tables：{paths['tables']}")
    print(f"[DONE] Cache：{paths['models']}")


if __name__ == "__main__":
    main()
