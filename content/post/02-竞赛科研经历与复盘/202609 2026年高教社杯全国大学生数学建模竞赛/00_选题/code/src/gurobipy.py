# -*- coding: utf-8 -*-
"""
gurobipy.py
gurobipy 兼容层（HiGHS 后端）。

本项目原先依赖 Gurobi，但 Gurobi 许可证受限/被禁止。
本模块用开源求解器 HiGHS（经 scipy.optimize.milp 调用）实现了
src/ 下各求解器实际用到的 gurobipy 子集，从而无需改动求解器的
业务逻辑即可替换求解器。

覆盖的接口（仅这些，与 model_base/question1/2/3 的用法一一对应）：
    gp.Model / gp.quicksum / gp.LinExpr / gp.tupledict
    gp.Var / gp.Constr / GRB 常量
    model.addVar / addVars / addConstr / setObjective / optimize
    model.Params.OutputFlag / model.Status / model.ObjVal / var.X

不支持的 gurobipy 高级特性（本项目未使用）会抛出明确的 TypeError/ValueError。
"""

from __future__ import annotations

import itertools
from typing import Any, Iterable, Optional


# ============================================================================
# 常量
# ============================================================================

class GRB:
    """gurobipy.GRB 的常量子集。"""

    MINIMIZE = 1
    MAXIMIZE = -1

    CONTINUOUS = "C"
    BINARY = "B"
    INTEGER = "I"

    OPTIMAL = 2
    INFEASIBLE = 3
    INF_OR_UNBD = 4
    UNBOUNDED = 5
    TIME_LIMIT = 9
    SUBOPTIMAL = 13

    INFINITY = float("inf")

    EQUAL = "="
    LESS_EQUAL = "<"
    GREATER_EQUAL = ">"


# ============================================================================
# 线性表达式
# ============================================================================

def _expr_parts(x: Any) -> tuple[dict[int, float], float]:
    """把 Var / LinExpr / 数字 拆成 (系数表, 常数)。"""
    if isinstance(x, LinExpr):
        return x._coeffs, x._constant
    if isinstance(x, (int, float)):
        return {}, float(x)
    raise TypeError(f"不支持的操作数类型：{type(x)!r}")


def _as_lin(x: Any) -> "LinExpr":
    """把 Var / 数字 归一为 LinExpr。"""
    if isinstance(x, LinExpr):
        return x
    if isinstance(x, (int, float)):
        e = LinExpr()
        e._constant = float(x)
        return e
    raise TypeError(f"不支持的操作数类型：{type(x)!r}")


def _new_expr(coeffs: dict[int, float], constant: float) -> "LinExpr":
    e = LinExpr()
    e._coeffs = {
        k: float(v)
        for k, v in coeffs.items()
        if v != 0.0
    }
    e._constant = float(constant)
    return e


class LinExpr:
    """线性表达式：coeffs·x + constant。"""

    def __init__(self, constant: float = 0.0):
        self._coeffs: dict[int, float] = {}
        self._constant: float = float(constant)

    # -- 算术 ----------------------------------------------------------------
    def __add__(self, other: Any) -> "LinExpr":
        c2, k2 = _expr_parts(other)
        c = dict(self._coeffs)
        for i, v in c2.items():
            c[i] = c.get(i, 0.0) + v
        return _new_expr(c, self._constant + k2)

    def __radd__(self, other: Any) -> "LinExpr":
        return self.__add__(other)

    def __sub__(self, other: Any) -> "LinExpr":
        c2, k2 = _expr_parts(other)
        c = dict(self._coeffs)
        for i, v in c2.items():
            c[i] = c.get(i, 0.0) - v
        return _new_expr(c, self._constant - k2)

    def __rsub__(self, other: Any) -> "LinExpr":
        c2, k2 = _expr_parts(other)
        c = {i: -v for i, v in self._coeffs.items()}
        for i, v in c2.items():
            c[i] = c.get(i, 0.0) + v
        return _new_expr(c, k2 - self._constant)

    def __mul__(self, other: Any) -> "LinExpr":
        if isinstance(other, (int, float)):
            s = float(other)
            return _new_expr(
                {i: v * s for i, v in self._coeffs.items()},
                self._constant * s,
            )
        raise TypeError("不支持非线性项（变量×变量）。")

    def __rmul__(self, other: Any) -> "LinExpr":
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> "LinExpr":
        if isinstance(other, (int, float)):
            return self.__mul__(1.0 / float(other))
        raise TypeError("仅支持线性表达式除以标量。")

    def __neg__(self) -> "LinExpr":
        return _new_expr(
            {i: -v for i, v in self._coeffs.items()},
            -self._constant,
        )

    # -- 比较（生成临时约束，交给 model.addConstr 消费） ---------------------
    def __eq__(self, other: Any) -> "_TempConstr":  # type: ignore[override]
        return _TempConstr(self, _as_lin(other), GRB.EQUAL)

    def __le__(self, other: Any) -> "_TempConstr":
        return _TempConstr(self, _as_lin(other), GRB.LESS_EQUAL)

    def __ge__(self, other: Any) -> "_TempConstr":
        return _TempConstr(self, _as_lin(other), GRB.GREATER_EQUAL)

    def __hash__(self) -> int:
        return id(self)


class Var(LinExpr):
    """单个决策变量（本身就是含一项系数的线性表达式）。"""

    def __init__(
        self,
        model: "Model",
        index: int,
        lb: Optional[float],
        ub: Optional[float],
        vtype: str,
        name: str = "",
    ):
        super().__init__(0.0)
        self._coeffs = {index: 1.0}
        self._model = model
        self._index = index
        self._lb = lb
        self._ub = ub
        self._vtype = vtype
        self._name = name
        self.X: float = 0.0

    def __repr__(self) -> str:
        return f"<Var {self._name or self._index}>"


class Constr:
    """约束占位对象（本项目仅存储，不读取其属性）。"""

    def __init__(self, constr: "_TempConstr", name: str = ""):
        self._constr = constr
        self.ConstrName = name


class _TempConstr:
    """由比较运算临时生成的约束：lhs [sense] rhs。"""

    def __init__(self, lhs: LinExpr, rhs: LinExpr, sense: str):
        self.lhs = _as_lin(lhs)
        self.rhs = _as_lin(rhs)
        self.sense = sense


# ============================================================================
# tupledict
# ============================================================================

class tupledict(dict):
    """gurobipy.tupledict 的极简替代（本项目中只当普通 dict 使用）。"""

    def sum(self) -> LinExpr:
        total = LinExpr(0.0)
        for v in self.values():
            total = total + v
        return total

    def prod(self, coeffs: Any) -> LinExpr:
        total = LinExpr(0.0)
        for key, v in self.items():
            total = total + coeffs[key] * v
        return total


# ============================================================================
# quicksum
# ============================================================================

def quicksum(data: Iterable[Any]) -> LinExpr:
    """把可迭代对象中的各项累加为线性表达式。"""
    total = LinExpr(0.0)
    for term in data:
        if isinstance(term, (LinExpr, int, float)):
            total = total + term
        elif isinstance(term, tuple) and len(term) == 2:
            total = total + term[0] * term[1]
        else:
            raise TypeError(f"quicksum 无法处理项：{type(term)!r}")
    return total


# ============================================================================
# 模型
# ============================================================================

class _Params:
    def __init__(self):
        self.OutputFlag: int = 1
        self.TimeLimit: Optional[float] = None
        self.MIPGap: Optional[float] = None
        self.Threads: int = 0


class Model:
    """gurobipy.Model 的极简替代，底层调用 HiGHS。"""

    def __init__(self, name: str = ""):
        self.ModelName = name
        self.Params = _Params()
        self.Status: Optional[int] = None
        self.ObjVal: Optional[float] = None

        self._vars: list[Var] = []
        self._constrs: list[_TempConstr] = []
        self._objective: Optional[LinExpr] = None
        self._objective_sense: int = GRB.MINIMIZE
        self._optimized: bool = False

    # -- 变量 ----------------------------------------------------------------
    def addVar(
        self,
        lb: Optional[float] = 0.0,
        ub: Optional[float] = None,
        vtype: str = GRB.CONTINUOUS,
        name: str = "",
        obj: float = 0.0,
    ) -> Var:
        if vtype == GRB.BINARY:
            lb = 0.0 if lb is None else lb
            ub = 1.0 if ub is None else ub
        else:
            lb = 0.0 if lb is None else lb
            ub = GRB.INFINITY if ub is None else ub

        idx = len(self._vars)
        v = Var(self, idx, float(lb), float(ub), vtype, name)
        self._vars.append(v)

        if obj != 0.0:
            if self._objective is None:
                self._objective = LinExpr(0.0)
            self._objective = self._objective + obj * v

        self._optimized = False
        return v

    def addVars(
        self,
        *keys: Any,
        lb: Optional[float] = 0.0,
        ub: Optional[float] = None,
        vtype: str = GRB.CONTINUOUS,
        name: str = "",
        obj: Any = 0.0,
    ) -> tupledict:
        result = tupledict()
        if len(keys) == 1:
            for k in keys[0]:
                result[k] = self.addVar(lb=lb, ub=ub, vtype=vtype, name=name)
        else:
            for combo in itertools.product(*keys):
                key = combo[0] if len(combo) == 1 else combo
                result[key] = self.addVar(lb=lb, ub=ub, vtype=vtype, name=name)
        return result

    # -- 约束 ----------------------------------------------------------------
    def addConstr(
        self,
        lhs: Any,
        sense: Optional[str] = None,
        rhs: Any = None,
        name: str = "",
    ) -> Constr:
        if isinstance(lhs, _TempConstr):
            c = lhs
        else:
            if sense is None:
                raise TypeError("addConstr 需要比较表达式或显式给出 sense/rhs。")
            c = _TempConstr(_as_lin(lhs), _as_lin(rhs), sense)

        self._constrs.append(c)
        self._optimized = False
        return Constr(c, name)

    # -- 目标 ----------------------------------------------------------------
    def setObjective(self, expr: Any, sense: Optional[int] = None) -> None:
        self._objective = _as_lin(expr)
        if sense is not None:
            self._objective_sense = sense
        self._optimized = False

    # -- 求解 ----------------------------------------------------------------
    def update(self) -> None:
        return None

    def optimize(self) -> None:
        self._solve_highs()
        self._optimized = True

    def _solve_highs(self) -> None:
        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp
        from scipy.sparse import coo_matrix

        n = len(self._vars)
        if n == 0:
            self.Status = GRB.OPTIMAL
            self.ObjVal = 0.0
            return

        # 目标向量
        c = np.zeros(n, dtype=float)
        obj_const = 0.0
        if self._objective is not None:
            for idx, coeff in self._objective._coeffs.items():
                c[idx] = coeff
            obj_const = self._objective._constant
        if self._objective_sense == GRB.MAXIMIZE:
            c = -c
            obj_const = -obj_const

        # 变量边界与整数性
        lb = np.empty(n, dtype=float)
        ub = np.empty(n, dtype=float)
        has_integer = any(
            v._vtype in (GRB.BINARY, GRB.INTEGER) for v in self._vars
        )
        integrality = None
        if has_integer:
            integrality = np.zeros(n, dtype=np.uint8)
            for i, v in enumerate(self._vars):
                integrality[i] = (
                    1 if v._vtype in (GRB.BINARY, GRB.INTEGER) else 0
                )
        for i, v in enumerate(self._vars):
            lb[i] = v._lb if v._lb is not None else -np.inf
            ub[i] = v._ub if v._ub is not None else np.inf

        # 约束：统一为 (lhs - rhs) op 0
        rows: list[int] = []
        cols: list[int] = []
        data: list[float] = []
        c_lb: list[float] = []
        c_ub: list[float] = []

        for ci, constr in enumerate(self._constrs):
            coeffs: dict[int, float] = {}
            for idx, val in constr.lhs._coeffs.items():
                coeffs[idx] = coeffs.get(idx, 0.0) + val
            for idx, val in constr.rhs._coeffs.items():
                coeffs[idx] = coeffs.get(idx, 0.0) - val

            b = constr.rhs._constant - constr.lhs._constant

            for idx, val in coeffs.items():
                if val != 0.0:
                    rows.append(ci)
                    cols.append(idx)
                    data.append(val)

            if constr.sense == GRB.LESS_EQUAL:
                c_lb.append(-np.inf)
                c_ub.append(b)
            elif constr.sense == GRB.GREATER_EQUAL:
                c_lb.append(b)
                c_ub.append(np.inf)
            else:  # EQUAL
                c_lb.append(b)
                c_ub.append(b)

        constraints = None
        if self._constrs:
            A = coo_matrix(
                (data, (rows, cols)),
                shape=(len(self._constrs), n),
            ).tocsr()
            constraints = LinearConstraint(
                A,
                np.array(c_lb, dtype=float),
                np.array(c_ub, dtype=float),
            )

        bounds = Bounds(lb, ub)

        options = {"disp": self.Params.OutputFlag > 0}
        if self.Params.TimeLimit is not None:
            options["time_limit"] = float(self.Params.TimeLimit)
        if self.Params.MIPGap is not None:
            options["mip_rel_gap"] = float(self.Params.MIPGap)

        res = milp(
            c,
            integrality=integrality,
            bounds=bounds,
            constraints=constraints,
            options=options,
        )

        if res.status == 0:
            self.Status = GRB.OPTIMAL
        elif res.status == 2:
            self.Status = GRB.INFEASIBLE
        elif res.status == 3:
            self.Status = GRB.UNBOUNDED
        else:
            self.Status = int(res.status)

        if res.status == 0:
            x = res.x
            for i, v in enumerate(self._vars):
                xi = x[i]
                v.X = float(xi) if not np.isnan(xi) else 0.0
            self.ObjVal = float(res.fun) + obj_const
        else:
            for v in self._vars:
                v.X = 0.0
            self.ObjVal = None

    # -- 查询（供调试，本项目未直接使用） ------------------------------------
    @property
    def NumVars(self) -> int:
        return len(self._vars)

    @property
    def NumConstrs(self) -> int:
        return len(self._constrs)

    def getVars(self) -> list[Var]:
        return list(self._vars)
