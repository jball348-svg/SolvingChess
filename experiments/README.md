# Experiments

Each experiment is a directory `expNNN_short_name/` containing:

* `run.py` -- runnable from the repository root, takes a state budget, writes
  `results/expNNN_*.json` and prints a markdown table;
* `README.md` -- the question, the method, and the prediction stated *before*
  the run;
* `results.md` -- the pasted table, findings, limitations, and what comes next.

## Index

| # | Experiment | Tests | Verdict |
|---|---|---|---|
| [001](exp001_symmetry_compression/) | Symmetry compression | `research/03` H1 | Symmetry buys exactly `\|G\| <= 16` and 90-100% of its ceiling. Does not scale. |
| [002](exp002_minification_ladder/) | Minification ladder | `research/05` | `singleton-KQR@4x4` is a White win in 6 moves. Full Singleton 5x5 is ~10^15 states -- out of reach. |
| [003](exp003_quotient_gap/) | Structure gap | `research/03` H2 | Pawnless gap x1.0-x1.5; pawnful gap x2.7. Structure is combinatorial, not geometric. |

Planned experiments and their ordering are in [`docs/roadmap.md`](../docs/roadmap.md).

## Rules

**Never type a number into markdown.** Paste the table the script prints. The
repository once recorded a result its own code did not produce; every experiment
now emits JSON alongside prose so the two cannot drift.

**State the prediction before the run**, in the experiment README and in the
research note it tests. A hypothesis written after seeing the data is not a
hypothesis. Experiment 002's second prediction was wrong and says so; experiment
003's was right and says so.

**Report negative results with the same prominence as positive ones.**
Experiment 001 came out against the repository's founding hypothesis. That is
the standard, not an exception.
