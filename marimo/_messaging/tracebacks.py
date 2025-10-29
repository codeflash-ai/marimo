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

    first_line_end = traceback.find("\n")
    if first_line_end == -1:
        return traceback

    first_line = traceback[:first_line_end]
    if first_line != "Traceback (most recent call last):":
        return traceback

    second_line_start = first_line_end + 1
    second_line_end = traceback.find("\n", second_line_start)
    if second_line_end == -1:
        return traceback

    second_line = traceback[second_line_start:second_line_end]
    if (
        '/marimo/_runtime/executor.py", line ' not in second_line
        or not second_line.endswith(", in execute_cell")
    ):
        return traceback

    file_line_pos = traceback.find("\n  File ", second_line_end)
    if file_line_pos == -1:
        return traceback

    return "\n".join([first_line, traceback[file_line_pos + 1 :]])


def is_code_highlighting(value: str) -> bool:
    return 'class="codehilite"' in value
