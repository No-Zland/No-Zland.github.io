# -*- coding: utf-8 -*-
"""
question1_solver.py
问题1确定性日内购电优化求解器。

本模块严格继承 model_base.py，不重新定义公共变量体系和时间索引。

输入
----
1. data_loader.Attachment1Data
   - attachment1.aligned["price_yuan_per_kwh"] : 元/kWh
   - attachment1.aligned["load_kw"]             : kW
   - attachment1.aligned["pv_forecast_kw"]      : kW
2. initial_energy_kwh
   - 问题1默认 6000 kWh
3. StorageParams
   - 与已经冻结的公共储能参数保持一致

输出
----
- 计划购电量 q_buy[k]，kWh
- 充电量 q_ch[k]，kWh
- 放电量 q_dis[k]，kWh
- 弃光量 q_curt[k]，kWh
- 储电量轨迹 E[j]，j=0,...,144，kWh
- 总购电量，kWh
- 总费用，元
- 论文指定时段提取结果
- 结果合法性检查报告

问题1新增约束
------------
[Q1-01] E_0 = E_init
[Q1-02] E_144 = E_0

问题1目标函数
-------------
[Q1-OBJ]
    min C_1 = sum_{k=0}^{143} p_k * q_buy[k]

时间提取规则
------------
论文指定：
    10:00-10:10 -> k=60
    12:00-12:10 -> k=72
    14:00-14:10 -> k=84
    16:00-16:10 -> k=96
    18:00-18:10 -> k=108
    20:00-20:10 -> k=120

禁止根据附件时间字符串或结果模板显示文字搜索这些时段。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import pandas as pd

try:
    import gurobipy as gp
    from gurobipy import GRB
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "question1_solver.py 依赖 gurobipy。"
        "请在已安装并配置 Gurobi 的环境中运行。"
    ) from exc

from config import DEFAULT_CONFIG, ProjectConfig
from data_loader import Attachment1Data
from model_base import (
    ETA_C,
    ETA_D,
    E_MIN_KWH,
    E_MAX_KWH,
    P_BAT_MAX_KW,
    MicrogridBaseModel,
    kw_to_interval_kwh,
)
from time_index import build_time_map, validate_time_map


# ============================================================================
# 论文指定时段：只能通过模型k提取，不搜索任何Excel/模板字符串
# ============================================================================

REPORT_INTERVAL_INDEX: tuple[int, ...] = (
    60,   # 10:00-10:10
    72,   # 12:00-12:10
    84,   # 14:00-14:10
    96,   # 16:00-16:10
    108,  # 18:00-18:10
    120,  # 20:00-20:10
)


@dataclass(frozen=True)
class StorageParams:
    """
    问题1储能参数输入。

    当前公共模型已经冻结为：
        eta_c = eta_d = 0.9
        E_min = 1200 kWh
        E_max = 10800 kWh
        P_bat_max = 5000 kW

    为防止question1_solver与model_base出现两套物理口径，
    本模块会强制检查传入参数与公共模型一致。
    """

    eta_c: float = ETA_C
    eta_d: float = ETA_D
    e_min_kwh: float = E_MIN_KWH
    e_max_kwh: float = E_MAX_KWH
    p_bat_max_kw: float = P_BAT_MAX_KW

    def validate_against_model_base(self, tol: float = 1e-12) -> None:
        expected = {
            "eta_c": ETA_C,
            "eta_d": ETA_D,
            "e_min_kwh": E_MIN_KWH,
            "e_max_kwh": E_MAX_KWH,
            "p_bat_max_kw": P_BAT_MAX_KW,
        }
        actual = {
            "eta_c": self.eta_c,
            "eta_d": self.eta_d,
            "e_min_kwh": self.e_min_kwh,
            "e_max_kwh": self.e_max_kwh,
            "p_bat_max_kw": self.p_bat_max_kw,
        }

        bad = {
            key: (actual[key], expected[key])
            for key in expected
            if abs(float(actual[key]) - float(expected[key])) > tol
        }

        if bad:
            raise ValueError(
                "question1_solver的储能参数必须与model_base.py已冻结参数一致。"
                f"发现差异：{bad}"
            )


@dataclass
class Question1Result:
    """问题1求解结果。"""

    status: int
    objective_value_yuan: float

    # k=0,...,143
    plan_purchase_kwh: pd.Series
    charge_kwh: pd.Series
    discharge_kwh: pd.Series
    curtailment_kwh: pd.Series

    # j=0,...,144
    energy_kwh: pd.Series

    total_purchase_kwh: float
    total_cost_yuan: float

    # 论文指定时段
    paper_intervals: pd.DataFrame

    # 结果合法性检查
    legality_report: pd.DataFrame


def _prepare_attachment1_for_q1(
    attachment1: Attachment1Data,
    *,
    config: ProjectConfig,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    从附件1处理结果中获取：
        price_yuan_per_kwh
        load_kwh
        pv_forecast_kwh

    只使用attachment1.aligned中的模型k顺序。
    不读取附件1原始时间字符串进行定位。
    """
    if not isinstance(attachment1, Attachment1Data):
        raise TypeError(
            "attachment1必须是data_loader.load_attachment1()返回的"
            "Attachment1Data。"
        )

    aligned = attachment1.aligned

    required_columns = {
        "k",
        "price_yuan_per_kwh",
        "load_kw",
        "pv_forecast_kw",
    }
    missing = required_columns.difference(aligned.columns)
    if missing:
        raise ValueError(
            f"附件1处理结果缺少Q1所需字段：{sorted(missing)}"
        )

    if len(aligned) != config.intervals_per_day:
        raise ValueError(
            f"附件1处理结果必须为{config.intervals_per_day}行，"
            f"实际为{len(aligned)}。"
        )

    k_values = aligned["k"].astype(int).tolist()
    expected_k = list(range(config.intervals_per_day))
    if k_values != expected_k:
        raise ValueError(
            "附件1处理结果的k必须严格为0~143且按顺序排列。"
            "不得通过附件时间字符串重新定位。"
        )

    price = pd.to_numeric(
        aligned["price_yuan_per_kwh"],
        errors="raise",
    ).astype(float)
    price.index = expected_k
    price.name = "price_yuan_per_kwh"

    if price.isna().any():
        raise ValueError("附件1电价存在缺失值。")

    # 负荷/光伏原始单位kW，统一转换为每个10 min区间的kWh。
    load_kw = pd.to_numeric(
        aligned["load_kw"],
        errors="raise",
    ).astype(float)
    load_kw.index = expected_k
    load_kw.name = "load_kw"

    pv_kw = pd.to_numeric(
        aligned["pv_forecast_kw"],
        errors="raise",
    ).astype(float)
    pv_kw.index = expected_k
    pv_kw.name = "pv_forecast_kw"

    if (load_kw < 0).any():
        raise ValueError("附件1负荷功率存在负值。")
    if (pv_kw < 0).any():
        raise ValueError("附件1光伏预测功率存在负值。")

    load_kwh = kw_to_interval_kwh(
        load_kw,
        config=config,
        name="load_kw",
    )
    pv_kwh = kw_to_interval_kwh(
        pv_kw,
        config=config,
        name="pv_forecast_kw",
    )

    load_kwh.name = "load_kwh"
    pv_kwh.name = "pv_forecast_kwh"

    return price, load_kwh, pv_kwh


def extract_paper_intervals(
    *,
    plan_purchase_kwh: pd.Series,
    charge_kwh: pd.Series,
    discharge_kwh: pd.Series,
    curtailment_kwh: pd.Series,
    energy_kwh: pd.Series,
    time_map: pd.DataFrame,
) -> pd.DataFrame:
    """
    固定按REPORT_INTERVAL_INDEX提取论文指定时段。

    重要：
    本函数不搜索：
    - 附件1中的'10:00'/'10:10'
    - source_right_endpoint_label
    - paper_label字符串
    - template_display_label

    唯一定位方式是模型k：
        60,72,84,96,108,120
    """
    validate_time_map(time_map)

    rows = []

    for k in REPORT_INTERVAL_INDEX:
        tm = time_map.loc[time_map["k"] == k]
        if len(tm) != 1:
            raise ValueError(f"time_map中k={k}必须且只能出现一次。")

        tm_row = tm.iloc[0]

        rows.append(
            {
                "k": k,
                "paper_label": tm_row["paper_label"],
                "source_right_endpoint_label": (
                    tm_row["source_right_endpoint_label"]
                ),
                "plan_purchase_kwh": float(plan_purchase_kwh.loc[k]),
                "charge_kwh": float(charge_kwh.loc[k]),
                "discharge_kwh": float(discharge_kwh.loc[k]),
                "curtailment_kwh": float(curtailment_kwh.loc[k]),
                "energy_start_kwh": float(energy_kwh.loc[k]),
                "energy_end_kwh": float(energy_kwh.loc[k + 1]),
            }
        )

    result = pd.DataFrame(rows)

    expected = {
        60: "10:00-10:10",
        72: "12:00-12:10",
        84: "14:00-14:10",
        96: "16:00-16:10",
        108: "18:00-18:10",
        120: "20:00-20:10",
    }

    for row in result.itertuples(index=False):
        if row.paper_label != expected[row.k]:
            raise AssertionError(
                f"k={row.k}物理区间异常："
                f"{row.paper_label} != {expected[row.k]}"
            )

    return result


def check_question1_result_legality(
    *,
    result: Question1Result,
    attachment1: Attachment1Data,
    initial_energy_kwh: float,
    storage_params: StorageParams,
    config: ProjectConfig = DEFAULT_CONFIG,
    time_map: Optional[pd.DataFrame] = None,
    tolerance_kwh: float = 1e-5,
    tolerance_yuan: float = 1e-5,
    enforce_charge_discharge_exclusivity: bool = False,
) -> pd.DataFrame:
    """
    问题1结果合法性检查。

    检查内容：
    1. 索引和长度；
    2. 变量非负；
    3. [MB-02] 能量平衡；
    4. [MB-03] 弃光上界；
    5. [MB-04] SOC状态方程；
    6. [MB-05] 储电量上下界；
    7. [MB-06] 充放电量上限；
    8. [MB-07] 可选互斥；
    9. [Q1-01] E_0=E_init；
    10. [Q1-02] E_144=E_0；
    11. 总购电量重算；
    12. 总费用重算；
    13. 论文指定k提取一致性。
    """
    storage_params.validate_against_model_base()

    if time_map is None:
        time_map = build_time_map(config)
    validate_time_map(time_map, config)

    price, load_kwh, pv_kwh = _prepare_attachment1_for_q1(
        attachment1,
        config=config,
    )

    q_buy = result.plan_purchase_kwh
    q_ch = result.charge_kwh
    q_dis = result.discharge_kwh
    q_curt = result.curtailment_kwh
    E = result.energy_kwh

    checks = []

    def add_check(
        item: str,
        passed: bool,
        detail: str,
        max_residual: Optional[float] = None,
    ) -> None:
        checks.append(
            {
                "item": item,
                "passed": bool(passed),
                "max_residual": max_residual,
                "detail": detail,
            }
        )

    expected_k = list(range(config.intervals_per_day))
    expected_j = list(range(config.state_nodes_per_day))

    # 1. 长度与索引
    for name, series, expected in [
        ("plan_purchase_kwh", q_buy, expected_k),
        ("charge_kwh", q_ch, expected_k),
        ("discharge_kwh", q_dis, expected_k),
        ("curtailment_kwh", q_curt, expected_k),
        ("energy_kwh", E, expected_j),
    ]:
        index_ok = list(series.index) == expected
        add_check(
            f"{name}-index",
            index_ok,
            f"实际长度={len(series)}；期望长度={len(expected)}。",
        )

    # 2. 非负性
    for name, series in [
        ("q_buy", q_buy),
        ("q_ch", q_ch),
        ("q_dis", q_dis),
        ("q_curt", q_curt),
    ]:
        min_value = float(series.min())
        add_check(
            f"{name}-nonnegative",
            min_value >= -tolerance_kwh,
            f"最小值={min_value:.12g} kWh。",
            max_residual=max(0.0, -min_value),
        )

    # 3. [MB-02] q_buy + G + q_dis = L + q_ch + q_curt
    balance_residual = (
        q_buy
        + pv_kwh
        + q_dis
        - load_kwh
        - q_ch
        - q_curt
    )
    balance_max = float(balance_residual.abs().max())
    add_check(
        "[MB-02] energy_balance",
        balance_max <= tolerance_kwh,
        f"最大绝对残差={balance_max:.12g} kWh。",
        max_residual=balance_max,
    )

    # 4. [MB-03] 0 <= q_curt <= G
    curt_upper_violation = float(
        (q_curt - pv_kwh).clip(lower=0).max()
    )
    add_check(
        "[MB-03] curtailment_upper",
        curt_upper_violation <= tolerance_kwh,
        f"最大上界违反={curt_upper_violation:.12g} kWh。",
        max_residual=curt_upper_violation,
    )

    # 5. [MB-04] SOC状态方程
    transition_residual = pd.Series(
        {
            k: (
                E.loc[k + 1]
                - E.loc[k]
                - storage_params.eta_c * q_ch.loc[k]
                + q_dis.loc[k] / storage_params.eta_d
            )
            for k in expected_k
        },
        dtype=float,
    )
    transition_max = float(transition_residual.abs().max())
    add_check(
        "[MB-04] storage_transition",
        transition_max <= tolerance_kwh,
        f"最大绝对残差={transition_max:.12g} kWh。",
        max_residual=transition_max,
    )

    # 6. [MB-05] SOC上下界
    lower_violation = float(
        (storage_params.e_min_kwh - E).clip(lower=0).max()
    )
    upper_violation = float(
        (E - storage_params.e_max_kwh).clip(lower=0).max()
    )
    soc_violation = max(lower_violation, upper_violation)
    add_check(
        "[MB-05] energy_bounds",
        soc_violation <= tolerance_kwh,
        (
            f"下界最大违反={lower_violation:.12g} kWh；"
            f"上界最大违反={upper_violation:.12g} kWh。"
        ),
        max_residual=soc_violation,
    )

    # 7. [MB-06] 充放电上限
    q_max = storage_params.p_bat_max_kw * config.dt_minutes / 60.0
    charge_violation = float(
        (q_ch - q_max).clip(lower=0).max()
    )
    discharge_violation = float(
        (q_dis - q_max).clip(lower=0).max()
    )
    power_violation = max(charge_violation, discharge_violation)
    add_check(
        "[MB-06] charge_discharge_limit",
        power_violation <= tolerance_kwh,
        (
            f"q_max={q_max:.12g} kWh；"
            f"充电最大违反={charge_violation:.12g}；"
            f"放电最大违反={discharge_violation:.12g}。"
        ),
        max_residual=power_violation,
    )

    # 8. [MB-07] 可选互斥
    if enforce_charge_discharge_exclusivity:
        simultaneous = pd.concat(
            [q_ch, q_dis],
            axis=1,
        ).min(axis=1)
        simultaneous_max = float(simultaneous.max())
        add_check(
            "[MB-07] charge_discharge_exclusivity",
            simultaneous_max <= tolerance_kwh,
            f"最大同时充放电量={simultaneous_max:.12g} kWh。",
            max_residual=simultaneous_max,
        )
    else:
        add_check(
            "[MB-07] charge_discharge_exclusivity",
            True,
            "连续LP主模型未强制互斥；该项按模型设定通过。",
            max_residual=0.0,
        )

    # 9. [Q1-01] E_0 = initial
    init_residual = abs(float(E.loc[0]) - float(initial_energy_kwh))
    add_check(
        "[Q1-01] initial_energy",
        init_residual <= tolerance_kwh,
        f"|E_0-E_init|={init_residual:.12g} kWh。",
        max_residual=init_residual,
    )

    # 10. [Q1-02] E_144 = E_0
    terminal_residual = abs(
        float(E.loc[config.intervals_per_day]) - float(E.loc[0])
    )
    add_check(
        "[Q1-02] daily_energy_closure",
        terminal_residual <= tolerance_kwh,
        f"|E_144-E_0|={terminal_residual:.12g} kWh。",
        max_residual=terminal_residual,
    )

    # 11. 总购电量
    total_purchase_recalc = float(q_buy.sum())
    total_purchase_residual = abs(
        total_purchase_recalc - float(result.total_purchase_kwh)
    )
    add_check(
        "total_purchase_kwh",
        total_purchase_residual <= tolerance_kwh,
        (
            f"结果={result.total_purchase_kwh:.12g}；"
            f"重算={total_purchase_recalc:.12g} kWh。"
        ),
        max_residual=total_purchase_residual,
    )

    # 12. 总费用
    total_cost_recalc = float((price * q_buy).sum())
    total_cost_residual = abs(
        total_cost_recalc - float(result.total_cost_yuan)
    )
    add_check(
        "[Q1-OBJ] total_cost_yuan",
        total_cost_residual <= tolerance_yuan,
        (
            f"结果={result.total_cost_yuan:.12g}；"
            f"重算={total_cost_recalc:.12g} 元。"
        ),
        max_residual=total_cost_residual,
    )

    # 13. 论文指定k只能按常量索引提取
    expected_report_k = list(REPORT_INTERVAL_INDEX)
    actual_report_k = result.paper_intervals["k"].astype(int).tolist()
    add_check(
        "paper_report_fixed_k",
        actual_report_k == expected_report_k,
        (
            f"实际={actual_report_k}；"
            f"期望={expected_report_k}。"
        ),
    )

    report = pd.DataFrame(checks)
    return report


def assert_question1_result_legal(report: pd.DataFrame) -> None:
    """若问题1结果存在任何不合法项，则直接抛出异常。"""
    failed = report.loc[~report["passed"]]

    if failed.empty:
        return

    lines = []
    for row in failed.itertuples(index=False):
        lines.append(
            f"{row.item}: {row.detail}"
        )

    raise AssertionError(
        "问题1结果合法性检查未通过：\n"
        + "\n".join(lines)
    )


class Question1Solver(MicrogridBaseModel):
    """
    问题1求解器。

    继承：
        MicrogridBaseModel

    公共物理约束来自model_base.py；
    本类只新增：
        [Q1-01] E_0 = E_init
        [Q1-02] E_144 = E_0
        [Q1-OBJ] 最小化正常外网购电费用
    """

    def __init__(
        self,
        *,
        attachment1: Attachment1Data,
        initial_energy_kwh: float = 6000.0,
        storage_params: StorageParams = StorageParams(),
        config: ProjectConfig = DEFAULT_CONFIG,
        model: Optional[gp.Model] = None,
        enforce_charge_discharge_exclusivity: bool = False,
        solver_output: bool = False,
    ) -> None:
        storage_params.validate_against_model_base()

        if not (
            storage_params.e_min_kwh
            <= initial_energy_kwh
            <= storage_params.e_max_kwh
        ):
            raise ValueError(
                "initial_energy_kwh必须位于储能安全范围内："
                f"[{storage_params.e_min_kwh}, "
                f"{storage_params.e_max_kwh}]。"
            )

        self.attachment1 = attachment1
        self.initial_energy_kwh = float(initial_energy_kwh)
        self.storage_params = storage_params

        self.price_yuan_per_kwh, self.load_kwh, self.pv_kwh = (
            _prepare_attachment1_for_q1(
                attachment1,
                config=config,
            )
        )

        if model is None:
            model = gp.Model("question1")

        model.Params.OutputFlag = 1 if solver_output else 0

        # 必须继承model_base.py：
        # 公共变量、time_index、默认LP/可选MILP接口由父类创建。
        super().__init__(
            model,
            config=config,
            time_map=build_time_map(config),
            enforce_charge_discharge_exclusivity=(
                enforce_charge_discharge_exclusivity
            ),
            variable_name_prefix="",
        )

        self._q1_constraints_added = False
        self._q1_objective_added = False

        self.initial_energy_constraint: Optional[gp.Constr] = None
        self.terminal_energy_constraint: Optional[gp.Constr] = None

    def add_question1_constraints(self) -> None:
        """
        添加问题1全部约束。

        先调用父类公共约束：
            [MB-02] 能量平衡
            [MB-03] 弃光
            [MB-04] SOC状态方程
            [MB-05] SOC上下界（变量边界）
            [MB-06] 充放电限制（变量边界）
            [MB-07] 可选互斥
            [MB-08] 外网购电非负（变量边界）

        再新增：
            [Q1-01] E_0 = E_init
            [Q1-02] E_144 = E_0
        """
        if self._q1_constraints_added:
            return

        self.add_common_physical_constraints(
            load_kwh=self.load_kwh,
            pv_kwh=self.pv_kwh,
            q_emg=None,
            q_sur=None,
        )

        # [Q1-01] 日初储电量
        self.initial_energy_constraint = self.model.addConstr(
            self.vars.E[0] == self.initial_energy_kwh,
            name="q1_initial_energy",
        )

        # [Q1-02] 24:00储电量与0:00完全相同
        self.terminal_energy_constraint = self.model.addConstr(
            self.vars.E[self.config.intervals_per_day]
            == self.vars.E[0],
            name="q1_terminal_energy_closure",
        )

        self._q1_constraints_added = True

    def add_question1_objective(self) -> None:
        """
        添加问题1唯一目标函数。

        [Q1-OBJ]
            min C_1 = sum_k p_k * q_buy[k]

        p_k单位：元/kWh
        q_buy[k]单位：kWh
        因此目标函数单位：元
        """
        if self._q1_objective_added:
            return

        objective = gp.quicksum(
            float(self.price_yuan_per_kwh.loc[k])
            * self.vars.q_buy[k]
            for k in self.k
        )

        self.model.setObjective(
            objective,
            GRB.MINIMIZE,
        )

        self._q1_objective_added = True

    @staticmethod
    def _extract_k_series(
        var_dict: gp.tupledict,
        *,
        index: Sequence[int],
        name: str,
    ) -> pd.Series:
        """从Gurobi变量字典提取固定索引Series。"""
        return pd.Series(
            {
                int(i): float(var_dict[i].X)
                for i in index
            },
            dtype=float,
            name=name,
        )

    def solve(
        self,
        *,
        check_legality: bool = True,
        tolerance_kwh: float = 1e-5,
        tolerance_yuan: float = 1e-5,
    ) -> Question1Result:
        """
        求解问题1并返回结构化结果。

        不写Excel，不处理问题2及以后逻辑。
        """
        self.add_question1_constraints()
        self.add_question1_objective()

        self.model.optimize()

        if self.model.Status != GRB.OPTIMAL:
            raise RuntimeError(
                "问题1未得到最优解。"
                f"Gurobi Status={self.model.Status}"
            )

        q_buy = self._extract_k_series(
            self.vars.q_buy,
            index=self.k,
            name="plan_purchase_kwh",
        )
        q_ch = self._extract_k_series(
            self.vars.q_ch,
            index=self.k,
            name="charge_kwh",
        )
        q_dis = self._extract_k_series(
            self.vars.q_dis,
            index=self.k,
            name="discharge_kwh",
        )
        q_curt = self._extract_k_series(
            self.vars.q_curt,
            index=self.k,
            name="curtailment_kwh",
        )
        E = self._extract_k_series(
            self.vars.E,
            index=self.j,
            name="energy_kwh",
        )

        total_purchase_kwh = float(q_buy.sum())
        total_cost_yuan = float(
            (self.price_yuan_per_kwh * q_buy).sum()
        )

        paper_intervals = extract_paper_intervals(
            plan_purchase_kwh=q_buy,
            charge_kwh=q_ch,
            discharge_kwh=q_dis,
            curtailment_kwh=q_curt,
            energy_kwh=E,
            time_map=self.time_map,
        )

        # 先构造临时结果，合法性报告随后填充。
        result = Question1Result(
            status=int(self.model.Status),
            objective_value_yuan=float(self.model.ObjVal),
            plan_purchase_kwh=q_buy,
            charge_kwh=q_ch,
            discharge_kwh=q_dis,
            curtailment_kwh=q_curt,
            energy_kwh=E,
            total_purchase_kwh=total_purchase_kwh,
            total_cost_yuan=total_cost_yuan,
            paper_intervals=paper_intervals,
            legality_report=pd.DataFrame(),
        )

        legality_report = check_question1_result_legality(
            result=result,
            attachment1=self.attachment1,
            initial_energy_kwh=self.initial_energy_kwh,
            storage_params=self.storage_params,
            config=self.config,
            time_map=self.time_map,
            tolerance_kwh=tolerance_kwh,
            tolerance_yuan=tolerance_yuan,
            enforce_charge_discharge_exclusivity=(
                self.enforce_charge_discharge_exclusivity
            ),
        )

        result.legality_report = legality_report

        if check_legality:
            assert_question1_result_legal(legality_report)

        return result
