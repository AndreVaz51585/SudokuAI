from __future__ import annotations

from dataclasses import dataclass

from .sudoku_core import Board, Cage, normalize_board


@dataclass(frozen=True)
class KillerPuzzle:
    name: str
    board: Board
    cages: tuple[Cage, ...]


_DEMO_SOLUTION = normalize_board(
    [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
)

_DEMO_GIVENS = normalize_board(
    [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
)


def _make_demo_cages() -> tuple[Cage, ...]:
    cages: list[Cage] = []
    patterns = ([2, 2, 2, 3], [1, 2, 3, 3], [3, 2, 1, 3])
    for row in range(9):
        col = 0
        for size in patterns[row % len(patterns)]:
            cells = tuple((row, c) for c in range(col, col + size))
            target = sum(_DEMO_SOLUTION[r][c] for r, c in cells)
            cages.append((target, cells))
            col += size
    return tuple(cages)


def _make_singleton_cages() -> tuple[Cage, ...]:
    return tuple(
        (_DEMO_SOLUTION[row][col], ((row, col),))
        for row in range(9)
        for col in range(9)
    )


KILLER_PUZZLES: dict[str, KillerPuzzle] = {
    "demo": KillerPuzzle(
        name="demo",
        board=_DEMO_GIVENS,
        cages=_make_demo_cages(),
    ),
    "demo_mixed": KillerPuzzle(
        name="demo_mixed",
        board=normalize_board([[0] * 9 for _ in range(9)]),
        cages=_make_demo_cages(),
    )
}


def get_killer_puzzle(name: str) -> KillerPuzzle:
    try:
        return KILLER_PUZZLES[name]
    except KeyError as exc:
        available = ", ".join(sorted(KILLER_PUZZLES))
        raise ValueError(f"Unknown Killer Sudoku puzzle '{name}'. Available: {available}") from exc
