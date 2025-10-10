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

    # Fast path: avoid work if it's unlikely to match at all
    if not traceback.startswith("Traceback (most recent call last):\n"):
        return traceback

    # Find first two newlines and extract first two lines directly
    first_nl = traceback.find("\n")
    if first_nl == -1:
        return traceback
    second_nl = traceback.find("\n", first_nl + 1)
    if second_nl == -1:
        return traceback

    lines = [traceback[:first_nl], traceback[first_nl + 1 : second_nl]]

    if (
        len(lines) > 1
        and lines[0] == "Traceback (most recent call last):"
        and '/marimo/_runtime/executor.py", line ' in lines[1]
        and lines[1].endswith(", in execute_cell")
    ):
        rest = traceback[second_nl + 1 :]
        # Check if the first line starts with "  File "
        if rest.startswith("  File "):
            return "\n".join(lines[:1] + [rest])

        # Otherwise, find the first line that starts with "  File "
        idx = rest.find("\n  File ")
        if idx != -1:
            return "\n".join(lines[:1] + [rest[idx + 1 :]])

    return traceback


def is_code_highlighting(value: str) -> bool:
    return 'class="codehilite"' in value
