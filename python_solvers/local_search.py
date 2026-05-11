from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Sequence

from .sudoku_core import Board, Cage, random_mixed_neighbor, sudoku_cost, swap_cells


@dataclass(frozen=True)
class RepairResult:
    board: Board
    cost: int
    evaluations: int


def repair_by_block_swaps(
    board: Board,
    mutable_by_block: Sequence[Sequence[tuple[int, int]]],
    mutable_cells: Sequence[tuple[int, int]],
    rng: random.Random,
    cages: Sequence[Cage] | None = None,
    *,
    max_steps: int = 40_000,
    sample_size: int = 80,
    start_temperature: float = 0.35,
) -> RepairResult:
    current = board
    current_cost = sudoku_cost(current, cages=cages, include_blocks=True)
    best = current
    best_cost = current_cost
    evaluations = 1
    movable_blocks = [list(cells) for cells in mutable_by_block if len(cells) >= 2]
    if not movable_blocks:
        return RepairResult(best, best_cost, evaluations)

    for step in range(max_steps):
        if best_cost == 0:
            break
        candidate = None
        candidate_cost = 10**9
        for _ in range(sample_size):
            cells = rng.choice(movable_blocks)
            a, b = rng.sample(cells, 2)
            trial = swap_cells(current, a, b)
            trial_cost = sudoku_cost(trial, cages=cages, include_blocks=True)
            evaluations += 1
            if trial_cost < candidate_cost:
                candidate = trial
                candidate_cost = trial_cost

        if candidate is None:
            break

        temperature = max(0.01, start_temperature * (1 - step / max_steps))
        delta = candidate_cost - current_cost
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            current = candidate
            current_cost = candidate_cost
        else:
            current = random_mixed_neighbor(current, mutable_by_block, mutable_cells, rng, 0.35)
            current_cost = sudoku_cost(current, cages=cages, include_blocks=True)
            evaluations += 1

        if current_cost < best_cost:
            best = current
            best_cost = current_cost

    return RepairResult(best, best_cost, evaluations)
