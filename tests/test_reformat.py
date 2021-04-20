import pytest

from table_format import reformat


def test_reformat_empty():
    assert reformat("""[]""") == "[\n]"


def test_reformat_simple():
    assert reformat("""[
    [a, b, c],
    [defg, hi, jkl],
]""") == """[
    [a,    b,  c  ],
    [defg, hi, jkl],
]"""


def test_reformat_preserve_inital_indent():
    assert reformat("""    []""") == """    [
]"""


def test_reformat_align_commas():
    assert reformat("""[
    [a, b, c],
    [defg, hi, jkl],
]""", align_commas=True) == """[
    [a   , b , c  ],
    [defg, hi, jkl],
]"""


def test_reformat_guess_indent():
    assert reformat("""[
        [a, b],
        [defg, hi],
]""", guess_indent=True) == """[
        [a,    b ],
        [defg, hi],
    ]"""


def test_reformat_guess_indent_with_comment():
    assert reformat("""[
        # Hello
        [a, b],
        [defg, hi],
]""", guess_indent=True) == """[
        # Hello
        [a,    b ],
        [defg, hi],
    ]"""


def test_reformat_bad_syntax():
    with pytest.raises(AssertionError):
        reformat('[')


def test_reformat_not_a_list():
    with pytest.raises(AssertionError):
        reformat('1')


def test_reformat_not_a_list_of_lists():
    with pytest.raises(AssertionError):
        reformat('[1]')


def test_preserve_comments_between_lines():
    assert reformat("""[
    # Leading stuff
    # More leading stuff
    [abc, defg],
    # Middle stuff
    # More middle stuff
    [1, 2],
    # More middle stuff 2
    [3, 4]
    # Trailing stuff
    # More trailing stuff
]""") == """[
    # Leading stuff
    # More leading stuff
    [abc, defg],
    # Middle stuff
    # More middle stuff
    [1,   2   ],
    # More middle stuff 2
    [3,   4   ],
    # Trailing stuff
    # More trailing stuff
]"""


def test_preserve_comments_at_ends_of_lines():
    assert reformat("""[
    [abc, defg],  # Stuff
    [1, 2]  # More stuff
]""") == """[
    [abc, defg],  # Stuff
    [1,   2   ],  # More stuff
]"""


def test_preserve_comments_with_guess_indent():
    assert reformat("""[
    # Leading stuff
    [abc, defg],
    # Middle stuff
    [1, 2],
    # More middle stuff 2
    [3, 4]
    # Trailing stuff
]""", guess_indent=True) == """[
    # Leading stuff
    [abc, defg],
    # Middle stuff
    [1,   2   ],
    # More middle stuff 2
    [3,   4   ],
    # Trailing stuff
]"""


def test_whitespace_in_item():
    assert reformat("""[
    [  function_call(
       arg1,
       arg2 ,
       (tuple_1,),
       (tuple_2, x),
     ),
     a   +   b /2 or  3
    ]]""") == """[
    [function_call(arg1, arg2, (tuple_1,), (tuple_2, x)), a + b / 2 or 3],
]"""


# This would be nice, but hard.
# def test_preserve_quotes():
#     assert reformat("""[[""]]""") == """[\n    [""],\n]"""
#     assert reformat("""[['']]""") == """[\n    [''],\n]"""


def test_add_noqa():
    assert reformat("""[
    [abc, defg],
    [1, 2],  # A comment here
    [34, 56],  # noqa: X111
    [7, 8]  # noqa:X111,X999 and a comment
]""", add_noqa=["E202", "E501"]) == """[
    [abc, defg],  # noqa: E202,E501
    [1,   2   ],  # noqa: E202,E501  A comment here
    [34,  56  ],  # noqa: E202,E501,X111
    [7,   8   ],  # noqa: E202,E501,X111,X999  and a comment
]"""
