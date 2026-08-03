# Experiment 005 - Is there a scaling law to induct on?

## Question

`research/07-scaling-and-proof-strategy.md` argues that "solve it small, then
scale the proof" needs a quantity that behaves smoothly as the universe grows.
Nobody had checked whether one exists.

Does any structural quantity of a solved universe follow a law across board
sizes -- and if so, does a law fitted on small boards **predict** a board it has
never seen?

## Method

Solve `KR-K` and `KQ-K` on nine board shapes from 4x4 to 8x8. Measure the drawn
fraction, the maximum distance to mate and the mean distance to mate over won
positions.

Then split the boards:

* **fit set** -- 4x4, 4x5, 5x4, 4x6, 5x5, 5x6 (area 16 to 30);
* **held out** -- 6x6, 7x7 and 8x8, including the real chessboard.

Fit `quantity ~ a * driver^b` on the fit set only, predict the held-out boards,
and report the relative error. Nothing from the held-out set touches the fit.

A global fit can hide drift, so the **local exponent** between each consecutive
pair of boards is also reported. If the local exponent settles on a value as the
board grows, that value -- not the fitted average -- is the asymptotic law, and a
clean one is a candidate for something provable.

`KR-KR` is included as a secondary family with no holdout, because equal
material is a different regime and the contrast matters.

## Predictions, stated before the run

1. Drawn fraction falls smoothly with board area (this direction was already
   corrected once -- experiment 002 refuted the opposite guess).
2. Maximum DTM rises smoothly with board size.
3. No prediction was made about the *exponent*. That turned out to be the
   interesting part.

## Run

```
python experiments/exp005_scaling_law/run.py
```

About two minutes; writes `results/exp005_scaling_law.json`.

## Internal consistency check

`KR-K@4x5` and `KR-K@5x4` are the same universe transposed, and every reported
statistic matches to the digit. That is a free correctness check on the geometry
code and it passes.

## Results

See [results.md](results.md).
