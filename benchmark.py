from __future__ import annotations

from pathlib import Path

from python_solvers.genetic_algorithm import solve as solve_ga
from python_solvers.killer import get_killer_puzzle
from python_solvers.simulated_annealing import solve as solve_sa
from python_solvers.sudoku_core import load_puzzles

ROOT = Path(__file__).resolve().parent


def main() -> int:
    puzzles = load_puzzles(ROOT / "puzzles.txt")
    print("game,puzzle,algorithm,solved,cost,evaluations,time_ms")
    for case in puzzles:
        sa = solve_sa(case.board, seed=5, max_steps=120_000, restarts=4)
        print(f"classic,{case.name},sa,{sa.solved},{sa.cost},{sa.evaluations},{sa.seconds * 1000:.2f}")
        ga = solve_ga(case.board, seed=5, population_size=120, generations=800, runs=4)
        print(f"classic,{case.name},ga,{ga.solved},{ga.cost},{ga.evaluations},{ga.seconds * 1000:.2f}")

    killer = get_killer_puzzle("demo")
    sa = solve_sa(killer.board, killer.cages, seed=3, max_steps=50_000, restarts=3)
    print(f"killer,{killer.name},sa,{sa.solved},{sa.cost},{sa.evaluations},{sa.seconds * 1000:.2f}")
    ga = solve_ga(killer.board, killer.cages, seed=3, population_size=80, generations=500, runs=4)
    print(f"killer,{killer.name},ga,{ga.solved},{ga.cost},{ga.evaluations},{ga.seconds * 1000:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
