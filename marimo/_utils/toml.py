# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from marimo._dependencies.dependencies import DependencyManager

if TYPE_CHECKING:
    from pathlib import Path

_toml_backend_checked = False

_tomlkit_available = None

_TOMLKitError = None

_TOMLDecodeError = None


def read_toml(file_path: Union[str, Path]) -> dict[str, Any]:
    """Read and parse a TOML file."""

    # tomllib is only available in python 3.11+
    if DependencyManager.tomlkit.has():
        import tomlkit

        with open(file_path, "rb") as file:
            # Use unwrap() to convert tomlkit types to Python built-ins
            return tomlkit.load(file).unwrap()
    else:
        import tomllib

        with open(file_path, "rb") as file:
            return tomllib.load(file)


def read_toml_string(s: str) -> dict[str, Any]:
    """Read and parse a TOML string."""

    # tomllib is only available in python 3.11+
    if DependencyManager.tomlkit.has():
        import tomlkit

        # Use unwrap() to convert tomlkit types to Python built-ins
        return tomlkit.loads(s).unwrap()
    else:
        import tomllib

        return tomllib.loads(s)


def is_toml_error(e: Exception) -> bool:
    """Check if an exception is a TOML error."""
    _detect_toml_backend()
    if _tomlkit_available:
        return isinstance(e, _TOMLKitError)
    else:
        return isinstance(e, _TOMLDecodeError)


def _detect_toml_backend():
    global \
        _toml_backend_checked, \
        _tomlkit_available, \
        _TOMLKitError, \
        _TOMLDecodeError
    if not _toml_backend_checked:
        _toml_backend_checked = True
        _tomlkit_available = DependencyManager.tomlkit.has()
        if _tomlkit_available:
            import tomlkit

            _TOMLKitError = tomlkit.exceptions.TOMLKitError
        else:
            import tomllib

            _TOMLDecodeError = tomllib.TOMLDecodeError
