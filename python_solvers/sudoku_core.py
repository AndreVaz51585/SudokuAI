from __future__ import annotations

import ast
import re
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

Board = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Cage = tuple[int, tuple[Cell, ...]]

DIGITS = tuple(range(1, 10))
CELLS: tuple[Cell, ...] = tuple((r, c) for r in range(9) for c in range(9))
BLOCKS: tuple[tuple[Cell, ...], ...] = tuple(
    tuple((br + dr, bc + dc) for dr in range(3) for dc in range(3))
    for br in range(0, 9, 3)
    for bc in range(0, 9, 3)
)


@dataclass(frozen=True)
class PuzzleCase:
    name: str
    board: Board


def normalize_board(rows: Sequence[Sequence[int]]) -> Board:
    board = tuple(tuple(int(value) for value in row) for row in rows)
    if len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("A Sudoku board must be 9x9.")
    if any(value < 0 or value > 9 for row in board for value in row):
        raise ValueError("Sudoku values must be between 0 and 9.")
    return board


def board_to_lists(board: Board) -> list[list[int]]:
    return [list(row) for row in board]


def fixed_mask(board: Board) -> tuple[tuple[bool, ...], ...]:
    return tuple(tuple(value != 0 for value in row) for row in board)


def mutable_cells_by_block(mask: tuple[tuple[bool, ...], ...]) -> list[list[Cell]]:
    return [[cell for cell in block if not mask[cell[0]][cell[1]]] for block in BLOCKS]


def mutable_cells(mask: tuple[tuple[bool, ...], ...]) -> list[Cell]:
    return [(r, c) for r, c in CELLS if not mask[r][c]]


def unit_conflicts(values: Iterable[int]) -> int:
    filled = [value for value in values if value != 0]
    return len(filled) - len(set(filled))


def validate_given_numbers(board: Board, cages: Sequence[Cage] | None = None) -> None:
    units: list[list[int]] = []
    units.extend([list(row) for row in board])
    units.extend([[board[r][c] for r in range(9)] for c in range(9)])
    units.extend([[board[r][c] for r, c in block] for block in BLOCKS])
    for unit in units:
        if unit_conflicts(unit):
            raise ValueError("The puzzle has repeated fixed numbers in a row, column or block.")
    if cages:
        seen: set[Cell] = set()
        for target, cells in cages:
            if target <= 0:
                raise ValueError("Killer Sudoku cage targets must be positive.")
            for cell in cells:
                if cell in seen:
                    raise ValueError(f"Cell {cell} appears in more than one cage.")
                if not (0 <= cell[0] < 9 and 0 <= cell[1] < 9):
                    raise ValueError(f"Invalid cage cell {cell}.")
                seen.add(cell)
        if len(seen) != 81:
            raise ValueError("Killer Sudoku cages must cover all 81 cells exactly once.")


def random_block_solution(board: Board, rng: random.Random) -> Board:
    rows = board_to_lists(board)
    for block in BLOCKS:
        fixed_values = {rows[r][c] for r, c in block if rows[r][c] != 0}
        missing = [value for value in DIGITS if value not in fixed_values]
        rng.shuffle(missing)
        empty_cells = [(r, c) for r, c in block if rows[r][c] == 0]
        if len(missing) != len(empty_cells):
            raise ValueError("Invalid fixed numbers inside a 3x3 block.")
        for (r, c), value in zip(empty_cells, missing):
            rows[r][c] = value
    return normalize_board(rows)


def swap_cells(board: Board, a: Cell, b: Cell) -> Board:
    rows = board_to_lists(board)
    ar, ac = a
    br, bc = b
    rows[ar][ac], rows[br][bc] = rows[br][bc], rows[ar][ac]
    return normalize_board(rows)


def random_neighbor(
    board: Board,
    mutable_by_block: Sequence[Sequence[Cell]],
    rng: random.Random,
) -> Board:
    candidates = [cells for cells in mutable_by_block if len(cells) >= 2]
    if not candidates:
        return board
    cells = rng.choice(candidates)
    a, b = rng.sample(list(cells), 2)
    return swap_cells(board, a, b)


def random_mixed_neighbor(
    board: Board,
    mutable_by_block: Sequence[Sequence[Cell]],
    mutable: Sequence[Cell],
    rng: random.Random,
    global_swap_rate: float = 0.15,
) -> Board:
    if len(mutable) >= 2 and rng.random() < global_swap_rate:
        a, b = rng.sample(list(mutable), 2)
        return swap_cells(board, a, b)
    return random_neighbor(board, mutable_by_block, rng)


def sudoku_cost(
    board: Board,
    cages: Sequence[Cage] | None = None,
    include_blocks: bool = False,
) -> int:
    cost = 0
    cost += sum(unit_conflicts(row) for row in board)
    cost += sum(unit_conflicts(board[r][c] for r in range(9)) for c in range(9))
    if include_blocks:
        cost += sum(unit_conflicts(board[r][c] for r, c in block) for block in BLOCKS)
    if cages:
        for target, cells in cages:
            values = [board[r][c] for r, c in cells]
            cost += abs(sum(values) - target)
            cost += unit_conflicts(values) * 2
    return cost


def respects_fixed_values(board: Board, puzzle: Board) -> bool:
    return all(puzzle[r][c] == 0 or puzzle[r][c] == board[r][c] for r, c in CELLS)


def is_solution(board: Board, puzzle: Board, cages: Sequence[Cage] | None = None) -> bool:
    return (
        all(value != 0 for row in board for value in row)
        and respects_fixed_values(board, puzzle)
        and sudoku_cost(board, cages=cages, include_blocks=True) == 0
    )


def print_board(board: Board) -> str:
    lines: list[str] = []
    for r, row in enumerate(board):
        if r and r % 3 == 0:
            lines.append("------+-------+------")
        parts = []
        for c, value in enumerate(row):
            if c and c % 3 == 0:
                parts.append("|")
            parts.append(str(value) if value else ".")
        lines.append(" ".join(parts))
    return "\n".join(lines)


def sanitize_name(label: str) -> str:
    text = label.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "puzzle"


def _extract_first_matrix(text: str) -> str:
    start = text.find("[[")
    if start == -1:
        raise ValueError("No Sudoku matrix found.")
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError("Unclosed Sudoku matrix.")


def _parse_prolog_matrix(text: str) -> Board:
    matrix_text = _extract_first_matrix(text).replace("_", "0")
    return normalize_board(ast.literal_eval(matrix_text))


def load_puzzles(path: str | Path) -> list[PuzzleCase]:
    cases: list[PuzzleCase] = []
    seen: set[Board] = set()
    current_label = "puzzle"
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":") and not line.startswith("solve"):
            current_label = line[:-1]
            continue
        if not line.startswith("solve"):
            continue
        board = _parse_prolog_matrix(line)
        if board in seen:
            continue
        seen.add(board)
        base = sanitize_name(current_label)
        name = base
        suffix = 2
        while any(case.name == name for case in cases):
            name = f"{base}_{suffix}"
            suffix += 1
        cases.append(PuzzleCase(name=name, board=board))
    return cases


def board_to_prolog(board: Board) -> str:
    rows = []
    for row in board:
        rows.append("[" + ",".join("_" if value == 0 else str(value) for value in row) + "]")
    return "[" + ",".join(rows) + "]"
