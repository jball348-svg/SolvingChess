# CLAUDE.md

## Project Context

You are working on SolvingChess, a mathematical research project investigating whether chess can be understood or solved through deeper structures.

The project explores ideas from:

- higher dimensional geometry
- combinatorics
- algebra
- graph theory
- topology
- symmetry groups
- complex systems

## Current Mathematical Foundation

The primary starting point is 4D chess mathematics.

A four-dimensional chess board can be represented as:

B = {1,...,8}^4

Each square becomes a coordinate:

(x,y,z,w)

Piece movements become displacement sets in Z^4.

Example:

A rook moves along one axis:

(±a,0,0,0)
(0,±a,0,0)
(0,0,±a,0)
(0,0,0,±a)

This transforms chess movement into graph theory.

## Important Concepts

### Move Graphs

Every chess piece creates a graph:

- vertices = board positions
- edges = legal moves

Study:

- connectivity
- diameter
- spectral properties
- symmetry

### Hypercube Symmetry

The empty 4D board has rich symmetry. Explore whether these symmetries can reduce chess state complexity.

### Research Hypothesis

The project asks whether chess contains mathematical compression opportunities hidden by its normal 2D representation.

Possible routes:

- quotient spaces of equivalent positions
- group actions on states
- invariant discovery
- geometric embeddings
- algebraic descriptions of moves

## Agent Expectations

Do deep mathematical work.

Do not simply implement Stockfish-like search.

Prefer experiments that could reveal structure.

Every major idea should include:

- mathematical explanation
- small example
- computational experiment
- limitations
- next hypothesis
