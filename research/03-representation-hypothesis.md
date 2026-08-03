# 03 - The representation hypothesis

*Supersedes `wrong_mathematical_space_hypothesis.md`.*

## The claim, as usually stated

> Chess may be hard because we represent it badly. In some other coordinate
> system its structure would be visible and the problem would shrink.

As stated this is not testable. "Better representation" has no definition,
"structure" has no definition, and there is no measurement that could come out
against it. This note replaces it with three claims that can each be false.

## Sharpening it

Fix a universe with state space `Omega` and value function `v : Omega -> {W, D,
L}`. A **sound abstraction** is a map `f : Omega -> X` such that `v` factors
through `f` -- that is, `f(s) = f(t)` implies `v(s) = v(t)`, and `f` respects the
move relation well enough to answer questions about play.

The representation hypothesis then splits into:

**H1 (compression).** There exist sound abstractions with `|X|` much smaller
than `|Omega|`.

**H2 (description).** At least one such abstraction has a *short description* --
short in the Kolmogorov sense, i.e. a rule you could write down, not a lookup
table.

**H3 (transfer).** The short description is stable as the universe grows: the
same rule works on 4x4, 5x5, 6x6 and 8x8.

These are wildly different in difficulty. H1 is easy and already confirmed. H2
is the real question. H3 is the entire programme, and note 07 argues it is where
the risk lives.

## H1 is true and it is not enough

Board symmetry is a sound abstraction. `experiments/exp001_symmetry_compression`
measures it exactly:

| universe | \|G\| | raw states | orbits | compression | ceiling |
|---|---|---|---|---|---|
| K-K@4x4 | 16 | 312 | 21 | 93.27% | 93.75% |
| KR-K@4x4 | 8 | 3,496 | 443 | 87.33% | 87.50% |
| KR-KR@4x4 | 16 | 35,248 | 2,206 | 93.74% | 93.75% |
| KP-K@4x4 | 2 | 4,208 | 2,104 | 50.00% | 50.00% |
| KP-KP@4x4 | 4 | 52,624 | 13,156 | 75.00% | 75.00% |
| singleton-KQ@5x5 | 16 | 228,368 | 14,287 | 93.74% | 93.75% |

Read the last two columns together. Compression essentially *equals* the
group-order ceiling `1 - 1/|G|` in every case -- the measured efficiency is
90-100%. That is not a discovery about chess; it is the orbit-counting lemma
doing its job. Almost every position has a trivial stabiliser, so almost every
orbit has the full `|G|` elements.

Which means:

**Symmetry buys a constant factor of at most 16, and it buys essentially exactly
that.** Against a state space growing like `P(nsq, pieces)` a constant factor is
noise. Reducing 10^44 by 16 leaves 10^43.

Two further observations from the same table, both of which matter for the
minification programme:

* **Pawns destroy the group.** One pawn drops the applicable group from order 8
  to order 2 and compression from 87% to 50%, because pawn motion is
  direction-dependent: rank mirrors and diagonal reflections stop being game
  symmetries. Any minified universe that keeps pawns -- and a universe without
  pawns is barely chess -- forfeits most of its geometric symmetry.
* **The colour swap is worth as much as the entire dihedral group.** Going from
  `KR-K` (asymmetric material, `|G| = 8`) to `KR-KR` (symmetric, `|G| = 16`)
  doubles the group. Colour symmetry is not geometry, and it is the cheapest
  real compression available.

## H2 is the open question, and it is measurable

If symmetry only ever buys `|G|`, the interesting question is what a *maximal*
sound abstraction buys. That has a precise answer: the coarsest **bisimulation**
that separates values. It is the smallest graph that answers every question
about play that the original answers, so no sound abstraction of any kind --
geometric, algebraic, learned, or not yet invented -- can beat it.

`experiments/exp003_quotient_gap` computes both quantities on solved
micro-universes and reports the ratio

```
structure gap = |Omega / G| / |Omega / ~|
```

Interpretation:

* **gap ~ 1** -- geometry already captures essentially all the redundancy. The
  representation hypothesis has little room left, and effort should move to note
  06's non-representational mechanisms.
* **gap >> 1** -- there is genuine non-geometric redundancy in chess positions.
  H1 is confirmed far beyond symmetry, and the target becomes H2: find a short
  description of the bisimulation blocks. That is a concrete question about a
  concrete finite object, not a slogan.

This is the experiment that decides whether the founding hypothesis of this
repository is worth pursuing. **It has now been run**, and the answer is
uncomfortable:

| universe | symmetry orbits | bisimulation blocks | gap |
|---|---|---|---|
| KR-KR@4x4 | 2,669 | 2,559 | x1.0 |
| KN-K@4x4 | 544 | 495 | x1.1 |
| KR-K@5x5 | 2,346 | 2,162 | x1.1 |
| KQ-K@4x4 | 420 | 273 | x1.5 |
| **KP-K@4x4** | **9,370** | **3,456** | **x2.7** |

For pawnless material the gap is between x1.0 and x1.5. Since the bisimulation
quotient is the floor for *every possible* sound abstraction, this says that
after rotating the board there is essentially nothing left for any cleverer
representation to find. H1 is confirmed and exhausted; H2 has almost no room in
pawnless universes.

The exception is the interesting part. `KP-K` has a gap of x2.7 -- symmetry gets
50%, bisimulation gets 81.6%. There *is* substantial redundancy in pawn positions
that geometry cannot see. That was the prediction stated at the bottom of this
note before the run, and it held.

The conclusion is a redirection rather than a refutation: **the structure worth
hunting for is combinatorial and pawn-related, not geometric.** Full results and
the awkward corollary for the minification programme are in
`experiments/exp003_quotient_gap/results.md`.

## What "wrong space" would have to mean to be useful

Note that even a large structure gap does not by itself help. The bisimulation
quotient is computed *from the solved table*; you cannot use it to avoid solving.
For a representation to reduce the cost of solving, its blocks must be
recognisable **without knowing the values** -- from the position alone, in time
polynomial in the board size.

So H2's real form is:

> There is a polynomial-time computable feature map `phi` such that `phi(s) =
> phi(t)` implies `v(s) = v(t)`, with far fewer classes than orbits.

This is falsifiable on solved data: take the bisimulation blocks, and ask whether
they are predictable from cheap positional features. If a small feature set
separates blocks near-perfectly on 4x4 and 5x5, that is a candidate `phi` to
carry up the ladder. If nothing beats memorisation, the hypothesis fails at
exactly the size where we can still see it failing.

## Limitations

* Everything here is measured on universes with at most six pieces. The
  behaviour of the structure gap as material grows is unknown and is the first
  thing to extend.
* The bisimulation quotient preserves *value*. A quotient preserving distance to
  mate is much finer, and `exp003` reports both -- the DTM figure is the honest
  one if you care about producing a strategy rather than a value.
* Nothing here says anything about the tree-vs-graph distinction. All the
  compression discussed is on the state graph; transposition savings are already
  baked in and should not be double counted.

## Next hypothesis

The prediction stated here before `exp003` ran was: **the structure gap will be
largest exactly where the symmetry group is smallest**, i.e. in pawnful
universes, because the redundancy is still there but geometry can no longer see
it. It held -- `KP-K@4x4` has the smallest group (order 2) and the largest gap
(x2.7).

The successor hypothesis, again stated in advance: **the `KP-K@4x4` bisimulation
blocks correspond to named endgame concepts** -- opposition, key squares, the
square of the pawn. 3,456 blocks over 18,740 states is small enough to
characterise directly. If the blocks are nameable, the representation hypothesis
has produced its first real result, on the one family where the measurement says
to look. If they are not nameable, H2 fails where it had its best chance.
