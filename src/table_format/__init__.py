# -*- coding: utf-8 -*-
"""Format Python code (list of lists) as a fixed width table."""
import ast
import enum
import sys
from collections import defaultdict
from contextlib import contextmanager
from typing import List

import ast_decompiler.decompiler
import libcst
import parsy
from libcst._nodes.internal import CodegenState

ONE_INDENT = 4  # spaces. As God intended


OPENER = {
    libcst.List: "[",
    libcst.Tuple: "(",
}


CLOSER = {
    libcst.List: "]",
    libcst.Tuple: ")",
}


ITEM_SEP = ", "


class QuoteStyle(enum.Enum):
    SINGLE = "single"
    DOUBLE = "double"


def reformat(
    python_code: str,
    align_commas: bool = False,
    guess_indent: bool = False,
    add_noqa: List[str] = None,
    quote_style: QuoteStyle = QuoteStyle.SINGLE,
):
    """
    Reformat list of lists as fixed width table
    """
    # Who says your code can't just be one massive function...

    if add_noqa is None:
        add_noqa = []
    if python_code.strip() == "":
        return ""
    try:
        code_cst = libcst.parse_expression(python_code.strip())
    except Exception:
        raise AssertionError("Couldn't parse input as Python code")

    # Validate input
    if not isinstance(code_cst, libcst.List):
        raise AssertionError("Expected a list expression as single input expression.")
    for element in code_cst.elements:
        if not isinstance(element.value, (libcst.List, libcst.Tuple)):
            raise AssertionError(f"Expected each sub element to be a list or tuple, found {element.value}.")

    # Build all reprs of elements
    reprs = [
        [
            reformat_as_single_line(cst_node_to_code(element.value), quote_style=quote_style)
            for element in sublist.value.elements
        ]
        for sublist in code_cst.elements
    ]
    row_types = [type(element.value) for element in code_cst.elements]

    # Calculate max widths
    col_widths = defaultdict(int)
    col_count = 0
    for row in reprs:
        idx = 0
        for idx, item in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(item))
        col_count = max(col_count, idx + 1)

    # Indents
    indent = " " * ONE_INDENT
    initial_indent = ""
    final_indent = ""
    if python_code.startswith(" "):
        # Restore the initial indent, so code will copy-paste directly into
        # where it came from.
        initial_indent = " " * get_indent_size(python_code)

    if guess_indent:
        # We assuming code looks like this:
        # def test_foo():
        #     assert answer == [
        #         [a, b, c],
        #         [def, ghi, jkl],
        #     ]
        #
        # The user has selected text from first '['
        # We remove any comment lines
        lines = python_code.strip().split("\n")
        lines = [line for line in lines if not line.strip().startswith("#")]
        if len(lines) > 1:
            indent_size = get_indent_size(lines[1])
            indent = " " * indent_size
            final_indent = " " * max(indent_size - ONE_INDENT, 0)

    # Collect comments.

    # This is the most fragile bit - it would be easy to miss things here. The
    # alternative would a very different structure for the whole code, that
    # transforms code_cst, adjusting whitespace as we go. It might be harder and
    # more bug prone however. We cannot support comments in every location either,
    # so it might be simpler this way.

    # Comments before first row
    if hasattr(code_cst.lbracket.whitespace_after, "empty_lines"):
        initial_comments = [
            (line.comment.value if line.comment is not None else "") + "\n"
            for line in code_cst.lbracket.whitespace_after.empty_lines
        ]
    else:
        initial_comments = []

    # Comments at the end of each row - paired with rows
    end_of_row_comments = []
    for element in code_cst.elements:
        if (
            hasattr(element.comma, "whitespace_after")
            and hasattr(element.comma.whitespace_after, "first_line")
            and getattr(element.comma.whitespace_after.first_line, "comment", None)
        ):
            comment = element.comma.whitespace_after.first_line.comment.value
        else:
            comment = ""
        end_of_row_comments.append(comment)
    # Last row comment is attached to rbracket of main expression
    if hasattr(code_cst.rbracket.whitespace_before, "first_line") and getattr(
        code_cst.rbracket.whitespace_before.first_line, "comment", None
    ):
        end_of_row_comments[-1] = code_cst.rbracket.whitespace_before.first_line.comment.value

    # Comments on their own lines after each row - these will be paired with rows
    after_row_comments = []
    for element in code_cst.elements:
        if hasattr(element.comma, "whitespace_after") and hasattr(element.comma.whitespace_after, "empty_lines"):
            comment = "\n".join(
                getattr(line.comment, "value", "") for line in element.comma.whitespace_after.empty_lines
            )
        else:
            comment = ""
        after_row_comments.append(comment)

    # Comments on their own lines after the last row
    if hasattr(code_cst.rbracket.whitespace_before, "empty_lines"):
        final_comments = [
            (line.comment.value if line.comment is not None else "") + "\n"
            for line in code_cst.rbracket.whitespace_before.empty_lines
        ]
    else:
        final_comments = []

    # Output
    output = []
    output.append(initial_indent + "[\n")
    for comment in initial_comments:
        append_comment(output, indent, comment)
    for row, row_type, end_of_row_comment, after_row_comment in zip(
        reprs, row_types, end_of_row_comments, after_row_comments
    ):
        output.append(indent + OPENER[row_type])
        last_idx = -1
        for idx, item in enumerate(row):
            need_comma = idx < len(row) - 1
            separator = ITEM_SEP if need_comma else ""
            pre_separator = "" if align_commas else separator
            post_separator = separator if align_commas else ""
            output.append(item + pre_separator + " " * (col_widths[idx] - len(item)) + post_separator)
            last_idx = idx
        output.append(CLOSER[row_type] + ",")
        adjusted_end_of_row_comment = add_noqa_markers(end_of_row_comment, add_noqa)
        if adjusted_end_of_row_comment:
            # padding for ragged rows:
            comment_padding = sum(
                col_widths[i] + (len(ITEM_SEP) if i > 0 else 0) for i in range(last_idx + 1, col_count)
            )
            output.append(" " * comment_padding + "  # " + adjusted_end_of_row_comment)
        output.append("\n")
        if after_row_comment:
            for comment in after_row_comment.split("\n"):
                if comment.strip():
                    output.append(indent + comment + "\n")
                else:
                    output.append("\n")
    for comment in final_comments:
        append_comment(output, indent, comment)
    output.append(final_indent + "]")
    return "".join(output)


def cst_node_to_code(node):
    state = CodegenState(default_indent=4, default_newline="\n")
    node._codegen(state)
    return "".join(state.tokens)


def append_comment(output, indent, comment):
    line = indent + comment
    if not line.strip():
        # Whitespace only, preserve only vertical whitespace
        # so that we're not adding trailing whitespace to lines
        output.append(line.lstrip(" "))
    else:
        output.append(line)


def reformat_as_single_line(python_code, quote_style: QuoteStyle = QuoteStyle.SINGLE):
    code_ast = ast.parse(python_code.strip())
    # The following has the unfortunate effect of not preserving quote style.
    # But so far, for getting code formatted using normal PEP8 conventions, in a
    # single line, this approach seems much easier compared to other approaches
    # I've tried.
    #
    # Tried:
    #
    # - Using Black as a library: adds lots of vertical and horizontal
    #   whitespace in for long argument lists etc.
    #
    # - Using libcst - would require complicated manipulation of whitespace elements
    #   to produce the PEP8 spacings around operators etc. ast_decompiler does approx
    #   PEP8 formatting by default.

    reformatted = ast_decompiler_decompile(code_ast, quote_style=quote_style).strip()

    # This has the unfortunate problem of stripping `(` and `)` for tuples, which is not what we want
    if isinstance(code_ast.body[0].value, ast.Tuple):
        reformatted = f"({reformatted})"
    return reformatted


# Similar to ast_decompiler.decompile, with our modifications
def ast_decompiler_decompile(code_ast, quote_style=QuoteStyle.SINGLE):
    decompiler = CustomDecompiler(
        indentation=0,
        line_length=1000000,
        starting_indentation=0,
        quote_style=quote_style,
    )
    return decompiler.run(code_ast)


class CustomDecompiler(ast_decompiler.decompiler.Decompiler):
    def __init__(self, indentation, line_length, starting_indentation, quote_style=QuoteStyle.SINGLE):
        super().__init__(indentation, line_length, starting_indentation)
        self.quote_style = quote_style

    def _get_quote_styles(self):
        default_quote = "'" if self.quote_style == QuoteStyle.SINGLE else '"'
        other_quote = '"' if default_quote == "'" else "'"
        return default_quote, other_quote

    def write_string(self, string_value, kind=None):
        # Copy paste from super()
        if kind is not None:
            self.write(kind)
        default_quote, other_quote = self._get_quote_styles()
        if sys.version_info >= (3, 6) and self.has_parent_of_type(ast.FormattedValue):
            delimiter = other_quote
        else:
            delimiter = default_quote
        self.write(delimiter)
        s = string_value.encode("unicode-escape").decode("ascii")
        self.write(s.replace(delimiter, "\\" + delimiter))
        self.write(delimiter)

    @contextmanager
    def f_literalise_if(self, condition):
        if condition:
            default_quote, _ = self._get_quote_styles()
            self.write("f" + default_quote)
            yield
            self.write(default_quote)
        else:
            yield


def get_indent_size(text):
    return len(text) - len(text.lstrip(" "))


# 'noqa: EXXX' markers:
# We follow the formatting in https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html
# with some tolerance when parsing
def add_noqa_markers(comment: str, new_noqa_items: List[str]):
    comment = comment.lstrip(" ").lstrip("#")

    existing_noqa_parts, main_comment = parse_noqa_from_comment(comment)
    noqa_parts = sorted(list(set(existing_noqa_parts) | set(new_noqa_items)))
    if noqa_parts:
        comment = "noqa: " + ",".join(noqa_parts) + "  " + main_comment.strip()
    else:
        comment = main_comment
    return comment.strip()


# Parsing noqa bits
noqa_start = parsy.regex(r"noqa:\s*")
noqa_item = parsy.regex("[A-Z][0-9]+")
noqa_full = noqa_start >> noqa_item.sep_by(parsy.string(","))


def parse_noqa_from_comment(comment: str):
    comment = comment.strip()

    try:
        return noqa_full.parse_partial(comment)
    except parsy.ParseError:
        return [], comment
