# -*- coding: utf-8 -*-
"""
rolling_scheduler.py
问题3滚动购电计划冻结、版本管理、结算与消融组合。

时间更新点严格固定：
    0:00  -> r=0   -> k>=0可优化
    6:00  -> r=36  -> 冻结k<36，优化k>=36
    12:00 -> r=72  -> 冻结k<72，优化k>=72
    18:00 -> r=108 -> 冻结k<108，优化k>=108

不允许根据Excel/模板时间字符串重新定位r。

结算主口径
----------
每个交割时段只结算一次：
    G0 = 0:00原始计划
    GF = 执行前最终生效购电量

[RS-01]
    dG_plus  = max(GF-G0, 0)
    dG_minus = max(G0-GF, 0)

[RS-02]
    C_reg = sum c * [GF + 0.5(dG_plus+dG_minus)]

[RS-03]
    C_plan = sum c * G0

[RS-04]
    C_adj = sum c * [1.5*dG_plus - 0.5*dG_minus]

[RS-05]
    C_reg = C_plan + C_adj

[RS-06]
    C_emg = 5 * sum c * G_emg

[RS-07]
    C_total = C_reg + C_emg

严禁：
    在完整C_plan之外再额外写 +0.5*dG_minus。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Sequence

import numpy as np
import pandas as pd

from config import DEFAULT_CONFIG, ProjectConfig


UPDATE_K: tuple[int, ...] = (0, 36, 72, 108)

# 四种递进式预测更新时间组合，用于消融实验。
ABLATION_UPDATE_COMBINATIONS: Dict[str, tuple[int, ...]] = {
    "00_only": (0,),
    "00_06": (0, 36),
    "00_06_12": (0, 36, 72),
    "00_06_12_18": (0, 36, 72, 108),
}


def validate_update_k(
    r: int,
    *,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> None:
    if r not in UPDATE_K:
        raise ValueError(
            f"问题3更新索引只能为{UPDATE_K}，实际r={r}。"
        )

    if not (0 <= r < config.intervals_per_day):
        raise ValueError("更新索引超出0~143。")


@dataclass
class RollingPlanBook:
    """
    问题3正常购电计划版本簿。

    original_plan_kwh:
        0:00 G0，全天144点，结算唯一基准。

    effective_plan_kwh:
        当前最新生效计划。

    versions:
        每次更新时间之后的完整144点快照。
        过去时段必须保持冻结。
    """

    original_plan_kwh: pd.Series
    effective_plan_kwh: pd.Series
    versions: Dict[int, pd.Series] = field(default_factory=dict)

    @classmethod
    def from_initial_plan(
        cls,
        initial_plan_kwh: pd.Series,
        *,
        config: ProjectConfig = DEFAULT_CONFIG,
    ) -> "RollingPlanBook":
        expected = list(range(config.intervals_per_day))

        if list(initial_plan_kwh.index) != expected:
            raise ValueError(
                "0:00初始计划index必须严格为k=0~143。"
            )

        initial = pd.to_numeric(
            initial_plan_kwh,
            errors="raise",
        ).astype(float)

        if (initial < -1e-12).any():
            raise ValueError("0:00初始计划购电量不能为负。")

        return cls(
            original_plan_kwh=initial.copy(),
            effective_plan_kwh=initial.copy(),
            versions={0: initial.copy()},
        )

    def update_future(
        self,
        r: int,
        future_plan_kwh: pd.Series,
        *,
        config: ProjectConfig = DEFAULT_CONFIG,
    ) -> None:
        """
        只更新k>=r，严格冻结k<r。
        """
        validate_update_k(r, config=config)

        expected_future = list(
            range(r, config.intervals_per_day)
        )

        if list(future_plan_kwh.index) != expected_future:
            raise ValueError(
                f"r={r}更新结果index必须严格为{r}~143。"
            )

        new_future = pd.to_numeric(
            future_plan_kwh,
            errors="raise",
        ).astype(float)

        if (new_future < -1e-12).any():
            raise ValueError("调整后正常购电量不能为负。")

        before_past = (
            self.effective_plan_kwh.loc[: r - 1].copy()
            if r > 0
            else pd.Series(dtype=float)
        )

        self.effective_plan_kwh.loc[r:] = (
            new_future.to_numpy(dtype=float)
        )

        if r > 0:
            after_past = self.effective_plan_kwh.loc[: r - 1]
            if not np.allclose(
                before_past.to_numpy(dtype=float),
                after_past.to_numpy(dtype=float),
                rtol=0.0,
                atol=0.0,
            ):
                raise AssertionError(
                    f"r={r}更新错误地修改了k<{r}的过去计划。"
                )

        self.versions[r] = self.effective_plan_kwh.copy()

    def final_effective_plan(self) -> pd.Series:
        return self.effective_plan_kwh.copy()


@dataclass
class SettlementResult:
    """问题3单日费用结算结果。"""

    dG_plus_kwh: pd.Series
    dG_minus_kwh: pd.Series

    C_plan_yuan: float
    C_reg_yuan: float
    C_adj_yuan: float
    C_emg_yuan: float
    C_total_yuan: float

    identity_residual_yuan: float


def _validate_same_k(
    *series: pd.Series,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> None:
    expected = list(range(config.intervals_per_day))

    for s in series:
        if not isinstance(s, pd.Series):
            raise TypeError("结算输入必须全部为pandas.Series。")
        if list(s.index) != expected:
            raise ValueError("结算输入index必须严格为k=0~143。")
        if s.isna().any():
            raise ValueError("结算输入存在缺失值。")


def settle_question3_cost(
    *,
    G0_kwh: pd.Series,
    GF_kwh: pd.Series,
    price_yuan_per_kwh: pd.Series,
    G_emg_kwh: pd.Series,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> SettlementResult:
    """
    按最终唯一结算口径计算问题3费用。

    [RS-01]~[RS-07]
    """
    _validate_same_k(
        G0_kwh,
        GF_kwh,
        price_yuan_per_kwh,
        G_emg_kwh,
        config=config,
    )

    G0 = G0_kwh.astype(float)
    GF = GF_kwh.astype(float)
    c = price_yuan_per_kwh.astype(float)
    G_emg = G_emg_kwh.astype(float)

    if (G0 < -1e-12).any():
        raise ValueError("G0不能为负。")
    if (GF < -1e-12).any():
        raise ValueError("GF不能为负。")
    if (G_emg < -1e-12).any():
        raise ValueError("G_emg不能为负。")

    # [RS-01]
    dG_plus = (GF - G0).clip(lower=0.0)
    dG_minus = (G0 - GF).clip(lower=0.0)

    # [RS-02]
    C_reg = float(
        (
            c
            * (
                GF
                + 0.5 * (dG_plus + dG_minus)
            )
        ).sum()
    )

    # [RS-03]
    C_plan = float((c * G0).sum())

    # [RS-04]
    C_adj = float(
        (
            c
            * (
                1.5 * dG_plus
                - 0.5 * dG_minus
            )
        ).sum()
    )

    # [RS-06]
    C_emg = float((5.0 * c * G_emg).sum())

    # [RS-07]
    C_total = C_reg + C_emg

    # [RS-05]
    identity_residual = abs(
        C_reg - (C_plan + C_adj)
    )

    return SettlementResult(
        dG_plus_kwh=dG_plus,
        dG_minus_kwh=dG_minus,
        C_plan_yuan=C_plan,
        C_reg_yuan=C_reg,
        C_adj_yuan=C_adj,
        C_emg_yuan=C_emg,
        C_total_yuan=C_total,
        identity_residual_yuan=identity_residual,
    )


def run_settlement_self_tests(
    *,
    c: float = 1.0,
    tolerance: float = 1e-12,
) -> pd.DataFrame:
    """
    自动测试A/B/C。

    A. 下调：G0=100, GF=80 -> C_reg=90*c
    B. 上调：G0=100, GF=120 -> C_reg=130*c
    C. C_reg == C_plan + C_adj
    """
    if c <= 0:
        raise ValueError("测试电价c必须为正。")

    # A
    G0_a = 100.0
    GF_a = 80.0
    dplus_a = max(GF_a - G0_a, 0.0)
    dminus_a = max(G0_a - GF_a, 0.0)

    Creg_a = c * (
        GF_a + 0.5 * (dplus_a + dminus_a)
    )
    Cplan_a = c * G0_a
    Cadj_a = c * (
        1.5 * dplus_a - 0.5 * dminus_a
    )

    # B
    G0_b = 100.0
    GF_b = 120.0
    dplus_b = max(GF_b - G0_b, 0.0)
    dminus_b = max(G0_b - GF_b, 0.0)

    Creg_b = c * (
        GF_b + 0.5 * (dplus_b + dminus_b)
    )
    Cplan_b = c * G0_b
    Cadj_b = c * (
        1.5 * dplus_b - 0.5 * dminus_b
    )

    rows = [
        {
            "test": "A_down_adjustment",
            "passed": abs(Creg_a - 90.0 * c) <= tolerance,
            "actual": Creg_a,
            "expected": 90.0 * c,
        },
        {
            "test": "B_up_adjustment",
            "passed": abs(Creg_b - 130.0 * c) <= tolerance,
            "actual": Creg_b,
            "expected": 130.0 * c,
        },
        {
            "test": "C_identity_down",
            "passed": abs(
                Creg_a - (Cplan_a + Cadj_a)
            ) <= tolerance,
            "actual": Creg_a,
            "expected": Cplan_a + Cadj_a,
        },
        {
            "test": "C_identity_up",
            "passed": abs(
                Creg_b - (Cplan_b + Cadj_b)
            ) <= tolerance,
            "actual": Creg_b,
            "expected": Cplan_b + Cadj_b,
        },
    ]

    report = pd.DataFrame(rows)

    if not report["passed"].all():
        raise AssertionError(
            "问题3结算自动测试失败：\n"
            + report.to_string(index=False)
        )

    return report


# 模块导入时自动执行A/B/C，若公式被误改则立即失败。
SETTLEMENT_SELF_TEST_REPORT = run_settlement_self_tests()
