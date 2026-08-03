# 07 - Scaling and proof strategy

This note is about the step everything else depends on, and the one most likely
to fail. It should be read as the standing objection to the rest of the
repository.

## The proposal

> Build a small game that is essentially chess. Solve it exactly. Extract a
> mathematical proof of its value. Scale the proof up.

Steps one and two are done, for several universes (note 05). Step three is
partly attackable (note 06, mechanisms 5 and 7). **Step four has no known
mechanism, in any game, ever.**

That is not rhetoric. It is worth spelling out, because the strength of the whole
programme rests on whether step four can be made even slightly plausible.

## Why "solve small, then scale" has never worked

**Checkers.** Endgame databases were built bottom-up from 2 pieces to 10. Each
level was computed, not deduced from the level below. Knowing all 9-piece
positions gives you no shortcut to the 10-piece ones -- you still enumerate. The
final proof is roughly 10^14 computed positions plus a search tree, and it
contains no theorem about checkers.

**Chess endgame tablebases.** Same shape. The 6-piece tables gave no leverage on
the 7-piece tables beyond being needed as their base case. There is no formula
for KRBN vs KQ derived from KRB vs KQ.

**Hex.** The one clean counterexample -- and it cuts the other way. Hex's
ultra-weak solution scales to every board size *because it was never obtained by
solving a small board*. Strategy stealing is a size-independent argument from the
start. The small boards contributed nothing to it.

The pattern is consistent: **arguments that scale are size-independent from
birth; results obtained by exhausting a small instance stay stuck to that
instance.** Nothing in the minification programme, as stated, escapes this.

## Why chess is structurally worse than the games that were solved

Three specific obstacles, each of which can be checked on our own data.

**Board size is not a parameter of chess.** The 8x8 board is not the `n = 8` case
of a family the rules are stated over. Piece movement is defined in board-relative
terms (pawn direction, promotion rank, castling geometry), and several of these
change character as the board shrinks: on a 4x4 board a queen attacks most of the
board from anywhere, and king opposition -- the central invariant of pawn
endgames -- barely has room to exist. Our own results show this biting: `KQ vs K`
on 4x4 mates in 4 moves; on 8x8 it takes 10. The mechanism is not "the same, but
smaller"; it is qualitatively different because the mating net fits differently.

**Material multiplicity is what we removed, and it is where chess's difficulty
lives.** Singleton Chess deletes multiplicity precisely because multiplicity is
expensive. But pawn structure -- the single most theory-laden aspect of chess --
*is* multiplicity. A universe with one pawn a side has no pawn chains, no
majorities, no doubled pawns, no passed-pawn races. Whatever proof works there
has no vocabulary for the thing chess is mostly about. This is the sharpest
statement of the limitation and it is not repairable within the singleton family.

**Value is not monotone in the parameters.** Our data already shows the value
flipping as material is added at fixed board size (`singleton-KQ@4x4` is drawn,
`singleton-KQR@4x4` is a White win) and *not* flipping as the board grows at
fixed material (`singleton-KQ` is drawn on 3x3, 4x4 and 5x5 alike). Any inductive
argument would need a monotone quantity to induct on. We have not found one, and
the first thing we measured suggests the obvious candidates are not it.

## What a scaling argument would actually have to look like

For "prove it small, then scale" to be more than a hope, one of these has to be
true:

**(a) An induction on board size.** A statement `S(f, r)` about the `f x r`
board, plus a proof that `S(f, r)` implies `S(f+1, r)`. The inductive step is the
entire content; the base case is the part we can compute. Note that we have not
identified a single candidate for `S`.

**(b) An induction on material.** A statement about `k` pieces implying the
statement about `k+1`. This is what tablebase construction *looks* like but is
not: adding a piece adds genuinely new geometry, not a recursive instance.

**(c) A size-independent invariant, verified on small cases.** The Hex pattern
inverted -- guess the invariant from small solved data, then prove it holds in
general by an argument that never mentions the board size. **This is the only one
of the three with a plausible workflow**, and it is exactly mechanism 5 of note
06: fit on one rung, *predict* the next rung before solving it, and treat a
successful prediction as evidence the invariant is size-independent.

The programme should be restated around (c). "Solve the toy, then scale the
proof" is the wrong slogan. The right one is:

> Solve enough toys to guess an invariant, then test the guess by prediction, and
> only attempt a proof once the guess has survived rungs it was not fitted to.

That version has a failure mode we can reach this year, which is the main thing
to want from a research plan.

## Falsification criteria

The minification programme should be considered refuted if:

* No cheap feature map predicts values on a rung it was not fitted to, across
  three or more attempts on different universe families;
* The structure gap of note 03 comes out near 1, meaning there is no non-geometric
  redundancy to describe in the first place;
* The drawn fraction and DTM distributions do not follow any clean law across
  board sizes, meaning there is no quantity to induct on.

The third is the cheapest to check and should be done first.

## What is still worth doing even if scaling fails

This should be said, because it is the honest reason to continue.

* **Exactly solved chess-like games are objects nobody has systematically
  catalogued.** The multiplicity ladder appears to be genuinely unexplored. The
  catalogue has value independent of any scaling claim.
* **Phase boundaries are real results.** "In this family, White wins iff material
  density exceeds a threshold" is a theorem about a family of games, even if the
  family does not contain chess.
* **Negative results about compressibility are informative.** If micro-chess
  tables resist compression at 10^5 states, that is meaningful evidence against
  the hidden-structure hypothesis and worth publishing as such.

## Next hypothesis

The single cheapest test of the entire programme: take `KR-K`, solve it on 4x4,
4x5, 4x6, 5x5, 5x6 and 6x6, and plot drawn fraction and maximum DTM against
board dimensions. **If those two curves are not smooth, there is nothing to
induct on and the scaling story should be abandoned in its current form.** This
is one script and a few minutes of compute, and it is the next thing that should
be built.
