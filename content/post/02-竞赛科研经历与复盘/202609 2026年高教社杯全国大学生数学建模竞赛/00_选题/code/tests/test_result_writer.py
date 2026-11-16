# -*- coding: utf-8 -*-
import pandas as pd

from result_writer import (
    REPORT_INTERVAL_INDEX,
    merge_emergency_intervals,
)
from time_index import build_time_map


def test_paper_report_indices_are_fixed_model_k():
    assert REPORT_INTERVAL_INDEX == (
        60,
        72,
        84,
        96,
        108,
        120,
    )

    tm = build_time_map().set_index("k")
    assert tm.loc[60, "paper_label"] == "10:00-10:10"


def test_emergency_adjacent_physical_intervals_merge():
    q = pd.Series(
        0.0,
        index=list(range(144)),
        dtype=float,
    )
    q.loc[78] = 1.0
    q.loc[79] = 2.0
    q.loc[80] = 3.0

    events = merge_emergency_intervals(q)

    assert len(events) == 1
    assert events[0]["start_k"] == 78
    assert events[0]["end_k"] == 80
    assert events[0]["paper_interval"] == "13:00-13:30"
    assert events[0]["emergency_kwh"] == 6.0
