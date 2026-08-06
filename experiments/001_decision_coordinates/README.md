# Experiment 001: Decision Coordinates

## Objective

Transform a chess game into a sequence of mathematical decision states.

The aim is to represent a chess move not by traditional notation alone, but by its location within the available decision space.

## Representation

Each position is represented as:


Position:

FEN

Decision space:

deg+(Position)

Chosen action:

chosen_edge


Where:

- FEN uniquely identifies the chess state.
- deg+ is the out-degree of the position (number of legal moves).
- chosen_edge is the index of the selected move within the defined move ordering.

Example:


Position:

FEN:
rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1

deg+:
20

chosen_edge:
5


## Current move ordering

The move ordering is intentionally separated from the encoder.

Current placeholder:

- Sort legal moves by UCI notation.

Future experiments can replace this with alternative ordering systems.

## Research questions

Possible future questions:

- Do winning games have characteristic decision coordinate patterns?
- Are strong moves usually low-index or high-index choices?
- Does branching factor correlate with evaluation?
- Can chess be represented in a lower-dimensional decision space?
