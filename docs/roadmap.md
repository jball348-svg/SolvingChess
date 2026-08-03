# Roadmap

Ordered by expected information per unit of effort. Each item names the note it
tests and the artefact it produces.

## Status

| Experiment | State | Verdict |
|---|---|---|
| 001 symmetry compression | **Done** | Symmetry buys exactly `\|G\| <= 16`. Does not scale. |
| 002 minification ladder | **Done** | Six-piece singleton universes solvable; twelve-piece is not, by ~8 orders of magnitude. |
| 003 quotient gap | **Done** | See `experiments/exp003_quotient_gap/results.md`. |
| 004 invariant transfer | Not built | The highest-value unbuilt experiment. |
| 005 board-size scaling law | Not built | Cheapest test of the whole programme. |
| 006 zugzwang census | Not built | Decides whether ultra-weak routes are worth thinking about. |
| 007 certificate compression | Not built | The real test of "hidden structure". |
| 008 solver rewrite | Not built | Engineering; unblocks everything else by 2-3 rungs. |

## Next four, in order

### 005 -- Board-size scaling law

*Tests note 07. One script, minutes of compute.*

Solve `KR-K` and `KQ-K` on 4x4, 4x5, 4x6, 5x5, 5x6, 6x6. Plot drawn fraction and
maximum DTM against board dimensions.

**Why first.** Every scaling story in this repository assumes there is a smooth
quantity to induct on. Nobody has checked. If these curves are not smooth, the
"prove it small and scale it" framing should be abandoned in its current form,
and that changes what everything else is for. It is also the cheapest thing on
the list.

**Deliverable.** `results/exp005_scaling_law.json` plus a fitted exponent, or a
statement that no clean law exists.

### 004 -- Invariant transfer

*Tests note 03's H3 and note 06's mechanism 5.*

Fit a cheap feature map (king distance, opposition parity, rook alignment, edge
proximity, mobility counts) to predict exact values on `KR-K@4x4`. Then
**predict** `KR-K@5x5` and `KR-K@4x6` before solving them, and score the
prediction.

**Why it matters more than it looks.** This is the only experiment that produces
evidence about *transfer* rather than about one universe. A feature set that
predicts a rung it was not fitted to is the first real evidence that anything
here scales. A feature set that does not is a clean negative result.

**Deliverable.** Held-out accuracy per universe, and the feature set itself in a
form that can be carried up the ladder.

### 006 -- Zugzwang census

*Tests note 06's mechanism 3.*

For every solved universe, count states where the side to move would strictly
prefer to pass. Report the fraction, and its dependence on material and board
size.

**Why.** Strategy stealing -- the technique that gives Hex a size-independent
ultra-weak solution -- needs "an extra move never hurts". Zugzwang is exactly the
failure of that premise. If zugzwang is rare and confined to characterisable
material, a strategy-stealing argument modulo an exceptional set becomes
conceivable. If it is everywhere, the ultra-weak route is closed and we should
stop thinking about it.

**Deliverable.** A zugzwang frequency table across the ladder.

### 007 -- Certificate compression

*Tests note 06's mechanism 7, and is the sharpest form of the founding
hypothesis.*

Take the `KR-K@4x4` table and fit a minimal decision list over simple predicates.
Report exact accuracy and description length in bits, against the entropy of the
raw table.

**Why.** A solved game whose table compresses to a page is *understood*. One that
does not is merely *computed*. Both prior solved games produced oracles rather
than theorems. If micro-chess tables resist compression at 10^5 states, that is
substantive evidence against hidden structure, at a size where we can still see
it clearly.

## Later

### 008 -- Solver rewrite

Dense material indexing, bitboard move generation, numpy-vectorised retrograde
passes. Current throughput is roughly 20,000 states/second in pure Python; 10^6
is realistic. That is two to three extra rungs, which improves every experiment
above.

**Do this only when a specific experiment is blocked on table size.** It is the
most tempting item on the list and the least informative on its own.

### 009 -- Weak solving

Proof-number search seeded with whatever invariants survive 004, aimed at
`singleton-KQRBNP@5x5`. This is how Gardner's 5x5 was actually solved, and it is
the only realistic route to the top rung of the ladder. Depends on 004
producing something.

### 010 -- Decomposable universes

Construct universes forced to decompose into independent components (pawn chains
separated by blocked files) and test whether the game value equals the
combinatorial-game-theory sum of the parts. Tests note 06's mechanism 6.

### 011 -- n-dimensional kernel

Generalise `Geometry` beyond two dimensions. **Gated on 005**: if structural
quantities do not follow clean laws across 2D rectangles, they will not across
dimensions, and this refactor is not worth its cost. See note 04.

## Principles for adding to this list

* An experiment that cannot come out against its hypothesis is not an
  experiment.
* State the prediction before the run, in the note.
* Every result goes in `results/` as JSON and in the experiment's `results.md`
  as prose. Never type a number into markdown by hand -- that is how the
  original experiment ended up recording figures its own code did not produce.
* Negative results get the same prominence as positive ones.
