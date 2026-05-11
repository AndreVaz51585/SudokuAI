from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Literal, Sequence

from .sudoku_core import BLOCKS, Board, Cage, board_to_lists, fixed_mask, is_solution
from .sudoku_core import mutable_cells_by_block, normalize_board, random_block_solution
from .sudoku_core import random_neighbor, sudoku_cost, swap_cells, validate_given_numbers

Sense = Literal["minimize", "maximize"]


@dataclass(frozen=True)
class GeneticResult:
    board: Board
    cost: int
    solved: bool
    evaluations: int
    generations: int
    seconds: float


@dataclass(frozen=True)
class GAState:
    board: Board


@dataclass(frozen=True)
class GACoreResult:
    state: GAState
    cost: int
    evaluations: int
    generations: int
    best_history: tuple[int, ...]
    mean_history: tuple[float, ...]


def _best_index(costs: Sequence[int], sense: Sense) -> int:
    if sense == "maximize":
        return max(range(len(costs)), key=lambda index: costs[index])
    return min(range(len(costs)), key=lambda index: costs[index])


def _better(left: int, right: int, sense: Sense) -> bool:
    return left > right if sense == "maximize" else left < right


def _initial_population(
    data: Any,
    population_size: int,
    get_initial_solution: Callable[[Any], GAState],
) -> list[GAState]:
    return [get_initial_solution(data) for _ in range(population_size)]


def _evaluate_population(
    data: Any,
    population: Sequence[GAState],
    eval_func: Callable[[GAState, Any], int],
) -> list[int]:
    return [eval_func(state, data) for state in population]


def genetic_algorithm(
    data: Any,
    tmax: int,
    pop_size: int,
    cross_prob: float,
    mut_prob: float,
    select: Callable[[Sequence[GAState], Sequence[int], Sense, Any], list[GAState]],
    cross: Callable[[Any, Sequence[GAState], float], list[GAState]],
    mutate: Callable[[Any, Sequence[GAState], float], list[GAState]],
    get_initial_solution: Callable[[Any], GAState],
    eval_func: Callable[[GAState, Any], int],
    is_optimum: Callable[[int, Any], bool],
    sense: Sense,
) -> GACoreResult:
    """Generic GA adapted from the professor's Matlab/Octave GA.m."""
    evaluations = 0
    found_optimum = False

    population = _initial_population(data, pop_size, get_initial_solution)
    costs = _evaluate_population(data, population, eval_func)
    evaluations += pop_size
    best_history = [costs[_best_index(costs, sense)]]
    mean_history = [sum(costs) / len(costs)]

    generation = 0
    while generation < tmax and not found_optimum:
        generation += 1
        population = select(population, costs, sense, data)
        population = cross(data, population, cross_prob)
        population = mutate(data, population, mut_prob)
        costs = _evaluate_population(data, population, eval_func)
        evaluations += pop_size

        best_cost = costs[_best_index(costs, sense)]
        best_history.append(best_cost)
        mean_history.append(sum(costs) / len(costs))
        if is_optimum(best_cost, data):
            found_optimum = True

    index = _best_index(costs, sense)
    return GACoreResult(
        population[index],
        costs[index],
        evaluations,
        generation,
        tuple(best_history),
        tuple(mean_history),
    )


@dataclass
class SudokuGAData:
    puzzle: Board
    cages: Sequence[Cage] | None
    rng: random.Random
    mutable_by_block: Sequence[Sequence[tuple[int, int]]]
    elitism: int
    immigrants: int
    mutation_attempts: int


def _get_initial_solution(data: SudokuGAData) -> GAState:
    return GAState(random_block_solution(data.puzzle, data.rng))


def _eval_function(state: GAState, data: SudokuGAData) -> int:
    return sudoku_cost(state.board, cages=data.cages)


def _is_optimum(cost: int, _: SudokuGAData) -> bool:
    return cost == 0


def _tournament(
    population: Sequence[GAState],
    costs: Sequence[int],
    sense: Sense,
    data: SudokuGAData,
    size: int = 3,
) -> GAState:
    indexes = data.rng.sample(range(len(population)), size)
    best = indexes[0]
    for index in indexes[1:]:
        if _better(costs[index], costs[best], sense):
            best = index
    return population[best]


def _select(
    population: Sequence[GAState],
    costs: Sequence[int],
    sense: Sense,
    data: SudokuGAData,
) -> list[GAState]:
    ranked = sorted(
        zip(costs, population),
        key=lambda item: item[0],
        reverse=sense == "maximize",
    )
    new_population = [state for _, state in ranked[: data.elitism]]
    while len(new_population) < len(population) - data.immigrants:
        new_population.append(_tournament(population, costs, sense, data))
    while len(new_population) < len(population):
        new_population.append(_get_initial_solution(data))
    return new_population


def _blockwise_crossover(parent_a: Board, parent_b: Board, rng: random.Random) -> Board:
    rows = board_to_lists(parent_a)
    for block in BLOCKS:
        source = parent_a if rng.random() < 0.5 else parent_b
        for r, c in block:
            rows[r][c] = source[r][c]
    return normalize_board(rows)


def _cross(data: SudokuGAData, population: Sequence[GAState], cross_prob: float) -> list[GAState]:
    new_population = list(population)
    for index in range(data.elitism, len(new_population) - 1, 2):
        if data.rng.random() < cross_prob:
            first = new_population[index].board
            second = new_population[index + 1].board
            new_population[index] = GAState(_blockwise_crossover(first, second, data.rng))
            new_population[index + 1] = GAState(_blockwise_crossover(second, first, data.rng))
    return new_population


def _directed_swap(board: Board, data: SudokuGAData) -> Board:
    blocks = [list(cells) for cells in data.mutable_by_block if len(cells) >= 2]
    if not blocks:
        return board
    best = board
    best_cost = sudoku_cost(board, cages=data.cages)
    for _ in range(data.mutation_attempts):
        cells = data.rng.choice(blocks)
        a, b = data.rng.sample(cells, 2)
        candidate = swap_cells(board, a, b)
        candidate_cost = sudoku_cost(candidate, cages=data.cages)
        if candidate_cost < best_cost:
            best = candidate
            best_cost = candidate_cost
    if best is board:
        return random_neighbor(board, data.mutable_by_block, data.rng)
    return best


def _mutate(data: SudokuGAData, population: Sequence[GAState], mut_prob: float) -> list[GAState]:
    new_population = list(population)
    for index in range(data.elitism, len(new_population)):
        board = new_population[index].board
        if data.rng.random() < mut_prob:
            board = _directed_swap(board, data)
        if data.rng.random() < mut_prob * 0.35:
            board = random_neighbor(board, data.mutable_by_block, data.rng)
        new_population[index] = GAState(board)
    return new_population


def solve(
    puzzle: Board,
    cages: Sequence[Cage] | None = None,
    *,
    seed: int | None = None,
    population_size: int = 180,
    generations: int = 3_000,
    crossover_rate: float = 0.85,
    mutation_rate: float = 0.35,
    elitism: int = 6,
    immigrants: int = 4,
    mutation_attempts: int = 24,
    runs: int = 4,
) -> GeneticResult:
    validate_given_numbers(puzzle, cages)
    mask = fixed_mask(puzzle)
    start = time.perf_counter()
    best_board = puzzle
    best_cost = 10**9
    total_evaluations = 0
    total_generations = 0

    for run in range(max(1, runs)):
        run_seed = None if seed is None else seed + run * 7
        data = SudokuGAData(
            puzzle=puzzle,
            cages=cages,
            rng=random.Random(run_seed),
            mutable_by_block=mutable_cells_by_block(mask),
            elitism=elitism,
            immigrants=immigrants,
            mutation_attempts=mutation_attempts,
        )
        core = genetic_algorithm(
            data,
            generations,
            population_size,
            crossover_rate,
            mutation_rate,
            _select,
            _cross,
            _mutate,
            _get_initial_solution,
            _eval_function,
            _is_optimum,
            "minimize",
        )
        total_evaluations += core.evaluations
        total_generations += core.generations
        if core.cost < best_cost:
            best_board = core.state.board
            best_cost = core.cost
        if best_cost == 0 and is_solution(best_board, puzzle, cages):
            break

    elapsed = time.perf_counter() - start
    solved = best_cost == 0 and is_solution(best_board, puzzle, cages)
    return GeneticResult(best_board, best_cost, solved, total_evaluations, total_generations, elapsed)
