# Copyright 2025 Marimo. All rights reserved.
from __future__ import annotations

import io
import token as token_types
from dataclasses import dataclass
from tokenize import TokenError, tokenize
from typing import Callable


@dataclass
class CommentToken:
    text: str
    line: int
    col: int


class CommentPreserver:
    """Functor to preserve comments during source code transformations."""

    def __init__(self, sources: list[str]):
        self.sources = sources
        self.comments_by_source: dict[int, list[CommentToken]] = {}
        self._extract_all_comments()

    def _extract_all_comments(self) -> None:
        """Extract comments from all sources during initialization."""
        for i, source in enumerate(self.sources):
            self.comments_by_source[i] = self._extract_comments_from_source(
                source
            )

    def _extract_comments_from_source(self, source: str) -> list[CommentToken]:
        """Extract comments from a single source string."""
        if not source.strip():
            return []

        comments = []
        try:
            tokens = tokenize(io.BytesIO(source.encode("utf-8")).readline)
            for token in tokens:
                if token.type == token_types.COMMENT:
                    comments.append(
                        CommentToken(
                            text=token.string,
                            line=token.start[0],
                            col=token.start[1],
                        )
                    )
        except (TokenError, SyntaxError):
            # If tokenization fails, return empty list - no comments preserved
            pass

        return comments

    def __call__(
        self, transform_func: Callable[..., list[str]]
    ) -> Callable[..., list[str]]:
        """
        Method decorator that returns a comment-preserving version of transform_func.

        Usage: preserver(transform_func)(sources, *args, **kwargs)
        """

        def wrapper(*args: object, **kwargs: object) -> list[str]:
            # Apply the original transformation
            transformed_sources = transform_func(*args, **kwargs)

            # If sources weren't provided or transformation failed, return as-is
            if not args or not isinstance(args[0], list):
                return transformed_sources

            original_sources = args[0]

            # Merge comments back into transformed sources
            result = self._merge_comments(
                original_sources, transformed_sources
            )

            # Update our internal comment data to track only the clean transformed sources
            # This clears old comments that no longer apply
            self._update_comments_for_transformed_sources(transformed_sources)

            return result

        return wrapper

    def _merge_comments(
        self,
        original_sources: list[str],
        transformed_sources: list[str],
    ) -> list[str]:
        """Merge comments from original sources into transformed sources."""
        if len(original_sources) != len(transformed_sources):
            # If cell count changed, we can't preserve comments reliably
            return transformed_sources

        # Pre-allocate result list for better memory locality and avoid repeated resizing
        result = [None] * len(original_sources)

        # Use local variable access for speed in tight loop
        comments_by_source = self.comments_by_source
        _apply_comments_to_source = self._apply_comments_to_source

        for i in range(len(original_sources)):
            comments = comments_by_source.get(i, [])
            if not comments:
                result[i] = transformed_sources[i]
            else:
                # Apply comment preservation with variable name updates if needed
                result[i] = _apply_comments_to_source(
                    original_sources[i], transformed_sources[i], comments
                )

        return result

    def _apply_comments_to_source(
        self,
        original: str,
        transformed: str,
        comments: list[CommentToken],
    ) -> str:
        """Apply comments to a single transformed source."""
        if not comments:
            return transformed

        # Split lines once and reuse: avoid repeatedly calling .split
        original_lines = original.split("\n")
        transformed_lines = transformed.split("\n")

        # Group comments by line in a single pass with setdefault for speed
        comments_by_line: dict[int, list[CommentToken]] = {}
        for comment in comments:
            comments_by_line.setdefault(comment.line, []).append(comment)

        # Use a list mutation for efficiency, avoid copying transformed_lines unless necessary
        result_lines = transformed_lines[:]
        num_result_lines = len(result_lines)
        line_present_set = None  # Lazily populated if we encounter standalone (col==0) comments

        # Predeclare rstrip for method lookup efficiency
        rstrip = str.rstrip

        for line_num, line_comments in comments_by_line.items():
            target_line_idx = min(
                line_num - 1, num_result_lines - 1
            )  # Convert to 0-based, clamp to bounds

            if target_line_idx < 0:
                continue

            # Line comment (col == 0) takes precedence; else use the last inline comment
            line_comment = None
            inline_comment = None

            for comment in line_comments:
                if comment.col == 0:
                    line_comment = comment
                    break
                else:
                    inline_comment = comment  # Take the last inline_comment

            chosen_comment = line_comment if line_comment else inline_comment

            if chosen_comment:
                comment_text = chosen_comment.text
                col = chosen_comment.col

                if col > 0 and target_line_idx < len(original_lines):
                    # Inline comment - append to the line if not already present
                    current_line = result_lines[target_line_idx]
                    if not rstrip(current_line).endswith(rstrip(comment_text)):
                        result_lines[target_line_idx] = (
                            rstrip(current_line) + "  " + comment_text
                        )
                elif target_line_idx >= 0:
                    # Standalone comment - insert above the line if not already present
                    # Avoid O(N) .__contains__ on result_lines by using a set (only when needed)
                    if line_present_set is None:
                        line_present_set = set(result_lines)
                    if comment_text not in line_present_set:
                        result_lines.insert(target_line_idx, comment_text)
                        # Keep the set up to date
                        line_present_set.add(comment_text)
                        num_result_lines += 1  # Insert grows result_lines

        return "\n".join(result_lines)

    def _update_comments_for_transformed_sources(
        self, sources: list[str]
    ) -> None:
        """Update internal comment data to track the transformed sources."""
        self.sources = sources
        self.comments_by_source = {}
        self._extract_all_comments()
