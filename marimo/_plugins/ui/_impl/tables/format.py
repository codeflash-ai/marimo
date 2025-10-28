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
    # Fast path: None mapping or column not present
    if not format_mapping or col not in format_mapping:
        return value

    formatter = format_mapping[col]

    # If the value is None and formatter is a string, don't format
    if value is None and isinstance(formatter, str):
        return value

    # Rewrite flow to avoid double-checks and costly try/except
    try:
        if isinstance(formatter, str):
            # Optimize lookup for numeric formatting
            if isinstance(value, int):
                if "d" in formatter:
                    return formatter.format(value)
                else:
                    return formatter.format(float(value))
            if isinstance(value, float):
                return formatter.format(value)
            # Avoid formatting None, already checked above
            return formatter.format(value)
        elif callable(formatter):
            return formatter(value)
    except Exception as e:
        # Only log warning if an actual error occurs, do not pre-check
        LOGGER.warning(
            f"Error formatting for value {value} in column {col}: {str(e)}"
        )
        return value

    # Fallback if formatter is neither string nor callable
    return value


def format_row(
    row: dict[str, JSONType], format_mapping: FormatMapping
) -> dict[str, JSONType]:
    # Return input row if there is no format mapping
    if not format_mapping:
        return row
    # Use dictionary comprehension for fast row formatting
    return {
        col: format_value(col, value, format_mapping)
        for col, value in row.items()
    }


def format_column(
    col: str, values: list[JSONType], format_mapping: FormatMapping
) -> list[JSONType]:
    # Return None if the format mapping is None
    if format_mapping is None:
        return values
    # Apply formatting to each value in a column list
    return [format_value(col, value, format_mapping) for value in values]
