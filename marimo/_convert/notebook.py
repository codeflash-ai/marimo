# Copyright 2025 Marimo. All rights reserved.
from marimo._schemas.notebook import (
    NotebookCell,
    NotebookCellConfig,
    NotebookMetadata,
    NotebookV1,
)
from marimo._schemas.serialization import (
    AppInstantiation,
    CellDef,
    NotebookSerialization,
    NotebookSerializationV1,
)
from marimo._utils.code import hash_code
from marimo._version import __version__


def convert_from_ir_to_notebook_v1(
    notebook_ir: NotebookSerialization,
) -> NotebookV1:
    """Convert the notebook IR to the NotebookV1.

    Args:
        notebook_ir: The notebook IR.

    Returns:
        NotebookV1: The notebook v1.
    """
    cells: list[NotebookCell] = []
    for data in notebook_ir.cells:
        cells.append(
            NotebookCell(
                id=None,
                code=data.code,
                code_hash=hash_code(data.code) if data.code else None,
                name=data.name,
                config=NotebookCellConfig(
                    column=data.options.get("column", None),
                    disabled=data.options.get("disabled", False),
                    hide_code=data.options.get("hide_code", False),
                ),
            )
        )
    return NotebookV1(
        version="1",
        cells=cells,
        metadata=NotebookMetadata(marimo_version=__version__),
    )


def convert_from_notebook_v1_to_ir(
    notebook_v1: NotebookV1,
) -> NotebookSerialization:
    """Convert the notebook v1 to the python source code.

    Args:
        notebook_v1: The notebook v1.

    Returns:
        str: The python source code.
    """

    # Cache methods and constants for faster lookup
    get_cells = notebook_v1.get
    cells = get_cells("cells", [])

    # Pre-declare frequently reused dict key strings for potential perf benefit
    get_code = "code"
    get_name = "name"
    get_config = "config"
    get_column = "column"
    get_disabled = "disabled"
    get_hide_code = "hide_code"

    def build_cell(cell):
        config = cell.get(get_config, {})
        return CellDef(
            code=cell.get(get_code, "") or "",
            name=cell.get(get_name, "") or "",
            options={
                "column": config.get(get_column, None),
                "disabled": config.get(get_disabled, False),
                "hide_code": config.get(get_hide_code, False),
            },
        )

    cell_defs = [build_cell(cell) for cell in cells]

    return NotebookSerializationV1(
        app=AppInstantiation(options={}),
        header=None,
        version=None,
        cells=cell_defs,
        violations=[],
        valid=True,
    )
