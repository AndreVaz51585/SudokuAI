from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Literal, Sequence

from .sudoku_core import Board, Cage, fixed_mask, is_solution, mutable_cells_by_block
from .sudoku_core import random_block_solution, random_neighbor, sudoku_cost, validate_given_numbers

Sense = Literal["minimize", "maximize"]


@dataclass(frozen=True)
class AnnealingResult:
    board: Board
    cost: int
    solved: bool
    evaluations: int
    restarts: int
    seconds: float


@dataclass(frozen=True)
class SAState:
    board: Board


@dataclass(frozen=True)
class SACoreResult:
    state: SAState
    cost: int
    evaluations: int
    history: tuple[int, ...]


def _temperature(t: int, t_max: float, r: float) -> float:
    return t_max * math.exp(-r * t)


def _acceptance_probability(current_cost: int, new_cost: int, temperature: float, sense: Sense) -> float:
    if sense == "maximize":
        return math.exp((new_cost - current_cost) / temperature)
    return math.exp((current_cost - new_cost) / temperature)


def simulated_annealing(
    t_max: float,
    t_min: float,
    r: float,
    k: int,
    data: Any,
    get_initial_solution: Callable[[Any], SAState],
    get_random_neigh: Callable[[SAState, Any], SAState],
    eval_func: Callable[[SAState, Any], int],
    is_optimum: Callable[[int, Any], bool],
    sense: Sense,
) -> SACoreResult:
    """Generic SA adapted from the professor's Matlab/Octave SA.m."""
    t = 0
    temperature = t_max
    evaluations = 0
    found_optimum = False

    current = get_initial_solution(data)
    current_cost = eval_func(current, data)
    evaluations += 1
    history = [current_cost]

    while not found_optimum:
        i = 0
        while i < k and not found_optimum:
            neighbor = get_random_neigh(current, data)
            neighbor_cost = eval_func(neighbor, data)
            evaluations += 1

            delta = neighbor_cost - current_cost
            if sense == "maximize":
                delta = -delta

            if delta < 0:
                current = neighbor
                current_cost = neighbor_cost
            else:
                probability = _acceptance_probability(current_cost, neighbor_cost, temperature, sense)
                if random.random() <= probability:
                    current = neighbor
                    current_cost = neighbor_cost

            i += 1
            history.append(current_cost)
            if is_optimum(current_cost, data):
                found_optimum = True

        if not found_optimum:
            t += 1
            temperature = _temperature(t, t_max, r)
            if temperature < t_min:
                break

    return SACoreResult(current, current_cost, evaluations, tuple(history))


@dataclass
class SudokuSAData:
    puzzle: Board
    cages: Sequence[Cage] | None
    rng: random.Random
    mutable_by_block: Sequence[Sequence[tuple[int, int]]]


def _get_initial_solution(data: SudokuSAData) -> SAState:
    return SAState(random_block_solution(data.puzzle, data.rng))


def _get_random_neigh(state: SAState, data: SudokuSAData) -> SAState:
    return SAState(random_neighbor(state.board, data.mutable_by_block, data.rng))


def _eval_function(state: SAState, data: SudokuSAData) -> int:
    return sudoku_cost(state.board, cages=data.cages)


def _is_optimum(cost: int, _: SudokuSAData) -> bool:
    return cost == 0


def solve(
    puzzle: Board,
    cages: Sequence[Cage] | None = None,
    *,
    seed: int | None = None,
    max_steps: int = 250_000,
    restarts: int = 20,
    t_max: float = 2.5,
    t_min: float = 0.001,
    cooling_rate: float | None = None,
) -> AnnealingResult:
    validate_given_numbers(puzzle, cages)
    rng = random.Random(seed)
    random.seed(seed)
    mask = fixed_mask(puzzle)
    data = SudokuSAData(
        puzzle=puzzle,
        cages=cages,
        rng=rng,
        mutable_by_block=mutable_cells_by_block(mask),
    )
    start = time.perf_counter()
    total_evaluations = 0
    best_board = puzzle
    best_cost = 10**9
    effective_cooling_rate = cooling_rate
    if effective_cooling_rate is None:
        effective_cooling_rate = math.log(t_max / t_min) / max(1, max_steps)

    for restart in range(1, restarts + 1):
        core = simulated_annealing(
            t_max,
            t_min,
            effective_cooling_rate,
            1,
            data,
            _get_initial_solution,
            _get_random_neigh,
            _eval_function,
            _is_optimum,
            "minimize",
        )
        total_evaluations += core.evaluations
        if core.cost < best_cost:
            best_board = core.state.board
            best_cost = core.cost
        if best_cost == 0 and is_solution(best_board, puzzle, cages):
            elapsed = time.perf_counter() - start
            return AnnealingResult(best_board, 0, True, total_evaluations, restart, elapsed)

    elapsed = time.perf_counter() - start
    solved = best_cost == 0 and is_solution(best_board, puzzle, cages)
    return AnnealingResult(best_board, best_cost, solved, total_evaluations, restarts, elapsed)
