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
    if format_mapping is None:
        return values
    formatter = format_mapping.get(col)
    if formatter is None:
        return values
    # Inline the main logic loop to avoid repeated dict lookups
    result: list[JSONType] = []
    append_result = result.append
    # Handle string formatter
    if isinstance(formatter, str):
        has_d = "d" in formatter
        for value in values:
            if value is None:
                append_result(value)
                continue
            # Fast path for integer with 'd' formatter
            if isinstance(value, int) and has_d:
                try:
                    append_result(formatter.format(value))
                except Exception as e:
                    LOGGER.warning(
                        f"Error formatting for value {value} in column {col}: {str(e)}"
                    )
                    append_result(value)
                continue
            # Numeric formatting
            if isinstance(value, (int, float)):
                try:
                    append_result(formatter.format(float(value)))
                except Exception as e:
                    LOGGER.warning(
                        f"Error formatting for value {value} in column {col}: {str(e)}"
                    )
                    append_result(value)
                continue
            # Generic formatting
            try:
                append_result(formatter.format(value))
            except Exception as e:
                LOGGER.warning(
                    f"Error formatting for value {value} in column {col}: {str(e)}"
                )
                append_result(value)
        return result
    # Callable formatter
    if callable(formatter):
        for value in values:
            try:
                append_result(formatter(value))
            except Exception as e:
                LOGGER.warning(
                    f"Error formatting for value {value} in column {col}: {str(e)}"
                )
                append_result(value)
        return result
    # Unrecognized formatter type, fallback to plain values
    return values
