from inventory.stock import diff_counts


def test_diff():
    assert diff_counts({"a": 1}, {"a": 3}) == {"a": 2}
