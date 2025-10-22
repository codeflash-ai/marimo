# Copyright 2024 Marimo. All rights reserved.

import re

from markdown import Extension, Markdown, preprocessors  # type: ignore


class FlexibleIndentPreprocessor(preprocessors.Preprocessor):  # type: ignore[misc]
    """
    Preprocessor to standardize list indentation to specific levels.
    Normalizes inconsistent indentation to match the allowed levels.
    """

    # Pattern to match lines that start list items (ordered or unordered)
    # Captures: (indentation, list_marker, trailing_space, content)
    LIST_PATTERN = re.compile(r"^(\s*)([*+-]|\d+\.)(\s+)(.*)$", re.MULTILINE)
    INDENT_LEVELS = [2, 4]
    BASE_INDENT_SIZE = 4
    FOUR_SPACES = "    "

    def __init__(self, md: Markdown) -> None:
        super().__init__(md)

    def _detect_base_indent(self, lines: list[str]) -> int:
        """
        Detect the base indentation level used in the document.

        Returns 2 for 2-space indentation or 4 for 4-space indentation.
        """
        # Use local variable for better attribute access speed
        LIST_PATTERN = self.LIST_PATTERN
        FOUR_SPACES = self.FOUR_SPACES
        indents: list[int] = []
        append = indents.append  # localize for small gain in tight loop

        for line in lines:
            match = LIST_PATTERN.match(line)
            if match:
                indent_str = match.group(1)
                if indent_str:  # Skip non-indented items
                    # Avoid repeated replace by checking for tab
                    if "\t" in indent_str:
                        indent_str = indent_str.replace("\t", FOUR_SPACES)
                    indent_count = len(indent_str)
                    append(indent_count)

        if not indents:
            return self.BASE_INDENT_SIZE

        min_indent = min(indents)

        if min_indent <= 2:
            return 2
        else:
            return self.BASE_INDENT_SIZE

    def _normalize_indentation(self, indent_str: str, base_level: int) -> str:
        """
        Normalize indentation to consistent 2-space increments.

        This ensures that both 2-space and 4-space indentation patterns
        result in the same normalized output.

        Args:
            indent_str: The original indentation string
            base_level: The detected base indentation level (2 or 4)

        Returns:
            Normalized indentation string using 2-space increments
        """
        # Convert tabs to spaces (assuming 1 tab = 4 spaces)
        normalized = indent_str.replace("\t", self.FOUR_SPACES)
        indent_count = len(normalized)

        if indent_count == 0:
            return ""

        # Calculate the intended nesting level based on the base level
        nesting_level = max(1, round(indent_count / base_level))

        # Always output using 4-space increments since that is what the markdown spec requires
        return " " * (4 * nesting_level)

    def _get_list_depth(self, indent_str: str, base_level: int = 2) -> int:
        """Calculate the nesting depth of a list item."""
        normalized = indent_str.replace("\t", self.FOUR_SPACES)
        indent_count = len(normalized)

        if indent_count == 0:
            return 0

        # Calculate depth based on the base level
        return max(1, round(indent_count / base_level))

    def run(self, lines: list[str]) -> list[str]:
        """Process the lines and normalize list indentation."""
        if not lines:
            return lines

        base_level = self._detect_base_indent(lines)
        LIST_PATTERN = self.LIST_PATTERN
        normalize = self._normalize_indentation

        # Preallocate result_lines for memory efficiency where possible
        result_lines: list[str] = []
        append = result_lines.append  # Localize method for better perf

        for line in lines:
            match = LIST_PATTERN.match(line)
            if match:
                indent, marker, space, content = match.groups()
                normalized_indent = normalize(indent, base_level)
                append(f"{normalized_indent}{marker}{space}{content}")
            else:
                append(line)

        return result_lines


class FlexibleIndentExtension(Extension):  # type: ignore[misc]
    """
    Extension to provide flexible list indentation support.
    """

    def extendMarkdown(self, md: Markdown) -> None:
        """Add the preprocessor to the markdown instance."""
        # Register preprocessor to normalize indentation
        md.preprocessors.register(
            FlexibleIndentPreprocessor(md),
            "flexible_indent",
            # Run early, before breakless_lists and other list processing
            35,
        )
