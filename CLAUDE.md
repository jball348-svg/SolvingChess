# CLAUDE.md

Working instructions live in [AGENTS.md](AGENTS.md). Read that first; this file
adds only the orientation.

## What this project is

SolvingChess investigates whether chess has mathematical structure that makes it
tractable by means other than brute-force search. It is a research corpus plus an
experimentation base, not an engine.

Two directions run in parallel:

* **Minification** -- shrink the board and allow at most one piece of each type
  per side, until the game is exactly solvable. This is where the results are.
  See `research/05-minification-programme.md`.
* **Representation** -- symmetry, quotient spaces, higher-dimensional
  embeddings. This is the original hypothesis, now being measured rather than
  assumed. See `research/03-representation-hypothesis.md`.

## Where things are

| Path | Contents |
|---|---|
| `research/` | The corpus. Start at `research/README.md`. |
| `src/solvingchess/` | Micro-chess kernel: geometry, rules, symmetry, exact solver, quotients. |
| `experiments/` | Numbered experiments, each runnable and each with a results file. |
| `results/` | Machine-readable output. Never hand-edit. |
| `docs/roadmap.md` | What to build next, in order. |
| `docs/2026-08-review.md` | Audit of the repository's earlier state. |

## What has been measured

* Board symmetry compresses micro-chess by exactly its group order, at most 16,
  and a single pawn cuts that to 2.
* After symmetry, pawnless micro-chess has almost no value-preserving redundancy
  left -- the bisimulation floor is within 0-30% of the symmetry quotient.
* Pawnful positions are different: symmetry gets 50%, the floor is 82%. The
  remaining structure is combinatorial, not geometric.
* `singleton-KQR@4x4` -- king, queen and rook a side on 4x4 -- is a forced win
  for White in 6 moves.
* Full Singleton Chess on 5x5 projects to ~10^15 states. Out of reach.

The evidence so far runs *against* the strong form of the founding hypothesis,
and the repository says so in its own results files. Keep it that way.

## Ground rules

* Never write a number into markdown by hand; paste what the script prints.
* Never quote compression from an unverified symmetry group.
* Keep the 8x8 known-answer tests green (KQ vs K in 10, KR vs K in 16).
* State predictions before runs.
* Do not add castling, en passant or the fifty-move rule without reading the
  `rules.py` module docstring first.
