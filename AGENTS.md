# AGENTS.md - SolvingChess Agent Instructions

## Mission

This repository explores novel mathematical approaches toward solving chess. The goal is not to create a stronger traditional engine through brute force, but to investigate whether hidden mathematical structure can simplify, transform or reveal the chess problem.

## Core Research Direction

Prioritise:

1. Higher-dimensional geometry
2. Algebraic representations of chess states
3. Graph and topology based analysis
4. Symmetry and invariants
5. Alternative search architectures

## 4D Chess Foundation

The main inspiration is the mathematical framework for four-dimensional chess on the lattice {1,...,8}^4.

Important concepts:

- A board position is represented as a point (x,y,z,w).
- Moves are displacement vectors in Z^4.
- Movement can be analysed as graphs where squares are vertices and legal moves are edges.
- The hypercube symmetry group creates possible state reductions.

## Research Questions

Do higher dimensional representations reveal:

- hidden symmetries?
- equivalent chess states?
- useful invariants?
- compressed representations?
- better search strategies?

## Coding Principles

Prefer:

- clear mathematical notation
- reproducible experiments
- notebooks before production systems
- visualisations for geometric concepts
- proofs or empirical validation for claims

Avoid:

- assuming higher dimensions automatically solve chess
- replacing mathematical investigation with larger computation
- speculative claims without experiments

## Expected Agent Behaviour

When adding research:

1. Explain the mathematical idea.
2. Provide examples.
3. Implement small experiments.
4. Record assumptions and limitations.
5. Suggest follow-up experiments.
