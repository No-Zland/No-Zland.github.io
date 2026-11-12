# -*- coding: utf-8 -*-
from rolling_scheduler import run_settlement_self_tests


def test_q3_settlement_identity():
    report = run_settlement_self_tests(c=2.0)
    assert report["passed"].all()

    down = report.loc[
        report["test"] == "A_down_adjustment",
        "actual",
    ].iloc[0]
    up = report.loc[
        report["test"] == "B_up_adjustment",
        "actual",
    ].iloc[0]

    assert down == 180.0
    assert up == 260.0
