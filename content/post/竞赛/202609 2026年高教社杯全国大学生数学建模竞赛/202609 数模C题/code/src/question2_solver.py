# -*- coding: utf-8 -*-
"""
question2_solver.py
问题2：日前计划购电 + 多阶段非预见随机优化 + 10分钟因果滚动补救。

严格继承前文已经冻结的：
- 变量命名：
    q_buy, q_ch, q_dis, q_emg, q_curt, q_sur, E
- 时间索引：
    time_index.py 中的 k=0,...,143
- 数据接口：
    Attachment1Data, Attachment2Data
- 单位：
    功率输入kW；优化中的能量变量统一kWh
- 储能参数：
    model_base.py 中 ETA_C/ETA_D/E_MIN/E_MAX/P_BAT_MAX

本文件不编写问题3/4逻辑。

信息边界
--------
1. 每天0:00生成forecast(d)时，只使用日期s<d的附件2历史；
2. 每天0:00残差库只包含s<d的严格样本外历史残差；
3. 当天未来真实负荷/光伏绝不进入0:00优化；
4. q_buy[d,k|0]在0:00确定后全天固定；
5. 储能/弃光/计划富余/紧急购电按场景树node_id决策；
6. 不创建“每条完整叶场景一套从0:00就知道全天未来的动作”；
7. 实际运行采用条件滚动补救：
       在tau_k决定储能动作时只传入已完成真实前缀0..k-1和当前真实SOC；
       current_k及未来条件场景只来自预测与历史残差分布；
       current_k真实负荷/PV只在动作确定后用于事后紧急购电/弃光/富余；
       每次只执行current_k唯一根节点的储能第一步动作。
8. 实际E_144传递到下一天E_0，不做每日SOC重置；
9. 默认从2025-02-01开始保留正式结果，1月份用于暖启动和SOC推进。

数学编号
--------
[Q2-01] 0:00计划购电费用
[Q2-02] 节点能量平衡
[Q2-03] 节点储能状态转移
[Q2-04] 节点SOC上下界
[Q2-05] 节点充放电上限
[Q2-06] 节点弃光上限
[Q2-07] 5倍紧急购电期望费用
[Q2-08] 风险中性目标
[Q2-09] 非预见性：一节点一动作
[Q2-10] 跨日SOC连续
[Q2-11] CVaR叶路径紧急购电损失（可选）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np
import pandas as pd

try:
    import gurobipy as gp
    from gurobipy import GRB
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "question2_solver.py 依赖 gurobipy。"
        "请在已安装并配置 Gurobi 的环境中运行。"
    ) from exc

from config import DEFAULT_CONFIG, ProjectConfig
from data_loader import Attachment1Data, Attachment2Data
from forecast_model import (
    DayAheadForecast,
    ResidualLibrary,
    build_causal_residual_library,
    build_q2_day_ahead_forecast,
)
from model_base import (
    ETA_C,
    ETA_D,
    E_MIN_KWH,
    E_MAX_KWH,
    P_BAT_MAX_KW,
)
from scenario_tree import (
    NonanticipativeScenarioTree,
    ScenarioTrajectorySet,
    build_bootstrap_trajectory_set,
    build_conditional_trajectory_set,
    build_nonanticipative_tree,
    reduce_trajectory_set,
)
from time_index import build_time_map, validate_time_map


# ============================================================================
# 配置与结果结构
# ============================================================================


@dataclass(frozen=True)
class Question2Settings:
    """问题2随机优化和因果补救设置。"""

    # 因果残差库最多保留最近多少天
    max_residual_days: int = 60

    # 0:00场景
    dayahead_bootstrap_scenarios: int = 40
    dayahead_reduced_scenarios: int = 10
    dayahead_branch_every: int = 6       # 6×10min = 1h
    dayahead_max_branch: int = 3

    # 实际运行的条件滚动补救场景
    rolling_bootstrap_scenarios: int = 16
    rolling_reduced_scenarios: int = 6
    rolling_branch_every: int = 12       # 12×10min = 2h
    rolling_max_branch: int = 2
    conditioning_pool: int = 12

    # 风险设置：默认风险中性
    cvar_alpha: float = 0.95
    cvar_lambda: float = 0.0

    # 默认连续LP；如确有必要才开启MILP互斥
    enforce_charge_discharge_exclusivity: bool = False

    random_seed: int = 2025
    solver_output: bool = False

    def validate(self) -> None:
        integer_positive = {
            "max_residual_days": self.max_residual_days,
            "dayahead_bootstrap_scenarios": self.dayahead_bootstrap_scenarios,
            "dayahead_reduced_scenarios": self.dayahead_reduced_scenarios,
            "dayahead_branch_every": self.dayahead_branch_every,
            "dayahead_max_branch": self.dayahead_max_branch,
            "rolling_bootstrap_scenarios": self.rolling_bootstrap_scenarios,
            "rolling_reduced_scenarios": self.rolling_reduced_scenarios,
            "rolling_branch_every": self.rolling_branch_every,
            "rolling_max_branch": self.rolling_max_branch,
            "conditioning_pool": self.conditioning_pool,
        }

        for name, value in integer_positive.items():
            if int(value) <= 0:
                raise ValueError(f"{name}必须为正整数。")

        if not (0.0 < self.cvar_alpha < 1.0):
            raise ValueError("cvar_alpha必须位于(0,1)。")

        if not (0.0 <= self.cvar_lambda <= 1.0):
            raise ValueError("cvar_lambda必须位于[0,1]。")


@dataclass
class TreeOptimizationSolution:
    """一个场景树优化问题的内部求解结果。"""

    q_buy_kwh: pd.Series
    node_policy: pd.DataFrame

    objective_value: float
    expected_emergency_cost_yuan: float
    plan_cost_yuan: float

    leaf_emergency_loss: pd.DataFrame
    cvar_value_yuan: Optional[float]


@dataclass
class Question2DayResult:
    """问题2单日正式/暖启动运行结果。"""

    date: pd.Timestamp
    initial_energy_kwh: float
    end_energy_kwh: float

    # 0:00唯一锁定全天计划购电
    plan_purchase_kwh: pd.Series

    # 实际因果运行轨迹
    actual_charge_kwh: pd.Series
    actual_discharge_kwh: pd.Series
    actual_emergency_kwh: pd.Series
    actual_curtailment_kwh: pd.Series
    actual_surplus_kwh: pd.Series

    # j=0,...,144
    energy_kwh: pd.Series

    # 费用分解
    plan_cost_yuan: float
    emergency_cost_yuan: float
    total_cost_yuan: float
    total_plan_purchase_kwh: float
    total_emergency_kwh: float

    # 0:00预测
    load_forecast_kwh: pd.Series
    pv_forecast_kwh: pd.Series

    # 0:00场景树、节点策略及非预见性检查
    day_ahead_tree_nodes: pd.DataFrame
    day_ahead_node_policy: pd.DataFrame
    day_ahead_nonanticipativity_report: pd.DataFrame

    # 每个10分钟实际执行时的信息边界检查
    runtime_causality_report: pd.DataFrame

    # 最终物理/费用合法性
    legality_report: pd.DataFrame


@dataclass
class Question2PeriodResult:
    """
    多日滚动结果。

    formal_results:
        默认只保存2025-02-01及以后单日结果。

    cross_day_report:
        检查[Q2-10] E[d+1,0]=E[d,144]。
    """

    formal_results: Dict[pd.Timestamp, Question2DayResult]
    cross_day_report: pd.DataFrame
    warmup_end_energy_kwh: Optional[float]
    final_energy_kwh: float


# ============================================================================
# 公共准备函数
# ============================================================================


def _normalize_date(value) -> pd.Timestamp:
    return pd.Timestamp(value).normalize()


def _prepare_fixed_price(
    attachment1: Attachment1Data,
    config: ProjectConfig,
) -> pd.Series:
    """
    问题2沿用附件1固定日内电价。

    只按attachment1.aligned中的模型k=0~143读取，
    不搜索任何Excel时间字符串。
    """
    aligned = attachment1.aligned

    required = {"k", "price_yuan_per_kwh"}
    missing = required.difference(aligned.columns)
    if missing:
        raise ValueError(
            f"附件1处理结果缺少字段：{sorted(missing)}"
        )

    expected_k = list(range(config.intervals_per_day))

    if aligned["k"].astype(int).tolist() != expected_k:
        raise ValueError(
            "附件1.aligned的k必须严格为0~143。"
        )

    price = pd.to_numeric(
        aligned["price_yuan_per_kwh"],
        errors="raise",
    ).astype(float)
    price.index = expected_k
    price.name = "price_yuan_per_kwh"

    if price.isna().any():
        raise ValueError("固定电价存在缺失值。")

    if (price < 0).any():
        raise ValueError("当前问题2实现要求电价非负。")

    return price


def _validate_attachment2_model_grid(
    attachment2: Attachment2Data,
    config: ProjectConfig,
) -> None:
    expected_k = list(range(config.intervals_per_day))

    for name, frame in [
        ("load_kw", attachment2.load_kw),
        ("pv_kw", attachment2.pv_kw),
    ]:
        if list(frame.columns) != expected_k:
            raise ValueError(
                f"attachment2.{name}必须严格使用模型k=0~143。"
            )

        if frame.isna().any().any():
            raise ValueError(
                f"attachment2.{name}存在缺失值。"
            )

    if not attachment2.load_kw.index.equals(
        attachment2.pv_kw.index
    ):
        raise ValueError("附件2负荷/光伏日期不一致。")


def _seed_for(
    base_seed: int,
    date: pd.Timestamp,
    k: int = 0,
) -> int:
    """
    生成可复现实验随机种子。
    不读取任何未来数据。
    """
    day_number = int(date.dayofyear)
    return int(base_seed + day_number * 1000 + int(k))


def settle_realized_interval_after_storage(
    *,
    q_buy_kwh: float,
    q_ch_kwh: float,
    q_dis_kwh: float,
    actual_load_kwh: float,
    actual_pv_kwh: float,
    tolerance_kwh: float = 1e-9,
) -> tuple[float, float, float, float]:
    """
    在第k个10分钟储能动作已经确定之后，根据该区间最终实现的
    真实负荷/光伏计算事后补救量。

    时序：
        tau_k:
            q_buy[k] 已由0:00锁定；
            q_ch[k], q_dis[k] 只基于0..k-1历史和E_k决定。
        [tau_k, tau_{k+1})结束：
            actual_load[k], actual_pv[k] 才完整实现；
            随后计算 q_emg[k], q_curt[k], q_sur[k] 完成实际能量平衡。

    实际能量平衡：
        q_buy + q_emg + G_actual + q_dis
        =
        L_actual + q_ch + q_curt + q_sur

    分配规则：
    1. 若出现缺口，全部由紧急购电q_emg补齐；
    2. 若出现富余，优先将可再生光伏计为弃光，剩余部分计入q_sur；
    3. q_curt永远不超过actual_pv；
    4. 不允许负购电或售电。

    返回：
        q_emg, q_curt, q_sur, balance_residual
    """
    values = {
        "q_buy_kwh": q_buy_kwh,
        "q_ch_kwh": q_ch_kwh,
        "q_dis_kwh": q_dis_kwh,
        "actual_load_kwh": actual_load_kwh,
        "actual_pv_kwh": actual_pv_kwh,
    }

    for name, value in values.items():
        if float(value) < -tolerance_kwh:
            raise ValueError(f"{name}不能为负：{value}")

    q_buy = max(0.0, float(q_buy_kwh))
    q_ch = max(0.0, float(q_ch_kwh))
    q_dis = max(0.0, float(q_dis_kwh))
    load = max(0.0, float(actual_load_kwh))
    pv = max(0.0, float(actual_pv_kwh))

    net_before_expost = (
        q_buy + pv + q_dis - load - q_ch
    )

    if net_before_expost < 0.0:
        q_emg = -net_before_expost
        q_curt = 0.0
        q_sur = 0.0
    else:
        q_emg = 0.0
        q_curt = min(pv, net_before_expost)
        q_sur = net_before_expost - q_curt

    residual = (
        q_buy
        + q_emg
        + pv
        + q_dis
        - load
        - q_ch
        - q_curt
        - q_sur
    )

    if abs(residual) > max(tolerance_kwh, 1e-8):
        raise AssertionError(
            "事后补救未能闭合实际能量平衡："
            f"residual={residual}"
        )

    return (
        float(q_emg),
        float(q_curt),
        float(q_sur),
        float(residual),
    )


# ============================================================================
# 场景树Gurobi模型
# ============================================================================


def _solve_tree_optimization(
    *,
    tree: NonanticipativeScenarioTree,
    price_yuan_per_kwh: pd.Series,
    initial_energy_kwh: float,
    config: ProjectConfig,
    settings: Question2Settings,
    q_buy_fixed_kwh: Optional[pd.Series] = None,
    model_name: str = "q2_tree",
) -> TreeOptimizationSolution:
    """
    对一个非预见场景树求解Q2运行模型。

    两种模式
    --------
    1. q_buy_fixed_kwh is None:
       0:00日前优化。创建唯一的 q_buy[k]，对所有未来场景共享。

    2. q_buy_fixed_kwh is not None:
       实时条件滚动补救。q_buy全天已经在0:00锁定，
       本模型不能改变它，只优化节点补救动作。

    节点动作
    --------
    q_ch[node_id]
    q_dis[node_id]
    q_emg[node_id]
    q_curt[node_id]
    q_sur[node_id]
    E[node_id]

    因此没有leaf-indexed全天储能动作。
    """
    settings.validate()

    if not (
        E_MIN_KWH <= initial_energy_kwh <= E_MAX_KWH
    ):
        raise ValueError(
            f"initial_energy_kwh={initial_energy_kwh}超出"
            f"[{E_MIN_KWH},{E_MAX_KWH}]。"
        )

    expected_k = list(range(config.intervals_per_day))
    if list(price_yuan_per_kwh.index) != expected_k:
        raise ValueError("price_yuan_per_kwh.index必须严格为0~143。")

    if q_buy_fixed_kwh is not None:
        if list(q_buy_fixed_kwh.index) != expected_k:
            raise ValueError(
                "q_buy_fixed_kwh.index必须严格为0~143。"
            )
        if (q_buy_fixed_kwh < -1e-9).any():
            raise ValueError("固定的0:00计划购电量不能为负。")

    # 先验证随机信息结构。
    tree_report = tree.validate_nonanticipativity()
    if not tree_report["passed"].all():
        raise AssertionError(
            "场景树未通过非预见性检查，禁止进入优化。"
        )

    model = gp.Model(model_name)
    model.Params.OutputFlag = 1 if settings.solver_output else 0

    node_ids = tuple(sorted(tree.nodes))
    k_all = tuple(range(config.intervals_per_day))
    q_max = P_BAT_MAX_KW * config.dt_minutes / 60.0

    # ------------------------------------------------------------------
    # 0:00唯一计划购电变量
    # ------------------------------------------------------------------
    if q_buy_fixed_kwh is None:
        # [Q2-01] 一套q_buy[k]对所有场景共同生效。
        q_buy = model.addVars(
            k_all,
            lb=0.0,
            vtype=GRB.CONTINUOUS,
            name="q_buy",
        )
    else:
        q_buy = None

    # ------------------------------------------------------------------
    # 节点补救变量：每个信息节点仅一套动作 [Q2-09]
    # ------------------------------------------------------------------
    q_ch = model.addVars(
        node_ids,
        lb=0.0,
        ub=q_max,
        vtype=GRB.CONTINUOUS,
        name="q_ch",
    )
    q_dis = model.addVars(
        node_ids,
        lb=0.0,
        ub=q_max,
        vtype=GRB.CONTINUOUS,
        name="q_dis",
    )
    q_emg = model.addVars(
        node_ids,
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="q_emg",
    )
    q_curt = model.addVars(
        node_ids,
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="q_curt",
    )
    q_sur = model.addVars(
        node_ids,
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="q_sur",
    )

    # [Q2-04] 节点动作执行前的储能内部电量。
    E = model.addVars(
        node_ids,
        lb=E_MIN_KWH,
        ub=E_MAX_KWH,
        vtype=GRB.CONTINUOUS,
        name="E",
    )

    z = None
    if settings.enforce_charge_discharge_exclusivity:
        z = model.addVars(
            node_ids,
            vtype=GRB.BINARY,
            name="z",
        )

    # ------------------------------------------------------------------
    # 根节点当前真实/初始SOC
    # ------------------------------------------------------------------
    for root_id in tree.root_node_ids():
        model.addConstr(
            E[root_id] == float(initial_energy_kwh),
            name=f"root_energy[{root_id}]",
        )

    # ------------------------------------------------------------------
    # [Q2-02] 节点能量平衡
    # ------------------------------------------------------------------
    for node_id in node_ids:
        node = tree.nodes[node_id]
        k = node.k

        if q_buy is None:
            buy_expr = float(q_buy_fixed_kwh.loc[k])
        else:
            buy_expr = q_buy[k]

        model.addConstr(
            buy_expr
            + q_emg[node_id]
            + float(node.pv_kwh)
            + q_dis[node_id]
            ==
            float(node.load_kwh)
            + q_ch[node_id]
            + q_curt[node_id]
            + q_sur[node_id],
            name=f"energy_balance[{node_id}]",
        )

        # [Q2-06] 0 <= q_curt <= 当前节点光伏
        model.addConstr(
            q_curt[node_id] <= float(node.pv_kwh),
            name=f"curtailment_upper[{node_id}]",
        )

        if z is not None:
            # 可选MILP互斥；默认不启用。
            model.addConstr(
                q_ch[node_id] <= q_max * z[node_id],
                name=f"charge_exclusivity[{node_id}]",
            )
            model.addConstr(
                q_dis[node_id] <= q_max * (1 - z[node_id]),
                name=f"discharge_exclusivity[{node_id}]",
            )

    # ------------------------------------------------------------------
    # [Q2-03] 父子节点SOC状态转移
    # ------------------------------------------------------------------
    for node_id in node_ids:
        node = tree.nodes[node_id]

        if node.parent_id is None:
            continue

        parent_id = int(node.parent_id)

        model.addConstr(
            E[node_id]
            ==
            E[parent_id]
            + ETA_C * q_ch[parent_id]
            - q_dis[parent_id] / ETA_D,
            name=f"storage_transition[{parent_id}->{node_id}]",
        )

    # 最后一个10 min动作执行后也必须保持SOC安全。
    for leaf_id in tree.leaf_node_ids():
        terminal_expr = (
            E[leaf_id]
            + ETA_C * q_ch[leaf_id]
            - q_dis[leaf_id] / ETA_D
        )

        model.addConstr(
            terminal_expr >= E_MIN_KWH,
            name=f"terminal_energy_lower[{leaf_id}]",
        )
        model.addConstr(
            terminal_expr <= E_MAX_KWH,
            name=f"terminal_energy_upper[{leaf_id}]",
        )

    # ------------------------------------------------------------------
    # [Q2-01] 计划购电费用
    # ------------------------------------------------------------------
    if q_buy is None:
        plan_cost_expr = gp.LinExpr(0.0)
    else:
        plan_cost_expr = gp.quicksum(
            float(price_yuan_per_kwh.loc[k]) * q_buy[k]
            for k in k_all
        )

    # ------------------------------------------------------------------
    # [Q2-07] 5倍紧急购电期望费用
    # E(C_emg)=5 sum_n rho_n p_k q_emg[n]
    # ------------------------------------------------------------------
    expected_emergency_expr = gp.quicksum(
        5.0
        * float(tree.nodes[node_id].probability)
        * float(price_yuan_per_kwh.loc[tree.nodes[node_id].k])
        * q_emg[node_id]
        for node_id in node_ids
    )

    # ------------------------------------------------------------------
    # [Q2-11] 可选CVaR：严格基于叶路径紧急购电损失
    # ------------------------------------------------------------------
    cvar_expr = None
    zeta = None
    u = None

    if settings.cvar_lambda > 0.0:
        leaf_ids = tree.leaf_node_ids()

        zeta = model.addVar(
            lb=0.0,
            vtype=GRB.CONTINUOUS,
            name="cvar_zeta",
        )
        u = model.addVars(
            leaf_ids,
            lb=0.0,
            vtype=GRB.CONTINUOUS,
            name="cvar_u",
        )

        for leaf_id in leaf_ids:
            path = tree.path_to_leaf(leaf_id)

            leaf_loss_expr = gp.quicksum(
                5.0
                * float(
                    price_yuan_per_kwh.loc[
                        tree.nodes[node_id].k
                    ]
                )
                * q_emg[node_id]
                for node_id in path
            )

            model.addConstr(
                u[leaf_id] >= leaf_loss_expr - zeta,
                name=f"cvar_excess[{leaf_id}]",
            )

        cvar_expr = (
            zeta
            + 1.0
            / (1.0 - settings.cvar_alpha)
            * gp.quicksum(
                float(tree.nodes[leaf_id].probability)
                * u[leaf_id]
                for leaf_id in leaf_ids
            )
        )

        # [Q2-08] + [Q2-11]
        objective = (
            plan_cost_expr
            + (1.0 - settings.cvar_lambda)
            * expected_emergency_expr
            + settings.cvar_lambda * cvar_expr
        )
    else:
        # [Q2-08] 风险中性主模型
        objective = (
            plan_cost_expr
            + expected_emergency_expr
        )

    model.setObjective(objective, GRB.MINIMIZE)
    model.optimize()

    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(
            f"{model_name}未获得最优解，Gurobi Status={model.Status}"
        )

    # ------------------------------------------------------------------
    # 提取q_buy
    # ------------------------------------------------------------------
    if q_buy is None:
        q_buy_result = q_buy_fixed_kwh.astype(float).copy()
    else:
        q_buy_result = pd.Series(
            {
                k: float(q_buy[k].X)
                for k in k_all
            },
            dtype=float,
            name="plan_purchase_kwh",
        )

    # ------------------------------------------------------------------
    # 提取node policy：一node一动作
    # ------------------------------------------------------------------
    policy_rows = []

    for node_id in node_ids:
        node = tree.nodes[node_id]

        policy_rows.append(
            {
                "node_id": node_id,
                "k": node.k,
                "parent_id": node.parent_id,
                "probability": node.probability,
                "member_scenarios": node.member_scenarios,
                "load_kwh": node.load_kwh,
                "pv_kwh": node.pv_kwh,
                "q_ch_kwh": float(q_ch[node_id].X),
                "q_dis_kwh": float(q_dis[node_id].X),
                "q_emg_kwh": float(q_emg[node_id].X),
                "q_curt_kwh": float(q_curt[node_id].X),
                "q_sur_kwh": float(q_sur[node_id].X),
                "E_pre_kwh": float(E[node_id].X),
            }
        )

    node_policy = pd.DataFrame(policy_rows)

    expected_emergency_cost = float(
        sum(
            5.0
            * tree.nodes[node_id].probability
            * float(
                price_yuan_per_kwh.loc[
                    tree.nodes[node_id].k
                ]
            )
            * float(q_emg[node_id].X)
            for node_id in node_ids
        )
    )

    if q_buy is None:
        plan_cost_value = 0.0
    else:
        plan_cost_value = float(
            sum(
                float(price_yuan_per_kwh.loc[k])
                * float(q_buy[k].X)
                for k in k_all
            )
        )

    # 叶路径紧急购电损失，用于CVaR审计。
    leaf_rows = []
    for leaf_id in tree.leaf_node_ids():
        path = tree.path_to_leaf(leaf_id)
        loss = float(
            sum(
                5.0
                * float(
                    price_yuan_per_kwh.loc[
                        tree.nodes[node_id].k
                    ]
                )
                * float(q_emg[node_id].X)
                for node_id in path
            )
        )

        leaf_rows.append(
            {
                "leaf_id": leaf_id,
                "probability": tree.nodes[leaf_id].probability,
                "emergency_loss_yuan": loss,
                "path_node_ids": path,
            }
        )

    leaf_emergency_loss = pd.DataFrame(leaf_rows)

    cvar_value = None
    if cvar_expr is not None:
        cvar_value = float(cvar_expr.getValue())

    return TreeOptimizationSolution(
        q_buy_kwh=q_buy_result,
        node_policy=node_policy,
        objective_value=float(model.ObjVal),
        expected_emergency_cost_yuan=expected_emergency_cost,
        plan_cost_yuan=plan_cost_value,
        leaf_emergency_loss=leaf_emergency_loss,
        cvar_value_yuan=cvar_value,
    )


def _build_solver_nonanticipativity_report(
    tree: NonanticipativeScenarioTree,
    solution: TreeOptimizationSolution,
) -> pd.DataFrame:
    """
    场景树结构 + 优化动作索引联合检查。

    重点确认：
    - 每个node_id只有一行动作；
    - 动作表没有leaf_id索引；
    - q_buy只有一条144时段计划，不按场景重复。
    """
    base = tree.validate_nonanticipativity().copy()

    extra_rows = []

    policy = solution.node_policy
    node_unique = (
        len(policy) == len(tree.nodes)
        and policy["node_id"].is_unique
        and set(policy["node_id"]) == set(tree.nodes)
    )

    extra_rows.append(
        {
            "item": "one_action_row_per_information_node",
            "passed": bool(node_unique),
            "detail": (
                f"node数量={len(tree.nodes)}；"
                f"policy行数={len(policy)}；"
                f"node_id唯一={policy['node_id'].is_unique}"
            ),
        }
    )

    extra_rows.append(
        {
            "item": "no_leaf_indexed_advance_action",
            "passed": "leaf_id" not in policy.columns,
            "detail": (
                "储能/紧急购电等动作只按node_id索引，"
                "没有按完整叶场景提前创建全天动作。"
            ),
        }
    )

    q_buy_ok = (
        list(solution.q_buy_kwh.index) == list(range(144))
    )
    extra_rows.append(
        {
            "item": "single_day_ahead_q_buy_plan",
            "passed": bool(q_buy_ok),
            "detail": (
                "q_buy仅有k=0~143一套计划，对全部未来场景共享。"
            ),
        }
    )

    return pd.concat(
        [base, pd.DataFrame(extra_rows)],
        ignore_index=True,
    )


# ============================================================================
# 结果合法性检查
# ============================================================================


def check_question2_day_result_legality(
    *,
    result: Question2DayResult,
    attachment2: Attachment2Data,
    price_yuan_per_kwh: pd.Series,
    config: ProjectConfig = DEFAULT_CONFIG,
    tolerance_kwh: float = 1e-5,
    tolerance_yuan: float = 1e-5,
    enforce_charge_discharge_exclusivity: bool = False,
) -> pd.DataFrame:
    """
    单日运行结束后的事后合法性检查。

    注意：
    本函数可以在一天结束后读取完整当天实际轨迹，
    因为它只做事后审计，不参与此前任何决策。
    """
    d = result.date
    k_all = list(range(config.intervals_per_day))
    j_all = list(range(config.state_nodes_per_day))

    dt_hours = config.dt_minutes / 60.0

    actual_load_kwh = (
        attachment2.load_kw.loc[d].astype(float)
        * dt_hours
    )
    actual_pv_kwh = (
        attachment2.pv_kw.loc[d].astype(float)
        * dt_hours
    )
    actual_load_kwh.index = k_all
    actual_pv_kwh.index = k_all

    q_buy = result.plan_purchase_kwh
    q_ch = result.actual_charge_kwh
    q_dis = result.actual_discharge_kwh
    q_emg = result.actual_emergency_kwh
    q_curt = result.actual_curtailment_kwh
    q_sur = result.actual_surplus_kwh
    E = result.energy_kwh

    rows = []

    def add(
        item: str,
        passed: bool,
        detail: str,
        residual: Optional[float] = None,
    ) -> None:
        rows.append(
            {
                "item": item,
                "passed": bool(passed),
                "max_residual": residual,
                "detail": detail,
            }
        )

    for name, series, expected in [
        ("q_buy", q_buy, k_all),
        ("q_ch", q_ch, k_all),
        ("q_dis", q_dis, k_all),
        ("q_emg", q_emg, k_all),
        ("q_curt", q_curt, k_all),
        ("q_sur", q_sur, k_all),
        ("E", E, j_all),
    ]:
        ok = list(series.index) == expected
        add(
            f"{name}_index",
            ok,
            f"长度={len(series)}；期望={len(expected)}。",
        )

    # 非负
    for name, series in [
        ("q_buy", q_buy),
        ("q_ch", q_ch),
        ("q_dis", q_dis),
        ("q_emg", q_emg),
        ("q_curt", q_curt),
        ("q_sur", q_sur),
    ]:
        min_value = float(series.min())
        add(
            f"{name}_nonnegative",
            min_value >= -tolerance_kwh,
            f"最小值={min_value:.12g}",
            max(0.0, -min_value),
        )

    # [Q2-02] 实际轨迹能量平衡
    balance = (
        q_buy
        + q_emg
        + actual_pv_kwh
        + q_dis
        - actual_load_kwh
        - q_ch
        - q_curt
        - q_sur
    )
    balance_max = float(balance.abs().max())
    add(
        "[Q2-02] actual_energy_balance",
        balance_max <= tolerance_kwh,
        f"最大绝对残差={balance_max:.12g} kWh。",
        balance_max,
    )

    # [Q2-03] 实际SOC转移
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
        "[Q2-03] actual_storage_transition",
        transition_max <= tolerance_kwh,
        f"最大绝对残差={transition_max:.12g} kWh。",
        transition_max,
    )

    # [Q2-04] SOC边界
    lower = float((E_MIN_KWH - E).clip(lower=0).max())
    upper = float((E - E_MAX_KWH).clip(lower=0).max())
    soc_violation = max(lower, upper)
    add(
        "[Q2-04] actual_energy_bounds",
        soc_violation <= tolerance_kwh,
        f"下界违反={lower:.12g}；上界违反={upper:.12g}。",
        soc_violation,
    )

    # [Q2-05] 充放电限制
    q_max = P_BAT_MAX_KW * dt_hours
    ch_v = float((q_ch - q_max).clip(lower=0).max())
    dis_v = float((q_dis - q_max).clip(lower=0).max())
    limit_v = max(ch_v, dis_v)
    add(
        "[Q2-05] charge_discharge_limit",
        limit_v <= tolerance_kwh,
        f"q_max={q_max:.12g}; ch_v={ch_v:.12g}; dis_v={dis_v:.12g}",
        limit_v,
    )

    # [Q2-06] 弃光
    curt_v = float(
        (q_curt - actual_pv_kwh).clip(lower=0).max()
    )
    add(
        "[Q2-06] curtailment_upper",
        curt_v <= tolerance_kwh,
        f"最大违反={curt_v:.12g} kWh。",
        curt_v,
    )

    if enforce_charge_discharge_exclusivity:
        simultaneous = pd.concat(
            [q_ch, q_dis],
            axis=1,
        ).min(axis=1)
        sim_max = float(simultaneous.max())
        add(
            "charge_discharge_exclusivity",
            sim_max <= tolerance_kwh,
            f"最大同时充放电={sim_max:.12g} kWh。",
            sim_max,
        )
    else:
        add(
            "charge_discharge_exclusivity",
            True,
            "连续LP主模型默认未强制二进制互斥。",
            0.0,
        )

    # 初始/末端
    initial_resid = abs(
        float(E.loc[0]) - float(result.initial_energy_kwh)
    )
    end_resid = abs(
        float(E.loc[144]) - float(result.end_energy_kwh)
    )
    add(
        "initial_energy_consistency",
        initial_resid <= tolerance_kwh,
        f"残差={initial_resid:.12g} kWh。",
        initial_resid,
    )
    add(
        "end_energy_consistency",
        end_resid <= tolerance_kwh,
        f"残差={end_resid:.12g} kWh。",
        end_resid,
    )

    # 费用
    plan_cost = float((price_yuan_per_kwh * q_buy).sum())
    emergency_cost = float(
        (
            5.0
            * price_yuan_per_kwh
            * q_emg
        ).sum()
    )
    total_cost = plan_cost + emergency_cost

    add(
        "[Q2-01] plan_cost",
        abs(plan_cost - result.plan_cost_yuan)
        <= tolerance_yuan,
        (
            f"结果={result.plan_cost_yuan:.12g}; "
            f"重算={plan_cost:.12g}"
        ),
        abs(plan_cost - result.plan_cost_yuan),
    )
    add(
        "[Q2-07] emergency_cost",
        abs(emergency_cost - result.emergency_cost_yuan)
        <= tolerance_yuan,
        (
            f"结果={result.emergency_cost_yuan:.12g}; "
            f"重算={emergency_cost:.12g}"
        ),
        abs(emergency_cost - result.emergency_cost_yuan),
    )
    add(
        "[Q2-08] total_cost",
        abs(total_cost - result.total_cost_yuan)
        <= tolerance_yuan,
        (
            f"结果={result.total_cost_yuan:.12g}; "
            f"重算={total_cost:.12g}"
        ),
        abs(total_cost - result.total_cost_yuan),
    )

    # 非预见性
    day_tree_ok = bool(
        result.day_ahead_nonanticipativity_report["passed"].all()
    )
    add(
        "[Q2-09] day_ahead_nonanticipativity",
        day_tree_ok,
        "0:00场景树及node-indexed动作检查结果。",
    )

    runtime = result.runtime_causality_report
    runtime_ok = bool(
        runtime["future_actual_used"].eq(False).all()
        and (
            runtime["max_observed_k"].astype(int)
            == runtime["k"].astype(int) - 1
        ).all()
        and (
            runtime["observed_points"].astype(int)
            == runtime["k"].astype(int)
        ).all()
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
        "runtime_causal_recourse",
        runtime_ok,
        (
            "在tau_k储能决策前只允许0..k-1真实前缀；"
            "current_k真实值只在动作确定后用于紧急购电/弃光/富余结算；"
            "当前条件树唯一根且事后能量平衡闭合。"
        ),
    )

    return pd.DataFrame(rows)


def assert_question2_day_result_legal(
    report: pd.DataFrame,
) -> None:
    failed = report.loc[~report["passed"]]
    if failed.empty:
        return

    raise AssertionError(
        "问题2单日结果合法性检查失败：\n"
        + failed.to_string(index=False)
    )


# ============================================================================
# Question2Solver
# ============================================================================


class Question2Solver:
    """
    问题2全年/单日求解器。

    注意：
    model_base.py 的单路径公共变量是按k定义；
    问题2实时补救必须升级为场景树node_id索引。
    因此本求解器复用model_base已冻结的参数、单位和变量命名，
    但节点动作必须按node_id重新创建，不能错误复用单路径q_ch[k]
    来表示多个不确定节点。
    """

    def __init__(
        self,
        *,
        attachment1: Attachment1Data,
        attachment2: Attachment2Data,
        settings: Question2Settings = Question2Settings(),
        config: ProjectConfig = DEFAULT_CONFIG,
    ) -> None:
        settings.validate()
        _validate_attachment2_model_grid(
            attachment2,
            config,
        )

        self.attachment1 = attachment1
        self.attachment2 = attachment2
        self.settings = settings
        self.config = config

        self.time_map = build_time_map(config)
        validate_time_map(self.time_map, config)

        self.price_yuan_per_kwh = _prepare_fixed_price(
            attachment1,
            config,
        )

        self.dt_hours = config.dt_minutes / 60.0

    def _check_date_exists(
        self,
        date,
    ) -> pd.Timestamp:
        d = _normalize_date(date)

        if d not in self.attachment2.load_kw.index:
            raise KeyError(f"附件2中不存在日期{d.date()}。")
        if d not in self.attachment2.pv_kw.index:
            raise KeyError(f"附件2光伏中不存在日期{d.date()}。")

        return d

    def _build_day_ahead_tree(
        self,
        date: pd.Timestamp,
    ) -> tuple[
        DayAheadForecast,
        ResidualLibrary,
        ScenarioTrajectorySet,
        NonanticipativeScenarioTree,
    ]:
        """
        0:00只使用date之前历史构造预测、残差和场景树。
        """
        forecast = build_q2_day_ahead_forecast(
            self.attachment2,
            date,
            config=self.config,
        )

        residual_library = build_causal_residual_library(
            self.attachment2,
            date,
            max_residual_days=self.settings.max_residual_days,
            config=self.config,
        )

        # 强制信息边界审计
        if forecast.history_end_date is not None:
            if not forecast.history_end_date < date:
                raise AssertionError("0:00预测读取了当天/未来真实数据。")

        if residual_library.n_days > 0:
            if not (residual_library.dates < date).all():
                raise AssertionError("0:00残差库混入当天/未来数据。")

        bootstrap = build_bootstrap_trajectory_set(
            forecast,
            residual_library,
            n_bootstrap=self.settings.dayahead_bootstrap_scenarios,
            random_state=_seed_for(
                self.settings.random_seed,
                date,
                0,
            ),
        )

        reduced = reduce_trajectory_set(
            bootstrap,
            n_representatives=(
                self.settings.dayahead_reduced_scenarios
            ),
        )

        tree = build_nonanticipative_tree(
            reduced,
            branch_every=self.settings.dayahead_branch_every,
            max_branch=self.settings.dayahead_max_branch,
            force_single_root=False,
        )

        return forecast, residual_library, reduced, tree


    def _read_current_actual_kwh(
        self,
        date: pd.Timestamp,
        k: int,
    ) -> tuple[float, float]:
        """
        读取刚刚完成的第k个物理区间真实负荷/光伏。

        重要：
        本函数虽然仍保留原接口名以兼容前文代码，但只能在：
            第k个区间储能动作q_ch[k]/q_dis[k]已经决定之后
        调用。

        它返回的是：
            I_k=[tau_k,tau_{k+1})
        整个区间最终实现的10分钟电量。

        禁止在tau_k决定当前储能动作之前调用本函数。
        """
        if not (0 <= k < self.config.intervals_per_day):
            raise ValueError("k必须位于0~143。")

        load_kw = float(
            self.attachment2.load_kw.at[date, k]
        )
        pv_kw = float(
            self.attachment2.pv_kw.at[date, k]
        )

        return (
            load_kw * self.dt_hours,
            pv_kw * self.dt_hours,
        )


    def _run_causal_actual_day(
        self,
        *,
        date: pd.Timestamp,
        forecast: DayAheadForecast,
        residual_library: ResidualLibrary,
        plan_purchase_kwh: pd.Series,
        initial_energy_kwh: float,
    ) -> tuple[
        pd.Series,
        pd.Series,
        pd.Series,
        pd.Series,
        pd.Series,
        pd.Series,
        pd.DataFrame,
    ]:
        """
        严格因果的10分钟滚动补救。

        对每个物理区间k，执行顺序严格为：

        A. tau_k决策前：
           - 已知真实历史只有0..k-1；
           - 已知当前真实SOC E_k；
           - q_buy[k]仍是0:00锁定计划；
           - 基于历史分布构造k..143条件场景；
           - 只决定当前q_ch[k]/q_dis[k]。

        B. 区间I_k结束后：
           - 第k区间真实负荷/光伏才完整实现；
           - 再计算实际q_emg[k]/q_curt[k]/q_sur[k]闭合能量平衡；
           - 更新E_{k+1}；
           - 把实际k加入历史，供下一时段k+1使用。

        因此current_k真实值绝不会用于current_k储能动作。
        """
        k_all = list(range(self.config.intervals_per_day))

        # 在决定k动作前，这两个Series只能包含0..k-1。
        observed_load = pd.Series(dtype=float)
        observed_pv = pd.Series(dtype=float)

        q_ch_actual = pd.Series(
            index=k_all,
            dtype=float,
            name="actual_charge_kwh",
        )
        q_dis_actual = pd.Series(
            index=k_all,
            dtype=float,
            name="actual_discharge_kwh",
        )
        q_emg_actual = pd.Series(
            index=k_all,
            dtype=float,
            name="actual_emergency_kwh",
        )
        q_curt_actual = pd.Series(
            index=k_all,
            dtype=float,
            name="actual_curtailment_kwh",
        )
        q_sur_actual = pd.Series(
            index=k_all,
            dtype=float,
            name="actual_surplus_kwh",
        )

        E_actual = pd.Series(
            index=list(range(self.config.state_nodes_per_day)),
            dtype=float,
            name="energy_kwh",
        )
        E_actual.loc[0] = float(initial_energy_kwh)

        runtime_rows = []
        current_energy = float(initial_energy_kwh)

        for k in k_all:
            # --------------------------------------------------------------
            # 1. tau_k：严格检查真实信息只有0..k-1
            # --------------------------------------------------------------
            expected_prefix = list(range(k))
            if list(observed_load.index) != expected_prefix:
                raise AssertionError(
                    f"k={k}决策前真实负荷前缀必须严格为0..{k-1}。"
                )
            if list(observed_pv.index) != expected_prefix:
                raise AssertionError(
                    f"k={k}决策前真实光伏前缀必须严格为0..{k-1}。"
                )

            conditional_bootstrap = (
                build_conditional_trajectory_set(
                    forecast,
                    residual_library,
                    observed_load_kwh=observed_load.copy(),
                    observed_pv_kwh=observed_pv.copy(),
                    current_k=k,
                    n_bootstrap=(
                        self.settings.rolling_bootstrap_scenarios
                    ),
                    conditioning_pool=(
                        self.settings.conditioning_pool
                    ),
                    random_state=_seed_for(
                        self.settings.random_seed,
                        date,
                        k,
                    ),
                    config=self.config,
                )
            )

            conditional_reduced = reduce_trajectory_set(
                conditional_bootstrap,
                n_representatives=(
                    self.settings.rolling_reduced_scenarios
                ),
            )

            conditional_tree = build_nonanticipative_tree(
                conditional_reduced,
                branch_every=(
                    self.settings.rolling_branch_every
                ),
                max_branch=self.settings.rolling_max_branch,
                force_single_root=True,
            )

            tree_check = (
                conditional_tree.validate_nonanticipativity()
            )
            tree_passed = bool(tree_check["passed"].all())

            root_ids = conditional_tree.root_node_ids()
            single_root = len(root_ids) == 1

            if not single_root:
                raise AssertionError(
                    f"current_k={k}条件补救树必须只有一个当前信息根节点。"
                )

            # --------------------------------------------------------------
            # 2. 在不知道current_k真实值的条件下决定储能动作
            # --------------------------------------------------------------
            recourse_solution = _solve_tree_optimization(
                tree=conditional_tree,
                price_yuan_per_kwh=self.price_yuan_per_kwh,
                initial_energy_kwh=current_energy,
                config=self.config,
                settings=self.settings,
                q_buy_fixed_kwh=plan_purchase_kwh,
                model_name=f"q2_recourse_{date.date()}_k{k}",
            )

            root_id = int(root_ids[0])
            root_row = recourse_solution.node_policy.loc[
                recourse_solution.node_policy["node_id"]
                == root_id
            ]

            if len(root_row) != 1:
                raise AssertionError(
                    "当前根节点必须且只能有一行预决策动作。"
                )

            root_row = root_row.iloc[0]

            # 只有储能动作在tau_k真正执行。
            q_ch = float(root_row["q_ch_kwh"])
            q_dis = float(root_row["q_dis_kwh"])

            # --------------------------------------------------------------
            # 3. 储能动作确定以后，第k区间真实负荷/PV才实现
            # --------------------------------------------------------------
            load_now, pv_now = self._read_current_actual_kwh(
                date,
                k,
            )

            # --------------------------------------------------------------
            # 4. 事后紧急购电/弃光/计划富余闭合真实能量平衡
            # --------------------------------------------------------------
            (
                q_emg,
                q_curt,
                q_sur,
                balance_residual,
            ) = settle_realized_interval_after_storage(
                q_buy_kwh=float(plan_purchase_kwh.loc[k]),
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
                    f"k={k}执行后SOC越界：{next_energy}"
                )

            E_actual.loc[k] = current_energy
            E_actual.loc[k + 1] = next_energy
            current_energy = next_energy

            # --------------------------------------------------------------
            # 5. current_k结束后才写入真实历史，供k+1使用
            # --------------------------------------------------------------
            observed_load.loc[k] = load_now
            observed_pv.loc[k] = pv_now

            runtime_rows.append(
                {
                    "k": k,
                    "max_observed_k": k - 1,
                    "observed_points": k,
                    "future_actual_used": False,
                    "current_actual_used_for_storage_decision": False,
                    "current_actual_used_only_for_expost_balance": True,
                    "q_buy_plan_modified": False,
                    "single_current_root": single_root,
                    "conditional_tree_passed": tree_passed,
                    "current_root_id": root_id,
                    "current_root_expected_load_kwh": float(
                        root_row["load_kwh"]
                    ),
                    "current_root_expected_pv_kwh": float(
                        root_row["pv_kwh"]
                    ),
                    "realized_load_kwh": load_now,
                    "realized_pv_kwh": pv_now,
                    "predicted_root_q_emg_kwh_not_executed": float(
                        root_row["q_emg_kwh"]
                    ),
                    "expost_balance_residual_kwh": (
                        balance_residual
                    ),
                }
            )

        return (
            q_ch_actual,
            q_dis_actual,
            q_emg_actual,
            q_curt_actual,
            q_sur_actual,
            E_actual,
            pd.DataFrame(runtime_rows),
        )

    def solve_day(
        self,
        date,
        *,
        initial_energy_kwh: float,
        check_legality: bool = True,
    ) -> Question2DayResult:
        """
        求解并真实因果执行一天。

        0:00阶段：
            预测 -> 历史残差 -> 非预见场景树 -> 唯一q_buy计划

        实时阶段：
            current actual + current SOC
            -> 条件历史场景
            -> 固定q_buy的剩余期补救模型
            -> 只执行当前第一步
        """
        d = self._check_date_exists(date)

        if not (
            E_MIN_KWH
            <= float(initial_energy_kwh)
            <= E_MAX_KWH
        ):
            raise ValueError("initial_energy_kwh超出储能安全范围。")

        (
            forecast,
            residual_library,
            reduced,
            day_tree,
        ) = self._build_day_ahead_tree(d)

        # 0:00场景树模型：只锁定一套q_buy。
        day_solution = _solve_tree_optimization(
            tree=day_tree,
            price_yuan_per_kwh=self.price_yuan_per_kwh,
            initial_energy_kwh=float(initial_energy_kwh),
            config=self.config,
            settings=self.settings,
            q_buy_fixed_kwh=None,
            model_name=f"q2_dayahead_{d.date()}",
        )

        nonanticipativity_report = (
            _build_solver_nonanticipativity_report(
                day_tree,
                day_solution,
            )
        )

        if not nonanticipativity_report["passed"].all():
            raise AssertionError(
                "0:00模型未通过非预见性检查。"
            )

        plan_purchase = (
            day_solution.q_buy_kwh.astype(float).copy()
        )
        plan_purchase.name = "plan_purchase_kwh"

        (
            q_ch_actual,
            q_dis_actual,
            q_emg_actual,
            q_curt_actual,
            q_sur_actual,
            E_actual,
            runtime_report,
        ) = self._run_causal_actual_day(
            date=d,
            forecast=forecast,
            residual_library=residual_library,
            plan_purchase_kwh=plan_purchase,
            initial_energy_kwh=float(initial_energy_kwh),
        )

        plan_cost = float(
            (
                self.price_yuan_per_kwh
                * plan_purchase
            ).sum()
        )

        emergency_cost = float(
            (
                5.0
                * self.price_yuan_per_kwh
                * q_emg_actual
            ).sum()
        )

        total_cost = plan_cost + emergency_cost

        result = Question2DayResult(
            date=d,
            initial_energy_kwh=float(initial_energy_kwh),
            end_energy_kwh=float(E_actual.loc[144]),
            plan_purchase_kwh=plan_purchase,
            actual_charge_kwh=q_ch_actual,
            actual_discharge_kwh=q_dis_actual,
            actual_emergency_kwh=q_emg_actual,
            actual_curtailment_kwh=q_curt_actual,
            actual_surplus_kwh=q_sur_actual,
            energy_kwh=E_actual,
            plan_cost_yuan=plan_cost,
            emergency_cost_yuan=emergency_cost,
            total_cost_yuan=total_cost,
            total_plan_purchase_kwh=float(
                plan_purchase.sum()
            ),
            total_emergency_kwh=float(
                q_emg_actual.sum()
            ),
            load_forecast_kwh=forecast.load_kwh.copy(),
            pv_forecast_kwh=forecast.pv_kwh.copy(),
            day_ahead_tree_nodes=day_tree.to_frame(),
            day_ahead_node_policy=(
                day_solution.node_policy.copy()
            ),
            day_ahead_nonanticipativity_report=(
                nonanticipativity_report
            ),
            runtime_causality_report=runtime_report,
            legality_report=pd.DataFrame(),
        )

        legality = check_question2_day_result_legality(
            result=result,
            attachment2=self.attachment2,
            price_yuan_per_kwh=self.price_yuan_per_kwh,
            config=self.config,
            enforce_charge_discharge_exclusivity=(
                self.settings
                .enforce_charge_discharge_exclusivity
            ),
        )

        result.legality_report = legality

        if check_legality:
            assert_question2_day_result_legal(legality)

        return result

    def solve_period(
        self,
        *,
        start_date: str = "2025-01-01",
        end_date: str = "2025-12-31",
        initial_energy_kwh: float = 6000.0,
        save_from_date: str = "2025-02-01",
        check_legality: bool = True,
    ) -> Question2PeriodResult:
        """
        多日顺序滚动。

        [Q2-10]
            E^{act}_{d+1,0} = E^{act}_{d,144}

        默认：
        - 2025-01-01从6000 kWh开始；
        - 1月份正常模拟但不保存正式结果；
        - 2025-02-01起保存formal_results；
        - 绝不在2月1日重新把SOC设为6000。
        """
        start = _normalize_date(start_date)
        end = _normalize_date(end_date)
        save_from = _normalize_date(save_from_date)

        if end < start:
            raise ValueError("end_date不能早于start_date。")

        dates = pd.date_range(
            start,
            end,
            freq="D",
        )

        formal_results: Dict[
            pd.Timestamp,
            Question2DayResult
        ] = {}

        cross_rows = []

        current_energy = float(initial_energy_kwh)
        warmup_end_energy = None

        previous_date = None
        previous_end_energy = None

        for d in dates:
            if d not in self.attachment2.load_kw.index:
                raise KeyError(
                    f"附件2缺少日期{d.date()}，无法连续模拟。"
                )

            day_initial = current_energy

            # [Q2-10] 与前一天末SOC完全连续。
            if previous_date is not None:
                residual = abs(
                    day_initial - float(previous_end_energy)
                )
                cross_rows.append(
                    {
                        "previous_date": previous_date,
                        "current_date": d,
                        "previous_end_energy_kwh": (
                            previous_end_energy
                        ),
                        "current_initial_energy_kwh": (
                            day_initial
                        ),
                        "residual_kwh": residual,
                        "passed": residual <= 1e-8,
                    }
                )

            day_result = self.solve_day(
                d,
                initial_energy_kwh=day_initial,
                check_legality=check_legality,
            )

            current_energy = float(
                day_result.end_energy_kwh
            )

            print(
                f"[Q2] {d.date()} 完成：总成本 {day_result.total_cost_yuan:.2f} 元，"
                f"末SOC {current_energy:.2f} kWh",
                flush=True,
            )

            previous_date = d
            previous_end_energy = current_energy

            if d < save_from:
                # 暖启动结果不进入正式输出。
                warmup_end_energy = current_energy
            else:
                formal_results[d] = day_result

        cross_report = pd.DataFrame(cross_rows)

        if (
            not cross_report.empty
            and not cross_report["passed"].all()
        ):
            raise AssertionError(
                "跨日SOC连续性检查失败。"
            )

        return Question2PeriodResult(
            formal_results=formal_results,
            cross_day_report=cross_report,
            warmup_end_energy_kwh=warmup_end_energy,
            final_energy_kwh=float(current_energy),
        )
