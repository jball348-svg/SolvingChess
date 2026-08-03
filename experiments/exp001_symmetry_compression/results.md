# Experiment 001 - Results

Run on 2026-08-03. Raw data: `results/exp001_symmetry_compression.json`.
Every group below was verified against a solved table: **zero orbits with
inconsistent game values**.

| universe | \|G\| | raw states | orbits | compression | ceiling | efficiency |
|---|---|---|---|---|---|---|
| K-K@4x4 | 16 | 312 | 21 | 93.27% | 93.75% | 92.86% |
| K-K@5x5 | 16 | 912 | 63 | 93.09% | 93.75% | 90.48% |
| K-K@4x6 | 8 | 832 | 104 | 87.50% | 87.50% | 100.00% |
| KR-K@4x4 | 8 | 3,496 | 443 | 87.33% | 87.50% | 98.65% |
| KQ-K@4x4 | 8 | 2,996 | 378 | 87.38% | 87.50% | 99.07% |
| KN-K@4x4 | 8 | 3,968 | 502 | 87.35% | 87.50% | 98.80% |
| KR-KR@4x4 | 16 | 35,248 | 2,206 | 93.74% | 93.75% | 99.86% |
| KP-K@4x4 | 2 | 4,208 | 2,104 | 50.00% | 50.00% | 100.00% |
| KP-KP@4x4 | 4 | 52,624 | 13,156 | 75.00% | 75.00% | 100.00% |
| KQ-KQ@4x4 | 16 | 22,688 | 1,419 | 93.75% | 93.75% | 99.93% |
| singleton-KQ@4x4 | 16 | 22,688 | 1,419 | 93.75% | 93.75% | 99.93% |
| singleton-KQ@5x5 | 16 | 228,368 | 14,287 | 93.74% | 93.75% | 99.90% |

*efficiency* = achieved reduction factor divided by `|G|`.

## Reading the table

**Symmetry delivers its group order and nothing more.** Efficiency is 90-100%
everywhere, and above four pieces it is essentially 100%. Almost every position
has a trivial stabiliser, so almost every orbit has the full `|G|` elements. This
is the orbit-counting lemma behaving exactly as it must; it is not a discovery
about chess.

The consequence is worth being blunt about. Symmetry buys a **constant factor of
at most 16**. Against a state space that grows like `P(nsq, pieces)` a constant
factor is not progress. Dividing 10^44 by 16 gives 10^43.

**One pawn destroys most of the group.** `KR-K@4x4` has `|G| = 8` and compresses
87%. `KP-K@4x4` has `|G| = 2` and compresses 50%. Pawn motion is
direction-dependent, so rank mirrors and diagonal reflections stop being game
symmetries. Any minified universe that keeps pawns -- and a pawnless universe is
barely chess -- forfeits most of its geometric symmetry.

**The colour swap is worth as much as the whole dihedral group.** `KR-K`
(asymmetric material) gets `|G| = 8`; `KR-KR` (symmetric) gets `|G| = 16`. The
factor of two from exchanging colours equals the factor from all four rotations.
Colour symmetry is not geometry, and it is the cheapest real compression
available.

**Rectangular boards lose the diagonal.** `K-K@4x6` gets `|G| = 8` against
`K-K@4x4`'s 16, because transposition is not a map of a 4x6 board to itself.

## Interpretation

This experiment closes one question and opens a better one.

Closed: *does board symmetry compress chess state spaces?* Yes, by exactly
`|G|`, verified. That is a fact about group actions, not about chess, and it does
not scale.

Opened: *is there redundancy that geometry cannot see?* Symmetry is one
value-preserving abstraction among many. Experiment 003 computes the coarsest
one that exists -- the bisimulation quotient -- and reports the ratio between the
two. That ratio, not the numbers above, is the real test of the "wrong
mathematical space" hypothesis.

## Limitations

* All universes have at most four pieces, because enumerating every placement
  costs `P(nsq, pieces)`. Six-piece universes are measured on their reachable
  set in experiment 002 instead.
* Verification samples up to 20,000 states per universe rather than all of them
  for the larger tables.
* The counts are of *legal placements*, which is a superset of the *reachable*
  states from any particular start position. The two differ and should not be
  compared across experiments without care.

## Next

* Experiment 003 -- the structure gap, which decides whether the founding
  hypothesis has room left.
* Not yet built: measure the stabiliser distribution directly. Positions with
  non-trivial stabilisers are exactly the symmetric ones (kings on a diagonal,
  material mirrored), and whether that set has any strategic significance is an
  open and rather appealing question.
