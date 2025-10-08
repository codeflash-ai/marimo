# Copyright 2025 Marimo. All rights reserved.
import random
import string
from uuid import UUID, uuid4

from marimo._types.ids import CellId_t


class CellIdGenerator:
    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix
        self.random_seed = random.Random(42)
        self.seen_ids: set[CellId_t] = set()
        # Precompute ascii_letters as a tuple for faster .choices
        self._ascii_letters_tuple = tuple(string.ascii_letters)

    def create_cell_id(self) -> CellId_t:
        """Create a new unique cell ID.

        Returns:
            CellId_t: A new cell ID consisting of the manager's prefix followed by 4 random letters.
        """
        # For performance: localize hot attributes
        random_seed = self.random_seed
        prefix = self.prefix
        ascii_letters_tuple = self._ascii_letters_tuple
        seen_ids = self.seen_ids
        CellId_t_local = CellId_t

        attempts = 0
        while attempts < 100:
            # 4 random letters (use tuple for slightly faster access)
            _id = prefix + "".join(
                random_seed.choices(ascii_letters_tuple, k=4)
            )
            cell_id = CellId_t_local(_id)
            # Avoid repeated conversion by computing cell_id once
            if cell_id not in seen_ids:
                seen_ids.add(cell_id)
                return cell_id
            attempts += 1

        raise ValueError(
            f"Failed to create a unique cell ID after {attempts} attempts"
        )


def external_prefix() -> str:
    """Get the prefix for external cell IDs."""
    return str(uuid4())


def is_external_cell_id(cell_id: CellId_t) -> bool:
    """
    Check if cell_id is external (cloned app).

    Uses the fact that external cell IDs are UUIDs.

    >>> is_external_cell_id("c9bf9e57-1685-4c89-bafb-ff5af830be8aHbol")
    True
    >>> is_external_cell_id("Hbol")
    False
    """

    # UUIDs are 36 characters long, including hyphens
    uuid_to_test = str(cell_id)[:36]
    try:
        uuid_obj = UUID(uuid_to_test, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
