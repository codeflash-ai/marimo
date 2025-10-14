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
    # Optimization: avoid creating intermediate sets by using views directly
    # union of keys in both dicts, but with less overhead than set union
    seen = set()
    result: dict[Any, Any] = {}
    for key in original:
        result[key] = _merge_key(original, update, key)
        seen.add(key)
    for key in update:
        if key not in seen:
            result[key] = _merge_key(original, update, key)
    return result
