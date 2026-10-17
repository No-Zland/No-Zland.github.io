# -*- coding: utf-8 -*-
"""
scenario_tree.py
问题2严格非预见场景生成、场景压缩与多阶段场景树。

本模块不创建Gurobi变量，只负责随机信息结构。

核心原则
--------
1. 历史残差按“整日联合轨迹”抽样，保留负荷/光伏误差的日内相关性；
2. 完整样本轨迹只用于生成树，不能直接对应一套从0:00就知道未来的动作；
3. 通过逐阶段共同节点保证：
       同一已实现信息节点 -> 同一当前动作
4. stage k场景树分支只使用已经完成的0..k-1历史，不使用当前k实现；
5. 条件滚动场景只接收过去已完成真实前缀，不接受current_k及未来真实值。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from config import DEFAULT_CONFIG, ProjectConfig
from forecast_model import (
    DayAheadForecast,
    ResidualLibrary,
    validate_observed_prefix,
)


@dataclass
class ScenarioTrajectorySet:
    """
    一组完整/剩余时域联合轨迹。

    load_kwh / pv_kwh:
        index = scenario_id
        columns = 连续模型k，例如0~143或当前k~143

    probability:
        index = scenario_id，和为1

    source_dates:
        每条轨迹来自哪一个历史残差日；无历史时可为NaT/None。
    """

    load_kwh: pd.DataFrame
    pv_kwh: pd.DataFrame
    probability: pd.Series
    source_dates: pd.Series

    def validate(self) -> None:
        if not self.load_kwh.index.equals(self.pv_kwh.index):
            raise ValueError("负荷场景和光伏场景scenario_id不一致。")

        if not self.load_kwh.columns.equals(self.pv_kwh.columns):
            raise ValueError("负荷场景和光伏场景k列不一致。")

        if not self.load_kwh.index.equals(self.probability.index):
            raise ValueError("场景概率index与scenario_id不一致。")

        if not self.load_kwh.index.equals(self.source_dates.index):
            raise ValueError("source_dates index与scenario_id不一致。")

        columns = [int(k) for k in self.load_kwh.columns]
        if not columns:
            raise ValueError("场景轨迹不能没有物理区间。")

        expected = list(range(columns[0], columns[-1] + 1))
        if columns != expected:
            raise ValueError("场景轨迹k必须为连续物理区间。")

        if self.load_kwh.isna().any().any():
            raise ValueError("负荷场景存在缺失值。")
        if self.pv_kwh.isna().any().any():
            raise ValueError("光伏场景存在缺失值。")

        if (self.load_kwh < -1e-12).any().any():
            raise ValueError("负荷场景存在负值。")
        if (self.pv_kwh < -1e-12).any().any():
            raise ValueError("光伏场景存在负值。")

        prob = self.probability.astype(float)
        if (prob < -1e-15).any():
            raise ValueError("场景概率不能为负。")

        total = float(prob.sum())
        if total <= 0:
            raise ValueError("场景概率和必须为正。")

        if abs(total - 1.0) > 1e-10:
            self.probability = prob / total

    @property
    def scenario_ids(self) -> tuple[int, ...]:
        return tuple(int(i) for i in self.load_kwh.index)

    @property
    def k_values(self) -> tuple[int, ...]:
        return tuple(int(k) for k in self.load_kwh.columns)

    @property
    def start_k(self) -> int:
        return self.k_values[0]

    @property
    def end_k(self) -> int:
        return self.k_values[-1]

    @property
    def n_scenarios(self) -> int:
        return len(self.load_kwh)


@dataclass(frozen=True)
class ScenarioTreeNode:
    """一个信息节点，而不是一条完整叶场景的私有动作节点。"""

    node_id: int
    k: int
    parent_id: Optional[int]

    probability: float
    load_kwh: float
    pv_kwh: float

    member_scenarios: Tuple[int, ...]


class NonanticipativeScenarioTree:
    """
    多阶段非预见场景树。

    同一node_id代表同一已实现信息历史。
    后续优化模型必须对每个node_id只创建一套：
        q_ch, q_dis, q_emg, q_curt, q_sur, E
    从结构上保证非预见性。
    """

    def __init__(
        self,
        nodes: Dict[int, ScenarioTreeNode],
        *,
        start_k: int,
        end_k: int,
    ) -> None:
        self.nodes = dict(nodes)
        self.start_k = int(start_k)
        self.end_k = int(end_k)

        stage_map: Dict[int, List[int]] = {
            k: [] for k in range(self.start_k, self.end_k + 1)
        }
        children_map: Dict[int, List[int]] = {
            node_id: [] for node_id in self.nodes
        }

        for node_id, node in self.nodes.items():
            stage_map[node.k].append(node_id)
            if node.parent_id is not None:
                children_map[node.parent_id].append(node_id)

        self._stage_map = {
            k: tuple(sorted(v))
            for k, v in stage_map.items()
        }
        self._children_map = {
            node_id: tuple(sorted(v))
            for node_id, v in children_map.items()
        }

    def stage_node_ids(self, k: int) -> tuple[int, ...]:
        return self._stage_map[int(k)]

    def root_node_ids(self) -> tuple[int, ...]:
        return self.stage_node_ids(self.start_k)

    def children(self, node_id: int) -> tuple[int, ...]:
        return self._children_map[int(node_id)]

    def leaf_node_ids(self) -> tuple[int, ...]:
        return self.stage_node_ids(self.end_k)

    def path_to_leaf(self, leaf_id: int) -> tuple[int, ...]:
        """返回从当前树根阶段到该叶节点的唯一node路径。"""
        path = []
        current = int(leaf_id)

        while True:
            node = self.nodes[current]
            path.append(current)
            if node.parent_id is None:
                break
            current = int(node.parent_id)

        path.reverse()
        return tuple(path)

    def to_frame(self) -> pd.DataFrame:
        rows = []
        for node_id in sorted(self.nodes):
            node = self.nodes[node_id]
            rows.append(
                {
                    "node_id": node.node_id,
                    "k": node.k,
                    "parent_id": node.parent_id,
                    "probability": node.probability,
                    "load_kwh": node.load_kwh,
                    "pv_kwh": node.pv_kwh,
                    "member_scenarios": node.member_scenarios,
                    "member_count": len(node.member_scenarios),
                }
            )
        return pd.DataFrame(rows)

    def validate_nonanticipativity(self, tol: float = 1e-9) -> pd.DataFrame:
        """
        检查场景树结构是否真正满足“共同历史共享节点”。

        这里不检查Gurobi动作数值，而是检查：
        - 每个节点只有一个父节点；
        - 父节点一定来自上一物理区间；
        - 子节点的成员场景是父节点成员场景子集；
        - 每个stage节点概率和为1；
        - 叶节点概率和为1；
        - 树结构只需要node-indexed动作，不需要leaf-indexed提前动作。
        """
        rows = []

        def add(item: str, passed: bool, detail: str) -> None:
            rows.append(
                {
                    "item": item,
                    "passed": bool(passed),
                    "detail": detail,
                }
            )

        # stage概率
        bad_stage = []
        for k in range(self.start_k, self.end_k + 1):
            total = sum(
                self.nodes[n].probability
                for n in self.stage_node_ids(k)
            )
            if abs(total - 1.0) > tol:
                bad_stage.append((k, total))

        add(
            "stage_probability_sum",
            len(bad_stage) == 0,
            "全部stage概率和为1。"
            if not bad_stage
            else f"异常stage前5个={bad_stage[:5]}",
        )

        # 父子阶段
        bad_parent = []
        bad_subset = []
        for node_id, node in self.nodes.items():
            if node.k == self.start_k:
                if node.parent_id is not None:
                    bad_parent.append((node_id, node.parent_id))
                continue

            if node.parent_id is None:
                bad_parent.append((node_id, None))
                continue

            parent = self.nodes[node.parent_id]
            if parent.k != node.k - 1:
                bad_parent.append(
                    (node_id, node.parent_id, parent.k, node.k)
                )

            if not set(node.member_scenarios).issubset(
                parent.member_scenarios
            ):
                bad_subset.append((node_id, node.parent_id))

        add(
            "parent_previous_stage",
            len(bad_parent) == 0,
            "所有非根节点父节点均位于k-1。"
            if not bad_parent
            else f"异常={bad_parent[:5]}",
        )

        add(
            "child_history_subset",
            len(bad_subset) == 0,
            "所有子节点场景成员均为父节点成员子集。"
            if not bad_subset
            else f"异常={bad_subset[:5]}",
        )

        leaf_prob = sum(
            self.nodes[n].probability
            for n in self.leaf_node_ids()
        )
        add(
            "leaf_probability_sum",
            abs(leaf_prob - 1.0) <= tol,
            f"叶节点概率和={leaf_prob:.12g}",
        )

        add(
            "node_indexed_policy_structure",
            True,
            (
                "树按信息节点node_id组织。优化器对每个node_id只需一套动作，"
                "不存在按完整叶场景在0:00提前创建独立全天动作的必要。"
            ),
        )

        return pd.DataFrame(rows)


def _standardized_feature_matrix(
    load: np.ndarray,
    pv: np.ndarray,
) -> np.ndarray:
    """负荷/光伏联合标准化特征。"""
    load_scale = max(float(np.std(load)), 1e-9)
    pv_scale = max(float(np.std(pv)), 1e-9)

    return np.hstack(
        [
            load / load_scale,
            pv / pv_scale,
        ]
    )


def _pairwise_squared_distance(x: np.ndarray) -> np.ndarray:
    diff = x[:, None, :] - x[None, :, :]
    return np.einsum("ijk,ijk->ij", diff, diff)


def _kmedoids_labels(
    x: np.ndarray,
    n_clusters: int,
    *,
    max_iter: int = 30,
) -> tuple[np.ndarray, np.ndarray]:
    """
    轻量确定性k-medoids，用于场景压缩/节点分裂。

    不依赖sklearn，便于比赛环境复现。
    """
    n = x.shape[0]
    if n == 0:
        raise ValueError("不能对空样本聚类。")

    n_clusters = max(1, min(int(n_clusters), n))

    if n_clusters == 1:
        return np.zeros(n, dtype=int), np.array([0], dtype=int)

    # 如果所有轨迹完全相同，不做无意义分裂。
    if np.allclose(x, x[0], rtol=0.0, atol=1e-12):
        return np.zeros(n, dtype=int), np.array([0], dtype=int)

    dist = _pairwise_squared_distance(x)

    # farthest-first确定性初始化
    mean = x.mean(axis=0)
    first = int(np.argmin(((x - mean) ** 2).sum(axis=1)))
    medoids = [first]

    while len(medoids) < n_clusters:
        nearest = dist[:, medoids].min(axis=1)
        nearest[medoids] = -1.0
        candidate = int(np.argmax(nearest))
        if candidate in medoids:
            break
        medoids.append(candidate)

    medoids = np.array(medoids, dtype=int)

    for _ in range(max_iter):
        labels = np.argmin(dist[:, medoids], axis=1)
        new_medoids = medoids.copy()

        for c in range(len(medoids)):
            members = np.where(labels == c)[0]
            if len(members) == 0:
                continue
            within = dist[np.ix_(members, members)]
            cost = within.sum(axis=1)
            new_medoids[c] = members[int(np.argmin(cost))]

        if np.array_equal(new_medoids, medoids):
            break

        medoids = new_medoids

    labels = np.argmin(dist[:, medoids], axis=1)
    return labels, medoids


def build_bootstrap_trajectory_set(
    forecast: DayAheadForecast,
    residual_library: ResidualLibrary,
    *,
    n_bootstrap: int = 40,
    random_state: int = 2025,
) -> ScenarioTrajectorySet:
    """
    0:00历史联合残差Bootstrap。

    从同一历史日期同时抽取：
        load residual trajectory
        pv residual trajectory

    以保留二者历史联合关系。

    若历史残差库为空（仅用于年初暖启动），退化为单一路径点预测。
    """
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap必须为正整数。")

    columns = list(forecast.load_kwh.index)

    if residual_library.n_days == 0:
        load = pd.DataFrame(
            [forecast.load_kwh.to_numpy(dtype=float)],
            index=[0],
            columns=columns,
        )
        pv = pd.DataFrame(
            [forecast.pv_kwh.to_numpy(dtype=float)],
            index=[0],
            columns=columns,
        )
        probability = pd.Series([1.0], index=[0], dtype=float)
        source_dates = pd.Series([pd.NaT], index=[0], dtype=object)

        result = ScenarioTrajectorySet(
            load_kwh=load,
            pv_kwh=pv,
            probability=probability,
            source_dates=source_dates,
        )
        result.validate()
        return result

    rng = np.random.default_rng(random_state)
    available_dates = residual_library.dates

    sampled_dates = rng.choice(
        available_dates.to_numpy(),
        size=n_bootstrap,
        replace=True,
    )

    load_rows = []
    pv_rows = []

    for s in sampled_dates:
        s = pd.Timestamp(s).normalize()

        load_path = (
            forecast.load_kwh
            + residual_library.load_residual_kwh.loc[s]
        ).clip(lower=0.0)

        pv_path = (
            forecast.pv_kwh
            + residual_library.pv_residual_kwh.loc[s]
        ).clip(lower=0.0)

        load_rows.append(load_path.to_numpy(dtype=float))
        pv_rows.append(pv_path.to_numpy(dtype=float))

    ids = list(range(n_bootstrap))

    result = ScenarioTrajectorySet(
        load_kwh=pd.DataFrame(
            load_rows,
            index=ids,
            columns=columns,
            dtype=float,
        ),
        pv_kwh=pd.DataFrame(
            pv_rows,
            index=ids,
            columns=columns,
            dtype=float,
        ),
        probability=pd.Series(
            np.full(n_bootstrap, 1.0 / n_bootstrap),
            index=ids,
            dtype=float,
        ),
        source_dates=pd.Series(
            [pd.Timestamp(x).normalize() for x in sampled_dates],
            index=ids,
            dtype=object,
        ),
    )
    result.validate()
    return result



def build_conditional_trajectory_set(
    forecast: DayAheadForecast,
    residual_library: ResidualLibrary,
    *,
    observed_load_kwh: pd.Series,
    observed_pv_kwh: pd.Series,
    current_k: int,
    n_bootstrap: int = 16,
    conditioning_pool: int = 12,
    random_state: int = 2025,
    config: ProjectConfig = DEFAULT_CONFIG,
) -> ScenarioTrajectorySet:
    """
    构造区间k开始时的严格因果条件未来场景。

    信息边界
    --------
    在tau_k决定I_k=[tau_k,tau_{k+1})的储能动作时：
        已知真实区间：0,...,k-1
        未知真实区间：k,...,143

    因而本函数只接受0..k-1真实前缀。
    current_k本身及其未来全部由：
        当前点预测 + 历史残差后缀
    生成，绝不使用当天真实current_k。

    k=0时没有当日真实前缀，直接从全部可用历史残差日抽样。
    """
    observed_load, observed_pv = validate_observed_prefix(
        observed_load_kwh,
        observed_pv_kwh,
        current_k,
        config=config,
    )

    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap必须为正整数。")
    if conditioning_pool <= 0:
        raise ValueError("conditioning_pool必须为正整数。")

    future_columns = list(
        range(current_k, config.intervals_per_day)
    )

    # 年初无残差历史：退化为当前点预测路径。
    # 注意：绝不使用current_k真实值覆盖预测。
    if residual_library.n_days == 0:
        load_path = forecast.load_kwh.loc[future_columns].copy()
        pv_path = forecast.pv_kwh.loc[future_columns].copy()

        result = ScenarioTrajectorySet(
            load_kwh=pd.DataFrame(
                [load_path.to_numpy(dtype=float)],
                index=[0],
                columns=future_columns,
            ),
            pv_kwh=pd.DataFrame(
                [pv_path.to_numpy(dtype=float)],
                index=[0],
                columns=future_columns,
            ),
            probability=pd.Series([1.0], index=[0], dtype=float),
            source_dates=pd.Series([pd.NaT], index=[0], dtype=object),
        )
        result.validate()
        return result

    # 已经完成的真实区间，仅0..k-1。
    prefix = list(range(current_k))

    if current_k == 0:
        # 当天尚无真实信息，所有历史残差日均可作为候选。
        selected_dates = residual_library.dates
    else:
        observed_load_resid = (
            observed_load
            - forecast.load_kwh.loc[prefix]
        )
        observed_pv_resid = (
            observed_pv
            - forecast.pv_kwh.loc[prefix]
        )

        hist_load = residual_library.load_residual_kwh.loc[:, prefix]
        hist_pv = residual_library.pv_residual_kwh.loc[:, prefix]

        load_scale = max(
            float(hist_load.to_numpy(dtype=float).std()),
            1e-9,
        )
        pv_scale = max(
            float(hist_pv.to_numpy(dtype=float).std()),
            1e-9,
        )

        load_diff = (
            hist_load.to_numpy(dtype=float)
            - observed_load_resid.to_numpy(dtype=float)[None, :]
        ) / load_scale

        pv_diff = (
            hist_pv.to_numpy(dtype=float)
            - observed_pv_resid.to_numpy(dtype=float)[None, :]
        ) / pv_scale

        distance = np.sqrt(
            np.mean(load_diff**2, axis=1)
            + np.mean(pv_diff**2, axis=1)
        )

        order = np.argsort(distance)
        pool_size = min(conditioning_pool, len(order))
        selected_dates = residual_library.dates[order[:pool_size]]

    if len(selected_dates) == 0:
        raise ValueError("条件场景没有可用历史残差日。")

    rng = np.random.default_rng(random_state)
    sampled_dates = rng.choice(
        selected_dates.to_numpy(),
        size=n_bootstrap,
        replace=True,
    )

    load_rows = []
    pv_rows = []

    for s in sampled_dates:
        s = pd.Timestamp(s).normalize()

        # current_k及以后全部来自预测+历史残差，绝不覆盖成当天真实值。
        load_path = (
            forecast.load_kwh.loc[future_columns]
            + residual_library.load_residual_kwh.loc[
                s, future_columns
            ]
        ).clip(lower=0.0)

        pv_path = (
            forecast.pv_kwh.loc[future_columns]
            + residual_library.pv_residual_kwh.loc[
                s, future_columns
            ]
        ).clip(lower=0.0)

        load_rows.append(load_path.to_numpy(dtype=float))
        pv_rows.append(pv_path.to_numpy(dtype=float))

    ids = list(range(n_bootstrap))

    result = ScenarioTrajectorySet(
        load_kwh=pd.DataFrame(
            load_rows,
            index=ids,
            columns=future_columns,
            dtype=float,
        ),
        pv_kwh=pd.DataFrame(
            pv_rows,
            index=ids,
            columns=future_columns,
            dtype=float,
        ),
        probability=pd.Series(
            np.full(n_bootstrap, 1.0 / n_bootstrap),
            index=ids,
            dtype=float,
        ),
        source_dates=pd.Series(
            [pd.Timestamp(x).normalize() for x in sampled_dates],
            index=ids,
            dtype=object,
        ),
    )
    result.validate()
    return result


def reduce_trajectory_set(
    trajectories: ScenarioTrajectorySet,
    *,
    n_representatives: int = 10,
) -> ScenarioTrajectorySet:
    """
    通过联合负荷/光伏轨迹k-medoids压缩场景。

    每个代表场景概率 = 原场景簇概率和。
    代表轨迹取真实medoid轨迹，不人工平均出不存在的整日路径。
    """
    trajectories.validate()

    n = trajectories.n_scenarios
    if n_representatives <= 0:
        raise ValueError("n_representatives必须为正整数。")

    if n <= n_representatives:
        result = ScenarioTrajectorySet(
            load_kwh=trajectories.load_kwh.copy(),
            pv_kwh=trajectories.pv_kwh.copy(),
            probability=(
                trajectories.probability
                / trajectories.probability.sum()
            ).copy(),
            source_dates=trajectories.source_dates.copy(),
        )
        result.validate()
        return result

    load = trajectories.load_kwh.to_numpy(dtype=float)
    pv = trajectories.pv_kwh.to_numpy(dtype=float)

    features = _standardized_feature_matrix(load, pv)
    labels, medoid_positions = _kmedoids_labels(
        features,
        n_representatives,
    )

    rows_load = []
    rows_pv = []
    probs = []
    sources = []

    old_ids = list(trajectories.load_kwh.index)

    for cluster_id, medoid_pos in enumerate(medoid_positions):
        members_pos = np.where(labels == cluster_id)[0]
        if len(members_pos) == 0:
            continue

        medoid_old_id = old_ids[int(medoid_pos)]

        rows_load.append(
            trajectories.load_kwh.loc[
                medoid_old_id
            ].to_numpy(dtype=float)
        )
        rows_pv.append(
            trajectories.pv_kwh.loc[
                medoid_old_id
            ].to_numpy(dtype=float)
        )

        member_ids = [old_ids[int(i)] for i in members_pos]
        probs.append(
            float(
                trajectories.probability.loc[member_ids].sum()
            )
        )

        source_values = tuple(
            trajectories.source_dates.loc[member_ids].tolist()
        )
        sources.append(source_values)

    new_ids = list(range(len(rows_load)))

    result = ScenarioTrajectorySet(
        load_kwh=pd.DataFrame(
            rows_load,
            index=new_ids,
            columns=trajectories.load_kwh.columns,
            dtype=float,
        ),
        pv_kwh=pd.DataFrame(
            rows_pv,
            index=new_ids,
            columns=trajectories.pv_kwh.columns,
            dtype=float,
        ),
        probability=pd.Series(
            probs,
            index=new_ids,
            dtype=float,
        ),
        source_dates=pd.Series(
            sources,
            index=new_ids,
            dtype=object,
        ),
    )

    result.probability = (
        result.probability / result.probability.sum()
    )
    result.validate()
    return result


def _split_members(
    trajectories: ScenarioTrajectorySet,
    members: Sequence[int],
    *,
    observed_columns: Sequence[int],
    max_branch: int,
) -> list[tuple[int, ...]]:
    """
    仅利用截至当前阶段已经“可观察”的列对父节点成员进行分裂。

    不允许用当前阶段之后的未来列决定当前节点身份。
    """
    members = tuple(int(x) for x in members)

    if len(members) <= 1 or max_branch <= 1:
        return [members]

    n_clusters = min(max_branch, len(members))

    load = trajectories.load_kwh.loc[
        list(members), list(observed_columns)
    ].to_numpy(dtype=float)
    pv = trajectories.pv_kwh.loc[
        list(members), list(observed_columns)
    ].to_numpy(dtype=float)

    features = _standardized_feature_matrix(load, pv)

    labels, medoids = _kmedoids_labels(
        features,
        n_clusters,
    )

    # _kmedoids_labels可能因完全相同样本只返回1类。
    unique_labels = sorted(set(int(x) for x in labels))
    groups = []

    for c in unique_labels:
        group = tuple(
            members[i]
            for i in range(len(members))
            if int(labels[i]) == c
        )
        if group:
            groups.append(group)

    return groups



def build_nonanticipative_tree(
    trajectories: ScenarioTrajectorySet,
    *,
    branch_every: int = 6,
    max_branch: int = 3,
    force_single_root: bool = False,
) -> NonanticipativeScenarioTree:
    """
    将压缩联合轨迹转化为严格“决策先于当前区间实现”的非预见场景树。

    时序定义
    --------
    stage k 的节点动作发生在tau_k。
    因此stage k最多只能依赖已经完成的：
        start_k,...,k-1
    不能使用第k个区间自身的负荷/PV实现来区分当前动作。

    于是：
    - start_k阶段永远只有一个根信息节点；
    - 若在stage k发生分支，聚类特征只使用
          observed_columns = start_k,...,k-1；
    - 从不使用column k或更未来的数据决定stage k节点身份。

    参数
    ----
    force_single_root:
        保留该参数以兼容前文接口。
        在严格时序下根节点无论如何都必须唯一。
        当其为True时，允许在start_k+1立即根据刚完成的start_k区间
        进行第一次分支；否则按branch_every控制首次分支。
    """
    trajectories.validate()

    if branch_every <= 0:
        raise ValueError("branch_every必须为正整数。")
    if max_branch <= 0:
        raise ValueError("max_branch必须为正整数。")

    start_k = trajectories.start_k
    end_k = trajectories.end_k
    all_members = tuple(trajectories.scenario_ids)

    nodes: Dict[int, ScenarioTreeNode] = {}
    next_node_id = 0

    def add_node(
        k: int,
        parent_id: Optional[int],
        members: tuple[int, ...],
    ) -> int:
        nonlocal next_node_id

        member_list = list(members)
        weights = trajectories.probability.loc[
            member_list
        ].to_numpy(dtype=float)

        probability = float(weights.sum())
        normalized = weights / probability

        # 当前stage尚未观测第k区间，因此节点中的L/G是该信息集下
        # 对current interval的条件均值，而不是当天真实值。
        load_values = trajectories.load_kwh.loc[
            member_list, k
        ].to_numpy(dtype=float)
        pv_values = trajectories.pv_kwh.loc[
            member_list, k
        ].to_numpy(dtype=float)

        load_kwh = float(np.dot(normalized, load_values))
        pv_kwh = float(np.dot(normalized, pv_values))

        node_id = next_node_id
        next_node_id += 1

        nodes[node_id] = ScenarioTreeNode(
            node_id=node_id,
            k=k,
            parent_id=parent_id,
            probability=probability,
            load_kwh=load_kwh,
            pv_kwh=pv_kwh,
            member_scenarios=tuple(sorted(members)),
        )

        return node_id

    # 严格非预见：当前start_k尚无当前区间实现，因此根节点唯一。
    current_groups = [all_members]
    group_to_node: Dict[tuple[int, ...], int] = {}

    root_id = add_node(start_k, None, all_members)
    group_to_node[tuple(sorted(all_members))] = root_id

    last_branch_k = start_k

    for k in range(start_k + 1, end_k + 1):
        if force_single_root and k == start_k + 1:
            should_branch = True
        else:
            should_branch = (k - last_branch_k) >= branch_every

        next_groups: list[tuple[int, ...]] = []

        if should_branch:
            # stage k动作前只看已经完成到k-1的真实历史。
            observed_columns = list(range(start_k, k))

            for group in current_groups:
                split = _split_members(
                    trajectories,
                    group,
                    observed_columns=observed_columns,
                    max_branch=max_branch,
                )
                next_groups.extend(split)

            last_branch_k = k
        else:
            next_groups = list(current_groups)

        next_group_to_node: Dict[tuple[int, ...], int] = {}

        for group in next_groups:
            group_key = tuple(sorted(group))

            parent_group = None
            for candidate in current_groups:
                if set(group_key).issubset(candidate):
                    parent_group = tuple(sorted(candidate))
                    break

            if parent_group is None:
                raise AssertionError("无法为场景树子节点找到父信息节点。")

            parent_id = group_to_node[parent_group]
            node_id = add_node(k, parent_id, group_key)
            next_group_to_node[group_key] = node_id

        current_groups = next_groups
        group_to_node = next_group_to_node

    tree = NonanticipativeScenarioTree(
        nodes,
        start_k=start_k,
        end_k=end_k,
    )

    report = tree.validate_nonanticipativity()

    if len(tree.root_node_ids()) != 1:
        raise AssertionError(
            "严格决策时序要求当前stage只能有一个根信息节点。"
        )

    if not report["passed"].all():
        failed = report.loc[~report["passed"]]
        raise AssertionError(
            "生成的场景树未通过非预见性检查：\n"
            + failed.to_string(index=False)
        )

    return tree
