# 00 - Glossary and notation

Shared vocabulary. If a note uses a term differently, the note is wrong.

## The game

**Universe.** A board geometry plus a material signature plus a rule set. `KR-K
on 4x4` is a universe; so is standard chess. In code: `solvingchess.rules.Rules`.

**Geometry.** A rectangular board with `files` columns and `ranks` rows. Square
`s = rank * files + file`. Rank 0 is White's home rank; White pawns move towards
increasing rank.

**Material signature.** An ordered list of `(colour, piece_type)` slots, written
`KQ-KR` for "White has king and queen, Black has king and rook". The list length
never changes during a game: a captured piece takes an off-board value and a
promoting pawn changes the type stored in its own slot.

**State.** A material placement plus the side to move. Written `s`. The set of
all reachable states is `Omega`.

**Move relation.** `s -> t` when `t` follows from `s` by one legal move. The
state graph is `G = (Omega, E)`.

**Value.** `v(s)` in `{WIN, DRAW, LOSS}`, **always from the perspective of the
side to move at `s`**. This convention matters: it is what makes the colour-swap
symmetry value-preserving.

**DTM.** Distance to mate, counted in plies. `-1` for drawn states.

## Solving

**Ultra-weak solution.** The value of the initial position, with no strategy.

**Weak solution.** The value of the initial position plus a strategy that
achieves it from the initial position against any defence.

**Strong solution.** `v(s)` for every legal `s`. An endgame tablebase is a
strong solution of its material signature.

## Structure

**Symmetry group `G`.** A group acting on states such that `v(g . s) = v(s)` for
all `g`. For a pawnless universe on a square board this is the dihedral group
`D4` of order 8, optionally doubled by a colour swap. For a universe containing
a pawn it collapses to the file mirror alone, order 2. See
`solvingchess.symmetry`.

**Orbit.** `Orb(s) = {g . s : g in G}`. **Canonical form**: the least encoding in
the orbit, used as the orbit's name.

**Quotient.** `Omega / G`, one representative per orbit. Searching the quotient
is sound exactly when `G` is a symmetry group in the sense above -- which is why
`SymmetryGroup.verify` re-checks it against a solved table rather than trusting
the derivation.

**Bisimulation.** An equivalence `~` on states such that equivalent states have
equal value and matching successor blocks. The coarsest such `~` gives the
smallest graph that answers every question about play that the original answers.
Its size is a hard floor for any sound abstraction, symmetry included.

**Structure gap.** `|Omega / G| / |Omega / ~|`. How much redundancy exists that
board geometry cannot see. Measured in `experiments/exp003_quotient_gap`.

## Minification

**Singleton Chess.** This project's construction: shrink the board *and* allow
at most one piece of each type per side. Written `singleton-KQR@5x5` for "one
king, queen and rook a side, on a 5x5 board". Full Singleton Chess is
`singleton-KQRBNP@5x5`: Gardner's 5x5 minichess with four of five pawns removed
from each side.

**Ladder.** An ordered family of universes differing by one controlled step
(one more piece, or one more file), used to measure how a quantity grows rather
than to compute it once.

## Conventions used by the solver

* Infinite play is a draw. The backward induction labels a state drawn exactly
  when neither side can force resolution, which is the standard loopy-game
  convention and lets us keep repetition history out of the state.
* No castling, no en passant, no fifty-move rule. Double pawn steps are off by
  default (which is what removes en passant). See the module docstring of
  `solvingchess.rules` for why.
