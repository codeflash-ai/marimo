# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

T = TypeVar("T")

sentinel = object()  # Unique sentinel object


def memoize_last_value(func: Callable[..., T]) -> Callable[..., T]:
    """
    This differs from functools.lru_cache in that is checks for
    object identity for positional arguments instead of equality
    which for functools requires the arguments to be hashable.
    """
    last_input_args: tuple[Any, ...] = ()
    last_input_kwargs: frozenset[tuple[str, Any]] = frozenset()
    last_output: T = cast(T, sentinel)

    def wrapper(*args: Any, **kwargs: Any) -> T:
        nonlocal last_input_args, last_input_kwargs, last_output

        if (
            last_output is not sentinel
            and len(args) == len(last_input_args)
            and all(
                arg is last_arg for arg, last_arg in zip(args, last_input_args)
            )
            and frozenset(kwargs.items()) == last_input_kwargs
        ):
            assert last_output is not sentinel
            return last_output

        result: T = func(*args, **kwargs)
        last_input_args = args
        last_input_kwargs = frozenset(kwargs.items())
        last_output = result

        return result

    return wrapper
