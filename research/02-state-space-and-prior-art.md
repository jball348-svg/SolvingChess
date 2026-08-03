# 02 - State space and prior art

The numbers that get quoted in this area are often quoted loosely. This note
pins down what is actually known, because the minification programme (note 05)
is only interesting relative to an accurate picture of what has already been
done.

## The size of chess

| Quantity | Value | Note |
|---|---|---|
| Shannon number (game-tree size) | ~10^120 | Shannon's 1950 back-of-envelope: 30 legal moves, 40 moves each. An estimate of the *tree*, not the *state space*, and it is routinely misquoted as the latter. |
| Legal positions | ~10^44 | Tromp's computation gives an upper bound of about 4.8 x 10^44 with a rigorous confidence interval. |
| 7-piece tablebase | >5 x 10^14 positions | Lomonosov, 2012. Complete. |
| 8-piece tablebase | in progress | Partial coverage as of 2026 (Bourzutschky and collaborators). Not complete. |

Two things follow immediately.

**The tree is not the target.** Solving is a statement about the *state graph*,
not the game tree; the gap between 10^120 and 10^44 is 76 orders of magnitude of
transposition. Anyone claiming a "reduction" should say which of the two numbers
they are reducing.

**Even the state graph is not the target for a weak solution.** A weak solution
covers only positions reachable under its own strategy. This is why checkers,
with roughly 5 x 10^20 positions, was weakly solved by computing on the order of
10^14 of them.

## What has actually been solved

| Game | Level | Result | Year |
|---|---|---|---|
| Checkers | Weak | Draw | 2007 (Schaeffer et al.) |
| Losing Chess (Antichess) | Weak | White wins, 1.e3 | 2016 (Watkins) |
| Gardner's 5x5 minichess | Weak | Draw | 2013 (Mhalla and Prost) |
| Chess, <= 7 pieces | Strong | Complete tables | 2012 |
| Chess | -- | Open | -- |

Three of these deserve a closer look, because each is a template the
minification programme could follow or fail to follow.

### Checkers

Schaeffer's team combined a strong solution of the endgame (all positions with
<= 10 pieces, about 4 x 10^13 of them) with a forward proof-tree search from the
opening, meeting in the middle. The lesson is structural: **the endgame was
solved by exhaustion and the opening by search, and the two were glued
together.** No compressed description of checkers was discovered along the way.
The proof is a large data object, not a theorem.

### Losing Chess

Watkins weakly solved a *chess variant on a full 8x8 board* -- the same
geometry, the same piece set, a different objective. It is the strongest
existing evidence that "chess-sized" games are not automatically beyond reach.
The win is comparatively shallow because the forced-capture rule prunes the tree
brutally: the branching factor collapses. That is the caveat. Losing Chess is
solvable because its rules make it narrow, not because 8x8 is tractable.

### Gardner's minichess

5x5, full back rank (R N B Q K), five pawns a side, roughly 9 x 10^18 legal
positions -- comparable to checkers. Weakly solved as a **draw**, and notably
with modest computing power, by exploiting the narrowness of the drawing line
rather than by brute enumeration.

This is the single most important prior result for this repository, because it
is exactly the "shrink the board" idea, executed, at the largest board size where
it has succeeded. Two consequences:

1. **5x5 with full material is already at the frontier.** Singleton Chess 5x5
   (note 05) is strictly smaller than Gardner's, so it is plausibly reachable --
   but not by naive exhaustion, and not by this codebase in its current form
   (see the projection in `experiments/exp002_minification_ladder`).
2. **The Gardner result did not produce a theorem.** It produced oracles.
   Minification delivered a *solution*; it did not deliver *understanding*. That
   is the outcome the scaling question in note 07 has to confront.

## Smaller minichess universes

Boards of 3x3, 3x4, 4x4 and 4x5 with reduced material have been solved
repeatedly in the literature and are the natural regression tests for any new
solver. Our own known-answer tests use full-board endgames instead, because
those have unambiguous published values:

* KQ vs K on 8x8: maximum distance to mate is **10 moves**.
* KR vs K on 8x8: maximum distance to mate is **16 moves**.

Our solver reproduces both (`tests/test_solvingchess.py`). Any structural claim
made in this repository rests on that check.

## Limitations of this note

The 8-piece tablebase status changes; treat the row above as "as of 2026" and
re-check before quoting it. The legal-position count is an upper bound from a
sampling argument, not an exact enumeration -- the exact number is not known.

## Next hypothesis

Both weak solutions above (checkers, Gardner) produced *data*, not *theory*. The
testable question this raises, and the one exp003 is built to answer: when a
micro-universe is solved exactly, **how far can the resulting table be
compressed without losing any answer it gives?** If solved games are
fundamentally incompressible, the "hidden structure" hypothesis is in trouble,
and we should be able to see that at 10^4 states rather than 10^44.

## References

* Shannon, C. (1950). "Programming a Computer for Playing Chess."
  *Philosophical Magazine* 41(314).
* Tromp, J. [Number of legal chess positions](https://github.com/tromp/ChessPositionRanking).
* Schaeffer, J. et al. (2007). "Checkers Is Solved." *Science* 317(5844).
* Watkins, M. (2016). [*Losing Chess: 1. e3 wins for White*](https://magma.maths.usyd.edu.au/~watkins/LOSING_CHESS/LCsolved.pdf).
* Mhalla, M. and Prost, F. (2013). [*Gardner's Minichess Variant is Solved*](https://arxiv.org/abs/1307.7118).
* [Lomonosov 7-piece tablebases](https://tb7.chessok.com/).
