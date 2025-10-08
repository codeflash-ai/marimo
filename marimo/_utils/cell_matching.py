# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from marimo._types.ids import CellId_t

if TYPE_CHECKING:
    from collections.abc import Sequence


def similarity_score(s1: str, s2: str) -> float:
    """Fast similarity score based on common prefix and suffix.
    Returns lower score for more similar strings."""
    # Find common prefix length
    prefix_len = 0
    min_len = min(len(s1), len(s2))
    while prefix_len < min_len and s1[prefix_len] == s2[prefix_len]:
        prefix_len += 1

    # Find common suffix length if strings differ in middle
    if prefix_len < min_len:
        s1_len = len(s1)
        s2_len = len(s2)
        suffix_len = 0
        # Only go up to the point where prefix and suffix don't overlap
        while (
            suffix_len < min_len - prefix_len
            and s1[s1_len - 1 - suffix_len] == s2[s2_len - 1 - suffix_len]
        ):
            suffix_len += 1
    else:
        suffix_len = 0

    # Return inverse similarity - shorter common affix means higher score
    return len(s1) + len(s2) - 2.0 * (prefix_len + suffix_len)


def group_lookup(
    ids: Sequence[CellId_t], codes: Sequence[str]
) -> dict[str, list[tuple[int, CellId_t]]]:
    lookup: dict[str, list[tuple[int, CellId_t]]] = {}
    for idx, (cell_id, code) in enumerate(zip(ids, codes)):
        if code in lookup:
            lookup[code].append((idx, cell_id))
        else:
            lookup[code] = [(idx, cell_id)]
    return lookup


def extract_order(
    codes: list[str], lookup: dict[str, list[tuple[int, CellId_t]]]
) -> list[list[int]]:
    offset = 0
    order: list[list[int]] = [None] * len(codes)
    for i, code in enumerate(codes):
        dupes = len(lookup[code])
        indices = list(range(offset, offset + dupes))
        order[i] = indices
        offset += dupes
    return order


def get_unique(
    codes: Sequence[str], available: dict[str, list[tuple[int, CellId_t]]]
) -> list[str]:
    # Order matters, required opposed to using set()
    # Optimization: collect available keys set once
    available_keys = set(available.keys())
    seen = set()
    unique_codes = []
    for code in codes:
        if code not in seen and code in available_keys:
            seen.add(code)
            unique_codes.append(code)
    return unique_codes


def pop_local(available: list[tuple[int, CellId_t]], idx: int) -> CellId_t:
    """Find and pop the index that is closest to idx"""
    # NB. by min implementation a preference is given to the lower index when equidistant
    min_dist = float("inf")
    best_idx = 0
    for i, (avail_idx, _) in enumerate(available):
        dist = abs(avail_idx - idx)
        if dist < min_dist:
            min_dist = dist
            best_idx = i
    return available.pop(best_idx)[1]


def _hungarian_algorithm(scores: list[list[float]]) -> list[int]:
    """Implements the Hungarian algorithm to find the best matching.

    In general this class of problem is known as the assignment problem and is
    pretty well studied. This is a textbook implementation to avoid additional
    dependencies. Links:
    - https://en.wikipedia.org/wiki/Hungarian_algorithm
    """
    n = len(scores)
    # Defensive: use memoryview/list copy if row elements are not copy-heavy
    score_matrix = [row.copy() for row in scores]

    # Step 1: Subtract row minima
    for i in range(n):
        min_value = min(score_matrix[i])
        if min_value != 0.0:  # Skip redundant subtracts
            row = score_matrix[i]
            for j in range(n):
                row[j] -= min_value

    # Step 2: Subtract column minima
    for j in range(n):
        col = [score_matrix[i][j] for i in range(n)]
        min_value = min(col)
        if min_value != 0.0:
            for i in range(n):
                score_matrix[i][j] -= min_value

    # Step 3: Find initial assignment
    row_assignment = [-1] * n
    col_assignment = [-1] * n

    for i in range(n):
        row = score_matrix[i]
        for j in range(n):
            if (
                row[j] == 0
                and row_assignment[i] == -1
                and col_assignment[j] == -1
            ):
                row_assignment[i] = j
                col_assignment[j] = i

    # Step 4: Improve assignment iteratively
    while True:
        assigned_count = sum(1 for x in row_assignment if x != -1)
        if assigned_count == n:
            break

        # Find minimum uncovered value
        min_uncovered = float("inf")
        row_unassigned = [i for i, v in enumerate(row_assignment) if v == -1]
        col_unassigned = [j for j, v in enumerate(col_assignment) if v == -1]
        for i in row_unassigned:
            row = score_matrix[i]
            for j in col_unassigned:
                v = row[j]
                if v < min_uncovered:
                    min_uncovered = v

        if min_uncovered == float("inf"):
            break

        # Update matrix
        # Precompute masks for faster loop
        assigned_rows = set(i for i, k in enumerate(row_assignment) if k != -1)
        assigned_cols = set(j for j, k in enumerate(col_assignment) if k != -1)
        for i in range(n):
            for j in range(n):
                if i not in assigned_rows and j not in assigned_cols:
                    score_matrix[i][j] -= min_uncovered
                elif i in assigned_rows and j in assigned_cols:
                    score_matrix[i][j] += min_uncovered

        # Try to find new assignments
        for i in row_unassigned:
            for j in col_unassigned:
                if score_matrix[i][j] == 0 and col_assignment[j] == -1:
                    row_assignment[i] = j
                    col_assignment[j] = i
                    break

    # Convert to result format
    result = [-1] * n
    for i in range(n):
        if row_assignment[i] != -1:
            result[row_assignment[i]] = i

    return result


def _match_cell_ids_by_similarity(
    prev_ids: Sequence[CellId_t],
    prev_codes: Sequence[str],
    next_ids: Sequence[CellId_t],
    next_codes: Sequence[str],
) -> list[CellId_t]:
    """Match cell IDs based on code similarity."""
    assert len(prev_codes) == len(prev_ids)
    assert len(next_codes) == len(next_ids)

    # ids that are not in prev_ids but in next_ids
    id_pool = set(next_ids) - set(prev_ids)

    def get_next_available_id(idx: int) -> CellId_t:
        cell_id = next_ids[idx]
        # Use the id from the pool if available
        if cell_id in id_pool:
            id_pool.remove(cell_id)
        elif id_pool:
            # Otherwise just use the next available id
            cell_id = id_pool.pop()
        else:
            # If no ids are available, we could generate a new one
            # but this should never run.
            raise RuntimeError(
                "No available IDs left to assign. This should not happen."
            )
        return cell_id

    def filter_and_backfill() -> list[CellId_t]:
        for idx, _ in enumerate(next_ids):
            if result[idx] is None:
                # If we have a None, we need to fill it with an available ID
                result[idx] = get_next_available_id(idx)
        # Only needed to appease the type checker. We just filled all None
        # values.
        return [_id for _id in result if _id is not None]

    # Hash matching to capture permutations
    # covers next is a subset of prev (i.e. next - prev == {})
    previous_lookup = group_lookup(prev_ids, prev_codes)
    next_lookup = group_lookup(next_ids, next_codes)

    result: list[Optional[CellId_t]] = [None] * len(next_codes)
    filled = 0
    for idx, code in enumerate(next_codes):
        if code in previous_lookup:
            # If we have an exact match, use it
            filled += 1
            result[idx] = pop_local(previous_lookup[code], idx)
            if not previous_lookup[code]:
                del previous_lookup[code]
            # Clean up the next_lookup match too.
            if code in next_lookup:
                pop_local(next_lookup[code], idx)
                if not next_lookup[code]:
                    del next_lookup[code]

    # If we filled all positions, return the result
    # or if prev is a subset of next, then prev has been dequeued and emptied,
    # we can just backfill and return.
    if filled == len(next_codes) or not previous_lookup:
        return filter_and_backfill()

    # The remaining case is (next - prev) is not empty.
    # Establish specific order of remaining unique codes so we can match them
    added_code = get_unique(next_codes, next_lookup)
    deleted_code = get_unique(prev_codes, previous_lookup)

    # Build order mappings for the Hungarian algorithm
    next_order = extract_order(added_code, next_lookup)
    prev_order = extract_order(deleted_code, previous_lookup)

    # grab indices for lookup
    next_inverse = {code: i for i, code in enumerate(added_code)}
    # and inverse mapping for prev
    inverse_order = {
        idx: i for i, idxs in enumerate(prev_order) for idx in idxs
    }

    # Pad the scores matrix to ensure it is square
    n = max(len(next_codes) - filled, len(prev_codes) - filled)
    scores = [[0.0] * n for _ in range(n)]
    # Fill matrix, accounting for dupes
    for i, code in enumerate(added_code):
        o1 = next_order[i]
        for j, prev_code in enumerate(deleted_code):
            score = similarity_score(prev_code, code)
            o2 = prev_order[j]
            for x in o1:
                for y in o2:
                    # NB. transposed indices for Hungarian
                    scores[y][x] = score

    # Use Hungarian algorithm to find the best matching
    matches = _hungarian_algorithm(scores)
    for idx, code in enumerate(next_codes):
        if result[idx] is None:
            match_idx = next_order[next_inverse[code]].pop(0)
            if match_idx != -1 and matches[match_idx] in inverse_order:
                prev_idx = inverse_order[matches[match_idx]]
                prev_code = deleted_code[prev_idx]
                result[idx] = pop_local(previous_lookup[prev_code], idx)

    return filter_and_backfill()


def match_cell_ids_by_similarity(
    prev_data: dict[CellId_t, str], next_data: dict[CellId_t, str]
) -> dict[CellId_t, CellId_t]:
    """Match cell IDs based on code similarity.

    NB. There is similar code in the front end that matches session results to
    cells, but there are a few caveats for why the logic is different:
      - Session matching is inherent order dependent. If the order is wrong,
        there is no match. Moreover, the code must be an exact match for a
        session to be paired.
      - Cell matching in this context is not order dependent, we assume the
        notebook can be totally scrambled and we still want to match. Lose cell
        matching is also allowed.
    As such, in the frontend case a Lavenshtein edit is used to match cells to
    session results based on code.
    While here we can naively use a direct match, and non-matching cells are still
    attempted to match based on some similarity metric.

    Args:
        prev_data: Mapping of previous cell IDs to code
        next_data: Mapping of next cell IDs to code

    Returns:
        A map of old ids to new ids, using prev_ids where possible
    """

    prev_ids, prev_codes = zip(*prev_data.items())
    next_ids, next_codes = zip(*next_data.items())

    sorted_ids = _match_cell_ids_by_similarity(
        prev_ids,
        prev_codes,
        next_ids,
        next_codes,
    )

    return dict(zip(sorted_ids, next_ids))
