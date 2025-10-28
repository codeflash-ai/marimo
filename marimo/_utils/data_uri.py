# Copyright 2025 Marimo. All rights reserved.
from __future__ import annotations

import base64


def build_data_url(mimetype: str, data: bytes) -> str:
    assert mimetype is not None
    # `data` must be base64 encoded
    str_repr = data.decode("utf-8").replace("\n", "")
    return f"data:{mimetype};base64,{str_repr}"


# Format: data:mime_type;base64,data
def from_data_uri(data: str) -> tuple[str, bytes]:
    assert isinstance(data, str)
    assert data.startswith("data:")

    # Split on the first comma only to separate metadata from payload
    comma_idx = data.find(",")
    if comma_idx == -1:
        raise ValueError("Invalid data URI format: missing comma separator")
    meta, payload = data[:comma_idx], data[comma_idx + 1 :]

    # Efficient extraction of mime_type without additional intermediate objects
    semi_idx = meta.find(";")
    if semi_idx == -1:
        # No ";base64" - mime type extends to end
        mime_type = meta[5:]
    else:
        mime_type = meta[5:semi_idx]

    return mime_type, base64.b64decode(payload)
