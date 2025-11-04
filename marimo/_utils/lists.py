# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from collections.abc import Iterable
from typing import Optional, TypeVar, Union

T = TypeVar("T")


def first(iterable: Union[Iterable[T], T]) -> T:
    if isinstance(iterable, Iterable):
        return next(iter(iterable))  # type: ignore[no-any-return]
    else:
        return iterable


def as_list(value: Union[T, Optional[T], list[T]]) -> list[T]:
    # Direct identity/None check first, only list conversion on demand
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]  # type: ignore[no-any-return]
