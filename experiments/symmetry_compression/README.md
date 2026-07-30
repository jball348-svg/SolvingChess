# Experiment 001: Symmetry Compression in a Tiny Chess Universe

## Research question

Can mathematical representations of chess states remove redundant complexity by identifying equivalent states under symmetry transformations?

Traditional chess engines treat every legal board position as a unique state. This experiment tests the hypothesis that some of this complexity may come from the coordinate representation itself rather than the underlying game structure.

## Why representation matters

A state is represented as:

\[
S
\]

A symmetry group:

\[
G
\]

can transform that state into equivalent states, forming an orbit:

\[
Orb(S)=\{gS:g\in G\}
\]

Instead of searching every state:

\[
S_1,S_2,S_3,...
\]

we can search equivalence classes:

\[
[S]
\]

This is a quotient-space idea: many apparently different states may represent the same underlying mathematical situation.

## Relationship to SolvingChess

SolvingChess investigates whether chess may be difficult partly because it is represented in the wrong mathematical space. Before attempting large-scale solutions, we test whether alternative mathematical structures can compress toy versions of chess.

This experiment uses two kings on a 4x4 board as a minimal universe where the effect of symmetry can be measured exactly.

## Why symmetry reduction matters

Symmetry appears throughout mathematics, physics and computer science. If states related by a symmetry transformation have identical structural meaning, treating them separately introduces redundancy.

The dihedral symmetry group of a square, D4, provides eight geometric transformations. This experiment measures how much of the state space can be collapsed using these transformations.

## Limitations

This is not a chess solver. It is a proof-of-concept demonstrating that mathematical representation choices can change the apparent size of a search space.
