#!/usr/bin/env python3
"""Experiment 005 -- is there a scaling law to induct on?

`research/07-scaling-and-proof-strategy.md` argues that every "solve it small,
then scale the proof" programme needs a quantity that behaves smoothly as the
universe grows. Nobody had checked whether one exists.

This experiment solves the same material signature across a range of board
shapes and measures two quantities: the fraction of positions that are drawn,
and the maximum distance to mate. Then it does the thing that actually matters:

    fit the law on SMALL boards only, PREDICT the large boards, and score the
    prediction against the solved answer.

That is the methodology of `docs/roadmap.md` item 004 applied to the cheapest
possible parameter. If a law fitted on 4x4 through 5x6 predicts 8x8, the
quantity is a candidate for something size-independent. If it does not, there is
nothing to induct on and the scaling story needs restating.

Run: ``python experiments/exp005_scaling_law/run.py``
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np

from solvingchess import report
from solvingchess.solver import StateBudgetExceeded, solve_material
from solvingchess.variants import endgame_variant

# Boards are split into a fitting set and a held-out set. Nothing from the
# held-out set touches the fit.
FIT_SHAPES = [(4, 4), (4, 5), (5, 4), (4, 6), (5, 5), (5, 6)]
HOLDOUT_SHAPES = [(6, 6), (7, 7), (8, 8)]

FAMILIES = ["KR-K", "KQ-K"]
SECONDARY = [("KR-KR", [(4, 4), (4, 5), (5, 5)])]


def solve_shape(spec: str, files: int, ranks: int, budget: int) -> dict | None:
    rules = endgame_variant(spec, files, ranks).rules
    started = time.perf_counter()
    try:
        solution = solve_material(rules, max_states=budget)
    except StateBudgetExceeded:
        print(f"  {spec}@{files}x{ranks:<3} over budget", flush=True)
        return None

    counts = solution.counts()
    _, max_dtm = solution.longest_win()
    won = solution.dtm[solution.dtm >= 0]
    row = {
        "universe": f"{spec}@{files}x{ranks}",
        "spec": spec,
        "files": files,
        "ranks": ranks,
        "area": files * ranks,
        "diameter": files + ranks,
        "states": solution.n_states,
        "draw_fraction": counts["draw"] / solution.n_states,
        "max_dtm": int(max_dtm),
        "mean_dtm": float(won.mean()) if won.size else float("nan"),
        "seconds": time.perf_counter() - started,
    }
    print(f"  {row['universe']:<12} states={row['states']:>9,}  "
          f"draws={row['draw_fraction']:6.2%}  maxDTM={row['max_dtm']:>3}  "
          f"meanDTM={row['mean_dtm']:5.1f}  [{row['seconds']:.0f}s]", flush=True)
    return row


def power_fit(xs, ys):
    """Least squares on log-log: returns (a, b) for y = a * x**b, plus R^2."""
    lx = np.log(np.asarray(xs, dtype=float))
    ly = np.log(np.asarray(ys, dtype=float))
    b, log_a = np.polyfit(lx, ly, 1)
    predicted = log_a + b * lx
    ss_res = float(((ly - predicted) ** 2).sum())
    ss_tot = float(((ly - ly.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
    return math.exp(log_a), float(b), r2


def fit_and_predict(rows, quantity: str, driver: str) -> dict:
    """Fit `quantity ~ a * driver**b` on the fit set; score it on the holdout."""
    fit_rows = [r for r in rows if (r["files"], r["ranks"]) in FIT_SHAPES]
    hold_rows = [r for r in rows if (r["files"], r["ranks"]) in HOLDOUT_SHAPES]
    if len(fit_rows) < 3 or not hold_rows:
        return {}

    a, b, r2 = power_fit([r[driver] for r in fit_rows], [r[quantity] for r in fit_rows])

    predictions = []
    for r in hold_rows:
        predicted = a * r[driver] ** b
        actual = r[quantity]
        predictions.append({
            "universe": r["universe"],
            "predicted": predicted,
            "actual": actual,
            "relative_error": abs(predicted - actual) / abs(actual) if actual else float("nan"),
        })
    errors = [p["relative_error"] for p in predictions]
    return {
        "quantity": quantity,
        "driver": driver,
        "a": a, "b": b, "fit_r2": r2,
        "fit_points": len(fit_rows),
        "predictions": predictions,
        "worst_relative_error": max(errors),
        "mean_relative_error": sum(errors) / len(errors),
    }


def local_exponents(rows, quantity: str, driver: str = "area") -> list:
    """Exponent measured between each consecutive pair of boards.

    A global fit can hide drift. If the *local* exponent settles on a value as
    the board grows, that value -- not the fitted average -- is the asymptotic
    law, and a clean one is a candidate for something provable.
    """
    ordered = sorted({r[driver]: r for r in rows}.values(), key=lambda r: r[driver])
    out = []
    for lo, hi in zip(ordered, ordered[1:]):
        if lo[quantity] <= 0 or hi[quantity] <= 0:
            continue
        out.append({
            "from": lo["universe"],
            "to": hi["universe"],
            "exponent": math.log(hi[quantity] / lo[quantity])
            / math.log(hi[driver] / lo[driver]),
        })
    return out


def report_fit(fit: dict) -> None:
    if not fit:
        return
    print(f"\n{fit['quantity']} ~ {fit['a']:.4g} * {fit['driver']}^{fit['b']:.3f}"
          f"   (fitted on {fit['fit_points']} small boards, R^2 = {fit['fit_r2']:.4f})")
    for p in fit["predictions"]:
        print(f"    {p['universe']:<12} predicted {p['predicted']:>8.3f}   "
              f"actual {p['actual']:>8.3f}   error {p['relative_error']:6.2%}")


def main() -> None:
    budget = 3_000_000
    results = {}

    for spec in FAMILIES:
        print(f"\n{spec}:")
        rows = []
        for files, ranks in FIT_SHAPES + HOLDOUT_SHAPES:
            row = solve_shape(spec, files, ranks, budget)
            if row:
                rows.append(row)
        results[spec] = {
            "rows": rows,
            "draw_fraction_vs_area": fit_and_predict(rows, "draw_fraction", "area"),
            "max_dtm_vs_area": fit_and_predict(rows, "max_dtm", "area"),
            "max_dtm_vs_diameter": fit_and_predict(rows, "max_dtm", "diameter"),
            "mean_dtm_vs_diameter": fit_and_predict(rows, "mean_dtm", "diameter"),
            "draw_fraction_local_exponents": local_exponents(rows, "draw_fraction"),
        }

    for spec, shapes in SECONDARY:
        print(f"\n{spec} (secondary, no holdout):")
        rows = [r for r in (solve_shape(spec, f, k, budget) for f, k in shapes) if r]
        results[spec] = {
            "rows": rows,
            "draw_fraction_local_exponents": local_exponents(rows, "draw_fraction"),
        }

    print("\n" + "=" * 72)
    print("PREDICTIONS FROM SMALL BOARDS ONLY")
    print("=" * 72)
    for spec in FAMILIES:
        print(f"\n--- {spec} ---")
        for key in ("draw_fraction_vs_area", "max_dtm_vs_area",
                    "max_dtm_vs_diameter", "mean_dtm_vs_diameter"):
            report_fit(results[spec][key])

    print("\n" + "=" * 72)
    print("LOCAL EXPONENT OF DRAWN FRACTION AGAINST BOARD AREA")
    print("=" * 72)
    for spec in results:
        steps = results[spec].get("draw_fraction_local_exponents") or []
        if not steps:
            continue
        print(f"\n--- {spec} ---")
        for step in steps:
            print(f"    {step['from']:<12} -> {step['to']:<12} "
                  f"exponent {step['exponent']:+.3f}")

    print("\n### Solved universes\n")
    all_rows = [r for spec in results for r in results[spec]["rows"]]
    print(report.markdown_table(all_rows, [
        ("universe", "universe", None),
        ("area", "area", None),
        ("states", "states", report.integer),
        ("drawn", "draw_fraction", lambda v: f"{v:.2%}"),
        ("max DTM", "max_dtm", None),
        ("mean DTM", "mean_dtm", lambda v: f"{v:.1f}"),
        ("time", "seconds", report.seconds),
    ]))

    path = report.save("exp005_scaling_law", {
        "fit_shapes": FIT_SHAPES,
        "holdout_shapes": HOLDOUT_SHAPES,
        "families": results,
    })
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
