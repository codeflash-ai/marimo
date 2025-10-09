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
    # Avoid constructing unnecessary set objects twice
    keys = original.keys()
    update_keys = update.keys()
    out = {}
    for key in keys:
        out[key] = _merge_key(original, update, key)
    for key in update_keys:
        if key not in original:
            out[key] = _merge_key(original, update, key)
    return out
