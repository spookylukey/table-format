# fmt: off
# Black tends to obfuscate these tests, turned off for whole file

import subprocess


def test_cli_simple():
    output = subprocess.check_output(['table-format'], input=b'[]')  # noqa:S607
    assert output == b'''[
]'''


def test_cli_quote_style():
    output = subprocess.check_output(['table-format', '--quote-style', 'double'], input=b'[["hi"]]')  # noqa:S607
    assert output == b'''[
    ["hi"],
]'''
