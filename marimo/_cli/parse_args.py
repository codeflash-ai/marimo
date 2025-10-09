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
    append_new_arg = new_args.append
    for arg in args:
        if arg.startswith(("-", "--")):
            append_new_arg(arg)
        elif new_args:
            new_args[-1] += f" {arg}"

    # Precompute bool values for faster matching
    bool_true = {"True", "true"}
    bool_false = {"False", "false"}

    for arg in new_args:
        if arg.startswith(("-", "--")):
            # Strip leading dashes
            arg = arg.lstrip("-")
            key: str
            value: Any

            eq_idx = arg.find("=")
            if eq_idx != -1:
                key, value = arg[:eq_idx], arg[eq_idx + 1 :]
            else:
                sp_idx = arg.find(" ")
                if sp_idx != -1:
                    key, value = arg[:sp_idx], arg[sp_idx + 1 :]
                    key = key.strip()
                    value = value.strip()
                else:
                    key = arg
                    value = ""

            # Try numeric conversion
            if value and (
                value[0].isdigit()
                or (value[0] == "-" and len(value) > 1 and value[1].isdigit())
            ):
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass

            # Try boolean conversion
            elif value in bool_true:
                value = True
            elif value in bool_false:
                value = False

            # Create a list for duplicate arguments
            if key in args_dict:
                current = args_dict[key]
                if isinstance(current, list):
                    current.append(value)
                else:
                    args_dict[key] = [current, value]
            else:
                args_dict[key] = value

    return args_dict


def args_from_argv() -> SerializedCLIArgs:
    return parse_args(sys.argv[1:])
