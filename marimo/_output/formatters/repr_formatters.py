# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import Any, Callable, Optional, cast

from marimo._messaging.mimetypes import KnownMimeType
from marimo._output.formatters.iframe import maybe_wrap_in_iframe
from marimo._output.md import md
from marimo._plugins.core.media import io_to_data_url
from marimo._utils.methods import is_callable_method

MEDIA_MIME_PREFIXES = (
    "image/",
    "audio/",
    "video/",
    "application/pdf",
)


def maybe_get_repr_formatter(
    obj: Any,
) -> Optional[Callable[[Any], tuple[KnownMimeType, str]]]:
    """
    Get a formatter that uses the object's _repr_ methods.
    """
    md_mime_types: list[KnownMimeType] = [
        "text/markdown",
        "text/latex",
    ]

    # Check for the misc _repr_ methods
    # Order dictates preference
    reprs: list[tuple[str, KnownMimeType]] = [
        ("_repr_html_", "text/html"),  # text/html is preferred first
        ("_repr_mimebundle_", "application/vnd.marimo+mimebundle"),
        ("_repr_svg_", "image/svg+xml"),
        ("_repr_json_", "application/json"),
        ("_repr_png_", "image/png"),
        ("_repr_jpeg_", "image/jpeg"),
        ("_repr_markdown_", "text/markdown"),
        ("_repr_latex_", "text/latex"),
        ("_repr_text_", "text/plain"),  # last
    ]

    # Optimized HOTSPOT: break as soon as a callable method is found
    has_possible_repr = next(
        (True for attr, _ in reprs if is_callable_method(obj, attr)), False
    )
    if has_possible_repr:
        # Pre-import md function for use in closure scope and avoid inside loop import
        md_func = md

        def f_repr(obj: Any) -> tuple[KnownMimeType, str]:
            # Avoid repeated imports in tight loop scope
            for attr, mime_type in reprs:
                # Pull method object directly to avoid repeated lookups/calling is_callable_method twice
                method = getattr(obj, attr, None)
                if method is None or not callable(method):
                    continue
                if attr == "_repr_mimebundle_":
                    try:
                        contents = method(include=[], exclude=[])
                    except TypeError:
                        contents = method()

                    if isinstance(contents, tuple) and len(contents) == 2:
                        contents, _metadata = cast(
                            tuple[dict[str, Any], dict[str, Any]], contents
                        )

                    if isinstance(contents, dict):
                        # items needs to be listed for mutating while iterating
                        for mime_key, data in list(contents.items()):
                            if mime_key.startswith(
                                MEDIA_MIME_PREFIXES
                            ) and isinstance(data, bytes):
                                data_url = io_to_data_url(data, mime_key)
                                if data_url:
                                    contents[mime_key] = data_url

                    if (
                        isinstance(contents, dict)
                        and "text/plain" in contents
                        and len(contents) > 1
                    ):
                        contents.pop("text/plain")
                    # Only convert markdown/latex to html if text/html not present
                    for md_mime_type in md_mime_types:
                        if (
                            "text/html" not in contents
                            and md_mime_type in contents
                        ):
                            contents["text/html"] = md_func(
                                str(contents[md_mime_type])
                            ).text
                else:
                    contents = method()

                if contents is None:
                    continue

                if isinstance(contents, bytes):
                    data_url = io_to_data_url(
                        contents, fallback_mime_type=mime_type
                    )
                    return (mime_type, data_url or "")
                if mime_type in md_mime_types:
                    return ("text/html", md_func(contents or "").text)
                if mime_type == "text/html":
                    contents = maybe_wrap_in_iframe(contents)
                return (mime_type, contents)

            return ("text/html", "")

        return f_repr

    return None
