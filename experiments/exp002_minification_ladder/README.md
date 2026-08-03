# Experiment 002 - The minification ladder

## Question

Shrink chess until it is exactly solvable, keeping it recognisably chess. How
far up can we climb, and how does the cost grow?

The growth curve is the point. A single solved toy is a curiosity; the rate at
which solving cost rises as pieces go back on is what decides whether "solve the
toy, then scale" is a programme or a wish.

## Two ladders

**Singleton ladder.** Boards of 3x3, 4x4 and 5x5 carrying at most one of each
piece type per side -- `K`, then `K+Q`, then `K+Q+R`, and so on. Each rung is
solved **from its own start position**, so the output is the game-theoretic
value of a complete game, not an endgame table. See
`research/05-minification-programme.md` for the definition of Singleton Chess.

**Endgame ladder.** Classical material signatures solved over every legal
placement. Cheaper, and gives a cleaner read on how state count and drawn
fraction scale at fixed board size.

## Method

Exploration walks the state graph forward from the roots; captures and
promotions are ordinary moves, so one pass covers the whole sub-material tree.
Backward induction then labels every state win/loss/draw from the side to move's
perspective, with unresolved states drawn -- the loopy-game convention.

Singleton rungs are solved on the symmetry quotient (`SymmetryGroup.canonical`),
which is sound because the group is verified in experiment 001. Endgame rungs
are solved raw so their state counts are directly comparable.

A state budget stops a rung rather than exhausting memory. Rungs that exceed it
are reported as such; the budget is recorded in the results JSON.

## Predictions, stated before the run

1. Drawn fraction decreases monotonically as pieces are added at fixed board
   size.
2. Drawn fraction increases monotonically as the board grows at fixed material.

Prediction 2 was **wrong**. See [results.md](results.md).

## Run

```
python experiments/exp002_minification_ladder/run.py --budget 1200000
python experiments/exp002_minification_ladder/run.py --quick    # cheap rungs only
```

About twenty minutes at the default budget, most of it spent on rungs that
exceed it. Writes `results/exp002_minification_ladder.json`.

## Results

See [results.md](results.md).
