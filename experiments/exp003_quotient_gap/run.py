#!/usr/bin/env python3
"""Experiment 003 -- how much structure is symmetry missing?

Experiment 001 measures what board symmetry collapses. This one measures what
*anything* could collapse.

For a solved universe we compute three sizes:

``raw``
    every reachable state.
``symmetry``
    orbits under the largest board symmetry group that preserves the game.
``bisimulation``
    blocks of the coarsest partition that separates win/draw/loss and is stable
    under the move relation. No sound value-preserving abstraction can be
    smaller, so this is the floor.

The ratio ``symmetry / bisimulation`` is the interesting number. If it is close
to 1, geometry is already capturing essentially all the redundancy and the
"wrong mathematical space" hypothesis has little room left. If it is large,
there is real non-geometric structure in chess positions that no rotation or
reflection can see -- and finding a *closed-form description* of those blocks is
then a concrete, well-posed research target rather than a slogan.

Run: ``python experiments/exp003_quotient_gap/run.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from solvingchess import report
from solvingchess.quotient import bisimulation_quotient, symmetry_quotient_size
from solvingchess.solver import solve_material
from solvingchess.symmetry import SymmetryGroup
from solvingchess.variants import endgame_variant

UNIVERSES = [
    ("K-K", 4, 4),
    ("KR-K", 4, 4),
    ("KQ-K", 4, 4),
    ("KN-K", 4, 4),
    ("KB-K", 4, 4),
    ("KP-K", 4, 4),
    ("KR-KR", 4, 4),
    ("KQ-K", 5, 5),
    ("KR-K", 5, 5),
]


def main() -> None:
    rows = []
    for spec, files, ranks in UNIVERSES:
        rules = endgame_variant(spec, files, ranks).rules
        solution = solve_material(rules, max_states=1_500_000)
        group = SymmetryGroup(rules)

        checked, violations = group.verify(solution)
        if violations:
            print(f"{spec}@{files}x{ranks}: symmetry group invalid, skipping")
            continue

        sym = symmetry_quotient_size(solution, group)
        wdl = bisimulation_quotient(solution, label="wdl")
        dtm = bisimulation_quotient(solution, label="dtm")

        row = {
            "universe": f"{spec}@{files}x{ranks}",
            "group_order": group.order,
            "raw": solution.n_states,
            "symmetry": sym,
            "bisim_wdl": wdl.n_blocks,
            "bisim_dtm": dtm.n_blocks,
            "sym_compression": 100.0 * (1 - sym / solution.n_states),
            "wdl_compression": 100.0 * (1 - wdl.n_blocks / solution.n_states),
            "gap": sym / wdl.n_blocks,
            "rounds": wdl.rounds,
        }
        rows.append(row)
        print(f"{row['universe']:<12} raw={row['raw']:>8,} "
              f"sym={row['symmetry']:>8,} bisim(WDL)={row['bisim_wdl']:>7,} "
              f"bisim(DTM)={row['bisim_dtm']:>7,}  gap x{row['gap']:.1f}",
              flush=True)

    print()
    print(report.markdown_table(rows, [
        ("universe", "universe", None),
        ("raw", "raw", report.integer),
        ("symmetry orbits", "symmetry", report.integer),
        ("bisim (WDL)", "bisim_wdl", report.integer),
        ("bisim (DTM)", "bisim_dtm", report.integer),
        ("symmetry compression", "sym_compression", report.percent),
        ("bisim compression", "wdl_compression", report.percent),
        ("gap (sym / bisim)", "gap", lambda v: f"x{v:.1f}"),
    ]))
    path = report.save("exp003_quotient_gap", {"rows": rows})
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
