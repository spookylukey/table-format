from table_format import reformat


def test_reformat_empty():
    assert reformat("""[]""") == "[\n]"


def test_reformat_simple():
    assert (
        reformat(
            """ [
    [a, b, c],
    [defg, hi, jkl],
]"""
        )
        == """ [
    [a,    b,  c  ],
    [defg, hi, jkl],
]"""
    )


def test_reformat_align_commas():
    assert (
        reformat(
            """ [
    [a, b, c],
    [defg, hi, jkl],
]""",
            align_commas=True,
        )
        == """ [
    [a   , b , c  ],
    [defg, hi, jkl],
]"""
    )


def test_reformat_guess_indent_commas():
    assert (
        reformat(
            """ [
        [a, b],
        [defg, hi],
]""",
            guess_indent=True,
        )
        == """ [
        [a,    b ],
        [defg, hi],
    ]"""
    )
