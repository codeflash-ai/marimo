# Copyright 2025 Marimo. All rights reserved.
import os

_env_get = os.environ.get


# Could be replaced with `find_uv_bin` from uv Python package in the future
def find_uv_bin() -> str:
    return _env_get("UV", "uv")
