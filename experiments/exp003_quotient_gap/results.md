# Experiment 003 - Results

Run on 2026-08-03. Raw data: `results/exp003_quotient_gap.json`.
Every symmetry group was verified against the solved table before use.

| universe | raw | symmetry orbits | bisim (WDL) | bisim (DTM) | symmetry compression | bisim compression | gap (sym / bisim) |
|---|---|---|---|---|---|---|---|
| K-K@4x4 | 312 | 21 | 1 | 1 | 93.27% | 99.68% | x21.0 |
| KR-K@4x4 | 3,808 | 485 | 410 | 410 | 87.26% | 89.23% | x1.2 |
| KQ-K@4x4 | 3,308 | 420 | 273 | 273 | 87.30% | 91.75% | x1.5 |
| KN-K@4x4 | 4,280 | 544 | 495 | 495 | 87.29% | 88.43% | x1.1 |
| KB-K@4x4 | 4,180 | 529 | 473 | 473 | 87.34% | 88.68% | x1.1 |
| **KP-K@4x4** | 18,740 | 9,370 | 3,456 | 3,456 | 50.00% | **81.56%** | **x2.7** |
| KR-KR@4x4 | 42,536 | 2,669 | 2,559 | 2,559 | 93.73% | 93.98% | x1.0 |
| KQ-K@5x5 | 16,376 | 2,081 | 1,702 | 1,702 | 87.29% | 89.61% | x1.2 |
| KR-K@5x5 | 18,440 | 2,346 | 2,162 | 2,162 | 87.28% | 88.28% | x1.1 |

Orbit counts here are over the *reachable* solved state set, which includes
sub-material after captures. They therefore differ slightly from experiment 001,
which counts orbits over legal placements of the full signature only.

## Findings

### 1. The structure gap is small -- for pawnless material, almost nothing is left

Excluding the degenerate `K-K` row, gaps run from **x1.0 to x1.5** on pawnless
universes. `KR-KR@4x4` is x1.0 to two significant figures: the bisimulation
quotient is 2,559 blocks against 2,669 orbits, a 4% improvement over symmetry.

This is a strong negative result for the founding hypothesis in its general
form. After board symmetry, there is **essentially no value-preserving
redundancy left to find** in pawnless micro-chess. Not "none we have found" --
none that exists, because the bisimulation quotient is the floor for every
possible sound abstraction.

Whatever a cleverer representation of pawnless chess could buy, it is bounded
above by 50%, and measured at 0-30%.

### 2. Pawns are where the structure hides

`KP-K@4x4` has a gap of **x2.7**, by far the largest non-degenerate value.
Symmetry manages 50% compression -- its ceiling, since a pawn leaves only the
file mirror. Bisimulation reaches **81.6%**.

So there is genuine redundancy in pawn positions that no rotation or reflection
can see, and it is roughly three times what geometry offers.

**The prediction stated in `research/03` before the run was that the gap would
be largest exactly where the symmetry group is smallest. It is.** This is the
first confirmed prediction in the repository, and it points somewhere specific:
the structure worth looking for is combinatorial and pawn-related, not geometric.

That is also, awkwardly, the direction the minification programme cuts away.
Singleton Chess keeps one pawn a side, which preserves the *mechanism* but
removes pawn structure -- the thing this result suggests carries the redundancy.

### 3. Distance-to-mate is free

`bisim(WDL)` and `bisim(DTM)` are identical in every row. Refining by win/draw/loss
and then closing under move-stability already separates distance to mate -- which
is what it should do, since DTM is determined recursively by successor blocks.

The practical consequence is worth noting: the coarsest value-preserving
abstraction of these universes loses nothing about *how* to play, only about
which specific position you are in. There is no cheaper "value only, no strategy"
abstraction to be had.

### 4. Symmetry is close to optimal, which is not the good news it sounds like

Read Findings 1 and experiment 001 together and the picture is unified:

* symmetry achieves 90-100% of its own ceiling `1 - 1/|G|` (exp001);
* that ceiling is within 0-30% of the *absolute* floor for pawnless material
  (this experiment).

So board symmetry is a nearly optimal abstraction. It is also worth a constant
factor of at most 16 against a state space growing like `P(nsq, k)`. Both
statements are true and the second dominates. "Nearly optimal" and "nearly
useless" are not in tension here; the ceiling itself is low.

## Interpretation

The repository was founded on the idea that chess may be hard because of how it
is represented. This experiment is the first direct test of the strongest form of
that idea, and the result is:

> For pawnless micro-chess, no representation can do much better than rotating
> the board. For pawnful micro-chess, something can do about three times better,
> and we do not know what it is.

The second sentence is where the remaining research value is. The concrete next
question is no longer "is there structure" but "what are the `KP-K` bisimulation
blocks, in words?" -- 3,456 blocks over 18,740 states is a small enough object to
characterise by hand or by rule induction.

If those blocks turn out to correspond to something nameable -- opposition,
key squares, the square of the pawn -- that is the representation hypothesis
producing an actual result, on the one family where the measurement says to look.

## Limitations

* All universes have at most four pieces. The gap's behaviour as material grows
  is unknown, and the pawnful result rests on two rows.
* The bisimulation quotient is computed **from the values**. It bounds what is
  achievable; it cannot be used to avoid solving. A useful abstraction must be
  recognisable from the position alone -- see `research/03`, H2.
* Bisimulation here is the standard successor-set version. Coarser notions
  (simulation-based, or quotients preserving only the value of the root) would
  give smaller numbers and are not computed.
* `K-K@4x4` collapses to a single block because every state is drawn. It is
  included as a sanity check, not as a data point.

## Next

* Characterise the `KP-K@4x4` blocks. This is the highest-value follow-up in the
  repository and it is a small, concrete, finite task.
* Re-run on `KP-KP@4x4` (1,022,828 states) to see whether the pawnful gap grows
  with pawn count. If it does, the case for looking at pawn structure rather than
  geometry gets much stronger.
* Feed the block structure into experiment 004 (invariant transfer) as candidate
  features.
