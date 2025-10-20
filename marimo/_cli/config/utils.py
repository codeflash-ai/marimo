# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from marimo._cli.print import orange


def highlight_toml_headers(toml_string: str) -> str:
    # Process lines using a generator to avoid intermediate list
    highlighted_lines: list[str] = [
        orange(line)
        if line.strip().startswith("[") and line.strip().endswith("]")
        else line
        for line in toml_string.splitlines()
    ]
    return "\n".join(highlighted_lines)
