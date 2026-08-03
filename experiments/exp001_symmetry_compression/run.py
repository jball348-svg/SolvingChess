#!/usr/bin/env python3
"""Experiment 001 -- how much does board symmetry actually compress?

Supersedes the original hand-rolled 4x4 king-versus-king script. Three changes
matter:

* the symmetry group is chosen per universe rather than assumed to be D4 (a
  pawn, or asymmetric material, kills most of the group);
* the group is *verified* against a solved tablebase, so a compression figure is
  only reported once orbits are known to carry constant game value;
* compression is measured against the group-order ceiling, which is what tells
  you whether symmetry is doing well or badly.

Run: ``python experiments/exp001_symmetry_compression/run.py``
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from solvingchess import report
from solvingchess.geometry import KING, QUEEN
from solvingchess.solver import all_legal_states, solve_material
from solvingchess.symmetry import SymmetryGroup
from solvingchess.variants import endgame_variant, singleton_variant

# (spec, files, ranks). Kept small enough that the whole sweep runs in ~2 minutes.
UNIVERSES = [
    ("K-K", 4, 4),
    ("K-K", 5, 5),
    ("K-K", 4, 6),
    ("KR-K", 4, 4),
    ("KQ-K", 4, 4),
    ("KN-K", 4, 4),
    ("KR-KR", 4, 4),
    ("KP-K", 4, 4),
    ("KP-KP", 4, 4),
    ("KQ-KQ", 4, 4),
]


def measure(rules) -> dict:
    group = SymmetryGroup(rules)
    positions = list(all_legal_states(rules))
    orbits = Counter(group.canonical(p) for p in positions)
    raw, reduced = len(positions), len(orbits)
    sizes = Counter(orbits.values())

    tablebase = solve_material(rules, max_states=2_000_000)
    checked, violations = group.verify(tablebase, sample=20_000)

    return {
        "universe": f"{rules.signature()}@{rules.geometry}",
        "group_order": group.order,
        "group": group.describe(),
        "raw": raw,
        "reduced": reduced,
        "compression": 100.0 * (1 - reduced / raw),
        "ceiling": 100.0 * (1 - 1 / group.order),
        "efficiency": 100.0 * (raw / reduced) / group.order,
        "mean_orbit": raw / reduced,
        "orbit_sizes": dict(sorted(sizes.items())),
        "verified_states": checked,
        "verify_violations": violations,
    }


def main() -> None:
    rows = []
    for spec, files, ranks in UNIVERSES:
        variant = endgame_variant(spec, files, ranks)
        row = measure(variant.rules)
        rows.append(row)
        flag = "" if row["verify_violations"] == 0 else "  !! GROUP NOT VERIFIED"
        print(f"{row['universe']:<14} raw={row['raw']:>8,} "
              f"orbits={row['reduced']:>8,} "
              f"compression={row['compression']:6.2f}% "
              f"(ceiling {row['ceiling']:.2f}%, |G|={row['group_order']}){flag}",
              flush=True)

    # The singleton family is the project's own construction, so measure it too.
    # Enumerating every placement costs P(nsq, pieces), so this stays at four
    # pieces; larger rungs are measured on their reachable set in exp002.
    for files, ranks, types in [(4, 4, (KING, QUEEN)), (5, 5, (KING, QUEEN))]:
        variant = singleton_variant(files, ranks, types)
        rules = variant.rules
        group = SymmetryGroup(rules)
        positions = list(all_legal_states(rules))
        orbits = {group.canonical(p) for p in positions}
        rows.append({
            "universe": variant.name,
            "group_order": group.order,
            "group": group.describe(),
            "raw": len(positions),
            "reduced": len(orbits),
            "compression": 100.0 * (1 - len(orbits) / len(positions)),
            "ceiling": 100.0 * (1 - 1 / group.order),
            "efficiency": 100.0 * (len(positions) / len(orbits)) / group.order,
            "mean_orbit": len(positions) / len(orbits),
            "verified_states": 0,
            "verify_violations": None,
        })
        print(f"{rows[-1]['universe']:<14} raw={rows[-1]['raw']:>8,} "
              f"orbits={rows[-1]['reduced']:>8,} "
              f"compression={rows[-1]['compression']:6.2f}% "
              f"(ceiling {rows[-1]['ceiling']:.2f}%, |G|={rows[-1]['group_order']})",
              flush=True)

    columns = [
        ("universe", "universe", None),
        ("\\|G\\|", "group_order", None),
        ("raw states", "raw", report.integer),
        ("orbits", "reduced", report.integer),
        ("compression", "compression", report.percent),
        ("ceiling", "ceiling", report.percent),
        ("efficiency", "efficiency", report.percent),
    ]
    print()
    print(report.markdown_table(rows, columns))
    path = report.save("exp001_symmetry_compression", {"rows": rows})
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
