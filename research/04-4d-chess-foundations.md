# 04 - 4D chess foundations

*Revision of `4d_chess_mathematical_foundations.md`, with the source identified
and the claims separated into "established", "ours" and "conjecture".*

## The source

Kaufmann, D. (2026). "A Mathematical Framework for Four-Dimensional Chess:
Extending Game Mechanics Through Higher-Dimensional Geometry." *AppliedMath*
6(3), 48. [doi:10.3390/appliedmath6030048](https://doi.org/10.3390/appliedmath6030048)

What the paper does: defines chess on the discrete hypercubic lattice
`{1,...,8}^4`, formalises piece movement as displacement sets in `Z^4`, defines
adjacency by the Chebyshev metric, analyses the resulting move graphs for rook,
bishop, knight, queen and king, and ships an engine plus a visualiser that
renders all 64 `(z,w)`-slices simultaneously.

What the paper does **not** do, and should not be read as doing: claim that four
dimensions make chess easier, or offer any reduction of the 2D game.

## The framework

The board is `B = {1,...,8}^4 subset Z^4`; a square is `(x, y, z, w)`.

A piece is a **displacement set** `D subset Z^4`, and its move graph is
`G_D = (B, E)` with `E = {(u, v) : v - u in D, v in B}`.

**Rook.** `D_R = {a e_i : a != 0, i in 1..4}` -- movement along one axis.
The rook graph is the Cartesian product `K_8 x K_8 x K_8 x K_8` of complete
graphs, since a rook move changes exactly one coordinate and can change it to
any value. (Products of complete graphs are Hamming graphs; here `H(4, 8)`.)

**King.** `D_K = {d in Z^4 : 0 < max_i |d_i| <= 1}` -- the Chebyshev ball of
radius 1, which is the **strong product** `P_8 boxtimes P_8 boxtimes P_8
boxtimes P_8` of path graphs. A king has up to `3^4 - 1 = 80` neighbours, versus
8 in two dimensions.

**Bishop.** Ambiguous in 4D and the choice matters. "Change exactly two
coordinates by equal magnitude" and "change any subset of coordinates by equal
magnitude" give different graphs with different connectivity. The colour-parity
invariant that confines a 2D bishop to one colour generalises to a parity
invariant on coordinate sums, but which one depends on this choice.

**Knight.** `D_N = {d : multiset of |d_i| is {2, 1, 0, 0}}`, giving
`4 x 3 x 2 x 2 = ` 48 moves at an interior square.

## Worked example

On a 4x4x4x4 board, from `(1,1,1,1)`:

* rook: `3 x 4 = 12` destinations (three per axis, four axes);
* king: `2^4 - 1 = 15` destinations at this corner (each coordinate may stay or
  increase), versus 80 at an interior square;
* knight: the corner is heavily restricted, which is exactly the "edge effect"
  that makes corner mating patterns work in 2D and is worth checking survives.

The point of the example: the *shape* of edge effects, not just their size, is
what generalises.

## What this is actually good for

The honest assessment, which the original version of this note did not give.

**It is a good source of clean graph-theoretic objects.** Hamming graphs and
strong products of paths have known spectra, diameters and automorphism groups.
If we want to ask "what does the spectrum of a move graph tell you about the
game played on it", 4D gives a family of exactly-known cases to calibrate
against. That is real value.

**It is a good stress test for representation code.** Our `Geometry` class is 2D;
a genuinely dimension-agnostic rewrite would be forced to separate "board
topology" from "piece semantics", which is good hygiene regardless.

**It is not a route to solving chess, and the arithmetic is not close.** The
empty-board symmetry group of the 4-cube is the hyperoctahedral group `B_4` of
signed permutations, order `2^4 x 4! = 384`. That is 24 times bigger than the
best symmetry group available in 2D. From exp001 we know precisely what a
symmetry group of order `|G|` buys: a factor of `|G|`. Meanwhile the state space
of a 4D board grows from `64` squares to `4096`, so the same material sits in a
space larger by a factor of `64^k` for `k` pieces. **The symmetry gain is a
constant; the state-space cost is exponential in pieces.** Going up in dimension
loses badly, and it loses for a reason we have measured rather than guessed.

## The one version of the 4D idea that could work

Not "solve chess in 4D". Rather: **use dimension as a parameter and look for
what is invariant across it.**

If a structural quantity -- the fraction of drawn positions in `KR-K`, the
scaling exponent of distance-to-mate against board diameter, the structure gap
of note 03 -- takes the same form in 2D, 3D and 4D, that is evidence it is a
property of *chess as a rule system* rather than of the 8x8 board. Such
quantities are exactly the candidates for a proof that survives rescaling, which
is what note 07 says the whole programme needs.

That reframes 4D from "a bigger board where things might be easier" to "an extra
axis of variation along which to test invariance". The second is a legitimate
experimental design; the first is not.

## Limitations

* No 4D code exists in this repository. `Geometry` is rectangular and 2D, and
  making it `n`-dimensional is a real refactor (rays, pawn direction, symmetry
  group construction, and the state encoding all assume two axes).
* Pawns in 4D are undefined in an interesting way: "forward" needs a
  distinguished axis, which breaks the symmetry between the four coordinates.
  Any 4D result about pawnless material may not transfer.
* The claim that hypercube symmetry "creates possible state reductions" -- as
  the original note put it -- is now quantified and is disappointing: a factor of
  384 against a state space multiplied by `64^k`.

## Next hypothesis

Before writing any 4D code, run the cheap version of the invariance test in 2D
alone. Take `KR-K` and `KQ-K` across board sizes 4x4, 5x5, 6x6, 4x6, 4x8 and
measure the drawn fraction and maximum distance to mate. **If those quantities
do not already follow a clean law across 2D rectangles, they will not do so
across dimensions, and the 4D refactor is not worth the cost.** This is a cheap
experiment we can run now and it gates all further 4D work.
