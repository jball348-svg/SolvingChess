# Experiment 004 - Do invariants transfer to bigger boards?

## Question

Experiment 005 showed that an *aggregate* law -- the drawn fraction of a whole
universe -- fitted on small boards predicts the real 8x8 board. This experiment
asks the harder version: does a **per-position** rule transfer?

That is a much stronger requirement, and it is the one a proof would actually
need. Knowing that 7.25% of `KR-K@8x8` positions are drawn says nothing about
*which* ones.

## Method

1. Solve a tiny universe exactly. Every state has ground truth.
2. Fit a short decision rule over board-size-independent features
   (`src/solvingchess/features.py`): confinement, opposition, king distance,
   edge and corner distance, mobility, piece en prise, whether a slider cuts
   between the kings.
3. **Predict** the values of universes the rule has never seen -- bigger boards,
   and in one trial a different piece.
4. Score against the majority-class baseline. Most positions in these universes
   are wins, so a rule that beats nothing is worth nothing.

The learner (`src/solvingchess/induction.py`) is hand-rolled and depth-limited
so the output is readable English. If a solved game has a short description, we
want to be able to read it.

## The normalisation experiment

"The defending king is confined" can mean two different things:

* it holds a small **share** of the board (`confinement_bucket`), or
* it holds a small **number of squares**, regardless of board size
  (`confinement_absolute`).

Only one of those can be the size-independent concept, and which one it is
changes what a scaling argument would have to say. Three feature sets are fitted
and transferred separately: `fraction`, `absolute`, and `both`.

## Unseen-value fallback

A rule fitted on a 4x4 board can never have seen "the king reaches more than 16
squares" -- the board only has 16 squares. On 8x8 such rows fall back to an
internal node's majority class, and that fallback can score well by accident.

Every transfer therefore reports the **fallback rate** alongside accuracy. A high
accuracy with a high fallback rate is an artefact, not transfer. This was added
after a first run produced exactly that trap.

## Predictions, stated before the run

1. Accuracy will decay with board size but stay above baseline.
2. `fraction` will transfer better than `absolute`, because it is normalised.
3. Cross-family transfer (rook rule applied to queens) will be much worse than
   same-family transfer.

Prediction 3 was **wrong**, interestingly so. See [results.md](results.md).

## Run

```
python experiments/exp004_invariant_transfer/run.py
```

About four minutes; writes `results/exp004_invariant_transfer.json`.

## Results

See [results.md](results.md).
