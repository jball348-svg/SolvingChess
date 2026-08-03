# Experiment 002 - Results

Run on 2026-08-03, state budget 1,200,000. Raw data:
`results/exp002_minification_ladder.json`.

## Singleton ladder

Solved from the start position, on the symmetry quotient. Value is from White's
perspective at move one; DTM in plies.

| universe | pieces | placements | orbit-states | value (White to move) | DTM | time | status |
|---|---|---|---|---|---|---|---|
| singleton-K@3x3 | 2 | 72 | 5 | draw | - | 0.0s | solved |
| singleton-K@4x4 | 2 | 240 | 21 | draw | - | 0.0s | solved |
| singleton-K@5x5 | 2 | 600 | 63 | draw | - | 0.0s | solved |
| singleton-KQ@3x3 | 4 | 3,024 | 66 | draw | - | 0.0s | solved |
| singleton-KQ@4x4 | 4 | 43,680 | 1,805 | draw | - | 0.2s | solved |
| singleton-KQ@5x5 | 4 | 303,600 | 16,296 | draw | - | 3.3s | solved |
| **singleton-KQR@4x4** | **6** | **5,765,760** | **169,223** | **win** | **11** | **31.0s** | **solved** |
| singleton-KQR@5x5 | 6 | 127,512,000 | - | - | - | 161.5s | over budget |
| singleton-KQRB@4x4 | 8 | 518,918,400 | - | - | - | 172.5s | over budget |
| singleton-KQRBNP@5x5 | 12 | 2,490,952,020,480,000 | - | - | - | 48.6s | over budget |

## Endgame ladder

All legal placements, solved raw (no symmetry reduction) so counts are directly
comparable.

| universe | pieces | states | edges | draws | max DTM (plies) | time |
|---|---|---|---|---|---|---|
| K-K@4x4 | 2 | 312 | 1,152 | 100.0% | - | 0.0s |
| K-K@5x5 | 2 | 912 | 4,320 | 100.0% | - | 0.0s |
| KN-K@4x4 | 3 | 4,280 | 18,832 | 100.0% | - | 0.1s |
| KB-K@4x4 | 3 | 4,180 | 18,536 | 100.0% | - | 0.1s |
| KR-K@4x4 | 3 | 3,808 | 17,576 | 24.3% | 14 | 0.1s |
| KQ-K@4x4 | 3 | 3,308 | 13,984 | 31.9% | 8 | 0.1s |
| KP-K@4x4 | 3 | 18,740 | 81,884 | 63.7% | 23 | 0.3s |
| KN-K@5x5 | 3 | 20,288 | 118,272 | 100.0% | - | 0.4s |
| KB-K@5x5 | 3 | 19,824 | 119,888 | 100.0% | - | 0.4s |
| KR-K@5x5 | 3 | 18,440 | 121,416 | 16.9% | 20 | 0.4s |
| KQ-K@5x5 | 3 | 16,376 | 109,288 | 20.7% | 12 | 0.4s |
| KP-K@5x5 | 3 | 92,416 | 559,482 | 59.4% | 35 | 1.8s |
| KR-KR@4x4 | 4 | 42,536 | 225,088 | 49.1% | 17 | 1.1s |
| KQ-KQ@4x4 | 4 | 28,992 | 142,504 | 39.3% | 11 | 0.9s |
| KN-KN@4x4 | 4 | 54,600 | 273,536 | 99.9% | 1 | 1.2s |
| KP-KP@4x4 | 4 | 1,022,828 | 5,098,824 | 56.3% | 52 | 21.7s |
| KRN-K@4x4 | 4 | 50,784 | 242,488 | 23.9% | 14 | 1.1s |
| KQR-K@4x4 | 4 | 41,484 | 150,800 | 10.3% | 14 | 0.9s |

## Findings

### 1. `singleton-KQR@4x4` is a forced win for White in 6 moves

King, queen and rook a side on a 4x4 board, every piece moving exactly as it
does in chess, promotion available, checkmate and stalemate intact -- solved
exactly from the start position. 169,223 symmetry classes; 31 seconds.

This is a complete solved game with a definite answer, not an endgame table, and
it is small enough to inspect by hand.

### 2. The draw/win transition is driven by material, not board size

`singleton-KQ` is drawn on 3x3, 4x4 **and** 5x5. Board area does not move it.
Adding one rook a side on 4x4 flips it to a White win.

On a cramped board the first player's tempo converts once there is enough force
to convert it, and area is not the controlling variable. This is a phase
boundary and locating it precisely is the obvious next step.

### 3. Prediction 2 was wrong, and interestingly so

We predicted that drawn fraction would **increase** with board size at fixed
material. It decreases:

| universe | 4x4 | 5x5 |
|---|---|---|
| KR-K | 24.3% | **16.9%** |
| KQ-K | 31.9% | **20.7%** |
| KN-K | 100% | 100% |
| KP-K | 63.7% | **59.4%** |

The intuition behind the prediction -- more space means more escape -- had it
backwards. On a 4x4 board the defending king is never far from the attacking
piece, so it captures it or forces stalemate far more often. Cramped boards
favour the *defender*, not the attacker. Maximum DTM rises with board size at the
same time (KR-K: 14 to 20 plies), which is the compensating effect: wins get
rarer but longer.

This matters for the programme. Both quantities move smoothly and in opposite
directions, which is mildly encouraging for the existence of a law to induct on
(note 07) -- but the direction of one of them was guessed wrong on the first try,
which is a fair warning about reasoning from intuition here.

### 4. Growth is essentially linear in placement count

Fitting `states ~ placements^b` across 25 solved rungs gives **b = 0.968**.

There is no sub-exponential magic. The reachable state count tracks the raw
combinatorial placement count almost exactly, with the legality and reachability
constraints contributing only a constant factor. Every structural reduction
available -- symmetry, sub-material sharing, reachability -- amounts to a
constant.

### 5. Full Singleton Chess 5x5 is out of reach by about eight orders of magnitude

`singleton-KQRBNP@5x5` has 2.49 x 10^15 piece placements. The fitted law projects
**~6.8 x 10^14 reachable states**.

For scale: that is comparable to the *computed* portion of the checkers proof, a
multi-year distributed effort, and about four billion times the largest universe
solved here. Symmetry divides it by at most 2, because it has pawns.

So the answer to "make it small enough and it becomes solvable" is **yes**, and
the answer to "is full Singleton Chess small enough" is **no**. Gardner's larger
5x5 game was weakly solved with modest hardware precisely because a *weak*
solution does not enumerate the state space; a strong solution of Singleton 5x5
is a bigger object than the weak solution of the bigger game containing it.

### 6. Two knights cannot mate, except when they can

`KN-KN@4x4` is 99.9% drawn with a maximum DTM of 1 ply -- the only wins are
immediate mates, which exist because the defender's *own* knight can block its
king's escape. A pleasing confirmation that the move generator handles
self-blocking correctly, and a reminder that "insufficient material" is a
statement about forcing, not about possibility.

## Limitations

* Singleton rungs are counted in symmetry classes and endgame rungs in raw
  states. Do not compare the two columns directly.
* The growth fit mixes both ladders and both counting conventions. It is a
  first-order estimate; treat 0.968 as "essentially 1", not as a precise
  exponent.
* No fifty-move rule. `KP-KP@4x4` already reaches DTM 52 plies (26 moves), which
  is within the fifty-move limit, but the margin is no longer large. Any claim
  about a longer win must be re-checked against FIDE rules.
* The back-rank ordering (Gardner's `R N B Q K`, centred) is a choice. On a 4x4
  board `R Q K` and `Q R K` are different games and we have not measured whether
  the value depends on it. It probably does, which weakens "essentially the same
  game".

## Next

* Fill in the (board area, piece count) grid to locate the draw/win boundary
  found in Finding 2.
* Experiment 005 in `docs/roadmap.md`: solve `KR-K` across six board shapes and
  check whether Finding 3's curves are smooth enough to induct on.
* Weak rather than strong solving is the only realistic route past six pieces.
  See `research/05-minification-programme.md`, phase 4.
