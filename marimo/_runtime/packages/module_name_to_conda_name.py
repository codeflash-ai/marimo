# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from marimo._runtime.packages.module_name_to_pypi_name import (
    module_name_to_pypi_name,
)

# Cache the conda mapping on first use to avoid repeated dict copying and mutation.
_CONDA_MAPPING: dict[str, str] | None = None


def module_name_to_conda_name() -> dict[str, str]:
    global _CONDA_MAPPING
    if _CONDA_MAPPING is None:
        mapping = module_name_to_pypi_name().copy()
        mapping["cv2"] = "opencv"
        mapping["ibis"] = "ibis-duckdb"
        _CONDA_MAPPING = mapping
    return _CONDA_MAPPING
