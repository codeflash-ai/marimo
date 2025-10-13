# Copyright 2025 Marimo. All rights reserved.

from __future__ import annotations

import re


def compile_regex(query: str) -> tuple[re.Pattern[str] | None, bool]:
    """
    Returns compiled regex pattern and whether the query is a valid regex.
    """
    cache = getattr(compile_regex, "_cache", None)
    if cache is None:
        cache = {}
        compile_regex._cache = cache

    key = (query, re.IGNORECASE)
    if key in cache:
        return cache[key]

    try:
        result = re.compile(query, re.IGNORECASE), True
        cache[key] = result
        return result
    except re.error:
        result = None, False
        cache[key] = result
        return result


def is_fuzzy_match(
    query: str,
    name: str,
    compiled_pattern: re.Pattern[str] | None,
    is_regex: bool,
) -> bool:
    """
    Fuzzy match using pre-compiled regex. If is not regex, fallback to substring match.

    Args:
        query: The query to match.
        name: The name to match against.
        compiled_pattern: Pre-compiled regex pattern (None if not regex).
        is_regex: Whether the query is a valid regex.
    """
    if is_regex and compiled_pattern:
        return bool(compiled_pattern.search(name))
    else:
        return query.lower() in name.lower()
