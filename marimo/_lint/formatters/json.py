# Copyright 2025 Marimo. All rights reserved.
"""JSON formatter and types for lint output."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, TypedDict, Union

from marimo._lint.formatters.base import DiagnosticFormatter
from marimo._types.ids import CellId_t

if TYPE_CHECKING:
    from marimo._lint.diagnostic import Diagnostic


class DiagnosticJSON(TypedDict, total=False):
    """Typed structure for diagnostic JSON output."""

    # Required fields
    type: Literal["diagnostic"]
    message: str
    filename: str
    line: int
    column: int

    # Optional fields
    lines: list[int]
    columns: list[int]
    severity: Literal["formatting", "runtime", "breaking"]
    name: str
    code: str
    fixable: Union[bool, Literal["unsafe"]]
    fix: str
    cell_id: list[CellId_t]


class FileErrorJSON(TypedDict):
    """Typed structure for file-level errors."""

    type: Literal["error"]
    filename: str
    error: str


class SummaryJSON(TypedDict):
    """Typed structure for summary JSON output."""

    total_files: int
    files_with_issues: int
    total_issues: int
    fixed_issues: int
    errored: bool


# Union type for all issue types
IssueJSON = Union[DiagnosticJSON, FileErrorJSON]


class LintResultJSON(TypedDict):
    """Typed structure for complete lint result JSON output."""

    issues: list[IssueJSON]
    summary: SummaryJSON


class JSONFormatter(DiagnosticFormatter):
    """JSON formatter that outputs diagnostics as structured JSON."""

    def format(
        self,
        diagnostic: Diagnostic,
        filename: str,
        code_lines: list[str] | None = None,  # noqa: ARG002
    ) -> str:
        """Format the diagnostic as JSON."""
        return json.dumps(
            self.to_json_dict(diagnostic, filename), ensure_ascii=False
        )

    def to_json_dict(
        self, diagnostic: Diagnostic, filename: str
    ) -> DiagnosticJSON:
        """Convert diagnostic to typed JSON dictionary."""
        # Avoid tuple/list conversions and extra branching
        lines, columns = diagnostic.sorted_lines

        line = lines[0] if lines else 0
        column = columns[0] if columns else 0
        # Defer allocation of lists by using locals for >1 branching
        lines_out = None
        columns_out = None
        if len(lines) > 1:
            lines_out = list(lines)
        if len(columns) > 1:
            columns_out = list(columns)

        severity_value = (
            diagnostic.severity.value
            if diagnostic.severity is not None
            else None
        )

        # Use a tuple of raw fields to avoid extra dict allocation before filtering
        items = (
            ("type", "diagnostic"),
            ("message", diagnostic.message),
            ("filename", filename),
            ("line", line),
            ("column", column),
            ("lines", lines_out),
            ("columns", columns_out),
            ("severity", severity_value),
            ("name", diagnostic.name),
            ("code", diagnostic.code),
            ("fixable", diagnostic.fixable),
            ("fix", diagnostic.fix),
            ("cell_id", diagnostic.cell_id),
        )
        # Filter out None values in construction loop for lower peak memory use
        filtered = {k: v for k, v in items if v is not None}
        return DiagnosticJSON(filtered)  # type: ignore
