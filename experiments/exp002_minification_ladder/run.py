#!/usr/bin/env python3
"""Experiment 002 -- the minification ladder.

The idea under test: shrink chess until it is exactly solvable, keep it
recognisably chess, then measure how the cost of solving grows as you put the
missing pieces back. The growth curve is the thing we actually want -- it tells
us whether "solve the toy, then scale the proof" is a programme or a wish.

Two ladders are climbed.

**Singleton ladder.** Boards of 3x3, 4x4 and 5x5 carrying at most one of each
piece type per side (K, then K+Q, then K+Q+R, ...). Each rung is solved from its
own start position, so the output is the game-theoretic value of a complete
game, not just an endgame table.

**Endgame ladder.** Classical material signatures solved over all legal
placements. These are cheaper and give a cleaner read on how state count scales
with piece count at fixed board size.

Run: ``python experiments/exp002_minification_ladder/run.py [--budget N]``
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from solvingchess import report
from solvingchess.geometry import BISHOP, KING, PIECE_LETTER, QUEEN, ROOK
from solvingchess.solver import (
    StateBudgetExceeded, VALUE_NAME, solve_material, solve_variant,
)
from solvingchess.symmetry import SymmetryGroup
from solvingchess.variants import SINGLETON_ORDER, endgame_variant, singleton_variant

SINGLETON_RUNGS = [
    (3, 3, (KING,)),
    (4, 4, (KING,)),
    (5, 5, (KING,)),
    (3, 3, (KING, QUEEN)),
    (4, 4, (KING, QUEEN)),
    (5, 5, (KING, QUEEN)),
    (4, 4, (KING, QUEEN, ROOK)),
    (5, 5, (KING, QUEEN, ROOK)),
    (4, 4, (KING, QUEEN, ROOK, BISHOP)),
    (5, 5, SINGLETON_ORDER),
]

ENDGAME_RUNGS = [
    ("K-K", 4, 4), ("K-K", 5, 5),
    ("KN-K", 4, 4), ("KB-K", 4, 4), ("KR-K", 4, 4), ("KQ-K", 4, 4), ("KP-K", 4, 4),
    ("KN-K", 5, 5), ("KB-K", 5, 5), ("KR-K", 5, 5), ("KQ-K", 5, 5), ("KP-K", 5, 5),
    ("KR-KR", 4, 4), ("KQ-KQ", 4, 4), ("KN-KN", 4, 4), ("KP-KP", 4, 4),
    ("KRN-K", 4, 4), ("KQR-K", 4, 4),
]


def permutation_count(nsq: int, npieces: int) -> int:
    return math.perm(nsq, npieces)


def run_singleton(files: int, ranks: int, types, budget: int) -> dict:
    label = "".join(PIECE_LETTER[t] for t in types)
    name = f"singleton-{label}@{files}x{ranks}"
    try:
        variant = singleton_variant(files, ranks, types)
    except ValueError as exc:
        return {"universe": name, "status": f"not constructible: {exc}"}

    group = SymmetryGroup(variant.rules)
    npieces = 2 * len(types)
    row = {
        "universe": name,
        "pieces": npieces,
        "squares": files * ranks,
        "placements": permutation_count(files * ranks, npieces),
        "group_order": group.order,
    }

    started = time.perf_counter()
    try:
        solution = solve_variant(variant, canonical=group.canonical, max_states=budget)
    except StateBudgetExceeded:
        row["status"] = f"exceeded budget of {budget:,} orbit-states"
        row["seconds"] = time.perf_counter() - started
        print(f"  {name:<26} OVER BUDGET after {row['seconds']:.0f}s", flush=True)
        return row

    root = solution.roots[0]
    counts = solution.counts()
    row.update({
        "status": "solved",
        "states": solution.n_states,
        "edges": solution.n_edges,
        "value": VALUE_NAME[solution.value_of(root)],
        "dtm": solution.dtm_of(root),
        "wins": counts["win"], "losses": counts["loss"], "draws": counts["draw"],
        "seconds": solution.explore_seconds + solution.solve_seconds,
        "pv_length": len(solution.principal_variation(root)),
    })
    print(f"  {name:<26} states={row['states']:>9,}  value={row['value']:<5} "
          f"dtm={row['dtm']:<4} [{row['seconds']:.0f}s]", flush=True)
    return row


def run_endgame(spec: str, files: int, ranks: int, budget: int) -> dict:
    variant = endgame_variant(spec, files, ranks)
    rules = variant.rules
    group = SymmetryGroup(rules)
    npieces = rules.nslots
    row = {
        "universe": f"{spec}@{files}x{ranks}",
        "pieces": npieces,
        "squares": files * ranks,
        "placements": permutation_count(files * ranks, npieces),
        "group_order": group.order,
    }
    started = time.perf_counter()
    try:
        solution = solve_material(rules, max_states=budget)
    except StateBudgetExceeded:
        row["status"] = f"exceeded budget of {budget:,} states"
        row["seconds"] = time.perf_counter() - started
        print(f"  {row['universe']:<14} OVER BUDGET", flush=True)
        return row

    counts = solution.counts()
    _, longest = solution.longest_win()
    row.update({
        "status": "solved",
        "states": solution.n_states,
        "edges": solution.n_edges,
        "wins": counts["win"], "losses": counts["loss"], "draws": counts["draw"],
        "draw_fraction": counts["draw"] / solution.n_states,
        "max_dtm": longest,
        "seconds": solution.explore_seconds + solution.solve_seconds,
    })
    print(f"  {row['universe']:<14} states={row['states']:>9,}  "
          f"draws={row['draw_fraction']:5.1%}  maxDTM={longest:<3} "
          f"[{row['seconds']:.0f}s]", flush=True)
    return row


def extrapolate(rows) -> dict:
    """Fit states ~ a * placements^b over the solved rungs and project forward."""
    solved = [r for r in rows if r.get("status") == "solved" and r.get("states", 0) > 1]
    if len(solved) < 3:
        return {}
    xs = [math.log(r["placements"]) for r in solved]
    ys = [math.log(r["states"]) for r in solved]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    var = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / var if var else 0.0
    intercept = my - slope * mx
    target = permutation_count(25, 12)   # Singleton Chess 5x5
    projected = math.exp(intercept + slope * math.log(target))
    return {
        "fit_slope": slope,
        "fit_intercept": intercept,
        "fit_points": n,
        "singleton_5x5_placements": target,
        "singleton_5x5_projected_states": projected,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, default=1_200_000,
                        help="ceiling on explored states per rung")
    parser.add_argument("--quick", action="store_true",
                        help="only run the cheap rungs (used by the test suite)")
    args = parser.parse_args()
    budget = 40_000 if args.quick else args.budget

    print("Singleton ladder (solved from the start position):")
    singleton_rows = [run_singleton(f, r, t, budget) for f, r, t in SINGLETON_RUNGS]

    print("\nEndgame ladder (all legal placements):")
    endgame_rows = [run_endgame(spec, f, r, budget) for spec, f, r in ENDGAME_RUNGS]

    fit = extrapolate(singleton_rows + endgame_rows)

    print("\n### Singleton ladder\n")
    print(report.markdown_table(singleton_rows, [
        ("universe", "universe", None),
        ("pieces", "pieces", None),
        ("placements", "placements", report.integer),
        ("orbit-states", "states", report.integer),
        ("value (White to move)", "value", None),
        ("DTM", "dtm", None),
        ("time", "seconds", report.seconds),
        ("status", "status", None),
    ]))

    print("\n### Endgame ladder\n")
    print(report.markdown_table(endgame_rows, [
        ("universe", "universe", None),
        ("pieces", "pieces", None),
        ("states", "states", report.integer),
        ("edges", "edges", report.integer),
        ("draws", "draw_fraction", lambda v: f"{v:.1%}"),
        ("max DTM (plies)", "max_dtm", None),
        ("time", "seconds", report.seconds),
    ]))

    if fit:
        print(f"\nEmpirical growth: states ~ placements^{fit['fit_slope']:.3f} "
              f"over {fit['fit_points']} solved rungs.")
        print(f"Singleton Chess 5x5 has {fit['singleton_5x5_placements']:,} "
              f"piece placements; the fit projects "
              f"~{fit['singleton_5x5_projected_states']:.3g} reachable states.")

    path = report.save("exp002_minification_ladder", {
        "budget": budget,
        "singleton": singleton_rows,
        "endgame": endgame_rows,
        "extrapolation": fit,
    })
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
