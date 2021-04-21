# -*- coding: utf-8 -*-

"""Command line interface for :mod:`table_format`.

Why does this file exist, and why not put this in ``__main__``? You might be tempted to import things from ``__main__``
later, but that will cause problems--the code will get executed twice:

- When you run ``python3 -m table_format`` python will execute``__main__.py`` as a script.
  That means there won't be any ``table_format.__main__`` in ``sys.modules``.
- When you import __main__ it will get executed again (as a module) because
  there's no ``table_format.__main__`` in ``sys.modules``.

"""
import argparse
import sys

__all__ = ["main"]

from . import reformat

argument_parser = argparse.ArgumentParser(usage="Reads Python code from stdin and prints reformatted code to stdout")
argument_parser.add_argument("--align-commas", action="store_true", help="Pass this to make commas aligned")
argument_parser.add_argument(
    "--guess-indent", action="store_true", help="Pass this to attempt to guess indent (from second line of text)"
)
argument_parser.add_argument(
    "--flake8_check", action="store_true", help="Pass this to silence the flake8 checks"
)


def main():
    args = argument_parser.parse_args()
    input_data = sys.stdin.read()
    try:
        sys.stdout.write(
            reformat(
                input_data,
                align_commas=args.align_commas,
                guess_indent=args.guess_indent,
                flake8_check=args.flake8_check,
            )
        )
    except Exception as e:
        # For the sake of tools that are piping output as replacement,
        # return what our input was:
        sys.stdout.write(input_data)
        # And then write the error to stderr and exit
        sys.stderr.write(repr(e) + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
