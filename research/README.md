# Research corpus

Reference notes for the project. Each note is meant to be readable on its own
and to end with something falsifiable.

House rules for anything added here:

1. State the mathematical claim precisely enough that it could be wrong.
2. Give a small worked example.
3. Point at the experiment that tests it, or say that none exists yet.
4. Record the limitations honestly, including the ones that hurt.
5. Distinguish **established** results (with a citation) from **our own
   measurements** (with a results file) from **conjecture** (labelled as such).

## Notes

| # | Note | What it is for |
|---|------|----------------|
| 00 | [Glossary and notation](00-glossary.md) | Shared vocabulary so notes do not drift |
| 01 | [What "solving chess" means](01-what-solving-chess-means.md) | Ultra-weak / weak / strong, and which one we are chasing |
| 02 | [State space and prior art](02-state-space-and-prior-art.md) | The numbers everyone quotes, checked; what has actually been solved |
| 03 | [The representation hypothesis](03-representation-hypothesis.md) | "Chess is hard because we describe it badly" -- sharpened into tests |
| 04 | [4D chess foundations](04-4d-chess-foundations.md) | The hypercube lattice framework and what it is genuinely good for |
| 05 | [The minification programme](05-minification-programme.md) | Singleton Chess: shrink the game until it is exactly solvable |
| 06 | [Candidate mechanisms](06-candidate-mechanisms.md) | Ten routes to a solution, each with an experiment attached |
| 07 | [Scaling and proof strategy](07-scaling-and-proof-strategy.md) | The hard question: what survives when the board grows |

## Status of the central claims

| Claim | Status |
|---|---|
| Board symmetry compresses micro-chess state spaces | **Measured** -- `experiments/exp001_symmetry_compression` |
| Symmetry is far from the best possible value-preserving compression | **Measured** -- `experiments/exp003_quotient_gap` |
| Small one-of-each-piece universes are exactly solvable | **Measured** -- `experiments/exp002_minification_ladder` |
| Full Singleton Chess 5x5 is within reach of this codebase | **False** -- projection in exp002 |
| A proof about a small board lifts to 8x8 | **Open, and the main risk to the whole programme** -- note 07 |
| 4D representations reveal structure hidden in 2D chess | **Untested conjecture** -- no experiment yet |
