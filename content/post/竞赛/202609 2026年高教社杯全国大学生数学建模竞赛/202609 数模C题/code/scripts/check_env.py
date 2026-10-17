# -*- coding: utf-8 -*-
"""
scripts/check_env.py
服务器运行前环境检查。
"""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def check_import(module_name: str) -> tuple[bool, str]:
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "")
        return True, version or "OK"
    except Exception as exc:
        return False, repr(exc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-gurobi",
        action="store_true",
        help="额外检查Gurobi许可证是否能启动",
    )
    parser.add_argument(
        "--config",
        default="configs/default.json",
    )
    args = parser.parse_args()

    print("=" * 68)
    print("C题 server environment check")
    print("=" * 68)
    print("Python:", sys.version.replace("\n", " "))
    print("Platform:", platform.platform())
    print("Project:", PROJECT_ROOT)

    required = [
        "pandas",
        "numpy",
        "matplotlib",
        "openpyxl",
        "artifact_tool",
    ]

    if args.require_gurobi:
        required.append("gurobipy")

    failed = []

    for name in required:
        ok, detail = check_import(name)
        print(f"{name:<16} {'OK' if ok else 'FAIL'}  {detail}")
        if not ok:
            failed.append(name)

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    if not config_path.exists():
        failed.append("config")
        print("config           FAIL", config_path)
    else:
        with config_path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)

        data_dir = Path(cfg["paths"]["data_dir"])
        if not data_dir.is_absolute():
            data_dir = PROJECT_ROOT / data_dir

        print("config           OK  ", config_path)

        for fname in [
            "附件1.xlsx",
            "附件2.xlsx",
            "附件3.xlsx",
            "附件4.xlsx",
        ]:
            path = data_dir / fname
            ok = path.exists()
            print(
                f"{fname:<16} "
                f"{'OK' if ok else 'FAIL'}  {path}"
            )
            if not ok:
                failed.append(fname)

    if args.require_gurobi and "gurobipy" not in failed:
        try:
            import gurobipy as gp

            print("Gurobi version:", gp.gurobi.version())

            # 仅创建空环境验证许可证，不建求解模型。
            env = gp.Env(empty=True)
            env.setParam("OutputFlag", 0)
            env.start()
            env.dispose()

            print("Gurobi license: OK")
        except Exception as exc:
            failed.append("gurobi_license")
            print("Gurobi license: FAIL", repr(exc))

    # time_index是项目最关键的内部接口之一。
    try:
        from time_index import build_time_map, validate_time_map

        tm = build_time_map()
        validate_time_map(tm)
        print("time_index       OK  144 rows + key assertions")
    except Exception as exc:
        failed.append("time_index")
        print("time_index       FAIL", repr(exc))

    print("=" * 68)

    if failed:
        print("Environment check FAILED:", failed)
        raise SystemExit(1)

    print("Environment check PASSED.")


if __name__ == "__main__":
    main()
