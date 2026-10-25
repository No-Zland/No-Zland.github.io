# -*- coding: utf-8 -*-
"""
question4_solver.py
问题4：动态实时电价下复用问题2 / 问题3。

本文件不复制问题2、问题3整套优化代码。

复用关系
--------
Q4-2:
    CausalPriceModule
    + Question2Solver
    -> result4-2

Q4-3:
    CausalPriceModule.price_provider
    + Question3Solver
    -> result4-3

附件4时间映射
-------------
只使用 data_loader.Attachment4Data.price：
    index = date
    columns = model k=0,...,143

该DataFrame已经由 data_loader.py + time_index.py 按“右端点标签”对齐：
    k=0   -> [0:00,0:10)   <- source 0:10
    k=36  -> [6:00,6:10)   <- source 6:10
    k=60  -> [10:00,10:10) <- source 10:10
    k=143 -> [23:50,24:00) <- source 0:00+1

本文件绝不直接读取附件4原始表头来推断k。

价格主策略
----------
未来实际价格未知，采用严格因果预测：
1. 基础：最近最多4个“目标日期同星期属性”的历史日同k均值；
2. 决策日内：只用decision_datetime之前已经实现的当前日价格偏差
   对未来价格整体修正；
3. 当前时刻以后的附件4实际价格只能用于后续实现和最终结算。

完美预知价格Oracle
------------------
可选，仅用于基准比较，默认不启用。
Oracle允许把附件4未来实际价直接作为优化价格，但必须明确标记，
不得作为主策略结果。

Q4费用分解
----------
Q4-2:
    C_plan = sum p_act * G0
    C_reg  = C_plan
    C_adj  = 0
    C_emg  = 5 sum p_act * G_emg
    C_total= C_reg + C_emg

Q4-3:
    严格沿用rolling_scheduler问题3最终结算：
    C_reg=sum p_act[GF+0.5(dG_plus+dG_minus)]
    C_plan=sum p_act G0
    C_adj=sum p_act[1.5dG_plus-0.5dG_minus]
    C_emg=5 sum p_act G_emg
    C_total=C_reg+C_emg
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from config import DEFAULT_CONFIG, ProjectConfig
from data_loader import (
    Attachment1Data,
    Attachment2Data,
    Attachment3Data,
    Attachment4Data,
)
from question2_solver import (
    Question2DayResult,
    Question2Settings,
    Question2Solver,
)
from question3_solver import (
    Question3DayResult,
    Question3Settings,
    Question3Solver,
)
from rolling_scheduler import (
    SettlementResult,
    settle_question3_cost,
)
from time_index import build_time_map, validate_time_map


# ============================================================================
# 因果动态价格模块
# ============================================================================


@dataclass
class PriceForecastResult:
    target_date: pd.Timestamp
    decision_datetime: pd.Timestamp
    forecast_yuan_per_kwh: pd.Series
    history_dates: tuple[pd.Timestamp, ...]
    observed_current_day_intervals: int
    observed_actual_k_max: Optional[int]
    future_actual_used: bool


class CausalPriceModule:
    """
    问题4严格因果价格预测模块。

    任何预测只允许使用：
    - decision day之前完整历史日；
    - decision_datetime之前当前日已经实现的k；
    - 已知fallback基准（附件1固定日内电价）。

    禁止使用：
    - 当前日decision时刻以后的附件4真实价格；
    - target future day自身真实价格。
    """

    def __init__(
        self,
        *,
        attachment4: Attachment4Data,
        fallback_price_yuan_per_kwh: pd.Series,
        config: ProjectConfig = DEFAULT_CONFIG,
        similar_days: int = 4,
    ) -> None:
        self.attachment4 = attachment4
        self.config = config
        self.similar_days = int(similar_days)

        if self.similar_days <= 0:
            raise ValueError("similar_days必须为正整数。")

        expected_k = list(range(config.intervals_per_day))

        if list(attachment4.price.columns) != expected_k:
            raise ValueError(
                "Attachment4Data.price必须严格为模型k=0~143。"
            )

        if attachment4.price.isna().any().any():
            raise ValueError("附件4模型价格网格存在缺失值。")

        if list(fallback_price_yuan_per_kwh.index) != expected_k:
            raise ValueError(
                "fallback_price_yuan_per_kwh.index必须为0~143。"
            )

        self.fallback_price = pd.to_numeric(
            fallback_price_yuan_per_kwh,
            errors="raise",
        ).astype(float)

        self.fallback_price.index = expected_k

        self.time_map = build_time_map(config)
        validate_time_map(self.time_map, config)

        self._cache: Dict[
            tuple[pd.Timestamp, pd.Timestamp],
            PriceForecastResult,
        ] = {}

    @staticmethod
    def _normalize_date(value) -> pd.Timestamp:
        return pd.Timestamp(value).normalize()

    def _base_forecast(
        self,
        target_date: pd.Timestamp,
        decision_datetime: pd.Timestamp,
    ) -> tuple[pd.Series, tuple[pd.Timestamp, ...]]:
        """
        基础相似日预测。

        完整历史日必须严格早于decision_datetime所在自然日。
        即使预测的是次日，也不能把“当前日未来尚未实现部分”当完整历史日。
        """
        decision_day = decision_datetime.normalize()

        history = self.attachment4.price.loc[
            self.attachment4.price.index < decision_day
        ]

        if history.empty:
            return self.fallback_price.copy(), tuple()

        same_weekday = history.loc[
            history.index.weekday == target_date.weekday()
        ]

        if same_weekday.empty:
            selected = history.tail(self.similar_days)
        else:
            selected = same_weekday.tail(self.similar_days)

        base = selected.mean(axis=0).astype(float)
        base.index = list(range(self.config.intervals_per_day))

        return (
            base,
            tuple(
                pd.Timestamp(x).normalize()
                for x in selected.index
            ),
        )

    def forecast(
        self,
        target_date,
        decision_datetime,
    ) -> PriceForecastResult:
        """
        返回target_date的144点价格预测。

        decision_datetime可为任意10分钟决策时刻。
        当前日真实偏差只使用k < current_k的已实现区间。

        例如：
        6:00决策 -> current_k=36 -> 最多读取实际k=0..35，
        对应附件4最后可用右端点标签6:00。
        绝不读取source 6:10（k=36）。
        """
        target = self._normalize_date(target_date)
        decision = pd.Timestamp(decision_datetime)

        cache_key = (target, decision)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            return PriceForecastResult(
                target_date=cached.target_date,
                decision_datetime=cached.decision_datetime,
                forecast_yuan_per_kwh=(
                    cached.forecast_yuan_per_kwh.copy()
                ),
                history_dates=cached.history_dates,
                observed_current_day_intervals=(
                    cached.observed_current_day_intervals
                ),
                observed_actual_k_max=(
                    cached.observed_actual_k_max
                ),
                future_actual_used=False,
            )

        base, history_dates = self._base_forecast(
            target,
            decision,
        )

        decision_day = decision.normalize()
        minute = decision.hour * 60 + decision.minute

        if minute % self.config.dt_minutes != 0:
            raise ValueError(
                "decision_datetime必须落在10分钟边界。"
            )

        current_k = minute // self.config.dt_minutes

        # 只允许读取当前日已经完成的k<current_k。
        observed_count = 0
        observed_k_max = None
        bias = 0.0

        if (
            decision_day in self.attachment4.price.index
            and current_k > 0
        ):
            observed_index = list(range(current_k))

            actual_prefix = (
                self.attachment4.price.loc[
                    decision_day,
                    observed_index,
                ].astype(float)
            )

            # 当前日基准也必须是仅由更早完整历史日生成。
            current_day_base, _ = self._base_forecast(
                decision_day,
                decision,
            )

            residual_prefix = (
                actual_prefix
                - current_day_base.loc[observed_index]
            )

            bias = float(residual_prefix.mean())
            observed_count = current_k
            observed_k_max = current_k - 1

        forecast = (base + bias).clip(lower=0.0)
        forecast.name = "price_forecast_yuan_per_kwh"

        result = PriceForecastResult(
            target_date=target,
            decision_datetime=decision,
            forecast_yuan_per_kwh=forecast,
            history_dates=history_dates,
            observed_current_day_intervals=observed_count,
            observed_actual_k_max=observed_k_max,
            future_actual_used=False,
        )

        self._cache[cache_key] = result
        return PriceForecastResult(
            target_date=result.target_date,
            decision_datetime=result.decision_datetime,
            forecast_yuan_per_kwh=result.forecast_yuan_per_kwh.copy(),
            history_dates=result.history_dates,
            observed_current_day_intervals=(
                result.observed_current_day_intervals
            ),
            observed_actual_k_max=result.observed_actual_k_max,
            future_actual_used=False,
        )

    def price_provider(
        self,
        abs_date: pd.Timestamp,
        model_k: int,
        decision_datetime: pd.Timestamp,
    ) -> float:
        """
        给Question3Solver注入的严格因果价格接口。
        """
        forecast = self.forecast(
            abs_date,
            decision_datetime,
        )
        return float(
            forecast.forecast_yuan_per_kwh.loc[
                int(model_k)
            ]
        )

    def actual_price(
        self,
        date,
    ) -> pd.Series:
        """
        事后真实价格。

        只从Attachment4Data.price按模型k读取，
        不解析附件4原始时间字符串。
        """
        d = self._normalize_date(date)

        if d not in self.attachment4.price.index:
            raise KeyError(f"附件4缺少日期{d.date()}。")

        result = (
            self.attachment4.price.loc[d]
            .astype(float)
            .copy()
        )
        result.index = list(range(self.config.intervals_per_day))
        result.name = "actual_price_yuan_per_kwh"
        return result


class OraclePriceModule(CausalPriceModule):
    """
    完美预知价格Oracle，仅用于基准。

    本类故意允许使用target_date完整真实价格。
    绝不能作为main_strategy=True的正式策略。
    """

    def forecast(
        self,
        target_date,
        decision_datetime,
    ) -> PriceForecastResult:
        target = self._normalize_date(target_date)
        decision = pd.Timestamp(decision_datetime)

        actual = self.actual_price(target)
        return PriceForecastResult(
            target_date=target,
            decision_datetime=decision,
            forecast_yuan_per_kwh=actual,
            history_dates=tuple(),
            observed_current_day_intervals=0,
            observed_actual_k_max=None,
            future_actual_used=True,
        )


# ============================================================================
# Q4结果
# ============================================================================


@dataclass
class Question42DayResult:
    date: pd.Timestamp

    base_result: Question2DayResult

    day_ahead_price_forecast: pd.Series
    actual_price_yuan_per_kwh: pd.Series
    price_forecast_audit: PriceForecastResult

    C_plan_yuan: float
    C_reg_yuan: float
    C_adj_yuan: float
    C_emg_yuan: float
    C_total_yuan: float

    is_oracle: bool


@dataclass
class Question43DayResult:
    date: pd.Timestamp

    base_result: Question3DayResult

    day_ahead_price_forecast: pd.Series
    actual_price_yuan_per_kwh: pd.Series
    price_forecast_audit: PriceForecastResult

    C_plan_yuan: float
    C_reg_yuan: float
    C_adj_yuan: float
    C_emg_yuan: float
    C_total_yuan: float

    settlement_identity_residual_yuan: float
    is_oracle: bool


@dataclass
class Question4BothResult:
    """同时返回result4-2和result4-3。"""

    result4_2: Question42DayResult
    result4_3: Question43DayResult


@dataclass
class Question4PeriodResult:
    formal_results: Dict[pd.Timestamp, object]
    cross_day_report: pd.DataFrame
    warmup_end_energy_kwh: Optional[float]
    final_energy_kwh: float


# ============================================================================
# Question4Solver：薄适配层
# ============================================================================


class Question4Solver:
    """
    问题4薄封装。

    不复制Q2/Q3模型：
    - Q4-2直接实例化Question2Solver并注入0:00因果价格预测；
    - Q4-3直接实例化Question3Solver并注入price_provider。
    """

    def __init__(
        self,
        *,
        attachment1: Attachment1Data,
        attachment2: Attachment2Data,
        attachment3: Attachment3Data,
        attachment4: Attachment4Data,
        q2_settings: Question2Settings = Question2Settings(),
        q3_settings: Question3Settings = Question3Settings(),
        config: ProjectConfig = DEFAULT_CONFIG,
    ) -> None:
        self.attachment1 = attachment1
        self.attachment2 = attachment2
        self.attachment3 = attachment3
        self.attachment4 = attachment4
        self.q2_settings = q2_settings
        self.q3_settings = q3_settings
        self.config = config

        self.time_map = build_time_map(config)
        validate_time_map(self.time_map, config)

        expected_k = list(range(config.intervals_per_day))
        if list(attachment4.price.columns) != expected_k:
            raise ValueError(
                "附件4必须通过data_loader/time_index按右端点映射后再进入Q4。"
            )

        fallback_price = (
            attachment1.aligned["price_yuan_per_kwh"]
            .astype(float)
            .copy()
        )
        fallback_price.index = expected_k

        self.price_module = CausalPriceModule(
            attachment4=attachment4,
            fallback_price_yuan_per_kwh=fallback_price,
            config=config,
        )

        self.oracle_price_module = OraclePriceModule(
            attachment4=attachment4,
            fallback_price_yuan_per_kwh=fallback_price,
            config=config,
        )

    @staticmethod
    def _normalize_date(value) -> pd.Timestamp:
        return pd.Timestamp(value).normalize()

    def solve_q4_2_day(
        self,
        date,
        *,
        initial_energy_kwh: float,
        use_oracle: bool = False,
        check_legality: bool = True,
    ) -> Question42DayResult:
        """
        Q4-2 = 动态电价下复用Question2Solver。

        主策略：
            use_oracle=False

        Oracle：
            use_oracle=True，仅用于完美价格信息基准。
        """
        d = self._normalize_date(date)

        price_module = (
            self.oracle_price_module
            if use_oracle
            else self.price_module
        )

        decision_datetime = d
        price_forecast = price_module.forecast(
            d,
            decision_datetime,
        )

        if (
            not use_oracle
            and price_forecast.future_actual_used
        ):
            raise AssertionError(
                "Q4-2主策略价格预测发生未来信息泄露。"
            )

        # --------------------------------------------------------------
        # 直接复用Question2Solver，不复制问题2优化代码。
        # --------------------------------------------------------------
        solver = Question2Solver(
            attachment1=self.attachment1,
            attachment2=self.attachment2,
            settings=self.q2_settings,
            config=self.config,
        )

        # Q2内部所有价格位置统一使用这一144点预测。
        solver.price_yuan_per_kwh = (
            price_forecast
            .forecast_yuan_per_kwh
            .copy()
        )

        base = solver.solve_day(
            d,
            initial_energy_kwh=initial_energy_kwh,
            check_legality=check_legality,
        )

        # --------------------------------------------------------------
        # 事后按附件4真实价格重新结算
        # --------------------------------------------------------------
        actual_price = self.price_module.actual_price(d)

        G0 = base.plan_purchase_kwh
        G_emg = base.actual_emergency_kwh

        C_plan = float((actual_price * G0).sum())

        # Q4-2没有日内正常购电调整：
        C_reg = C_plan
        C_adj = 0.0

        C_emg = float(
            (5.0 * actual_price * G_emg).sum()
        )

        C_total = C_reg + C_emg

        return Question42DayResult(
            date=d,
            base_result=base,
            day_ahead_price_forecast=(
                price_forecast
                .forecast_yuan_per_kwh.copy()
            ),
            actual_price_yuan_per_kwh=actual_price,
            price_forecast_audit=price_forecast,
            C_plan_yuan=C_plan,
            C_reg_yuan=C_reg,
            C_adj_yuan=C_adj,
            C_emg_yuan=C_emg,
            C_total_yuan=C_total,
            is_oracle=bool(use_oracle),
        )

    def solve_q4_3_day(
        self,
        date,
        *,
        initial_energy_kwh: float,
        use_oracle: bool = False,
        update_combination: Optional[
            tuple[int, ...]
        ] = None,
        check_legality: bool = True,
    ) -> Question43DayResult:
        """
        Q4-3 = 动态电价下复用Question3Solver。

        Question3Solver的所有滚动购电调整和10分钟实时补救代码不复制，
        这里只注入动态price_provider。
        """
        d = self._normalize_date(date)

        price_module = (
            self.oracle_price_module
            if use_oracle
            else self.price_module
        )

        day_ahead_audit = price_module.forecast(
            d,
            d,
        )

        if (
            not use_oracle
            and day_ahead_audit.future_actual_used
        ):
            raise AssertionError(
                "Q4-3主策略0:00价格预测发生未来泄露。"
            )

        solver = Question3Solver(
            attachment1=self.attachment1,
            attachment2=self.attachment2,
            attachment3=self.attachment3,
            settings=self.q3_settings,
            config=self.config,
            price_provider=price_module.price_provider,
        )

        base = solver.solve_day(
            d,
            initial_energy_kwh=initial_energy_kwh,
            update_combination=update_combination,
            check_legality=check_legality,
        )

        # --------------------------------------------------------------
        # 最终Q4-3只按附件4真实实现价格结算。
        # --------------------------------------------------------------
        actual_price = self.price_module.actual_price(d)

        settlement = settle_question3_cost(
            G0_kwh=base.original_plan_kwh,
            GF_kwh=base.final_effective_plan_kwh,
            price_yuan_per_kwh=actual_price,
            G_emg_kwh=base.actual_emergency_kwh,
            config=self.config,
        )

        if settlement.identity_residual_yuan > 1e-8:
            raise AssertionError(
                "Q4-3真实动态价格下C_reg != C_plan + C_adj。"
            )

        return Question43DayResult(
            date=d,
            base_result=base,
            day_ahead_price_forecast=(
                day_ahead_audit
                .forecast_yuan_per_kwh.copy()
            ),
            actual_price_yuan_per_kwh=actual_price,
            price_forecast_audit=day_ahead_audit,
            C_plan_yuan=settlement.C_plan_yuan,
            C_reg_yuan=settlement.C_reg_yuan,
            C_adj_yuan=settlement.C_adj_yuan,
            C_emg_yuan=settlement.C_emg_yuan,
            C_total_yuan=settlement.C_total_yuan,
            settlement_identity_residual_yuan=(
                settlement.identity_residual_yuan
            ),
            is_oracle=bool(use_oracle),
        )

    def solve_both_day(
        self,
        date,
        *,
        initial_energy_q4_2_kwh: float,
        initial_energy_q4_3_kwh: float,
        check_legality: bool = True,
    ) -> Question4BothResult:
        """
        同一天同时得到result4-2 / result4-3主策略。
        """
        result4_2 = self.solve_q4_2_day(
            date,
            initial_energy_kwh=initial_energy_q4_2_kwh,
            use_oracle=False,
            check_legality=check_legality,
        )

        result4_3 = self.solve_q4_3_day(
            date,
            initial_energy_kwh=initial_energy_q4_3_kwh,
            use_oracle=False,
            check_legality=check_legality,
        )

        return Question4BothResult(
            result4_2=result4_2,
            result4_3=result4_3,
        )

    def solve_q4_2_period(
        self,
        *,
        start_date: str = "2025-01-01",
        end_date: str = "2025-12-31",
        initial_energy_kwh: float = 6000.0,
        save_from_date: str = "2025-02-01",
        use_oracle: bool = False,
        check_legality: bool = True,
    ) -> Question4PeriodResult:
        """
        Q4-2跨日连续运行。
        """
        return self._solve_period(
            mode="q4-2",
            start_date=start_date,
            end_date=end_date,
            initial_energy_kwh=initial_energy_kwh,
            save_from_date=save_from_date,
            use_oracle=use_oracle,
            check_legality=check_legality,
        )

    def solve_q4_3_period(
        self,
        *,
        start_date: str = "2025-01-01",
        end_date: str = "2025-12-31",
        initial_energy_kwh: float = 6000.0,
        save_from_date: str = "2025-02-01",
        use_oracle: bool = False,
        update_combination: Optional[
            tuple[int, ...]
        ] = None,
        check_legality: bool = True,
    ) -> Question4PeriodResult:
        """
        Q4-3跨日连续运行。
        """
        return self._solve_period(
            mode="q4-3",
            start_date=start_date,
            end_date=end_date,
            initial_energy_kwh=initial_energy_kwh,
            save_from_date=save_from_date,
            use_oracle=use_oracle,
            update_combination=update_combination,
            check_legality=check_legality,
        )

    def _solve_period(
        self,
        *,
        mode: str,
        start_date: str,
        end_date: str,
        initial_energy_kwh: float,
        save_from_date: str,
        use_oracle: bool,
        check_legality: bool,
        update_combination: Optional[
            tuple[int, ...]
        ] = None,
    ) -> Question4PeriodResult:
        start = self._normalize_date(start_date)
        end = self._normalize_date(end_date)
        save_from = self._normalize_date(save_from_date)

        if mode not in {"q4-2", "q4-3"}:
            raise ValueError("mode只能为q4-2或q4-3。")

        formal_results = {}
        cross_rows = []

        current_energy = float(initial_energy_kwh)
        warmup_end = None
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
                        "current_initial_energy_kwh": current_energy,
                        "residual_kwh": residual,
                        "passed": residual <= 1e-8,
                    }
                )

            if mode == "q4-2":
                day = self.solve_q4_2_day(
                    d,
                    initial_energy_kwh=current_energy,
                    use_oracle=use_oracle,
                    check_legality=check_legality,
                )
            else:
                day = self.solve_q4_3_day(
                    d,
                    initial_energy_kwh=current_energy,
                    use_oracle=use_oracle,
                    update_combination=update_combination,
                    check_legality=check_legality,
                )

            current_energy = float(
                day.base_result.end_energy_kwh
            )
            previous_end = current_energy
            previous_date = d

            print(
                f"[Q4] {mode} {d.date()} 完成：总成本 "
                f"{day.base_result.C_total_yuan:.2f} 元，"
                f"末SOC {current_energy:.2f} kWh",
                flush=True,
            )

            if d < save_from:
                warmup_end = current_energy
            else:
                formal_results[d] = day

        cross_report = pd.DataFrame(cross_rows)

        if (
            not cross_report.empty
            and not cross_report["passed"].all()
        ):
            raise AssertionError("Q4跨日SOC连续性失败。")

        return Question4PeriodResult(
            formal_results=formal_results,
            cross_day_report=cross_report,
            warmup_end_energy_kwh=warmup_end,
            final_energy_kwh=current_energy,
        )


# ============================================================================
# 论文可视化代码
# ============================================================================
# 说明：
# - 使用matplotlib，不使用seaborn；
# - 每个函数只创建一张独立图，不使用subplots；
# - 不手工指定颜色，交给matplotlib默认循环；
# - 图中标题/坐标/图例默认使用英文，便于避免环境中文字体问题。
# ============================================================================


def plot_price_forecast_vs_actual(
    result: Question42DayResult | Question43DayResult,
    *,
    output_path: Optional[str] = None,
):
    """
    论文图：0:00动态电价预测 vs 实际实时电价。
    """
    import matplotlib.pyplot as plt

    x = np.arange(144) / 6.0

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        x,
        result.day_ahead_price_forecast.to_numpy(dtype=float),
        label="Day-ahead price forecast",
    )
    ax.plot(
        x,
        result.actual_price_yuan_per_kwh.to_numpy(dtype=float),
        label="Actual real-time price",
    )

    ax.set_xlabel("Time of day (hour)")
    ax.set_ylabel("Electricity price (CNY/kWh)")
    ax.set_title(
        f"Dynamic Price Forecast vs Actual - "
        f"{result.date.date()}"
    )
    ax.legend()
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )

    return fig, ax


def plot_q4_cost_breakdown(
    result4_2: Question42DayResult,
    result4_3: Question43DayResult,
    *,
    output_path: Optional[str] = None,
):
    """
    论文图：Q4-2与Q4-3费用分解。
    """
    import matplotlib.pyplot as plt

    labels = [
        "Plan cost",
        "Adjustment net",
        "Emergency cost",
        "Total cost",
    ]

    values_42 = [
        result4_2.C_plan_yuan,
        result4_2.C_adj_yuan,
        result4_2.C_emg_yuan,
        result4_2.C_total_yuan,
    ]

    values_43 = [
        result4_3.C_plan_yuan,
        result4_3.C_adj_yuan,
        result4_3.C_emg_yuan,
        result4_3.C_total_yuan,
    ]

    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(
        x - width / 2,
        values_42,
        width,
        label="Q4-2",
    )
    ax.bar(
        x + width / 2,
        values_43,
        width,
        label="Q4-3",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Cost (CNY)")
    ax.set_title("Cost Breakdown under Dynamic Electricity Price")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )

    return fig, ax


def plot_soc_profile(
    result: Question42DayResult | Question43DayResult,
    *,
    output_path: Optional[str] = None,
):
    """
    论文图：145节点SOC/储能电量轨迹。
    """
    import matplotlib.pyplot as plt

    E = result.base_result.energy_kwh
    x = np.arange(145) / 6.0

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        x,
        E.to_numpy(dtype=float),
        label="Battery energy",
    )

    ax.set_xlabel("Time of day (hour)")
    ax.set_ylabel("Battery energy (kWh)")
    ax.set_title(
        f"Battery Energy Trajectory - "
        f"{result.date.date()}"
    )
    ax.legend()
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )

    return fig, ax


def plot_purchase_and_emergency(
    result: Question42DayResult | Question43DayResult,
    *,
    output_path: Optional[str] = None,
):
    """
    论文图：正常购电与紧急购电10分钟电量。
    """
    import matplotlib.pyplot as plt

    x = np.arange(144) / 6.0

    if isinstance(result, Question43DayResult):
        normal = (
            result.base_result.final_effective_plan_kwh
        )
    else:
        normal = result.base_result.plan_purchase_kwh

    emergency = result.base_result.actual_emergency_kwh

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        x,
        normal.to_numpy(dtype=float),
        label="Normal grid purchase",
    )
    ax.plot(
        x,
        emergency.to_numpy(dtype=float),
        label="Emergency purchase",
    )

    ax.set_xlabel("Time of day (hour)")
    ax.set_ylabel("Energy per 10-min interval (kWh)")
    ax.set_title(
        f"Grid Purchase Profile - "
        f"{result.date.date()}"
    )
    ax.legend()
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )

    return fig, ax
