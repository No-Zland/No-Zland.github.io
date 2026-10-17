# -*- coding: utf-8 -*-
import pandas as pd
import pytest

from forecast_model import validate_observed_prefix


def test_current_k_zero_requires_empty_history():
    load = pd.Series(dtype=float)
    pv = pd.Series(dtype=float)

    a, b = validate_observed_prefix(
        load,
        pv,
        current_k=0,
    )

    assert len(a) == 0
    assert len(b) == 0


def test_current_k_36_allows_only_0_to_35():
    idx = list(range(36))
    load = pd.Series(1.0, index=idx)
    pv = pd.Series(0.5, index=idx)

    a, b = validate_observed_prefix(
        load,
        pv,
        current_k=36,
    )

    assert list(a.index) == list(range(36))
    assert list(b.index) == list(range(36))


def test_current_interval_actual_must_not_enter_decision():
    idx = list(range(37))
    load = pd.Series(1.0, index=idx)
    pv = pd.Series(0.5, index=idx)

    with pytest.raises(ValueError):
        validate_observed_prefix(
            load,
            pv,
            current_k=36,
        )
