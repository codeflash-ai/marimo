# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import Callable, Union

from marimo import _loggers
from marimo._plugins.core.web_component import JSONType

LOGGER = _loggers.marimo_logger()

FormatMapping = dict[str, Union[str, Callable[..., JSONType]]]


def format_value(
    col: str, value: JSONType, format_mapping: FormatMapping
) -> JSONType:
    if not format_mapping or col not in format_mapping:
        return value

    formatter = format_mapping[col]

    # If the value is None, we don't want to format it
    # with strings for formatting, but we do want to
    # format it with callables.
    if value is None and isinstance(formatter, str):
        return value

    try:
        if isinstance(formatter, str):
            # Handle numeric formatting specially to preserve signs and separators
            if isinstance(value, int):
                # Keep integers as integers for 'd' format specifier
                if "d" in formatter:
                    return formatter.format(value)
                # Convert to float for float formatting (avoids another isinstance check)
                return formatter.format(float(value))
            elif isinstance(value, float):
                return formatter.format(value)
            return formatter.format(value)
        if callable(formatter):
            return formatter(value)
    except Exception as e:
        LOGGER.warning(
            f"Error formatting for value {value} in column {col}: {str(e)}"
        )
        return value

    return value


def format_row(
    row: dict[str, JSONType], format_mapping: FormatMapping
) -> dict[str, JSONType]:
    # Return None if the format mapping is None
    if format_mapping is None:
        return row
    # Apply formatting to each value in a row dictionary
    return {
        col: format_value(col, value, format_mapping)
        for col, value in row.items()
    }


def format_column(
    col: str, values: list[JSONType], format_mapping: FormatMapping
) -> list[JSONType]:
    # Return early if the format mapping is None
    if not format_mapping:
        return values
    # Use list comprehension for speed, referring directly to local function and objects
    return [format_value(col, value, format_mapping) for value in values]
