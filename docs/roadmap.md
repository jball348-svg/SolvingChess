# Roadmap

Ordered by expected information per unit of effort. Each item names the note it
tests and the artefact it produces.

For the *complete* list of testable ideas -- twenty-five of them, with Python
sketches -- see [`docs/experiment-catalogue.md`](experiment-catalogue.md). This
page is only the ordering.

## Status

| Experiment | State | Verdict |
|---|---|---|
| 001 symmetry compression | **Done** | Symmetry buys exactly `\|G\| <= 16`. Does not scale. |
| 002 minification ladder | **Done** | Six-piece singleton universes solvable; twelve-piece is not, by ~8 orders of magnitude. |
| 003 quotient gap | **Done** | Pawnless gap x1.0-x1.5, pawnful x2.7. Structure is combinatorial, not geometric. |
| 004 invariant transfer | **Done** | Per-position rules beat baseline everywhere but decay with board size. No size-independent rule found. |
| 005 scaling law | **Done** | Drawn fraction of KQ-K is `C/area`; a fit on boards of area 16-30 predicts 8x8 to 1.8%. |
| 006 zugzwang census | Not built | Decides whether ultra-weak routes are worth thinking about. |
| 007 certificate compression | Not built | The real test of "hidden structure". |
| 008 drawn-set decomposition | Not built | Would turn the `1/area` law from observation into mechanism. |
| 009 solver rewrite | Not built | Engineering; unblocks everything else by 2-3 rungs. |

## Where the programme stands

Experiments 004 and 005 together give the sharpest result the repository has:

> **Aggregate laws transfer. Per-position rules do not.**

A power law for the drawn fraction, fitted only on boards of area 16 to 30,
predicts the 8x8 board to within 1.8% for `KQ-K`. But a decision rule fitted on
`KR-K@4x4` decays from 96% accuracy on its own board to 61% on 8x8, and every
feature normalisation we tried decays.

That reshapes the target. The thing to hunt for is a **statistical invariant**
over a whole state space, not a positional one -- and the first candidate is
already in hand: the drawn fraction of `KQ vs K` goes as `1/area`, with the local
exponent sitting on -1.007 by 8x8.

## Next four, in order

### 008 -- Decompose the drawn set

*Turns experiment 005's law into a mechanism. Cheapest item on the list.*

The proposed explanation for `drawn fraction ~ 1/area` is that a `KQ-K` draw
requires the queen to sit in a bounded neighbourhood of the kings -- stalemate or
en prise -- which constrains one of three placements to `O(1)` choices instead of
`O(area)`. Partition the drawn states of `KQ-K` across board sizes into
stalemates, en-prise positions and everything else, and check that the third
bucket grows as `O(area)` rather than `O(area^2)`.

**Why first.** If the mechanism holds, the `1/area` law stops being a curve fit
and becomes a counting argument -- which is the first thing in this repository
that could plausibly be written up as a proof. If it fails, we have a law with no
explanation, which is worth knowing before building anything on top of it.

**Deliverable.** A three-way decomposition of the drawn set per board size, with
fitted growth exponents for each bucket.

### 006 -- Zugzwang census

*Tests `research/06` mechanism 3. One afternoon.*

For every solved universe, count states where the side to move would strictly
prefer to pass. Report the fraction against material and board size.

**Why.** Strategy stealing -- the technique that gives Hex a size-independent
ultra-weak solution -- needs "an extra move never hurts". Zugzwang is exactly the
failure of that premise. If it is rare and confined to characterisable material,
an ultra-weak argument modulo an exceptional set becomes conceivable. If it is
everywhere, that route is closed and we stop thinking about it.

Sketch: `docs/experiment-catalogue.md`, A1.

### 007 -- Certificate compression

*Tests `research/06` mechanism 7, and is the sharpest form of the founding
hypothesis.*

Fit decision lists of increasing size to a solved table and plot description
length against exactness. A knee means a short certificate exists; a straight
line to 100% means the table is being memorised.

Experiment 004 already gives a partial answer -- a 39-node rule reaches 96% on
`KR-K@4x4` -- but 96% is not a certificate. The question is what it costs to
reach 100%, and whether that cost grows with board size.

Sketch: `docs/experiment-catalogue.md`, A2.

### 010 -- Name the KP-K blocks

*The concrete follow-up experiment 003 pointed at.*

`KP-K@4x4` has 3,456 behavioural classes over 18,740 states, a x2.7 improvement
on symmetry -- the only place we found substantial non-geometric structure. Fit
features to predict *block membership* rather than value, and see whether the
blocks correspond to named endgame concepts.

Sketch: `docs/experiment-catalogue.md`, A4.

## Later

### 009 -- Solver rewrite

Dense material indexing, bitboard move generation, numpy-vectorised retrograde
passes. Current throughput is roughly 20,000 states/second; 10^6 is realistic.
Two to three extra rungs, which improves every experiment above.

**Do this only when a specific experiment is blocked on table size.** It is the
most tempting item on the list and the least informative on its own.

### 011 -- Board topology

Cylinders and tori. A cylindrical board has no edges, which removes the mating
net entirely. Experiment 005's proposed mechanism for the `1/area` law is
essentially an edge-and-corner argument, so a torus would falsify or confirm it
sharply -- and it is a much cheaper way to vary board structure than adding
dimensions. Sketch: `docs/experiment-catalogue.md`, D5.

### 012 -- Weak solving

Proof-number search seeded with whatever survives experiment 004, aimed at
`singleton-KQRBNP@5x5`. The only realistic route to the top rung of the
minification ladder, and how Gardner's 5x5 was actually done.

### 013 -- Rule perturbation

Make piece movement sets data rather than constants, then measure whether
chess's structural statistics are unusual among nearby rule sets. The only item
that asks whether chess is special at all, and the refactor that lets the
repository ask comparative questions. Sketch: `docs/experiment-catalogue.md`, D4.

### 014 -- n-dimensional kernel

Gated on 011. See `research/04`: dimension multiplies the symmetry group by a
constant and the state space exponentially, so it is a losing trade for
compression and is only worth building as an extra axis for invariance testing.

## Principles for adding to this list

* An experiment that cannot come out against its hypothesis is not an
  experiment.
* State the prediction before the run, in the note and in the experiment README.
* Report the artefact rate, not just the score. Experiment 004's first run
  produced a transfer number that turned out to be an unseen-value fallback;
  instrumentation caught it before it became a claim.
* Every result goes in `results/` as JSON and in the experiment's `results.md`
  as prose. Never type a number into markdown by hand.
* Negative results get the same prominence as positive ones.
