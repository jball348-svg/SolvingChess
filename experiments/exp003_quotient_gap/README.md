# Experiment 003 - The structure gap

## Question

Experiment 001 measures what board symmetry collapses. This one measures what
*anything* could collapse.

If there is redundancy in chess positions that geometry cannot see, this
experiment finds it. If there is not, the repository's founding hypothesis loses
most of its room.

## Three sizes

For a solved universe we compute:

**raw** -- every reachable state.

**symmetry** -- orbits under the largest board symmetry group that preserves the
game, verified against the solved table before use.

**bisimulation** -- blocks of the coarsest partition that separates
win/draw/loss and is stable under the move relation. Two states land in the same
block exactly when they are indistinguishable by any question about play. **No
sound value-preserving abstraction can be smaller than this**, so it is the
floor: geometric, algebraic, learned, or not yet invented.

The quantity of interest is

```
structure gap = |symmetry orbits| / |bisimulation blocks|
```

* **gap near 1** -- geometry already captures essentially all the redundancy.
  There is nothing left for a cleverer representation to find, and the
  "wrong mathematical space" hypothesis is in trouble.
* **gap large** -- there is real non-geometric structure. Finding a closed-form
  description of the blocks becomes a well-posed research target.

## Prediction, stated before the run

From `research/03-representation-hypothesis.md`:

> The structure gap will be largest exactly where the symmetry group is
> smallest, i.e. in pawnful universes, because the redundancy is still there but
> geometry can no longer see it.

This was **confirmed**. See [results.md](results.md).

## Method

1. Solve the universe over all legal placements.
2. Verify the symmetry group against the solved values; skip the universe if it
   fails.
3. Count orbits.
4. Refine the partition to its bisimulation fixpoint, initialised by win/draw/loss
   and separately by distance to mate.

Partition refinement is the naive `O(rounds * edges)` version. It is fast enough
at these sizes and correspondingly simple to check.

## Run

```
python experiments/exp003_quotient_gap/run.py
```

A few minutes; writes `results/exp003_quotient_gap.json`.

## Results

See [results.md](results.md).
