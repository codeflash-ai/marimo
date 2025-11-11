# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import Any


def _merge_key(
    original: dict[Any, Any], update: dict[Any, Any], key: str
) -> Any:
    # Precondition: key is in at least one of original and update
    if key not in update:
        # keep keys in original if they aren't in the update
        return original[key]
    elif key not in original:
        # new keys in update get added to original
        return update[key]
    elif isinstance(original[key], dict) and isinstance(update[key], dict):
        # both dicts, so recurse
        return deep_merge(original[key], update[key])
    else:
        # key is present in both original and update, but values are not
        # both dicts; just take the update value.
        return update[key]


def deep_merge(
    original: dict[Any, Any], update: dict[Any, Any]
) -> dict[Any, Any]:
    """Deep merge of two dicts."""
    # Avoid creating intermediate sets, iterate using keys directly for performance
    keys = original.keys()
    update_keys = update.keys()
    # Using a set() only if necessary (in case of overlap)
    if len(original) >= len(update):
        result = {key: _merge_key(original, update, key) for key in keys}
        for key in update_keys:
            if key not in original:
                result[key] = update[key]
        return result
    else:
        result = {
            key: _merge_key(original, update, key) for key in update_keys
        }
        for key in keys:
            if key not in update:
                result[key] = original[key]
        return result
