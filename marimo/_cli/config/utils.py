# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from marimo._cli.print import orange


def highlight_toml_headers(toml_string: str) -> str:
    # Use generator to avoid list allocation
    def _highlight_line(line: str) -> str:
        # Only check header format if line is non-empty and long enough
        if line and line[0] == "[" and line[-1] == "]":
            return orange(line)
        return line

    return "\n".join(
        _highlight_line(line) for line in toml_string.splitlines()
    )
