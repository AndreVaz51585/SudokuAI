from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .genetic_algorithm import solve as solve_ga
from .killer import KILLER_PUZZLES, get_killer_puzzle
from .simulated_annealing import solve as solve_sa
from .sudoku_core import Board, board_to_prolog, load_puzzles, print_board

ROOT = Path(__file__).resolve().parents[1]
PUZZLES_FILE = ROOT / "puzzles.txt"


def _classic_puzzles() -> dict[str, Board]:
    return {case.name: case.board for case in load_puzzles(PUZZLES_FILE)}


def _run_prolog(board: Board, algorithm: str) -> int:
    swipl = shutil.which("swipl")
    if not swipl:
        print("SWI-Prolog (swipl) was not found in PATH; cannot run Prolog algorithms.")
        return 2
    goal = f"use_module(main), main:solve({board_to_prolog(board)}, {algorithm}), halt."
    return subprocess.run([swipl, "-q", "-s", str(ROOT / "main.pl"), "-g", goal], cwd=ROOT).returncode


def _solve_python(args: argparse.Namespace, board: Board, cages=None) -> int:
    if args.algorithm == "sa":
        result = solve_sa(
            board,
            cages=cages,
            seed=args.seed,
            max_steps=args.max_steps,
            restarts=args.restarts,
        )
        iterations = f"restarts={result.restarts}"
    elif args.algorithm == "ga":
        result = solve_ga(
            board,
            cages=cages,
            seed=args.seed,
            population_size=args.population,
            generations=args.generations,
            runs=args.ga_runs,
        )
        iterations = f"generations={result.generations}"
    else:
        raise ValueError(f"Unsupported Python algorithm: {args.algorithm}")

    print(print_board(result.board))
    print()
    print(
        f"{args.algorithm.upper()} solved={result.solved} cost={result.cost} "
        f"evaluations={result.evaluations} {iterations} time={result.seconds * 1000:.2f} ms"
    )
    return 0 if result.solved else 1


def _interactive_defaults(args: argparse.Namespace) -> argparse.Namespace:
    if args.game and args.algorithm:
        return args
    print("Game mode:")
    print("1. Classic Sudoku")
    print("2. Killer Sudoku")
    game_choice = input("> ").strip()
    args.game = "killer" if game_choice == "2" else "classic"
    print("Algorithm:")
    print("1. Iterative Deepening (Prolog)")
    print("2. A* (Prolog)")
    print("3. Simulated Annealing (Python)")
    print("4. Genetic Algorithm (Python)")
    algorithm_choice = input("> ").strip()
    args.algorithm = {
        "1": "iterative_deepening",
        "2": "a_star",
        "3": "sa",
        "4": "ga",
    }.get(algorithm_choice, "sa")
    return args


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SudokuAI solver runner")
    parser.add_argument("--game", choices=["classic", "killer"])
    parser.add_argument("--algorithm", choices=["iterative_deepening", "a_star", "sa", "ga"])
    parser.add_argument("--puzzle", default=None, help="Puzzle name. Use --list to see names.")
    parser.add_argument("--list", action="store_true", help="List available puzzles.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-steps", type=int, default=250_000)
    parser.add_argument("--restarts", type=int, default=20)
    parser.add_argument("--population", type=int, default=180)
    parser.add_argument("--generations", type=int, default=3_000)
    parser.add_argument("--ga-runs", type=int, default=4)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    classic = _classic_puzzles()

    if args.list:
        print("Classic Sudoku:")
        for name in classic:
            print(f"  {name}")
        print("Killer Sudoku:")
        for name in sorted(KILLER_PUZZLES):
            print(f"  {name}")
        return 0

    args = _interactive_defaults(args)

    if args.game == "classic":
        puzzle_name = args.puzzle or next(iter(classic))
        if puzzle_name not in classic:
            parser.error(f"Unknown classic puzzle '{puzzle_name}'. Use --list.")
        board = classic[puzzle_name]
        if args.algorithm in {"a_star", "iterative_deepening"}:
            return _run_prolog(board, args.algorithm)
        return _solve_python(args, board)

    puzzle_name = args.puzzle or "demo"
    killer = get_killer_puzzle(puzzle_name)
    if args.algorithm in {"a_star", "iterative_deepening"}:
        parser.error("Killer Sudoku is currently supported by the Python SA and GA solvers.")
    return _solve_python(args, killer.board, killer.cages)


if __name__ == "__main__":
    raise SystemExit(main())
