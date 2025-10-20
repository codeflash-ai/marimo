# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

import sys

from marimo._messaging.types import Stderr


def _highlight_traceback(traceback: str) -> str:
    """
    Highlight the traceback with color.
    """

    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import PythonTracebackLexer

    formatter = HtmlFormatter()

    body = highlight(traceback, PythonTracebackLexer(), formatter)
    return f'<span class="codehilite">{body}</span>'


def write_traceback(traceback: str) -> None:
    if isinstance(sys.stderr, Stderr):
        sys.stderr._write_with_mimetype(
            _highlight_traceback(_trim_traceback(traceback)),
            mimetype="application/vnd.marimo+traceback",
        )
    else:
        sys.stderr.write(traceback)


def _trim_traceback(traceback: str) -> str:
    """
    Skip first DefaultExecutor.execute_cell traceback item which all traces start with.
    """

    newline = "\n"
    first = traceback.find(newline)
    if first == -1:
        return traceback
    second = traceback.find(newline, first + 1)
    if second == -1:
        return traceback

    line0 = traceback[:first]
    line1 = traceback[first + 1 : second]
    if (
        line0 == "Traceback (most recent call last):"
        and '/marimo/_runtime/executor.py", line ' in line1
        and line1.endswith(", in execute_cell")
    ):
        i = second + 1
        while True:
            next_nl = traceback.find(newline, i)
            if next_nl == -1:
                break
            if traceback.startswith("  File ", i):
                return line0 + newline + traceback[i:]
            i = next_nl + 1

    return traceback


def is_code_highlighting(value: str) -> bool:
    return 'class="codehilite"' in value
