# -*- coding: utf-8 -*-
"""
model_base.py
C题微网公共物理模型层（Q1-Q4复用）。

职责：
1. 只封装所有问题共同使用的物理变量与约束；
2. 严格使用 time_index.py 中已经确认的 k=0,...,143；
3. 能量平衡统一使用 kWh；
4. 默认采用连续LP变量；
5. 充放电互斥二进制变量仅作为可选开关，默认关闭；
6. 不建立任何具体问题的目标函数；
7. 不读取Excel，不根据Excel表头或结果模板文字重新定位时间。

统一决策变量：
    q_buy[k]   外网正常购电量，kWh
    q_ch[k]    母线侧储能充电量，kWh
    q_dis[k]   母线侧储能放电量，kWh
    q_curt[k]  弃光量，kWh
    E[j]       储能内部电量，kWh，j=0,...,144
    z[k]       可选充放电互斥二进制变量；默认不创建

具体问题自行增加：
    q_emg      紧急购电量（Q2-Q4）
    q_sur      已计划但无法利用的外网电量富余（Q2-Q4）
    初始/终端SOC约束
    跨日SOC
    场景树非预见性
    MPC冻结约束
    各问题目标函数

数学公式编号：
    [MB-01] 10 min功率-电量换算
    [MB-02] 微网能量平衡
    [MB-03] 弃光约束
    [MB-04] 储能状态转移
    [MB-05] 储能电量上下界
    [MB-06] 单时段最大充放电量
    [MB-07] 可选充放电互斥
    [MB-08] 外网购电非负
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

import pandas as pd

try:
    import gurobipy as gp
    from gurobipy import GRB
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "model_base.py 依赖 gurobipy。请在已安装并配置 Gurobi 的环境中运行。"
    ) from exc

from config import DEFAULT_CONFIG, ProjectConfig
from time_index import build_time_map, validate_time_map


# ============================================================================
# 已确定的统一储能参数
# ============================================================================

ETA_C = 0.90
ETA_D = 0.90
E_MIN_KWH = 1200.0
E_MAX_KWH = 10800.0
P_BAT_MAX_KW = 5000.0


@dataclass
class BaseVariables:
    """
    公共决策变量容器。

    变量名严格沿用已经确定的符号体系：
        q_buy, q_ch, q_dis, q_curt, E, z
    """

    q_buy: gp.tupledict
    q_ch: gp.tupledict
    q_dis: gp.tupledict
    q_curt: gp.tupledict
    E: gp.tupledict
    z: Optional[gp.tupledict] = None


@dataclass
class BaseConstraintRefs:
    """公共约束引用，便于后续调试、IIS分析和结果审计。"""

    energy_balance: Optional[gp.tupledict] = None
    curtailment_upper: Optional[gp.tupledict] = None
    storage_transition: Optional[gp.tupledict] = None
    charge_exclusivity: Optional[gp.tupledict] = None
    discharge_exclusivity: Optional[gp.tupledict] = None


def _validate_k_series(
    values: pd.Series,
    *,
    config: ProjectConfig,
    name: str,
    require_nonnegative: bool,
) -> pd.Series:
    """
    强制检查物理区间数据接口。

    只接受 pandas.Series，且 index 必须严格按顺序为：
        k = 0,1,...,143

    禁止通过Excel原始表头、paper_label或template_display_label重新推断k。
    """
    if not isinstance(values, pd.Series):
        raise TypeError(
            f"{name}必须是pandas.Series，且index严格为"
            f"k=0,...,{config.intervals_per_day - 1}。"
        )

    if len(values) != config.intervals_per_day:
        raise ValueError(
            f"{name}长度必须为{config.intervals_per_day}，实际为{len(values)}。"
        )

    try:
        actual_index = [int(x) for x in values.index]
    except Exception as exc:
        raise ValueError(f"{name}的index无法解释为模型k。") from exc

    expected_index = list(range(config.intervals_per_day))
    if actual_index != expected_index:
        raise ValueError(
            f"{name}的index必须严格为0~{config.intervals_per_day - 1}，"
            "不得根据Excel表头或结果模板显示文字重新定位。"
        )

    numeric = pd.to_numeric(values, errors="raise").astype(float).copy()
    numeric.index = expected_index

    if numeric.isna().any():
        bad = numeric[numeric.isna()].index.tolist()
        raise ValueError(f"{name}存在缺失值，k={bad[:10]}。")

    if require_nonnegative and (numeric < 0).any():
        bad = numeric[numeric < 0]
        preview = {int(k): float(v) for k, v in bad.head(10).items()}
        raise ValueError(f"{name}应非负，发现负值：{preview}")

    return numeric


def kw_to_interval_kwh(
    power_kw: pd.Series,
    config: ProjectConfig = DEFAULT_CONFIG,
    *,
    name: str = "power_kw",
) -> pd.Series:
    """
    将按模型k索引的功率(kW)转换为单个10 min物理区间电量(kWh)。

    [MB-01]
        q_k = P_k * Δt
        Δt = 10/60 = 1/6 h

    参数
    ----
    power_kw:
        pandas.Series，index必须严格为k=0,...,143，单位kW。

    返回
    ----
    pandas.Series
        相同k索引，单位kWh。
    """
    series = _validate_k_series(
        power_kw,
        config=config,
        name=name,
        require_nonnegative=False,
    )
    dt_hours = config.dt_minutes / 60.0
    result = series * dt_hours
    result.name = f"{name}_kwh"
    return result


class MicrogridBaseModel:
    """
    Q1-Q4共同物理模型构建器。

    约束层只使用 time_map["k"] 作为优化时段索引。
    source_right_endpoint_label、paper_label、template_display_label
    仅用于解释和输出，不参与变量定位。

    默认：
        enforce_charge_discharge_exclusivity=False

    因此默认公共模型全部为连续变量，可用于LP。
    """

    def __init__(
        self,
        model: gp.Model,
        *,
        config: ProjectConfig = DEFAULT_CONFIG,
        time_map: Optional[pd.DataFrame] = None,
        enforce_charge_discharge_exclusivity: bool = False,
        variable_name_prefix: str = "",
    ) -> None:
        self.model = model
        self.config = config
        self.enforce_charge_discharge_exclusivity = (
            enforce_charge_discharge_exclusivity
        )
        self.variable_name_prefix = variable_name_prefix

        # 唯一时间索引来源：time_index.py。
        if time_map is None:
            self.time_map = build_time_map(config)
        else:
            self.time_map = time_map.copy(deep=True)

        validate_time_map(self.time_map, config)

        # 优化模型只读取time_map中的k，不读取任何Excel时间字符串。
        self.k = tuple(int(x) for x in self.time_map["k"].tolist())
        self.j = tuple(range(config.state_nodes_per_day))

        expected_k = tuple(range(config.intervals_per_day))
        expected_j = tuple(range(config.intervals_per_day + 1))

        if self.k != expected_k:
            raise ValueError(
                "model_base只接受time_index.py定义的k=0,...,143。"
            )

        if self.j != expected_j:
            raise ValueError(
                "储能状态节点必须严格为j=0,...,144。"
            )

        self.dt_hours = config.dt_minutes / 60.0

        # [MB-06] q_bat^max = P_bat^max * Δt
        self.q_bat_max_kwh = P_BAT_MAX_KW * self.dt_hours

        self.vars = self._create_common_variables()
        self.constraints = BaseConstraintRefs()

        # [MB-07] 仅显式开启时才创建并加入互斥二进制约束。
        if self.enforce_charge_discharge_exclusivity:
            self.add_charge_discharge_exclusivity()

    def _vname(self, base: str) -> str:
        """生成Gurobi变量名，不改变数学变量体系。"""
        if not self.variable_name_prefix:
            return base
        return f"{self.variable_name_prefix}{base}"

    def _cname(self, base: str, k: Optional[int] = None) -> str:
        """生成Gurobi约束名。"""
        prefix = self.variable_name_prefix
        if k is None:
            return f"{prefix}{base}"
        return f"{prefix}{base}[{k}]"

    def _create_common_variables(self) -> BaseVariables:
        """
        创建所有问题共有变量。

        [MB-05]
            1200 <= E_j <= 10800  kWh

        [MB-06]
            0 <= q_ch,k <= P_bat^max*Δt
            0 <= q_dis,k <= P_bat^max*Δt

        [MB-08]
            q_buy,k >= 0

        上述约束使用Gurobi变量上下界直接实现。
        """

        # [MB-08] 外网正常购电非负。
        q_buy = self.model.addVars(
            self.k,
            lb=0.0,
            vtype=GRB.CONTINUOUS,
            name=self._vname("q_buy"),
        )

        # [MB-06] 母线侧充电量，单位kWh。
        q_ch = self.model.addVars(
            self.k,
            lb=0.0,
            ub=self.q_bat_max_kwh,
            vtype=GRB.CONTINUOUS,
            name=self._vname("q_ch"),
        )

        # [MB-06] 母线侧放电量，单位kWh。
        q_dis = self.model.addVars(
            self.k,
            lb=0.0,
            ub=self.q_bat_max_kwh,
            vtype=GRB.CONTINUOUS,
            name=self._vname("q_dis"),
        )

        # [MB-03] q_curt下界0在变量层设置；
        # 上界q_curt<=G_k在拿到pv_kwh后添加。
        q_curt = self.model.addVars(
            self.k,
            lb=0.0,
            vtype=GRB.CONTINUOUS,
            name=self._vname("q_curt"),
        )

        # [MB-05] 储能内部实际电量，单位kWh。
        E = self.model.addVars(
            self.j,
            lb=E_MIN_KWH,
            ub=E_MAX_KWH,
            vtype=GRB.CONTINUOUS,
            name=self._vname("E"),
        )

        # [MB-07] 默认不创建二进制变量。
        z = None
        if self.enforce_charge_discharge_exclusivity:
            z = self.model.addVars(
                self.k,
                vtype=GRB.BINARY,
                name=self._vname("z"),
            )

        return BaseVariables(
            q_buy=q_buy,
            q_ch=q_ch,
            q_dis=q_dis,
            q_curt=q_curt,
            E=E,
            z=z,
        )

    def validate_energy_inputs(
        self,
        *,
        load_kwh: pd.Series,
        pv_kwh: pd.Series,
    ) -> tuple[pd.Series, pd.Series]:
        """
        检查能量平衡输入。

        load_kwh、pv_kwh必须已经是每个10 min物理区间的kWh，
        且索引严格为time_index.py定义的k=0,...,143。
        """
        L = _validate_k_series(
            load_kwh,
            config=self.config,
            name="load_kwh",
            require_nonnegative=True,
        )
        G = _validate_k_series(
            pv_kwh,
            config=self.config,
            name="pv_kwh",
            require_nonnegative=True,
        )
        return L, G

    @staticmethod
    def _optional_var_at(
        mapping: Optional[Mapping[int, gp.Var]],
        k: int,
        name: str,
    ):
        """
        读取具体问题可选变量。

        Q1:
            q_emg=None, q_sur=None

        Q2-Q4:
            q_emg/q_sur由对应求解器创建后传入。
        """
        if mapping is None:
            return 0.0

        if k not in mapping:
            raise KeyError(f"{name}缺少模型索引k={k}。")

        return mapping[k]

    def add_energy_balance(
        self,
        *,
        load_kwh: pd.Series,
        pv_kwh: pd.Series,
        q_emg: Optional[Mapping[int, gp.Var]] = None,
        q_sur: Optional[Mapping[int, gp.Var]] = None,
    ) -> gp.tupledict:
        """
        添加逐10 min微网能量平衡。

        [MB-02]
            q_buy,k + q_emg,k + G_k + q_dis,k
            =
            L_k + q_ch,k + q_curt,k + q_sur,k

        对Q1：
            q_emg=None
            q_sur=None

        对Q2-Q4：
            q_emg、q_sur由具体问题求解器创建并传入。

        单位：
            q_buy/q_emg/G/q_dis/L/q_ch/q_curt/q_sur 全部为kWh。

        注意：
            充放电效率不出现在母线能量平衡式，只出现在[MB-04]。
        """
        L, G = self.validate_energy_inputs(
            load_kwh=load_kwh,
            pv_kwh=pv_kwh,
        )

        constr = gp.tupledict()

        for k in self.k:
            emg = self._optional_var_at(q_emg, k, "q_emg")
            sur = self._optional_var_at(q_sur, k, "q_sur")

            # [MB-02] 微网母线能量守恒。
            constr[k] = self.model.addConstr(
                self.vars.q_buy[k]
                + emg
                + float(G.loc[k])
                + self.vars.q_dis[k]
                ==
                float(L.loc[k])
                + self.vars.q_ch[k]
                + self.vars.q_curt[k]
                + sur,
                name=self._cname("energy_balance", k),
            )

        self.constraints.energy_balance = constr
        return constr

    def add_curtailment_constraints(
        self,
        *,
        pv_kwh: pd.Series,
    ) -> gp.tupledict:
        """
        添加弃光约束。

        [MB-03]
            0 <= q_curt,k <= G_k

        q_curt>=0已在变量创建时设置；
        本函数添加数据相关的q_curt<=G_k。
        """
        G = _validate_k_series(
            pv_kwh,
            config=self.config,
            name="pv_kwh",
            require_nonnegative=True,
        )

        constr = gp.tupledict()

        for k in self.k:
            # [MB-03]
            constr[k] = self.model.addConstr(
                self.vars.q_curt[k] <= float(G.loc[k]),
                name=self._cname("curtailment_upper", k),
            )

        self.constraints.curtailment_upper = constr
        return constr

    def add_storage_transition_constraints(self) -> gp.tupledict:
        """
        添加储能状态方程。

        [MB-04]
            E_{k+1}
            =
            E_k + eta_c*q_ch,k - q_dis,k/eta_d

        其中q_ch、q_dis已是10 min母线侧电量(kWh)，
        因此状态方程中不再乘Δt。
        """
        constr = gp.tupledict()

        for k in self.k:
            # [MB-04]
            constr[k] = self.model.addConstr(
                self.vars.E[k + 1]
                ==
                self.vars.E[k]
                + ETA_C * self.vars.q_ch[k]
                - self.vars.q_dis[k] / ETA_D,
                name=self._cname("storage_transition", k),
            )

        self.constraints.storage_transition = constr
        return constr

    def add_charge_discharge_exclusivity(
        self,
    ) -> tuple[gp.tupledict, gp.tupledict]:
        """
        可选：严格禁止同一10 min区间同时充电和放电。

        默认不开启。只有构造时显式设置：
            enforce_charge_discharge_exclusivity=True
        才创建z[k]并加入以下约束。

        [MB-07a]
            q_ch,k <= q_bat^max*z_k

        [MB-07b]
            q_dis,k <= q_bat^max*(1-z_k)

        [MB-07c]
            z_k in {0,1}

        开启后模型由连续LP扩展为MILP。
        """
        if not self.enforce_charge_discharge_exclusivity:
            raise RuntimeError(
                "当前模型未启用充放电互斥。"
                "如确有必要，请在构造时设置"
                "enforce_charge_discharge_exclusivity=True。"
            )

        if self.vars.z is None:
            raise RuntimeError("互斥开关已开启，但z变量未创建。")

        # 防止重复添加。
        if (
            self.constraints.charge_exclusivity is not None
            and self.constraints.discharge_exclusivity is not None
        ):
            return (
                self.constraints.charge_exclusivity,
                self.constraints.discharge_exclusivity,
            )

        ch_constr = gp.tupledict()
        dis_constr = gp.tupledict()

        for k in self.k:
            # [MB-07a]
            ch_constr[k] = self.model.addConstr(
                self.vars.q_ch[k]
                <= self.q_bat_max_kwh * self.vars.z[k],
                name=self._cname("charge_exclusivity", k),
            )

            # [MB-07b]
            dis_constr[k] = self.model.addConstr(
                self.vars.q_dis[k]
                <= self.q_bat_max_kwh * (1 - self.vars.z[k]),
                name=self._cname("discharge_exclusivity", k),
            )

        self.constraints.charge_exclusivity = ch_constr
        self.constraints.discharge_exclusivity = dis_constr

        return ch_constr, dis_constr

    def add_common_physical_constraints(
        self,
        *,
        load_kwh: pd.Series,
        pv_kwh: pd.Series,
        q_emg: Optional[Mapping[int, gp.Var]] = None,
        q_sur: Optional[Mapping[int, gp.Var]] = None,
    ) -> BaseConstraintRefs:
        """
        一次性添加所有需要显式约束行的公共物理关系。

        添加：
            [MB-02] 能量平衡
            [MB-03] 弃光上界
            [MB-04] 储能状态方程

        已通过变量上下界自动实现：
            [MB-05] 储能电量上下界
            [MB-06] 充放电功率/单步电量限制
            [MB-08] 外网购电非负

        若互斥开关开启：
            [MB-07] 已在构造时自动加入，不重复添加。

        本函数明确不添加：
            - E[0]初值
            - E[144]终端约束
            - 跨日SOC约束
            - q_emg/q_sur变量本身
            - 场景树非预见性
            - MPC冻结约束
            - 任何具体问题目标函数
        """
        self.add_energy_balance(
            load_kwh=load_kwh,
            pv_kwh=pv_kwh,
            q_emg=q_emg,
            q_sur=q_sur,
        )
        self.add_curtailment_constraints(
            pv_kwh=pv_kwh,
        )
        self.add_storage_transition_constraints()
        return self.constraints

    def get_physical_index(self) -> tuple[int, ...]:
        """
        返回唯一物理区间索引k=0,...,143。

        后续所有问题应直接复用该索引，不允许通过：
        - Excel原始时间标签
        - source_right_endpoint_label
        - paper_label
        - template_display_label
        反向生成或偏移k。
        """
        return self.k

    def get_state_index(self) -> tuple[int, ...]:
        """返回储能状态索引j=0,...,144。"""
        return self.j

    def get_time_map(self) -> pd.DataFrame:
        """
        返回time_map副本，仅用于解释、结果标注和输出适配。

        优化变量的索引定位始终使用self.k。
        """
        return self.time_map.copy(deep=True)
