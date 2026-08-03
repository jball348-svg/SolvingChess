# 01 - What "solving chess" means

Almost every disagreement about whether chess can be solved is really a
disagreement about which of three different problems is under discussion. This
note fixes the terms and states which one this project is aimed at.

## Zermelo's theorem, and what it does not give you

Chess is a finite, two-player, zero-sum, perfect-information game (finite once
the fifty-move and threefold-repetition rules are read as automatic rather than
claimable). Zermelo's theorem therefore already guarantees that exactly one of
the following is true:

* White can force a win,
* Black can force a win,
* both sides can force at least a draw.

So chess **has** a value. The open problem is not existence -- it is
*identification*, and identification is the part that costs 10^40-ish units of
something.

This matters for how we phrase hypotheses. "Does chess have a mathematical
structure that determines its value?" is not a research question; the answer is
trivially yes. The research question is whether that structure has a
**description shorter than the game tree**.

## The three levels

Following the standard taxonomy (Allis, 1994):

### Ultra-weak

Determine the value of the initial position, without producing a strategy.

Ultra-weak solutions are the ones that come from pure mathematics rather than
computation -- strategy stealing, pairing arguments, parity invariants. Hex is
the canonical example: strategy stealing proves the first player wins on any
board size in a few lines, and it produces no winning move whatsoever.

**This is the level where an argument from structure could plausibly beat
search**, and it is the only level at which a "proof then scale" programme has
historical precedent. It is also the level at which chess is most resistant:
chess has draws, so the strategy-stealing argument does not even get started
(see note 06, mechanism 3).

### Weak

Determine the value of the initial position *and* provide a strategy that
achieves it from the initial position against every defence.

Checkers was weakly solved this way (Schaeffer et al., 2007). Losing Chess was
weakly solved this way (Watkins, 2016). Gardner's 5x5 minichess was weakly
solved this way (Mhalla and Prost, 2013). A weak solution only has to cover
positions reachable under its own strategy, which is dramatically fewer than
all of them.

### Strong

Determine the value of every legal position.

Endgame tablebases are strong solutions restricted to a material signature.
Everything this repository computes exactly is a strong solution of a small
universe -- `solve_material` labels every legal placement, not just the ones on
a principal variation.

## Which one we are chasing

| Level | Chess | This project |
|---|---|---|
| Ultra-weak | Open | The only level where "find the structure" could plausibly win. No credible attack yet; note 06 lists the candidates. |
| Weak | Open | The realistic target for **minified** universes. exp002 weakly *and* strongly solves several. |
| Strong | Open beyond 7 pieces | What we compute for micro-universes, because it is what makes structural measurement possible. |

The reason we compute *strong* solutions of tiny universes even though the
long-run target is an *ultra-weak* argument about big ones: you cannot look for
an invariant without ground truth to test it against. A strong solution is a
labelled dataset over a complete state space. That is the substrate every
structural experiment in this repository runs on.

## Two things that are not solving chess

**Playing chess very well.** A 4000-Elo engine is not a partial solution. It
provides no bound on the value of the initial position.

**Estimating the value of the initial position.** The near-universal belief that
chess is a draw is evidence, not a proof, and no amount of self-play sharpens it
into one.

## Solver conventions in this repository

Our solver uses the *loopy game* convention: a state is drawn exactly when
neither side can force resolution. This is equivalent to "infinite play is a
draw" and it is what allows the state to omit move history entirely.

This differs from tournament chess in one respect worth being explicit about: a
position that is theoretically won but where the win requires more than fifty
moves without capture or pawn move is a win for us and a draw under FIDE rules.
For the micro-universes here the longest win found so far is 32 plies, so the
distinction has not yet bitten -- but it will if the ladder is climbed, and any
result quoted as "the value of X" should carry this footnote.

## Next hypothesis

The ultra-weak level is where the leverage is, and chess's draw-richness is
exactly what blocks the classical ultra-weak techniques. Hypothesis worth
testing on solved micro-universes: **in universes we can solve completely, is
the drawn region describable by a short certificate** (a small set of
predicates closed under moves) even when the won region is not? If yes, the
target shifts from "prove chess is a draw" to "find the invariant that certifies
the drawn region", which is a materially different and more tractable object.
This is testable today against exp002's solved tables and has no experiment
attached yet.

## References

* Allis, L. V. (1994). *Searching for Solutions in Games and Artificial
  Intelligence*. PhD thesis, University of Limburg. (Source of the
  ultra-weak/weak/strong taxonomy.)
* Schaeffer, J. et al. (2007). "Checkers Is Solved." *Science* 317(5844).
* Watkins, M. (2016). [*Losing Chess: 1. e3 wins for
  White*](https://magma.maths.usyd.edu.au/~watkins/LOSING_CHESS/LCsolved.pdf).
* Mhalla, M. and Prost, F. (2013). [*Gardner's Minichess Variant is
  Solved*](https://arxiv.org/abs/1307.7118).
