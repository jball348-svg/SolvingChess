#!/usr/bin/env python3
"""Experiment 004 -- do invariants guessed on small boards transfer to big ones?

This is the experiment `research/07-scaling-and-proof-strategy.md` argues the
whole programme should be restated around. The workflow is:

1. solve a tiny universe exactly, giving ground truth for every state;
2. fit a short, human-readable rule over board-size-independent features;
3. **predict** the values of a universe the rule has never seen, including the
   real 8x8 board;
4. score the prediction against the solved answer.

Step 3 is what produces evidence. A rule that scores well on the board it was
fitted to has learned that board. A rule that scores well on a board four times
larger has learned something about the *game*, and that is the only kind of
statement a scaling argument could be built from.

The experiment also runs a controlled comparison of two rival **normalisations**
of the same concept. "The defending king is confined" can mean it holds a small
*share* of the board, or a small *number of squares* regardless of board size.
Only one of those can be the size-independent idea, and which one it is decides
what a scaling argument would have to say. Three feature sets are fitted and
transferred separately:

* ``fraction`` -- confinement as a share of board area;
* ``absolute`` -- confinement as a square count;
* ``both`` -- everything, letting the learner choose.

Everything is scored against the majority-class baseline, because most positions
in these universes are wins and a rule that beats nothing is worth nothing.

Run: ``python experiments/exp004_invariant_transfer/run.py``
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from solvingchess import report
from solvingchess.features import (
    CONFINEMENT_ABSOLUTE, CONFINEMENT_FRACTION, FEATURE_NAMES, FEATURE_VALUES,
    FeatureExtractor,
)
from solvingchess.induction import (
    accuracy, fallback_rate, fit, majority_baseline, per_class_accuracy, render,
)
from solvingchess.solver import DRAW, LOSS, WIN, solve_material
from solvingchess.variants import endgame_variant

CLASS_NAMES = {WIN: "win", DRAW: "draw", LOSS: "loss"}

FRACTION_INDEX = FEATURE_NAMES.index(CONFINEMENT_FRACTION)
ABSOLUTE_INDEX = FEATURE_NAMES.index(CONFINEMENT_ABSOLUTE)

FEATURE_SETS = {
    "fraction": [i for i in range(len(FEATURE_NAMES)) if i != ABSOLUTE_INDEX],
    "absolute": [i for i in range(len(FEATURE_NAMES)) if i != FRACTION_INDEX],
    "both": list(range(len(FEATURE_NAMES))),
}

# Fit on the smallest board only. Everything else is held out.
TRIALS = [
    {"train": ("KR-K", 4, 4),
     "test": [("KR-K", 5, 5), ("KR-K", 6, 6), ("KR-K", 8, 8)]},
    {"train": ("KQ-K", 4, 4),
     "test": [("KQ-K", 5, 5), ("KQ-K", 6, 6), ("KQ-K", 8, 8)]},
    # Cross-family: does a rule learned about rooks say anything about queens?
    {"train": ("KR-K", 4, 4),
     "test": [("KQ-K", 5, 5), ("KQ-K", 8, 8)]},
    # Pawnful, where exp003 says the non-geometric structure lives.
    {"train": ("KP-K", 4, 4),
     "test": [("KP-K", 5, 5), ("KP-K", 4, 6), ("KP-K", 6, 6)]},
]

SAMPLE_CAP = 60_000     # features are not free; cap the larger tables
MAX_DEPTH = 6

_CACHE: dict = {}


def dataset(spec: str, files: int, ranks: int, rng: random.Random):
    """Solve a universe once and cache its (feature rows, labels, meta)."""
    key = (spec, files, ranks)
    if key in _CACHE:
        return _CACHE[key]

    rules = endgame_variant(spec, files, ranks).rules
    started = time.perf_counter()
    solution = solve_material(rules, max_states=3_000_000)

    states = solution.states
    sampled = False
    if len(states) > SAMPLE_CAP:
        states = rng.sample(states, SAMPLE_CAP)
        sampled = True

    extractor = FeatureExtractor(rules)
    rows = [extractor.extract(s) for s in states]
    labels = [solution.value_of(s) for s in states]
    meta = {
        "universe": f"{spec}@{files}x{ranks}",
        "solved_states": solution.n_states,
        "scored_states": len(rows),
        "sampled": sampled,
    }
    print(f"    {meta['universe']:<12} solved {solution.n_states:>8,} states, "
          f"{len(rows):>6,} scored  [{time.perf_counter() - started:.0f}s]", flush=True)
    _CACHE[key] = (rows, labels, meta)
    return _CACHE[key]


def project(rows, columns):
    return [tuple(row[i] for i in columns) for row in rows]


def run_trial(trial: dict, rng: random.Random) -> dict:
    spec, files, ranks = trial["train"]
    print(f"\nTraining on {spec}@{files}x{ranks}:")
    train_rows, train_labels, train_meta = dataset(spec, files, ranks, rng)
    test_sets = [dataset(s, f, r, rng) for s, f, r in trial["test"]]

    variants = {}
    for set_name, columns in FEATURE_SETS.items():
        names = [FEATURE_NAMES[i] for i in columns]
        tree = fit(project(train_rows, columns), train_labels, len(columns),
                   max_depth=MAX_DEPTH)
        train_accuracy = accuracy(tree, project(train_rows, columns), train_labels)

        transfers = []
        for rows, labels, meta in test_sets:
            projected = project(rows, columns)
            got = accuracy(tree, projected, labels)
            base = majority_baseline(train_labels, labels)
            transfers.append({
                **meta,
                "accuracy": got,
                "baseline": base,
                "lift": (got - base) / (1 - base) if base < 1 else float("nan"),
                "fallback_rate": fallback_rate(tree, projected),
                "per_class": per_class_accuracy(tree, projected, labels, CLASS_NAMES),
            })

        print(f"  [{set_name:<8}] {tree.size():>3} nodes, depth {tree.depth()}, "
              f"train {train_accuracy:.4f} -> "
              + "  ".join(f"{t['universe'].split('@')[1]}:{t['accuracy']:.3f}"
                          f"(fb {t['fallback_rate']:.0%})" for t in transfers),
              flush=True)

        variants[set_name] = {
            "features": names,
            "rule_nodes": tree.size(),
            "rule_depth": tree.depth(),
            "rule": render(tree, names, CLASS_NAMES, FEATURE_VALUES),
            "train_accuracy": train_accuracy,
            "train_baseline": majority_baseline(train_labels, train_labels),
            "transfers": transfers,
        }

    return {"train": train_meta, "variants": variants}


def main() -> None:
    rng = random.Random(20260803)
    trials = [run_trial(trial, rng) for trial in TRIALS]

    print("\n" + "=" * 78)
    print("TRANSFER BY FEATURE NORMALISATION")
    print("=" * 78)
    rows = []
    for trial in trials:
        origin = trial["train"]["universe"]
        for set_name, variant in trial["variants"].items():
            rows.append({
                "fitted on": origin,
                "features": set_name,
                "evaluated on": f"{origin} (train)",
                "nodes": variant["rule_nodes"],
                "accuracy": variant["train_accuracy"],
                "baseline": variant["train_baseline"],
                "lift": (variant["train_accuracy"] - variant["train_baseline"])
                / (1 - variant["train_baseline"]),
                "fallback": 0.0,
            })
            for transfer in variant["transfers"]:
                rows.append({
                    "fitted on": origin,
                    "features": set_name,
                    "evaluated on": transfer["universe"],
                    "nodes": variant["rule_nodes"],
                    "accuracy": transfer["accuracy"],
                    "baseline": transfer["baseline"],
                    "lift": transfer["lift"],
                    "fallback": transfer["fallback_rate"],
                })

    print()
    print(report.markdown_table(rows, [
        ("fitted on", "fitted on", None),
        ("features", "features", None),
        ("evaluated on", "evaluated on", None),
        ("nodes", "nodes", None),
        ("accuracy", "accuracy", lambda v: f"{v:.4f}"),
        ("baseline", "baseline", lambda v: f"{v:.4f}"),
        ("lift", "lift", lambda v: f"{v:+.4f}"),
        ("unseen-value fallback", "fallback", lambda v: f"{v:.1%}"),
    ]))

    print("\n### Decay of accuracy with board area (KR-K and KQ-K)\n")
    decay_rows = []
    for trial in trials[:2]:
        for set_name, variant in trial["variants"].items():
            entry = {"fitted on": trial["train"]["universe"], "features": set_name}
            for transfer in variant["transfers"]:
                entry[transfer["universe"].split("@")[1]] = transfer["accuracy"]
            decay_rows.append(entry)
    columns = [("fitted on", "fitted on", None), ("features", "features", None)]
    for shape in ("5x5", "6x6", "8x8"):
        columns.append((shape, shape, lambda v: f"{v:.4f}"))
    print(report.markdown_table(decay_rows, columns))

    print("\n### Best rule learned on KR-K@4x4\n")
    best = max(trials[0]["variants"].items(),
               key=lambda kv: kv[1]["transfers"][-1]["accuracy"])
    print(f"(feature set: {best[0]})\n")
    print("```")
    print(best[1]["rule"].rstrip())
    print("```")

    path = report.save("exp004_invariant_transfer", {
        "features": list(FEATURE_NAMES),
        "feature_sets": {k: [FEATURE_NAMES[i] for i in v]
                         for k, v in FEATURE_SETS.items()},
        "max_depth": MAX_DEPTH,
        "sample_cap": SAMPLE_CAP,
        "trials": trials,
        "summary": rows,
    })
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
