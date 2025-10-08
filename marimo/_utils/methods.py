# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

import inspect
import types
from typing import Any


def is_callable_method(obj: Any, attr: str) -> bool:
    # Avoid double attribute lookup by using getattr with default
    method = getattr(obj, attr, None)
    if method is None:
        return False
    if inspect.isclass(obj) and not isinstance(method, types.MethodType):
        return False
    return callable(method)
