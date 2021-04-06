from table_format import reformat


def test_reformat_empty():
    assert reformat("""[]""") == "[\n]"


def test_reformat_simple():
    assert reformat(""" [
    [a, b, c],
    [defg, hi, jkl],
]""") == """ [
    [a,    b,  c  ],
    [defg, hi, jkl],
]"""
