# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import Any, TypeVar, cast

from marimo._config.config import MarimoConfig, PartialMarimoConfig
from marimo._config.utils import deep_copy

SECRET_PLACEHOLDER = "********"

# TODO: mypy doesn't like using @overload here


def mask_secrets_partial(config: PartialMarimoConfig) -> PartialMarimoConfig:
    return cast(PartialMarimoConfig, mask_secrets(cast(MarimoConfig, config)))


def mask_secrets(config: MarimoConfig) -> MarimoConfig:
    def deep_remove_from_path(path: list[str], obj: dict[str, Any]) -> None:
        """Mutate obj in-place to mask secrets at the specified path."""
        idx = 0
        length = len(path)
        cur_obj = obj
        while idx < length:
            key = path[idx]
            if key == "*":
                # Instead of recursion, we process all values one by one here to reduce Python stack overhead.
                next_path = path[idx + 1 :]
                if not next_path:
                    return
                for v in cur_obj.values():
                    if isinstance(v, dict):
                        # inline loop for next level to avoid extra per-call function setup
                        nxt_obj = v
                        nxt_idx = 0
                        nxt_length = len(next_path)
                        while nxt_idx < nxt_length:
                            nxt_key = next_path[nxt_idx]
                            if nxt_key == "*":
                                nn_path = next_path[nxt_idx + 1 :]
                                if not nn_path:
                                    break
                                for nv in nxt_obj.values():
                                    if isinstance(nv, dict):
                                        deep_remove_from_path(nn_path, nv)
                                    elif isinstance(nv, list) and nn_path:
                                        for nitem in nv:
                                            if isinstance(nitem, dict):
                                                deep_remove_from_path(
                                                    nn_path, nitem
                                                )
                                break
                            if nxt_key not in nxt_obj:
                                break
                            if nxt_idx == nxt_length - 1:
                                if isinstance(nxt_obj[nxt_key], list):
                                    nxt_obj[nxt_key] = []
                                elif nxt_obj[nxt_key]:
                                    nxt_obj[nxt_key] = SECRET_PLACEHOLDER
                                break
                            nxt_obj = nxt_obj[nxt_key]
                            nxt_idx += 1
                    elif isinstance(v, list) and idx + 1 < length:
                        # Only first layer recursion for lists
                        for item in v:
                            if isinstance(item, dict):
                                deep_remove_from_path(path[idx + 1 :], item)
                return
            if key not in cur_obj:
                return
            if idx == length - 1:
                if isinstance(cur_obj[key], list):
                    cur_obj[key] = []
                elif cur_obj[key]:
                    cur_obj[key] = SECRET_PLACEHOLDER
                return
            cur_obj = cur_obj[key]
            idx += 1

    secrets = (
        ("ai", "*", "api_key"),
        ("ai", "bedrock", "aws_access_key_id"),
        ("ai", "bedrock", "aws_secret_access_key"),
        ("runtime", "dotenv"),
    )

    new_config = deep_copy(config)
    config_dict = cast(dict[str, Any], new_config)

    for secret in secrets:
        deep_remove_from_path(list(secret), config_dict)

    return new_config  # type: ignore


T = TypeVar("T")


def remove_secret_placeholders(config: T) -> T:
    def deep_remove(obj: Any) -> Any:
        if isinstance(obj, dict):
            # Filter all keys with value SECRET_PLACEHOLDER
            return {
                k: deep_remove(v)
                for k, v in obj.items()
                if v != SECRET_PLACEHOLDER
            }  # type: ignore
        if isinstance(obj, list):
            return [deep_remove(v) for v in obj]  # type: ignore
        if obj == SECRET_PLACEHOLDER:
            return None
        return obj

    return deep_remove(deep_copy(config))  # type: ignore
