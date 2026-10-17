# -*- coding: utf-8 -*-
"""
question3_solver.py
问题3：0/6/12/18滚动购电调整 + 附件3光伏预测 + 因果实时补救。

严格继承前文工程：
- config.py / time_index.py / data_loader.py
- forecast_model.py
- scenario_tree.py
- question2_solver.py 的条件场景实时补救求解器
- forecast_parser.py
- rolling_scheduler.py

不重新定义前文时间映射、变量单位或问题2变量命名。

问题3核心规则
-------------
1. 0:00：
       k>=0可优化，形成唯一原始计划G0。
2. 6:00：
       冻结k<36，只允许更新k>=36。
3. 12:00：
       冻结k<72，只允许更新k>=72。
4. 18:00：
       冻结k<108，只允许更新k>=108。
5. 每次更新使用真实当前SOC E_act[r]。
6. 正常购电更新只用：
       当前/过去真实状态 + 当前已发布预测 + 历史误差分布。
   禁止读取未来真实负荷/光伏。
7. 每10分钟在tau_k先基于0..k-1真实历史和E_k决定储能动作；
   current_k真实负荷/PV在区间结束后才用于紧急购电、弃光和计划富余；
   不允许current_k实际值参与current_k储能动作。
8. 18:00发布版本可以把次日0:00~18:00作为24小时预览窗口，
   只用于评价当前SOC的未来价值；次日预览购电变量全部丢弃，
   绝不提前写成次日正式计划。
9. 结算严格调用 rolling_scheduler.settle_question3_cost()：
       C_reg = sum c[GF + 0.5(dG+ + dG-)]
       C_adj = sum c[1.5dG+ - 0.5dG-]
       C_total = C_reg + C_emg
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Sequence

import numpy as np
import pandas as pd

try:
    import gurobipy as gp
    from gurobipy import GRB
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "question3_solver.py 依赖 gurobipy。"
        "请在已安装并配置 Gurobi 的环境中运行。"
    ) from exc

from config import DEFAULT_CONFIG, ProjectConfig
from data_loader import (
    Attachment1Data,
    Attachment2Data,
    Attachment3Data,
)
from forecast_model import (
    AvailableHistory,
    DayAheadForecast,
    ResidualLibrary,
    build_available_history,
    build_causal_residual_library,
    build_q2_day_ahead_forecast,
)
from forecast_parser import (
    ParsedForecastVersion,
    extract_current_day_model_kwh,
    parse_forecast_version,
)
from model_base import (
    ETA_C,
    ETA_D,
    E_MIN_KWH,
    E_MAX_KWH,
    P_BAT_MAX_KW,
)
from question2_solver import (
    Question2Settings,
    _solve_tree_optimization,
    settle_realized_interval_after_storage,
)
from rolling_scheduler import (
    ABLATION_UPDATE_COMBINATIONS,
    SETTLEMENT_SELF_TEST_REPORT,
    UPDATE_K,
    RollingPlanBook,
    SettlementResult,
    settle_question3_cost,
    validate_update_k,
)
from scenario_tree import (
    build_conditional_trajectory_set,
    build_nonanticipative_tree,
    reduce_trajectory_set,
)
from time_index import build_time_map, validate_time_map


# ============================================================================
# 配置 / 结果
# ============================================================================


@dataclass(frozen=True)
class Question3Settings:
    """问题3滚动优化设置。"""

    # 默认使用全部4次更新
    update_combination: tuple[int, ...] = (
        0,
        36,
        72,
        108,
    )

    # 每次更新使用24h滚动窗口
    rolling_horizon_intervals: int = 144

    # 实时因果补救沿用Q2条件场景
    q2_runtime_settings: Question2Settings = field(
        default_factory=Question2Settings
    )

    solver_output: bool = False
    enforce_charge_discharge_exclusivity: bool = False

    def validate(
        self,
        config: ProjectConfig = DEFAULT_CONFIG,
    ) -> None:
        if 0 not in self.update_combination:
            raise ValueError("问题3更新组合必须包含0:00。")

        if tuple(sorted(set(self.update_combination))) != (
            self.update_combination
        ):
            raise ValueError(
                "update_combination必须升序且不得重复。"
            )

        for r in self.update_combination:
            validate_update_k(r, config=config)

        if self.rolling_horizon_intervals != 144:
            raise ValueError(
                "附件3每次发布覆盖24h，本实现固定144个10分钟区间。"
            )

        self.q2_runtime_settings.validate()


@dataclass
class MPCUpdateRecord:
    """一次0/6/12/18更新记录。"""

    r: int
    issue_datetime: pd.Timestamp
    current_energy_kwh: float

    current_observed_pv_kw: float

    formal_future_plan_kwh: pd.Series

    # 只用于SOC未来价值，不进入正式次日计划。
    preview_purchase_kwh: pd.DataFrame

    objective_value_yuan: float

    parser_audit: pd.DataFrame


@dataclass
class Question3DayResult:
    """问题3单日结果。"""

    date: pd.Timestamp
    update_combination: tuple[int, ...]

    initial_energy_kwh: float
    end_energy_kwh: float

    # G0 / GF
    original_plan_kwh: pd.Series
    final_effective_plan_kwh: pd.Series

    # 每次更新后的计划版本
    plan_versions: Dict[int, pd.Series]
    update_records: Dict[int, MPCUpdateRecord]

    # 实际因果运行
    actual_charge_kwh: pd.Series
    actual_discharge_kwh: pd.Series
    actual_emergency_kwh: pd.Series
    actual_curtailment_kwh: pd.Series
    actual_surplus_kwh: pd.Series
    energy_kwh: pd.Series

    # 结算
    dG_plus_kwh: pd.Series
    dG_minus_kwh: pd.Series
    C_plan_yuan: float
    C_reg_yuan: float
    C_adj_yuan: float
    C_emg_yuan: float
    C_total_yuan: float

    # 因果/冻结/结算审计
    runtime_causality_report: pd.DataFrame
    update_freeze_report: pd.DataFrame
    settlement_test_report: pd.DataFrame
    legality_report: pd.DataFrame


@dataclass
class Question3PeriodResult:
    formal_results: Dict[pd.Timestamp, Question3DayResult]
    cross_day_report: pd.DataFrame
    warmup_end_energy_kwh: Optional[float]
    final_energy_kwh: float


# ============================================================================
# 数据准备
# ============================================================================


def _normalize_date(value) -> pd.Timestamp:
    return pd.Timestamp(value).normalize()


def _prepare_fixed_price(
    attachment1: Attachment1Data,
    config: ProjectConfig,
) -> pd.Series:
    """严格按attachment1.aligned中的k读取固定日内电价。"""
    aligned = attachment1.aligned
    expected = list(range(config.intervals_per_day))

    if aligned["k"].astype(int).tolist() != expected:
        raise ValueError(
            "attachment1.aligned必须严格使用k=0~143。"
        )

    price = pd.to_numeric(
        aligned["price_yuan_per_kwh"],
        errors="raise",
    ).astype(float)
    price.index = expected
    price.name = "price_yuan_per_kwh"

    if price.isna().any():
        raise ValueError("电价存在缺失值。")

    return price


def _causal_preview_load_for_next_day(
    history: AvailableHistory,
    *,
    current_date: pd.Timestamp,
    config: ProjectConfig,
) -> pd.Series:
    """
    为24h MPC跨日预览构造次日负荷预测。

    重要：
    只能使用 current_date 0:00以前的 AvailableHistory。
    绝不调用 target=next_day 的普通预测函数，否则可能读入current_date实际值。

    规则：
    - next_day对应的上周同星期日为 current_date-6；
    - 若该日已存在于历史，则使用其同k负荷；
    - 否则使用已有历史同k均值；
    - 无历史则返回0暖启动。
    """
    expected = list(range(config.intervals_per_day))

    if history.history_days == 0:
        return pd.Series(
            np.zeros(config.intervals_per_day),
            index=expected,
            dtype=float,
            name="next_day_preview_load_kwh",
        )

    next_day = current_date + pd.Timedelta(days=1)
    lag7_for_next = next_day - pd.Timedelta(days=7)

    if lag7_for_next in history.load_kw.index:
        load_kw = history.load_kw.loc[
            lag7_for_next
        ].astype(float)
    else:
        load_kw = history.load_kw.mean(axis=0).astype(float)

    load_kw.index = expected

    dt_hours = config.dt_minutes / 60.0
    result = load_kw.clip(lower=0.0) * dt_hours
    result.name = "next_day_preview_load_kwh"
    return result


def _current_observed_pv_kw(
    attachment2: Attachment2Data,
    date: pd.Timestamp,
    r: int,
    *,
    config: ProjectConfig,
) -> float:
    """
    生成附件3线性插值所需F0。

    r>0:
        使用刚刚完成的最后一个10min实际区间 k=r-1 的平均功率，
        作为发布边界时刻当前观测功率的可复现代理。
        例如6:00使用k=35，即附件2右端点6:00。

    r=0:
        使用前一自然日k=143（右端点0:00+1）的已实现功率；
        若不存在前一日（2025-01-01），使用0。

    从不读取当前未来区间k=r的实际光伏。
    """
    validate_update_k(r, config=config)

    if r > 0:
        return max(
            0.0,
            float(attachment2.pv_kw.at[date, r - 1]),
        )

    previous_date = date - pd.Timedelta(days=1)
    if previous_date in attachment2.pv_kw.index:
        return max(
            0.0,
            float(attachment2.pv_kw.at[previous_date, 143]),
        )

    return 0.0


def _build_effective_q3_forecast(
    base_forecast: DayAheadForecast,
    effective_pv_kwh: pd.Series,
) -> DayAheadForecast:
    """
    仅替换Q3当前已发布版本对未来的PV预测，
    负荷日前预测和历史信息边界保持Q2结构。
    """
    expected = list(base_forecast.load_kwh.index)

    if list(effective_pv_kwh.index) != expected:
        raise ValueError(
            "effective_pv_kwh必须覆盖当天k=0~143。"
        )

    dt_hours = 1.0 / 6.0
    pv_kw = effective_pv_kwh / dt_hours
    pv_kw.name = "pv_forecast_kw"

    return DayAheadForecast(
        target_date=base_forecast.target_date,
        load_kw=base_forecast.load_kw.copy(),
        pv_kw=pv_kw,
        load_kwh=base_forecast.load_kwh.copy(),
        pv_kwh=effective_pv_kwh.copy(),
        history_days=base_forecast.history_days,
        history_end_date=base_forecast.history_end_date,
        load_method=base_forecast.load_method,
        pv_method="attachment3_latest_released_version",
    )


# ============================================================================
# 24小时滚动计划优化
# ============================================================================


def _solve_deterministic_mpc_update(
    *,
    date: pd.Timestamp,
    r: int,
    current_energy_kwh: float,
    original_plan_kwh: Optional[pd.Series],
    load_today_kwh: pd.Series,
    load_next_day_preview_kwh: pd.Series,
    parsed_pv: ParsedForecastVersion,
    price_provider: Callable[
        [pd.Timestamp, int, pd.Timestamp], float
    ],
    config: ProjectConfig,
    enforce_charge_discharge_exclusivity: bool,
    solver_output: bool,
) -> tuple[pd.Series, pd.DataFrame, float]:
    """
    当前更新时刻的24h确定性MPC。

    current-day区间：
        q_buy为正式购电计划变量。

    next-day预览区间：
        q_buy_preview只用于评价当前SOC未来价值，
        求解后全部丢弃，不写入次日正式计划。

    price_provider(abs_date, model_k, decision_datetime):
        返回当前决策时刻允许使用的预测/已知价格。
        Q3固定电价时忽略decision_datetime；
        Q4-3可传入严格因果动态价格预测。
    """
    validate_update_k(r, config=config)

    issue_datetime = (
        date
        + pd.Timedelta(
            minutes=r * config.dt_minutes
        )
    )

    frame = parsed_pv.interval_forecast
    if len(frame) != 144:
        raise ValueError("附件3发布版本必须恰好144个10分钟区间。")

    if not (
        E_MIN_KWH
        <= current_energy_kwh
        <= E_MAX_KWH
    ):
        raise ValueError("当前真实SOC超出安全区间。")

    horizon = list(range(144))
    dt_hours = config.dt_minutes / 60.0
    q_max = P_BAT_MAX_KW * dt_hours

    model = gp.Model(
        f"q3_mpc_{date.date()}_r{r}"
    )
    model.Params.OutputFlag = 1 if solver_output else 0

    q_buy_h = model.addVars(
        horizon,
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="q_buy",
    )
    q_ch = model.addVars(
        horizon,
        lb=0.0,
        ub=q_max,
        vtype=GRB.CONTINUOUS,
        name="q_ch",
    )
    q_dis = model.addVars(
        horizon,
        lb=0.0,
        ub=q_max,
        vtype=GRB.CONTINUOUS,
        name="q_dis",
    )
    q_emg = model.addVars(
        horizon,
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="q_emg",
    )
    q_curt = model.addVars(
        horizon,
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="q_curt",
    )
    q_sur = model.addVars(
        horizon,
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="q_sur",
    )
    E = model.addVars(
        range(145),
        lb=E_MIN_KWH,
        ub=E_MAX_KWH,
        vtype=GRB.CONTINUOUS,
        name="E",
    )

    z = None
    if enforce_charge_discharge_exclusivity:
        z = model.addVars(
            horizon,
            vtype=GRB.BINARY,
            name="z",
        )

    model.addConstr(
        E[0] == float(current_energy_kwh),
        name="current_real_energy",
    )

    # 记录每个h对应绝对物理时间/自然日k
    mapping_rows = []
    current_day_h = []
    preview_h = []

    objective_terms = []

    dplus = {}
    dminus = {}

    for h in horizon:
        interval_start = pd.Timestamp(
            frame.iloc[h][
                "interval_start_datetime"
            ]
        )
        interval_end = pd.Timestamp(
            frame.iloc[h][
                "interval_end_datetime"
            ]
        )

        abs_date = interval_start.normalize()
        minute_of_day = (
            interval_start.hour * 60
            + interval_start.minute
        )
        model_k = minute_of_day // config.dt_minutes

        if not (0 <= model_k < 144):
            raise AssertionError("预览区间model_k异常。")

        if abs_date == date:
            if model_k < r:
                raise AssertionError(
                    "24h MPC窗口不应包含已执行当前日过去区间。"
                )
            load_kwh = float(load_today_kwh.loc[model_k])
            is_formal = True
            current_day_h.append((h, model_k))
        else:
            # 当前附件3版本最多跨到次日。
            if abs_date != date + pd.Timedelta(days=1):
                raise AssertionError(
                    "当前24h附件3窗口出现超过次日的区间。"
                )

            load_kwh = float(
                load_next_day_preview_kwh.loc[model_k]
            )
            is_formal = False
            preview_h.append((h, model_k))

        pv_kwh = float(
            frame.iloc[h]["forecast_kwh"]
        )

        price = float(
            price_provider(
                abs_date,
                int(model_k),
                issue_datetime,
            )
        )

        if price < 0:
            raise ValueError("当前实现要求预测/已知电价非负。")

        # 物理能量平衡
        model.addConstr(
            q_buy_h[h]
            + q_emg[h]
            + pv_kwh
            + q_dis[h]
            ==
            load_kwh
            + q_ch[h]
            + q_curt[h]
            + q_sur[h],
            name=f"energy_balance[{h}]",
        )

        model.addConstr(
            q_curt[h] <= pv_kwh,
            name=f"curtailment_upper[{h}]",
        )

        model.addConstr(
            E[h + 1]
            ==
            E[h]
            + ETA_C * q_ch[h]
            - q_dis[h] / ETA_D,
            name=f"storage_transition[{h}]",
        )

        if z is not None:
            model.addConstr(
                q_ch[h] <= q_max * z[h],
                name=f"charge_exclusive[{h}]",
            )
            model.addConstr(
                q_dis[h] <= q_max * (1 - z[h]),
                name=f"discharge_exclusive[{h}]",
            )

        if is_formal and r > 0:
            if original_plan_kwh is None:
                raise ValueError(
                    "r>0调整时必须提供0:00原始计划G0。"
                )

            # dG_plus / dG_minus
            dplus[h] = model.addVar(
                lb=0.0,
                vtype=GRB.CONTINUOUS,
                name=f"dG_plus[{model_k}]",
            )
            dminus[h] = model.addVar(
                lb=0.0,
                vtype=GRB.CONTINUOUS,
                name=f"dG_minus[{model_k}]",
            )

            model.addConstr(
                q_buy_h[h]
                - float(original_plan_kwh.loc[model_k])
                ==
                dplus[h] - dminus[h],
                name=f"adjustment_definition[{model_k}]",
            )

            # 正常购电及调整直接结算形式：
            # c * [GF + 0.5(dG+ + dG-)]
            objective_terms.append(
                price
                * (
                    q_buy_h[h]
                    + 0.5 * (dplus[h] + dminus[h])
                )
            )
        else:
            # r=0当前日正式计划，或跨日preview：
            # 只按正常购电成本评价。
            objective_terms.append(
                price * q_buy_h[h]
            )

        # forecast shortage emergency
        objective_terms.append(
            5.0 * price * q_emg[h]
        )

        mapping_rows.append(
            {
                "h": h,
                "interval_start_datetime": interval_start,
                "interval_end_datetime": interval_end,
                "date": abs_date,
                "model_k": int(model_k),
                "is_formal_current_day": is_formal,
                "price_used_yuan_per_kwh": price,
            }
        )

    model.setObjective(
        gp.quicksum(objective_terms),
        GRB.MINIMIZE,
    )
    model.optimize()

    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(
            f"问题3 r={r} MPC未获得最优解，"
            f"Gurobi Status={model.Status}"
        )

    formal = pd.Series(
        {
            model_k: float(q_buy_h[h].X)
            for h, model_k in current_day_h
        },
        dtype=float,
        name="formal_future_plan_kwh",
    )
    formal = formal.sort_index()

    expected_formal_index = list(range(r, 144))
    if list(formal.index) != expected_formal_index:
        raise AssertionError(
            f"r={r}正式计划必须只覆盖k={r}~143。"
        )

    preview_rows = []
    for h, model_k in preview_h:
        map_row = mapping_rows[h]
        preview_rows.append(
            {
                "h": h,
                "interval_start_datetime": (
                    map_row["interval_start_datetime"]
                ),
                "interval_end_datetime": (
                    map_row["interval_end_datetime"]
                ),
                "model_k": model_k,
                "preview_purchase_kwh": float(
                    q_buy_h[h].X
                ),
                "preview_energy_start_kwh": float(
                    E[h].X
                ),
                "preview_energy_end_kwh": float(
                    E[h + 1].X
                ),
            }
        )

    preview = pd.DataFrame(preview_rows)

    return formal, preview, float(model.ObjVal)


# ============================================================================
# 合法性检查
# ============================================================================


def check_question3_day_result_legality(
    *,
    result: Question3DayResult,
    attachment2: Attachment2Data,
    price_yuan_per_kwh: pd.Series,
    config: ProjectConfig = DEFAULT_CONFIG,
    tolerance_kwh: float = 1e-5,
    tolerance_yuan: float = 1e-5,
) -> pd.DataFrame:
    """问题3事后合法性审计；只在一天执行结束后读取完整真实轨迹。"""
    d = result.date
    k_all = list(range(144))
    dt_hours = config.dt_minutes / 60.0

    actual_load = (
        attachment2.load_kw.loc[d].astype(float)
        * dt_hours
    )
    actual_pv = (
        attachment2.pv_kw.loc[d].astype(float)
        * dt_hours
    )
    actual_load.index = k_all
    actual_pv.index = k_all

    rows = []

    def add(
        item: str,
        passed: bool,
        detail: str,
        residual: Optional[float] = None,
    ):
        rows.append(
            {
                "item": item,
                "passed": bool(passed),
                "max_residual": residual,
                "detail": detail,
            }
        )

    q_buy = result.final_effective_plan_kwh
    q_ch = result.actual_charge_kwh
    q_dis = result.actual_discharge_kwh
    q_emg = result.actual_emergency_kwh
    q_curt = result.actual_curtailment_kwh
    q_sur = result.actual_surplus_kwh
    E = result.energy_kwh

    balance = (
        q_buy + q_emg + actual_pv + q_dis
        - actual_load - q_ch - q_curt - q_sur
    )
    balance_max = float(balance.abs().max())
    add(
        "actual_energy_balance",
        balance_max <= tolerance_kwh,
        f"最大绝对残差={balance_max:.12g} kWh。",
        balance_max,
    )

    transition = pd.Series(
        {
            k: (
                E.loc[k + 1]
                - E.loc[k]
                - ETA_C * q_ch.loc[k]
                + q_dis.loc[k] / ETA_D
            )
            for k in k_all
        },
        dtype=float,
    )
    transition_max = float(transition.abs().max())
    add(
        "actual_storage_transition",
        transition_max <= tolerance_kwh,
        f"最大绝对残差={transition_max:.12g} kWh。",
        transition_max,
    )

    lower = float((E_MIN_KWH - E).clip(lower=0).max())
    upper = float((E - E_MAX_KWH).clip(lower=0).max())
    add(
        "energy_bounds",
        max(lower, upper) <= tolerance_kwh,
        f"lower={lower:.12g}; upper={upper:.12g}",
        max(lower, upper),
    )

    # 冻结检查
    freeze_ok = bool(
        result.update_freeze_report["passed"].all()
    )
    add(
        "past_frozen_at_all_updates",
        freeze_ok,
        "每次r只允许修改k>=r。",
    )

    runtime = result.runtime_causality_report
    causal_ok = bool(
        runtime["future_actual_used"].eq(False).all()
        and runtime["max_observed_k"].astype(int)
        .eq(runtime["k"].astype(int) - 1)
        .all()
        and runtime["observed_points"].astype(int)
        .eq(runtime["k"].astype(int))
        .all()
        and runtime[
            "current_actual_used_for_storage_decision"
        ].eq(False).all()
        and runtime[
            "current_actual_used_only_for_expost_balance"
        ].eq(True).all()
        and runtime["single_current_root"].eq(True).all()
        and runtime["conditional_tree_passed"].eq(True).all()
        and (
            runtime["expost_balance_residual_kwh"]
            .abs()
            .max()
            <= tolerance_kwh
        )
    )
    add(
        "runtime_no_future_actual",
        causal_ok,
        (
            "tau_k储能决策只读取0..k-1真实前缀；"
            "current_k实际值仅在储能动作确定后用于事后平衡。"
        ),
    )

    # 费用重算
    settlement = settle_question3_cost(
        G0_kwh=result.original_plan_kwh,
        GF_kwh=result.final_effective_plan_kwh,
        price_yuan_per_kwh=price_yuan_per_kwh,
        G_emg_kwh=result.actual_emergency_kwh,
        config=config,
    )

    costs = [
        (
            "C_plan",
            result.C_plan_yuan,
            settlement.C_plan_yuan,
        ),
        (
            "C_reg",
            result.C_reg_yuan,
            settlement.C_reg_yuan,
        ),
        (
            "C_adj",
            result.C_adj_yuan,
            settlement.C_adj_yuan,
        ),
        (
            "C_emg",
            result.C_emg_yuan,
            settlement.C_emg_yuan,
        ),
        (
            "C_total",
            result.C_total_yuan,
            settlement.C_total_yuan,
        ),
    ]

    for name, stored, recalculated in costs:
        residual = abs(float(stored) - float(recalculated))
        add(
            name,
            residual <= tolerance_yuan,
            (
                f"stored={stored:.12g}; "
                f"recalculated={recalculated:.12g}"
            ),
            residual,
        )

    add(
        "settlement_identity",
        settlement.identity_residual_yuan
        <= tolerance_yuan,
        (
            "C_reg必须等于C_plan+C_adj；"
            f"残差={settlement.identity_residual_yuan:.12g}"
        ),
        settlement.identity_residual_yuan,
    )

    return pd.DataFrame(rows)


# ============================================================================
# Question3Solver
# ============================================================================


class Question3Solver:
    """
    问题3求解器。

    price_provider为可选扩展点：
    - 默认Q3使用附件1固定日内价格；
    - Q4-3可传入严格因果动态价格预测provider，
      从而复用整个Question3Solver而不复制代码。
    """

    def __init__(
        self,
        *,
        attachment1: Attachment1Data,
        attachment2: Attachment2Data,
        attachment3: Attachment3Data,
        settings: Question3Settings = Question3Settings(),
        config: ProjectConfig = DEFAULT_CONFIG,
        price_provider: Optional[
            Callable[
                [pd.Timestamp, int, pd.Timestamp],
                float,
            ]
        ] = None,
    ) -> None:
        settings.validate(config)

        self.attachment1 = attachment1
        self.attachment2 = attachment2
        self.attachment3 = attachment3
        self.settings = settings
        self.config = config

        self.time_map = build_time_map(config)
        validate_time_map(self.time_map, config)

        self.fixed_price = _prepare_fixed_price(
            attachment1,
            config,
        )

        if price_provider is None:
            self.price_provider = self._fixed_price_provider
        else:
            self.price_provider = price_provider

        self.dt_hours = config.dt_minutes / 60.0

    def _fixed_price_provider(
        self,
        abs_date: pd.Timestamp,
        model_k: int,
        decision_datetime: pd.Timestamp,
    ) -> float:
        del abs_date, decision_datetime
        return float(self.fixed_price.loc[model_k])

    def _price_series_for_decision(
        self,
        date: pd.Timestamp,
        decision_k: int,
    ) -> pd.Series:
        """
        为Q2条件实时补救构造当前决策时刻可使用的144价格向量。

        Q3固定价格下等于附件1价格；
        Q4-3通过price_provider得到严格因果预测价格。
        """
        decision_datetime = (
            date
            + pd.Timedelta(
                minutes=decision_k * self.config.dt_minutes
            )
        )

        values = {}
        for k in range(144):
            # 当前日每个model_k的定价预测接口；
            # provider必须自行保证动态价格因果边界。
            values[k] = float(
                self.price_provider(
                    date,
                    k,
                    decision_datetime,
                )
            )

        result = pd.Series(
            values,
            dtype=float,
            name="price_yuan_per_kwh",
        )

        if (result < 0).any():
            raise ValueError("价格预测不能为负。")

        return result

    def _check_date_exists(
        self,
        date,
    ) -> pd.Timestamp:
        d = _normalize_date(date)
        if d not in self.attachment2.load_kw.index:
            raise KeyError(f"附件2缺少日期{d.date()}。")
        return d

    def _build_parser_version(
        self,
        date: pd.Timestamp,
        r: int,
    ) -> tuple[ParsedForecastVersion, float]:
        issue = (
            date
            + pd.Timedelta(
                minutes=r * self.config.dt_minutes
            )
        )

        F0 = _current_observed_pv_kw(
            self.attachment2,
            date,
            r,
            config=self.config,
        )

        parsed = parse_forecast_version(
            self.attachment3,
            issue,
            current_observed_pv_kw=F0,
            config=self.config,
        )

        return parsed, F0


    def _runtime_recourse_step(
        self,
        *,
        date: pd.Timestamp,
        k: int,
        current_energy_kwh: float,
        observed_load_kwh: pd.Series,
        observed_pv_kwh: pd.Series,
        effective_forecast: DayAheadForecast,
        residual_library: ResidualLibrary,
        fixed_plan_kwh: pd.Series,
    ) -> tuple[
        float,
        float,
        float,
        float,
        float,
        pd.DataFrame,
    ]:
        """
        复用问题2严格因果条件场景树和tree optimizer。

        在tau_k调用本函数时：
        - observed_load_kwh / observed_pv_kwh只能包含0..k-1；
        - current_k真实负荷/PV尚未知；
        - 当前真实SOC E_k已知；
        - 正常购电计划固定为最近一次滚动更新后的生效计划。

        本函数只真正执行根节点的q_ch/q_dis。
        根节点预测出的q_emg/q_curt/q_sur只作为优化内部预估，
        不能当作真实执行量；实际值必须在current_k真实负荷/PV实现后
        由settle_realized_interval_after_storage()计算。
        """
        runtime_settings = (
            self.settings.q2_runtime_settings
        )

        expected_prefix = list(range(k))
        if list(observed_load_kwh.index) != expected_prefix:
            raise ValueError(
                f"k={k}储能决策前真实负荷前缀必须严格为0..{k-1}。"
            )
        if list(observed_pv_kwh.index) != expected_prefix:
            raise ValueError(
                f"k={k}储能决策前真实光伏前缀必须严格为0..{k-1}。"
            )

        bootstrap = build_conditional_trajectory_set(
            effective_forecast,
            residual_library,
            observed_load_kwh=observed_load_kwh.copy(),
            observed_pv_kwh=observed_pv_kwh.copy(),
            current_k=k,
            n_bootstrap=(
                runtime_settings
                .rolling_bootstrap_scenarios
            ),
            conditioning_pool=(
                runtime_settings.conditioning_pool
            ),
            random_state=(
                runtime_settings.random_seed
                + int(date.dayofyear) * 1000
                + k
            ),
            config=self.config,
        )

        reduced = reduce_trajectory_set(
            bootstrap,
            n_representatives=(
                runtime_settings
                .rolling_reduced_scenarios
            ),
        )

        tree = build_nonanticipative_tree(
            reduced,
            branch_every=(
                runtime_settings.rolling_branch_every
            ),
            max_branch=(
                runtime_settings.rolling_max_branch
            ),
            force_single_root=True,
        )

        check = tree.validate_nonanticipativity()
        if not check["passed"].all():
            raise AssertionError(
                "问题3实时条件树未通过非预见性检查。"
            )

        root_ids = tree.root_node_ids()
        if len(root_ids) != 1:
            raise AssertionError(
                "问题3实时补救当前stage必须唯一根节点。"
            )

        price_for_runtime = (
            self._price_series_for_decision(
                date,
                k,
            )
        )

        solution = _solve_tree_optimization(
            tree=tree,
            price_yuan_per_kwh=price_for_runtime,
            initial_energy_kwh=current_energy_kwh,
            config=self.config,
            settings=runtime_settings,
            q_buy_fixed_kwh=fixed_plan_kwh,
            model_name=f"q3_recourse_{date.date()}_k{k}",
        )

        root_id = int(root_ids[0])
        row = solution.node_policy.loc[
            solution.node_policy["node_id"] == root_id
        ]

        if len(row) != 1:
            raise AssertionError("当前根节点动作不唯一。")

        row = row.iloc[0]

        audit = pd.DataFrame(
            [
                {
                    "k": k,
                    "max_observed_k": k - 1,
                    "observed_points": k,
                    "future_actual_used": False,
                    "current_actual_used_for_storage_decision": False,
                    "current_actual_used_only_for_expost_balance": True,
                    "single_current_root": True,
                    "conditional_tree_passed": True,
                    "current_root_id": root_id,
                    "current_root_expected_load_kwh": float(
                        row["load_kwh"]
                    ),
                    "current_root_expected_pv_kwh": float(
                        row["pv_kwh"]
                    ),
                    "predicted_root_q_emg_kwh_not_executed": float(
                        row["q_emg_kwh"]
                    ),
                }
            ]
        )

        return (
            float(row["q_ch_kwh"]),
            float(row["q_dis_kwh"]),
            float(row["q_emg_kwh"]),
            float(row["q_curt_kwh"]),
            float(row["q_sur_kwh"]),
            audit,
        )

    def solve_day(
        self,
        date,
        *,
        initial_energy_kwh: float,
        update_combination: Optional[
            tuple[int, ...]
        ] = None,
        check_legality: bool = True,
    ) -> Question3DayResult:
        """
        求解并真实因果执行一天。
        """
        d = self._check_date_exists(date)

        updates = (
            self.settings.update_combination
            if update_combination is None
            else update_combination
        )

        local_settings = Question3Settings(
            update_combination=updates,
            rolling_horizon_intervals=(
                self.settings.rolling_horizon_intervals
            ),
            q2_runtime_settings=(
                self.settings.q2_runtime_settings
            ),
            solver_output=self.settings.solver_output,
            enforce_charge_discharge_exclusivity=(
                self.settings
                .enforce_charge_discharge_exclusivity
            ),
        )
        local_settings.validate(self.config)

        if not (
            E_MIN_KWH
            <= initial_energy_kwh
            <= E_MAX_KWH
        ):
            raise ValueError("initial_energy_kwh越界。")

        # --------------------------------------------------------------
        # 0:00因果负荷预测 / 历史残差
        # --------------------------------------------------------------
        base_forecast = build_q2_day_ahead_forecast(
            self.attachment2,
            d,
            config=self.config,
        )

        residual_library = build_causal_residual_library(
            self.attachment2,
            d,
            max_residual_days=(
                self.settings.q2_runtime_settings
                .max_residual_days
            ),
            config=self.config,
        )

        history = build_available_history(
            self.attachment2,
            d,
            config=self.config,
        )

        next_day_load_preview = (
            _causal_preview_load_for_next_day(
                history,
                current_date=d,
                config=self.config,
            )
        )

        # 当前Q3生效的PV预测基线。
        effective_pv_forecast = pd.Series(
            np.zeros(144),
            index=list(range(144)),
            dtype=float,
            name="effective_pv_forecast_kwh",
        )

        observed_load = pd.Series(dtype=float)
        observed_pv = pd.Series(dtype=float)

        q_ch_actual = pd.Series(
            index=range(144),
            dtype=float,
            name="actual_charge_kwh",
        )
        q_dis_actual = pd.Series(
            index=range(144),
            dtype=float,
            name="actual_discharge_kwh",
        )
        q_emg_actual = pd.Series(
            index=range(144),
            dtype=float,
            name="actual_emergency_kwh",
        )
        q_curt_actual = pd.Series(
            index=range(144),
            dtype=float,
            name="actual_curtailment_kwh",
        )
        q_sur_actual = pd.Series(
            index=range(144),
            dtype=float,
            name="actual_surplus_kwh",
        )

        E_actual = pd.Series(
            index=range(145),
            dtype=float,
            name="energy_kwh",
        )
        E_actual.loc[0] = float(initial_energy_kwh)

        plan_book: Optional[RollingPlanBook] = None
        update_records: Dict[int, MPCUpdateRecord] = {}
        runtime_rows = []
        freeze_rows = []

        current_energy = float(initial_energy_kwh)

        for k in range(144):
            # ----------------------------------------------------------
            # 0/6/12/18：只在组合中启用的时刻重算未来计划
            # 更新发生在当前k实际区间开始之前。
            # ----------------------------------------------------------
            if k in updates:
                parsed, F0 = self._build_parser_version(
                    d,
                    k,
                )

                future_pv = extract_current_day_model_kwh(
                    parsed,
                    d,
                    start_k=k,
                    config=self.config,
                )

                # 只覆盖未来k>=r；过去预测值保留用于实时残差条件。
                effective_pv_forecast.loc[k:] = (
                    future_pv.to_numpy(dtype=float)
                )

                # 计划优化价格provider可由Q4注入。
                formal_future, preview, obj = (
                    _solve_deterministic_mpc_update(
                        date=d,
                        r=k,
                        current_energy_kwh=current_energy,
                        original_plan_kwh=(
                            None
                            if plan_book is None
                            else plan_book.original_plan_kwh
                        ),
                        load_today_kwh=(
                            base_forecast.load_kwh
                        ),
                        load_next_day_preview_kwh=(
                            next_day_load_preview
                        ),
                        parsed_pv=parsed,
                        price_provider=self.price_provider,
                        config=self.config,
                        enforce_charge_discharge_exclusivity=(
                            local_settings
                            .enforce_charge_discharge_exclusivity
                        ),
                        solver_output=(
                            local_settings.solver_output
                        ),
                    )
                )

                if k == 0:
                    if list(formal_future.index) != list(
                        range(144)
                    ):
                        raise AssertionError(
                            "0:00必须形成完整144点原始计划。"
                        )

                    plan_book = (
                        RollingPlanBook.from_initial_plan(
                            formal_future,
                            config=self.config,
                        )
                    )
                else:
                    if plan_book is None:
                        raise AssertionError(
                            "非0点更新前必须已有0:00原始计划。"
                        )

                    frozen_before = (
                        plan_book.effective_plan_kwh.loc[
                            : k - 1
                        ].copy()
                    )

                    plan_book.update_future(
                        k,
                        formal_future,
                        config=self.config,
                    )

                    frozen_after = (
                        plan_book.effective_plan_kwh.loc[
                            : k - 1
                        ].copy()
                    )

                    passed = bool(
                        np.array_equal(
                            frozen_before.to_numpy(),
                            frozen_after.to_numpy(),
                        )
                    )

                    freeze_rows.append(
                        {
                            "r": k,
                            "frozen_range": f"k<{k}",
                            "passed": passed,
                        }
                    )

                    if not passed:
                        raise AssertionError(
                            f"r={k}更新修改了过去计划。"
                        )

                parser_audit = parsed.hourly_anchors[
                    [
                        "lead_hour",
                        "target_datetime",
                        "forecast_kw",
                        "source",
                    ]
                ].copy()

                update_records[k] = MPCUpdateRecord(
                    r=k,
                    issue_datetime=parsed.issue_datetime,
                    current_energy_kwh=current_energy,
                    current_observed_pv_kw=F0,
                    formal_future_plan_kwh=(
                        formal_future.copy()
                    ),
                    preview_purchase_kwh=preview.copy(),
                    objective_value_yuan=obj,
                    parser_audit=parser_audit,
                )

            if plan_book is None:
                raise AssertionError(
                    "问题3必须在k=0建立原始计划。"
                )

            # ----------------------------------------------------------
            # tau_k：当前储能动作决策前，只允许真实历史0..k-1
            # ----------------------------------------------------------
            if list(observed_load.index) != list(range(k)):
                raise AssertionError(
                    f"k={k}决策前真实负荷前缀必须严格为0..{k-1}。"
                )
            if list(observed_pv.index) != list(range(k)):
                raise AssertionError(
                    f"k={k}决策前真实光伏前缀必须严格为0..{k-1}。"
                )

            effective_forecast = (
                _build_effective_q3_forecast(
                    base_forecast,
                    effective_pv_forecast,
                )
            )

            # ----------------------------------------------------------
            # 1. 不知道current_k实际值时先决定q_ch/q_dis
            # ----------------------------------------------------------
            (
                q_ch,
                q_dis,
                predicted_q_emg,
                predicted_q_curt,
                predicted_q_sur,
                step_audit,
            ) = self._runtime_recourse_step(
                date=d,
                k=k,
                current_energy_kwh=current_energy,
                observed_load_kwh=observed_load,
                observed_pv_kwh=observed_pv,
                effective_forecast=effective_forecast,
                residual_library=residual_library,
                fixed_plan_kwh=(
                    plan_book.effective_plan_kwh
                ),
            )

            # ----------------------------------------------------------
            # 2. 储能动作锁定后，第k区间真实负荷/PV才完整实现
            # ----------------------------------------------------------
            load_now = float(
                self.attachment2.load_kw.at[d, k]
            ) * self.dt_hours

            pv_now = float(
                self.attachment2.pv_kw.at[d, k]
            ) * self.dt_hours

            # ----------------------------------------------------------
            # 3. current_k实际实现后再计算紧急购电/弃光/计划富余
            # ----------------------------------------------------------
            (
                q_emg,
                q_curt,
                q_sur,
                balance_residual,
            ) = settle_realized_interval_after_storage(
                q_buy_kwh=float(
                    plan_book.effective_plan_kwh.loc[k]
                ),
                q_ch_kwh=q_ch,
                q_dis_kwh=q_dis,
                actual_load_kwh=load_now,
                actual_pv_kwh=pv_now,
            )

            q_ch_actual.loc[k] = q_ch
            q_dis_actual.loc[k] = q_dis
            q_emg_actual.loc[k] = q_emg
            q_curt_actual.loc[k] = q_curt
            q_sur_actual.loc[k] = q_sur

            next_energy = (
                current_energy
                + ETA_C * q_ch
                - q_dis / ETA_D
            )

            if (
                next_energy < E_MIN_KWH - 1e-6
                or next_energy > E_MAX_KWH + 1e-6
            ):
                raise AssertionError(
                    f"k={k}实际执行后SOC越界。"
                )

            E_actual.loc[k] = current_energy
            E_actual.loc[k + 1] = next_energy
            current_energy = next_energy

            # ----------------------------------------------------------
            # 4. 区间结束后才把actual k加入下一时段可用历史
            # ----------------------------------------------------------
            observed_load.loc[k] = load_now
            observed_pv.loc[k] = pv_now

            audit_row = step_audit.iloc[0].to_dict()
            audit_row.update(
                {
                    "realized_load_kwh": load_now,
                    "realized_pv_kwh": pv_now,
                    "predicted_q_emg_kwh_not_executed": (
                        predicted_q_emg
                    ),
                    "predicted_q_curt_kwh_not_executed": (
                        predicted_q_curt
                    ),
                    "predicted_q_sur_kwh_not_executed": (
                        predicted_q_sur
                    ),
                    "expost_balance_residual_kwh": (
                        balance_residual
                    ),
                }
            )
            runtime_rows.append(audit_row)

        if plan_book is None:
            raise AssertionError("全天计划簿未建立。")

        GF = plan_book.final_effective_plan()

        # Q3固定价格结算；Q4-3会在外层用附件4实际价格重新结算。
        # 当前Q3必须使用附件1固定价格。
        settlement = settle_question3_cost(
            G0_kwh=plan_book.original_plan_kwh,
            GF_kwh=GF,
            price_yuan_per_kwh=self.fixed_price,
            G_emg_kwh=q_emg_actual,
            config=self.config,
        )

        if not freeze_rows:
            # 仅0:00组合没有调整，冻结检查自然通过。
            freeze_rows.append(
                {
                    "r": 0,
                    "frozen_range": "none",
                    "passed": True,
                }
            )

        result = Question3DayResult(
            date=d,
            update_combination=updates,
            initial_energy_kwh=float(initial_energy_kwh),
            end_energy_kwh=float(E_actual.loc[144]),
            original_plan_kwh=(
                plan_book.original_plan_kwh.copy()
            ),
            final_effective_plan_kwh=GF.copy(),
            plan_versions={
                r: s.copy()
                for r, s in plan_book.versions.items()
            },
            update_records=update_records,
            actual_charge_kwh=q_ch_actual,
            actual_discharge_kwh=q_dis_actual,
            actual_emergency_kwh=q_emg_actual,
            actual_curtailment_kwh=q_curt_actual,
            actual_surplus_kwh=q_sur_actual,
            energy_kwh=E_actual,
            dG_plus_kwh=settlement.dG_plus_kwh,
            dG_minus_kwh=settlement.dG_minus_kwh,
            C_plan_yuan=settlement.C_plan_yuan,
            C_reg_yuan=settlement.C_reg_yuan,
            C_adj_yuan=settlement.C_adj_yuan,
            C_emg_yuan=settlement.C_emg_yuan,
            C_total_yuan=settlement.C_total_yuan,
            runtime_causality_report=pd.DataFrame(
                runtime_rows
            ),
            update_freeze_report=pd.DataFrame(
                freeze_rows
            ),
            settlement_test_report=(
                SETTLEMENT_SELF_TEST_REPORT.copy()
            ),
            legality_report=pd.DataFrame(),
        )

        legality = check_question3_day_result_legality(
            result=result,
            attachment2=self.attachment2,
            price_yuan_per_kwh=self.fixed_price,
            config=self.config,
        )
        result.legality_report = legality

        if check_legality:
            failed = legality.loc[~legality["passed"]]
            if not failed.empty:
                raise AssertionError(
                    "问题3结果合法性检查失败：\n"
                    + failed.to_string(index=False)
                )

        return result

    def run_ablation_day(
        self,
        date,
        *,
        initial_energy_kwh: float,
        check_legality: bool = True,
    ) -> Dict[str, Question3DayResult]:
        """
        四种更新时间组合消融。

        每种组合从同一个initial_energy_kwh开始，
        便于单日公平比较。
        """
        results = {}

        for name, updates in (
            ABLATION_UPDATE_COMBINATIONS.items()
        ):
            results[name] = self.solve_day(
                date,
                initial_energy_kwh=initial_energy_kwh,
                update_combination=updates,
                check_legality=check_legality,
            )

        return results

    def solve_period(
        self,
        *,
        start_date: str = "2025-01-01",
        end_date: str = "2025-12-31",
        initial_energy_kwh: float = 6000.0,
        save_from_date: str = "2025-02-01",
        update_combination: Optional[
            tuple[int, ...]
        ] = None,
        check_legality: bool = True,
    ) -> Question3PeriodResult:
        """
        跨日SOC连续滚动。

        次日正式购电计划始终在次日0:00重新生成；
        前一日18:00得到的next-day preview从不写入正式计划。
        """
        start = _normalize_date(start_date)
        end = _normalize_date(end_date)
        save_from = _normalize_date(save_from_date)

        if end < start:
            raise ValueError("end_date不能早于start_date。")

        formal_results = {}
        cross_rows = []

        current_energy = float(initial_energy_kwh)
        warmup_end_energy = None

        previous_date = None
        previous_end = None

        for d in pd.date_range(start, end, freq="D"):
            if previous_date is not None:
                residual = abs(
                    current_energy - float(previous_end)
                )
                cross_rows.append(
                    {
                        "previous_date": previous_date,
                        "current_date": d,
                        "previous_end_energy_kwh": previous_end,
                        "current_initial_energy_kwh": (
                            current_energy
                        ),
                        "residual_kwh": residual,
                        "passed": residual <= 1e-8,
                    }
                )

            day = self.solve_day(
                d,
                initial_energy_kwh=current_energy,
                update_combination=update_combination,
                check_legality=check_legality,
            )

            current_energy = float(day.end_energy_kwh)
            previous_end = current_energy
            previous_date = d

            print(
                f"[Q3] {d.date()} 完成：总成本 {day.C_total_yuan:.2f} 元，"
                f"末SOC {current_energy:.2f} kWh",
                flush=True,
            )

            if d < save_from:
                warmup_end_energy = current_energy
            else:
                formal_results[d] = day

        cross_report = pd.DataFrame(cross_rows)

        if (
            not cross_report.empty
            and not cross_report["passed"].all()
        ):
            raise AssertionError("问题3跨日SOC连续性失败。")

        return Question3PeriodResult(
            formal_results=formal_results,
            cross_day_report=cross_report,
            warmup_end_energy_kwh=warmup_end_energy,
            final_energy_kwh=current_energy,
        )
