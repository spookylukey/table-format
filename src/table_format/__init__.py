# -*- coding: utf-8 -*-
"""Format Python code (list of lists) as a fixed width table."""
import ast
from collections import defaultdict

import ast_decompiler

ONE_INDENT = 4  # spaces. As God intended


def reformat(python_code: str, align_commas=False, guess_indent=False):
    """
    Reformat list of lists as fixed width table
    """
    if python_code.strip() == "":
        return ""
    try:
        code_ast = ast.parse(python_code.strip())
    except SyntaxError:
        raise AssertionError("Couldn't parse input as Python code")

    # Validate input
    expressions = code_ast.body
    if not len(expressions) == 1:
        raise AssertionError("Expected a single expression in the submitted code.")
    expr = expressions[0]
    if not isinstance(expr.value, ast.List):
        raise AssertionError("Expected a list expression as single input expression.")
    main_list = expr.value
    for element in main_list.elts:
        if not isinstance(element, ast.List):
            raise AssertionError(f"Expected each sub element to be a list, found {element}.")

    # Build all reprs of elements
    reprs = [[ast_decompiler.decompile(element) for element in sublist.elts] for sublist in expr.value.elts]

    # Calculate max widths
    col_widths = defaultdict(int)
    for row in reprs:
        for idx, item in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(item))

    # Indents
    indent = " " * ONE_INDENT
    initial_indent = ""
    final_indent = ""
    if python_code.startswith(" "):
        # Restore the initial indent, so code will copy-paste directly into
        # where it came from.
        length_without_indent = len(python_code.lstrip(" "))
        initial_indent = python_code[0:-length_without_indent]

    if guess_indent:
        # We assuming code looks like this:
        # def test_foo():
        #     assert answer == [
        #         [a, b, c],
        #         [def, ghi, jkl],
        #     ]
        #
        # The user has selected text from first '['
        parts = python_code.strip().split("[")
        if len(parts) > 1 and parts[1].startswith("\n"):
            indent = parts[1].lstrip("\n")
            final_indent = max(len(indent) - ONE_INDENT, 0) * " "

    # Output
    output = []
    output.append(initial_indent + "[\n")
    for row in reprs:
        output.append(indent + "[")
        for idx, item in enumerate(row):
            need_comma = idx < len(row) - 1
            separator = ", " if need_comma else ""
            pre_separator = "" if align_commas else separator
            post_separator = separator if align_commas else ""
            output.append(item + pre_separator + " " * (col_widths[idx] - len(item)) + post_separator)
        output.append("],\n")
    output.append(final_indent + "]")
    return "".join(output)
