# 05 - The minification programme

The 4D work asks what happens when chess gets bigger. This note asks the
opposite question, and it is the one with a realistic chance of producing
something.

> Shrink the board and allow at most one piece of each type per side. Solve the
> result exactly. Then find out what, if anything, the solution tells you about
> chess.

## Singleton Chess

**Definition.** A *singleton universe* is a rectangular board of `f` files and
`r` ranks together with a piece-type set `T subset {K, Q, R, B, N, P}` containing
`K`, where each side has **exactly one** piece of each type in `T`. Non-king,
non-pawn pieces occupy the home rank in Gardner order (`R N B Q K`, centred);
the pawn stands in front of its king. The two sides are reflections of each
other, so the kings face down a common file, as in standard chess.

Written `singleton-<types>@<files>x<ranks>`, e.g. `singleton-KQR@4x4`.

**The maximal member** is `singleton-KQRBNP@5x5`:

```
5  r n b q k
4  . . . . p
3  . . . . .
2  p . . . P      (White pawn in front of White's king)
1  R N B Q K
   a b c d e
```

That is exactly **Gardner's 5x5 minichess with four of the five pawns removed
from each side**. Every piece type is present with its full movement geometry;
promotion still exists; checkmate, stalemate and zugzwang all still exist. What
is gone is multiplicity.

**Why this is the right cut.** There are two ways to make chess smaller, and
they are not equally good.

* *Remove piece types.* Cheap, but it deletes the thing being studied. A game
  without knights has no non-sliding piece; a game without pawns has no
  irreversibility, no promotion and no zugzwang worth the name. Endgame
  tablebases are this cut, and nobody claims KRK teaches you chess.
* *Remove multiplicity.* Keeps every movement rule, every interaction, and the
  entire tactical vocabulary -- forks, pins, discovered attacks, promotion races
  -- while cutting the combinatorics hard, because state count scales as
  `P(nsq, pieces)`.

Minification via multiplicity is the sharper instrument, and as far as we can
tell it is not a cut the literature has systematically studied. Reduced-material
minichess exists; a *systematic ladder in the multiplicity parameter* does not.

## What we have solved

From `experiments/exp002_minification_ladder`, all values are from the start
position with White to move, computed on the symmetry quotient:

| universe | pieces | orbit-states | value | DTM |
|---|---|---|---|---|
| singleton-K@3x3 | 2 | 5 | draw | -- |
| singleton-K@4x4 | 2 | 21 | draw | -- |
| singleton-K@5x5 | 2 | 63 | draw | -- |
| singleton-KQ@3x3 | 4 | 66 | draw | -- |
| singleton-KQ@4x4 | 4 | 1,805 | draw | -- |
| singleton-KQ@5x5 | 4 | 16,296 | draw | -- |
| singleton-KQR@4x4 | 6 | 169,223 | **White wins** | 11 plies |
| singleton-KQR@5x5 | 6 | over budget | -- | -- |
| singleton-KQRB@4x4 | 8 | over budget | -- | -- |
| singleton-KQRBNP@5x5 | 12 | far over budget | -- | -- |

Two findings worth stating plainly.

**Finding 1: `singleton-KQR@4x4` is a forced win for White in 6 moves.**

A complete, recognisably chess-like game -- king, queen and rook a side, all
moving exactly as they do in chess, on a 4x4 board -- is a first-player win, and
the win is short. This is a genuine solved game with a genuine answer, and the
whole state graph is small enough to inspect by hand.

**Finding 2: the transition from draw to first-player win happens at a specific
rung.** `singleton-KQ` is drawn on 3x3, 4x4 *and* 5x5 -- board size does not
change it. Adding one rook each on 4x4 flips it to a White win. The controlling
variable is material density, not board area: on a cramped board the extra piece
gives the first player enough force to convert the tempo.

This is the kind of statement minification is *for*. It is exact, it is about a
whole game rather than an endgame, and it identifies a phase boundary.

## Where it stops, and why

The scaling is brutal and worth confronting directly. State count grows roughly
as the number of piece placements, `P(nsq, k)`:

| universe | squares | pieces | placements |
|---|---|---|---|
| singleton-KQ@4x4 | 16 | 4 | 43,680 |
| singleton-KQR@4x4 | 16 | 6 | 5,765,760 |
| singleton-KQR@5x5 | 25 | 6 | 127,512,000 |
| singleton-KQRB@4x4 | 16 | 8 | 518,918,400 |
| **singleton-KQRBNP@5x5** | **25** | **12** | **2.49 x 10^15** |

Fitting `states ~ placements^b` across 25 solved rungs gives `b = 0.968` -- state
count tracks raw placement count almost exactly, so reachability and legality buy
a constant, not an order. The fit projects **6.8 x 10^14 reachable states** for
full Singleton Chess 5x5, and symmetry divides that by 2, not 16, because it has
pawns (note 03).

For reference, that is the same order of magnitude as the *computed* portion of
the checkers proof -- a multi-year distributed effort -- and about four billion
times the largest universe solved here.

So: **the answer to "make it small enough and it becomes solvable" is yes, and
the answer to "is full Singleton Chess small enough" is no**, by about eight
orders of magnitude with the current pure-Python explicit-graph solver, and by
several even with a good one. Gardner's full 5x5 was weakly solved with modest
hardware (note 02) precisely because a *weak* solution avoids enumerating the
state space; a strong solution of Singleton 5x5 is a much larger object than the
weak solution of the bigger game that contains it.

That is not a reason to abandon the programme. It is a reason to be precise
about which rung is the target and which level of solution is being claimed.

## The programme

**Phase 1 -- climb the ladder (partly done).** Solve every singleton universe
that fits in memory, record value, DTM distribution, drawn fraction and solving
cost. Done up to six pieces.

**Phase 2 -- find the phase boundary.** We have one data point on the draw/win
transition. Fill in the grid: vary board size and material independently and map
where the value flips. A clean boundary -- something like "White wins iff
material density exceeds a threshold" -- would be a real, if modest, theorem
about a family of chess-like games.

**Phase 3 -- look for a transferable invariant.** For each solved universe,
search for a cheaply computable function that predicts the value. Test it on the
next rung *before* solving that rung. A feature that predicts values on rungs it
was not fitted to is the first genuine evidence that anything here scales. This
is the experiment that has not been built yet and is the most valuable next
piece of work.

**Phase 4 -- weak rather than strong.** Switch from exhaustive solving to
proof-number search with the invariants from phase 3 as ordering heuristics, and
attempt a *weak* solution of `singleton-KQRBNP@5x5`. This is where the ladder
could actually reach the top rung, and it is how Gardner's 5x5 was done.

## Limitations

* Our solver strongly solves from a root; a weak solution needs different
  machinery (phase 4) and none of it is written.
* No castling, no en passant, no fifty-move rule. On these boards castling is
  meaningless and double pawn steps are conventionally absent, but the fifty-move
  omission means a "win" here can be a FIDE draw. No case has arisen yet -- the
  longest win found is 32 plies -- but it must be checked before any published
  claim.
* The Gardner-order back rank is a choice. On a 4x4 board `R Q K` versus
  `Q R K` are different games and we have not measured whether the value depends
  on it. It probably does, which weakens "essentially the same game".
* **The deepest limitation is that a solved toy is not a proof about chess.**
  Note 07 is about that, and it should be read before anyone gets excited by
  Finding 1.

## Next hypothesis

The hypothesis stated before the first run was: *the drawn fraction decreases
monotonically as pieces are added at fixed board size, and increases
monotonically as the board grows at fixed material.*

The first half held. **The second half was wrong** -- drawn fraction *falls* as
the board grows (`KR-K`: 24.3% on 4x4, 16.9% on 5x5), because a cramped board
lets the defending king reach the attacking piece. Cramped boards favour the
defender. Maximum DTM rises at the same time, so wins become rarer and longer
together.

Both quantities still move smoothly and monotonically, which is what a scaling
argument would need. The revised hypothesis, again stated in advance: **drawn
fraction decreases and maximum DTM increases with board area, both smoothly
enough to fit, for every fixed pawnless material signature.** Experiment 005 in
`docs/roadmap.md` tests this across six board shapes, and it is the cheapest
falsification test of the whole programme.
