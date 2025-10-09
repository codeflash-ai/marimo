# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from marimo._runtime.requests import SerializedCLIArgs

if TYPE_CHECKING:
    from collections.abc import Iterable


def parse_args(
    args: Iterable[str],
) -> SerializedCLIArgs:
    """
    Parse command line arguments into a dictionary.

    This does not support lists as values.
    """
    args_dict: SerializedCLIArgs = {}

    # Combine any arguments that are split by spaces
    new_args: list[str] = []
    append = new_args.append  # Local variable for faster access
    iter_args = iter(args)
    for arg in iter_args:
        if arg.startswith(("-", "--")):
            append(arg)
        elif new_args:
            # This can only ever be entered if new_args is nonempty
            # Use string concatenation directly instead of f-string (faster for single value)
            new_args[-1] += " " + arg

    # Local vars for faster lookup
    lstrip = str.lstrip
    split = str.split
    float_ = float
    int_ = int

    # Strings for comparison, reused to avoid recreating
    true_strs = {"True", "true"}
    false_strs = {"False", "false"}

    for arg in new_args:
        if arg.startswith(("-", "--")):
            arg = lstrip(arg, "-")
            key: str
            value: Any

            # Split only once (most common case fast-path)
            if "=" in arg:
                key, value = split(arg, "=", 1)
            elif " " in arg:
                key, value = split(arg, " ", 1)
                key = key.strip()
                value = value.strip()
            else:
                key = arg
                value = ""

            # Fast path: check for digit value first (int)
            if value and (value[0] == "-" or value[0].isdigit()):
                # Only int if possible, else float, else leave as str
                try:
                    value = int_(value)
                except ValueError:
                    try:
                        value = float_(value)
                    except ValueError:
                        pass
            else:
                # Try float only if value starts with digit (avoid float exception for words)
                try:
                    value = float_(value)
                except ValueError:
                    pass

            # Try boolean conversion
            # Faster set membership testing
            if value in true_strs:
                value = True
            elif value in false_strs:
                value = False

            # Create a list for duplicate arguments
            current = args_dict.get(key)
            if current is not None:
                if isinstance(current, list):
                    current.append(value)
                else:
                    args_dict[key] = [current, value]
            else:
                args_dict[key] = value

    return args_dict


def args_from_argv() -> SerializedCLIArgs:
    return parse_args(sys.argv[1:])
