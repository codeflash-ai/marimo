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
    if format_mapping is None:
        return value

    if col not in format_mapping:
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
            if isinstance(value, (int, float)):
                # Keep integers as integers for 'd' format specifier
                if isinstance(value, int) and "d" in formatter:
                    return formatter.format(value)
                # Convert to float for float formatting
                return formatter.format(float(value))
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
    # Return original row if the format mapping is None
    if format_mapping is None:
        return row
    # Produce the formatted row, avoiding function calls when not necessary
    result = {}
    for col, value in row.items():
        # Check if this column needs formatting as per mapping
        if col in format_mapping:
            formatted_value = format_value(col, value, format_mapping)
            result[col] = formatted_value
        else:
            result[col] = value
    return result


def format_column(
    col: str, values: list[JSONType], format_mapping: FormatMapping
) -> list[JSONType]:
    # Return original column if the format mapping is None
    if format_mapping is None:
        return values
    # Determine the formatter for the column once
    formatter = format_mapping.get(col, None)
    if formatter is None:
        return values
    # Only apply formatting if a formatter is present for the column
    # Avoids formatting function call overhead if not needed
    return [format_value(col, value, format_mapping) for value in values]
