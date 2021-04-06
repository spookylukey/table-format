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

__all__ = ['main']

from . import reformat

argument_parser = argparse.ArgumentParser(
    usage="Reads Python code from stdin and prints reformatted code to stdout"
)
argument_parser.add_argument("--align-commas", action="store_true",
                             help="Pass this to make commas aligned")
argument_parser.add_argument("--guess-indent", action="store_true",
                             help="Pass this to attempt to guess indent (from second line of text)")


def main():
    args = argument_parser.parse_args()
    sys.stdout.write(
        reformat(
            sys.stdin.read(),
            align_commas=args.align_commas,
            guess_indent=args.guess_indent,
        )
    )


if __name__ == "__main__":
    main()
