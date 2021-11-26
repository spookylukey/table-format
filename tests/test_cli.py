# fmt: off
# Black tends to obfuscate these tests, turned off for whole file

import subprocess


def test_cli_simple():
    output = subprocess.check_output(['table-format'], input=b'[]')  # noqa:S607
    assert output == b'''[
]'''
