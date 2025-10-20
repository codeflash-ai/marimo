# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import Optional, Union


class _HTMLBuilder:
    @staticmethod
    def div(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<div>{children_html}</div>"
        else:
            return f"<div {_join_params(params)}>{children_html}</div>"

    @staticmethod
    def img(
        *,
        src: Optional[str] = None,
        alt: Optional[str] = None,
        style: Optional[str] = None,
    ) -> str:
        params: list[tuple[str, Union[str, None]]] = []
        if src:
            params.append(("src", src))
        if alt:
            params.append(("alt", alt))
        if style:
            params.append(("style", style))

        if len(params) == 0:
            return "<img />"
        else:
            return f"<img {_join_params(params)} />"

    @staticmethod
    def video(
        *,
        src: Optional[str] = None,
        controls: bool = True,
        muted: bool = False,
        autoplay: bool = False,
        loop: bool = False,
        style: Optional[str] = None,
    ) -> str:
        params: list[tuple[str, Union[str, None]]] = []
        if src:
            params.append(("src", src))
        if controls:
            params.append(("controls", ""))
        if style:
            params.append(("style", style))
        if muted:
            params.append(("muted", ""))
        if autoplay:
            params.append(("autoplay", ""))
        if loop:
            params.append(("loop", ""))

        if len(params) == 0:
            return "<video></video>"
        else:
            return f"<video {_join_params(params)}></video>"

    @staticmethod
    def audio(
        *,
        src: Optional[str] = None,
        controls: bool = True,
    ) -> str:
        params: list[tuple[str, Union[str, None]]] = []
        if src:
            params.append(("src", src))
        if controls:
            params.append(("controls", ""))

        if len(params) == 0:
            return "<audio></audio>"
        else:
            return f"<audio {_join_params(params)}></audio>"

    @staticmethod
    def iframe(
        *,
        src: Optional[str] = None,
        srcdoc: Optional[str] = None,
        width: Optional[str] = None,
        height: Optional[str] = None,
        style: Optional[str] = None,
        onload: Optional[str] = None,
        # Opinionated defaults
        frameborder: Optional[str] = "0",
        **kwargs: str,
    ) -> str:
        # Preallocate the list of possible parameters (up to number of static + dynamic params)
        static_params_count = (
            7  # src, srcdoc, width, height, style, onload, frameborder
        )
        params_length = static_params_count + len(kwargs)
        params: list[tuple[str, Union[str, None]]] = []  # type: ignore

        append = params.append  # local var for performance

        if src is not None and src != "":
            append(("src", src))
        if srcdoc is not None and srcdoc != "":
            append(("srcdoc", srcdoc))
        if width is not None and width != "":
            append(("width", width))
        if height is not None and height != "":
            append(("height", height))
        if style is not None and style != "":
            append(("style", style))
        if onload is not None and onload != "":
            append(("onload", onload))
        if frameborder is not None and frameborder != "":
            append(("frameborder", frameborder))
        # All kwargs included, regardless of None or empty
        if kwargs:
            params.extend(kwargs.items())

        if not params:
            return "<iframe></iframe>"
        else:
            return f"<iframe {_join_params(params)}></iframe>"

    @staticmethod
    def pre(child: str, style: Optional[str] = None) -> str:
        params: list[tuple[str, Union[str, None]]] = []
        if style is not None:
            params.append(("style", style))

        if not params:
            return f"<pre>{child}</pre>"
        else:
            return f"<pre {_join_params(params)}>{child}</pre>"

    @staticmethod
    def component(
        component_name: str,
        params: list[tuple[str, Union[str, None]]],
    ) -> str:
        if len(params) == 0:
            return f"<{component_name}></{component_name}>"
        else:
            return (
                f"<{component_name} {_join_params(params)}></{component_name}>"
            )

    @staticmethod
    def figure(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<figure>{children_html}</figure>"
        else:
            return f"<figure {_join_params(params)}>{children_html}</figure>"

    @staticmethod
    def figcaption(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<figcaption>{children_html}</figcaption>"
        else:
            return f"<figcaption {_join_params(params)}>{children_html}</figcaption>"

    @staticmethod
    def h3(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<h3>{children_html}</h3>"
        else:
            return f"<h3 {_join_params(params)}>{children_html}</h3>"

    @staticmethod
    def span(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<span>{children_html}</span>"
        else:
            return f"<span {_join_params(params)}>{children_html}</span>"

    @staticmethod
    def table(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<table>{children_html}</table>"
        else:
            return f"<table {_join_params(params)}>{children_html}</table>"

    @staticmethod
    def tbody(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<tbody>{children_html}</tbody>"
        else:
            return f"<tbody {_join_params(params)}>{children_html}</tbody>"

    @staticmethod
    def tr(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<tr>{children_html}</tr>"
        else:
            return f"<tr {_join_params(params)}>{children_html}</tr>"

    @staticmethod
    def td(
        children: Union[str, list[str]], *, style: Optional[str] = None
    ) -> str:
        resolved_children = (
            [children] if isinstance(children, str) else children
        )

        params: list[tuple[str, Union[str, None]]] = []
        if style:
            params.append(("style", style))

        children_html = "".join(resolved_children)

        if len(params) == 0:
            return f"<td>{children_html}</td>"
        else:
            return f"<td {_join_params(params)}>{children_html}</td>"


def _join_params(params: list[tuple[str, Union[str, None]]]) -> str:
    # Avoid extra list construction where possible, just build fragments in a generator expression
    return " ".join(
        f"{k}='{v}'" if v is not None and v != "" else f"{k}"
        for k, v in params
        if v is not None
    )


h = _HTMLBuilder()
