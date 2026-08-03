# SolvingChess

A research corpus and experimentation base for mathematical approaches to
solving chess.

Two directions are pursued in parallel:

* **Up** -- higher-dimensional geometry, symmetry groups, quotient spaces. Does
  chess have structure that a different representation would expose?
* **Down** -- *minification*. Shrink the board and allow at most one piece of
  each type per side, until the game is small enough to solve exactly, and see
  what the exact solution tells you.

The second direction is where the results are. The first is where the original
hypothesis is, and it is being tested rather than assumed.

## What is here

```
research/       The corpus: eight notes, each ending in something falsifiable
src/solvingchess/   A parameterised micro-chess kernel and exact solver
experiments/    Numbered experiments, each with a runnable script and a results file
results/        Machine-readable output from every run
tests/          Correctness tests, including known-answer checks against published theory
docs/           Repository review and roadmap
notebooks/      Exploratory notebooks
```

## Results so far

**A law fitted on tiny boards predicts the real 8x8 board.** The drawn fraction
of KQ vs K, fitted as a power law on boards of area 16 to 30 only, predicts 8x8
to within **1.8%**. The exponent settles on **-1.007**: drawn fraction is
inversely proportional to board area. That is a size-independent statement about
a chess endgame, obtained from boards a quarter of the size.

**But per-position rules do not transfer.** A readable 39-node rule scores 96% on
`KR-K@4x4` and decays to 61% on 8x8. Every feature normalisation decays. Read
with the result above: **aggregate laws transfer, per-position rules do not** --
which moves the target from positional invariants to statistical ones.

**`singleton-KQR@4x4` is a forced win for White in 6 moves.** King, queen and
rook a side on a 4x4 board -- every piece moving exactly as it does in chess --
solved exactly, from the start position, whole game. 169,223 symmetry classes.

**Board symmetry buys a constant factor and nothing more.** Across twelve
universes, symmetry reduction achieves 90-100% of its theoretical ceiling
`1 - 1/|G|`, with `|G| <= 16`. A single pawn drops the group from order 8 to
order 2.

**And after symmetry, pawnless micro-chess has almost nothing left.** The
bisimulation quotient -- the floor for *any* value-preserving abstraction -- is
only 1.0x to 1.5x below the symmetry quotient. The exception is pawn positions,
at 2.7x, which is where the remaining structure lives.

**Full Singleton Chess 5x5 is out of reach, by about eight orders of magnitude.**
2.49 x 10^15 piece placements; measured growth projects ~7 x 10^14 states.

Details: [001 symmetry](experiments/exp001_symmetry_compression/results.md) *
[002 minification](experiments/exp002_minification_ladder/results.md) *
[003 structure gap](experiments/exp003_quotient_gap/results.md) *
[004 invariant transfer](experiments/exp004_invariant_transfer/results.md) *
[005 scaling law](experiments/exp005_scaling_law/results.md)

## Quick start

```bash
pip install -r requirements.txt

make test          # includes known-answer checks against published tablebase results
make exp002        # the minification ladder
```

```python
from solvingchess.variants import singleton_variant
from solvingchess.symmetry import SymmetryGroup
from solvingchess.solver import solve_variant

variant = singleton_variant(4, 4, types=(0, 1, 2))    # K, Q, R per side
group = SymmetryGroup(variant.rules)
solution = solve_variant(variant, canonical=group.canonical)

print(variant.rules.render(variant.start))
print(solution.value_of(solution.roots[0]), solution.dtm_of(solution.roots[0]))
```

## Correctness

Structural claims are only worth as much as the solver underneath them, so the
solver is pinned to published results. On a full 8x8 board it reproduces:

* KQ vs K -- maximum distance to mate **10 moves**;
* KR vs K -- maximum distance to mate **16 moves**.

Both are in `tests/test_solvingchess.py` and run in `make test`.

## Where to start reading

1. [research/01](research/01-what-solving-chess-means.md) -- what "solving
   chess" actually means, and which level is being chased.
2. [research/05](research/05-minification-programme.md) -- Singleton Chess and
   the ladder.
3. [research/07](research/07-scaling-and-proof-strategy.md) -- the standing
   objection to the whole programme. Read this before getting excited.
4. [research/06](research/06-candidate-mechanisms.md) -- ten routes to a
   solution, ranked, each with an experiment attached.
5. [docs/roadmap.md](docs/roadmap.md) -- what to build next and in what order.
6. [docs/experiment-catalogue.md](docs/experiment-catalogue.md) -- twenty-five
   testable ideas with Python sketches for each.

## Central question

Can chess be solved by discovering its underlying mathematical structure rather
than only searching its game tree? So far the evidence gathered here is
unfavourable to the strong form of that hypothesis and the repository says so.
The point is to find out, not to be right.
