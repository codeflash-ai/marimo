# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

import base64
import io
from typing import Any, Union

from marimo._plugins.core.media import is_data_empty
from marimo._runtime.virtual_file import (
    EMPTY_VIRTUAL_FILE,
    VirtualFile,
    VirtualFileLifecycleItem,
)


def pdf(data: bytes) -> VirtualFile:
    """Create a virtual file from a PDF.

    Args:
        data: PDF data in bytes

    Returns:
        A `VirtualFile` object.
    """
    item = VirtualFileLifecycleItem(ext="pdf", buffer=data)
    item.add_to_cell_lifecycle_registry()
    return item.virtual_file


def image(data: bytes, ext: str = "png") -> VirtualFile:
    """Create a virtual file from an image.

    Args:
        data (bytes): Image data in bytes
        ext (str): File extension

    Returns:
        A `VirtualFile` object.
    """
    item = VirtualFileLifecycleItem(ext=ext, buffer=data)
    item.add_to_cell_lifecycle_registry()
    return item.virtual_file


def audio(data: bytes, ext: str = "wav") -> VirtualFile:
    """Create a virtual file from audio.

    Args:
        data (bytes): Audio data in bytes
        ext (str): File extension

    Returns:
        A `VirtualFile` object.
    """
    item = VirtualFileLifecycleItem(ext=ext, buffer=data)
    item.add_to_cell_lifecycle_registry()
    return item.virtual_file


def csv(data: Union[str, bytes, io.BytesIO]) -> VirtualFile:
    """Create a virtual file for CSV data.

    Args:
        data: CSV data in bytes, or string representing a data URL, external URL
            or a Pandas DataFrame

    Returns:
        A `VirtualFile` object.
    """
    return any_data(data, ext="csv")  # type: ignore


def arrow(data: bytes) -> VirtualFile:
    """Create a virtual file for Arrow data.

    Args:
        data: Arrow data in bytes

    Returns:
        A `VirtualFile` object.
    """
    return any_data(data, ext="arrow")  # type: ignore


def parquet(data: bytes) -> VirtualFile:
    """Create a virtual file for Parquet data.

    Args:
        data: Parquet data in bytes

    Returns:
        A `VirtualFile` object.
    """
    return any_data(data, ext="parquet")  # type: ignore


def json(data: Union[str, bytes, io.BytesIO]) -> VirtualFile:
    """Create a virtual file for JSON data.

    Args:
        data: JSON data in bytes, or string representing a data URL, external URL
            or a Pandas DataFrame

    Returns:
        A `VirtualFile` object.
    """
    return any_data(data, ext="json")  # type: ignore


def js(data: str) -> VirtualFile:
    """Create a virtual file for JavaScript data.

    Args:
        data: JavaScript data as a string

    Returns:
        A `VirtualFile` object.
    """
    return any_data(data, ext="js")


def html(data: str) -> VirtualFile:
    """Create a virtual file for HTML data.

    Args:
        data: HTML data as a string

    Returns:
        A `VirtualFile` object.
    """
    return any_data(data, ext="html")


def any_data(data: Union[str, bytes, io.BytesIO], ext: str) -> VirtualFile:
    """Create a virtual file from any data.

    It can be a string, bytes, or a file-like object.
    For external URLs, these are passed through as-is.

    Args:
        data: Data in bytes, or string representing a data URL or external URL
        ext: File extension

    Returns:
        A `VirtualFile` object.
    """
    if data is None:
        return EMPTY_VIRTUAL_FILE

    if is_data_empty(data):
        return EMPTY_VIRTUAL_FILE

    # Base64 encoded data
    if isinstance(data, str) and data.startswith("data:"):
        base64str = data.split(",")[1]
        buffer = base64.b64decode(base64str)
        item = VirtualFileLifecycleItem(ext=ext, buffer=buffer)
        item.add_to_cell_lifecycle_registry()
        return item.virtual_file

    # URL
    if isinstance(data, str) and data.startswith("http"):
        return VirtualFile.from_external_url(data)

    # Bytes
    if isinstance(data, bytes):
        item = VirtualFileLifecycleItem(ext=ext, buffer=data)
        item.add_to_cell_lifecycle_registry()
        return item.virtual_file

    # String
    if isinstance(data, str):
        item = VirtualFileLifecycleItem(ext=ext, buffer=data.encode("utf-8"))
        item.add_to_cell_lifecycle_registry()
        return item.virtual_file

    # BytesIO
    if isinstance(data, io.BytesIO):
        # clone before reading, so we don't consume the stream
        buffer = io.BytesIO(data.getvalue()).read()
        item = VirtualFileLifecycleItem(ext=ext, buffer=buffer)
        item.add_to_cell_lifecycle_registry()
        return item.virtual_file

    raise ValueError(f"Unsupported data type: {type(data)}")


def sanitize_json_bigint(
    data: Union[str, dict[str, Any], list[dict[str, Any]]],
) -> str:
    """Sanitize JSON bigint to a string.

    This is necessary because the frontend will round ints larger than
    Number.MAX_SAFE_INTEGER to Number.MAX_SAFE_INTEGER.
    """
    from json import dumps, loads

    # JavaScript's safe integer limits
    MAX_SAFE_INTEGER = 9007199254740991
    MIN_SAFE_INTEGER = -9007199254740991

    # Performance optimizations:
    # - Replace inner function lookups with local variables for functions and constants.
    # - Use direct type comparisons ("type(obj) is int") for faster isinstance checks for int.
    # - Avoid unnecessary dict, list construction by pre-allocating when possible.

    def convert_key(key: Any) -> Any:
        # Keys must be str, int, float, bool, or None
        # Using type() for str/int/float/bool for faster single-checks
        if key is None:
            return key
        kt = type(key)
        if kt is str or kt is int or kt is float or kt is bool:
            return key
        return str(key)

    # To speed up recursion and minimize function call overhead, assign frequently used
    # constants and functions to local variables before the recursion starts.
    _MAX_SAFE = MAX_SAFE_INTEGER
    _MIN_SAFE = MIN_SAFE_INTEGER
    _convert_key = convert_key
    _str = str
    _type = type

    def convert_bigint(obj: Any) -> Any:
        ot = _type(obj)
        if ot is dict:
            # Pre-size for performance, avoid generator overhead
            result = {}
            items = obj.items()
            # Use direct for-loop instead of dict comprehension for less overhead on large dicts
            for k, v in items:
                result[_convert_key(k)] = convert_bigint(v)
            return result
        elif ot is list:
            # Pre-size for list allocation
            return [convert_bigint(item) for item in obj]
        elif ot is int:
            if obj > _MAX_SAFE or obj < _MIN_SAFE:
                return _str(obj)
            else:
                return obj
        else:
            return obj

    if isinstance(data, str):
        as_json = loads(data)
    else:
        as_json = data

    # Directly dump using optimized structure
    return dumps(
        convert_bigint(as_json),
        indent=None,
        separators=(",", ":"),
        default=str,
    )
