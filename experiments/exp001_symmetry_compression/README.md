# Experiment 001 - Symmetry compression

## Question

How much of a micro-chess state space does board symmetry actually remove, and
how does that compare to the theoretical maximum?

## Background

A symmetry group `G` acting on states with `v(g . s) = v(s)` lets a solver keep
one representative per orbit instead of every state. The orbit of `s` is
`Orb(s) = {g . s : g in G}` and the reduced space is the quotient `Omega / G`.

By orbit counting, `|Omega / G| >= |Omega| / |G|`, with equality exactly when
every stabiliser is trivial. The **ceiling** on compression is therefore
`1 - 1/|G|`, and the interesting measurement is not compression itself but how
close to that ceiling it lands -- which says whether the group does anything
beyond contributing its own size.

The applicable group differs by universe. A rank mirror is only a game symmetry
when no pawn is present, or when it is paired with a colour swap; diagonal
reflections need both a square board and no pawns. See
`src/solvingchess/symmetry.py`.

## Method

For each universe:

1. enumerate every legal placement of the material signature, both sides to move;
2. build the largest applicable symmetry group and canonicalise each position;
3. count orbits;
4. **solve the universe exactly and verify that every orbit carries a constant
   game value.**

Step 4 is what the original version of this experiment lacked. A compression
figure derived from an unverified group is meaningless.

## Run

```
python experiments/exp001_symmetry_compression/run.py
```

A couple of minutes; writes `results/exp001_symmetry_compression.json`.

## What changed from the original version

The first version enumerated king-versus-king on 4x4 with a hand-written `D4`
and recorded 78 raw positions reducing to 13. Three problems:

* the recorded numbers did not match what the code produced -- it prints 156 and
  21;
* it counted placements rather than states, omitting side to move;
* `D4` was assumed rather than derived. That happens to be safe for two bare
  kings and is wrong for most other material.

The rewrite derives the group per universe, includes side to move, and verifies
against a solved table.

## Results

See [results.md](results.md).
