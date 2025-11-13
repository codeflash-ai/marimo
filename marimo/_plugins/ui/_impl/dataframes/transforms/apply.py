# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import Any, Generic, TypeVar

from narwhals.dependencies import is_narwhals_dataframe

from marimo._dependencies.dependencies import DependencyManager
from marimo._plugins.ui._impl.dataframes.transforms.handlers import (
    IbisTransformHandler,
    PandasTransformHandler,
    PolarsTransformHandler,
)
from marimo._plugins.ui._impl.dataframes.transforms.types import (
    Transform,
    Transformations,
    TransformHandler,
    TransformType,
)
from marimo._utils.assert_never import assert_never

_transform_type_to_handler_method = {
    TransformType.COLUMN_CONVERSION: "handle_column_conversion",
    TransformType.RENAME_COLUMN: "handle_rename_column",
    TransformType.SORT_COLUMN: "handle_sort_column",
    TransformType.FILTER_ROWS: "handle_filter_rows",
    TransformType.GROUP_BY: "handle_group_by",
    TransformType.AGGREGATE: "handle_aggregate",
    TransformType.SELECT_COLUMNS: "handle_select_columns",
    TransformType.SHUFFLE_ROWS: "handle_shuffle_rows",
    TransformType.SAMPLE_ROWS: "handle_sample_rows",
    TransformType.EXPLODE_COLUMNS: "handle_explode_columns",
    TransformType.EXPAND_DICT: "handle_expand_dict",
    TransformType.UNIQUE: "handle_unique",
}

T = TypeVar("T")


def _handle(df: T, handler: TransformHandler[T], transform: Transform) -> T:
    method_name = _transform_type_to_handler_method.get(transform.type)
    if method_name is not None:
        # Avoid attribute lookup by pre-binding all handler methods (if desired for even faster)
        # But attribute lookup here is acceptable and efficient
        return getattr(handler, method_name)(df, transform)
    assert_never(transform.type)


def _apply_transforms(
    df: T, handler: TransformHandler[T], transforms: Transformations
) -> T:
    transforms_list = transforms.transforms
    if not transforms_list:
        return df
    for transform in transforms_list:
        df = _handle(df, handler, transform)
    return df


def get_handler_for_dataframe(
    df: Any,
) -> TransformHandler[Any]:
    """
    Gets the handler for the given dataframe.

    raises ValueError if the dataframe type is not supported.
    """
    if DependencyManager.pandas.imported():
        import pandas as pd

        if isinstance(df, pd.DataFrame):
            return PandasTransformHandler()
    if DependencyManager.polars.imported():
        import polars as pl

        if isinstance(df, pl.DataFrame):
            return PolarsTransformHandler()

    if DependencyManager.ibis.imported():
        import ibis  # type: ignore

        if isinstance(df, ibis.Table):
            return IbisTransformHandler()

    if DependencyManager.narwhals.imported():
        if is_narwhals_dataframe(df):
            return get_handler_for_dataframe(df.to_native())

    raise ValueError(
        "Unsupported dataframe type. Must be Pandas or Polars."
        f" Got: {type(df)}"
    )


class TransformsContainer(Generic[T]):
    """
    Keeps internal state of the last transformation applied to the dataframe.
    So that we can incrementally apply transformations.
    """

    def __init__(self, df: T, handler: TransformHandler[T]) -> None:
        self._original_df = df
        # The dataframe for the given transform.
        self._snapshot_df = df
        self._handler = handler
        self._transforms: list[Transform] = []

    def apply(self, transform: Transformations) -> T:
        """
        Applies the given transformations to the dataframe.
        """
        # If the new transformations are a superset of the existing ones,
        # then we can just apply the new ones to the snapshot dataframe.
        if self._is_superset(transform):
            transforms_to_apply = self._get_next_transformations(transform)
            self._snapshot_df = _apply_transforms(
                self._snapshot_df, self._handler, transforms_to_apply
            )
            self._transforms = transform.transforms
            return self._snapshot_df

        # If the new transformations are not a superset of the existing ones,
        # then we need to start from the original dataframe.
        else:
            self._snapshot_df = _apply_transforms(
                self._original_df, self._handler, transform
            )
            self._transforms = transform.transforms
            return self._snapshot_df

    def _is_superset(self, transforms: Transformations) -> bool:
        """
        Checks if the new transformations are a superset of the existing ones.
        """
        if not self._transforms:
            return False

        # If the new transformations are smaller than the existing ones,
        # then it's not a superset.
        if len(self._transforms) > len(transforms.transforms):
            return False

        for i, transform in enumerate(self._transforms):
            if transform != transforms.transforms[i]:
                return False

        return True

    def _get_next_transformations(
        self, transforms: Transformations
    ) -> Transformations:
        """
        Gets the next transformations to apply.
        """
        if self._is_superset(transforms):
            return Transformations(
                transforms.transforms[len(self._transforms) :]
            )
        else:
            return transforms
