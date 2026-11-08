# -*- coding: utf-8 -*-
from time_index import build_time_map, validate_time_map


def test_canonical_time_map():
    tm = build_time_map()
    validate_time_map(tm)

    by_k = tm.set_index("k")

    assert by_k.loc[0, "paper_label"] == "0:00-0:10"
    assert by_k.loc[0, "source_right_endpoint_label"] == "0:10"

    assert by_k.loc[36, "paper_label"] == "6:00-6:10"
    assert by_k.loc[36, "source_right_endpoint_label"] == "6:10"

    assert by_k.loc[60, "paper_label"] == "10:00-10:10"
    assert by_k.loc[60, "source_right_endpoint_label"] == "10:10"

    assert by_k.loc[143, "paper_label"] == "23:50-24:00"
    assert by_k.loc[143, "source_right_endpoint_label"] == "0:00+1"

    assert tm["template_slot"].tolist() == list(range(144))
