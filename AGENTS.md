# AGENTS.md - SolvingChess

## Mission

Investigate whether chess has mathematical structure that makes it tractable by
means other than brute-force search. Not to build a stronger engine.

The repository pursues two directions:

* **Minification** -- shrink the board and the material until the game is
  exactly solvable, then study what the exact solution shows. This is where the
  results are.
* **Representation** -- symmetry, quotient spaces, higher-dimensional
  embeddings. This is where the original hypothesis is, and it is being tested
  rather than assumed.

Read `research/README.md` for the corpus index and `docs/roadmap.md` for what to
build next.

## Non-negotiables

**Never write a number into markdown by hand.** Every experiment writes
`results/*.json` and prints a markdown table; paste the printed table. The
repository previously recorded a result its own code did not produce, and that
is the single most expensive kind of mistake here.

**Never report compression from an unverified group.** `SymmetryGroup.verify`
exists because a transformation that looks like a symmetry often is not -- a
pawn breaks rank mirrors, asymmetric material breaks the colour swap. Verify
against a solved table, then quote the number.

**Keep the known-answer tests green.** The solver reproduces the published
maximum distance-to-mate for KQ vs K (10 moves) and KR vs K (16 moves) on 8x8.
Every structural claim rests on those. If a change breaks them, the change is
wrong.

**State predictions before runs.** A hypothesis written after seeing the data is
not a hypothesis. Each research note ends with a "next hypothesis" section for
this reason.

**Give negative results equal prominence.** Experiment 001 came out against the
repository's founding hypothesis and says so in its own results file. That is
the standard.

## Working on the code

The kernel is `src/solvingchess/`:

| module | role |
|---|---|
| `geometry.py` | rectangular boards, attack tables, piece constants |
| `rules.py` | material signatures, state encoding, legal move generation |
| `variants.py` | named universes, including the Singleton Chess family |
| `symmetry.py` | per-universe symmetry groups, canonicalisation, verification |
| `solver.py` | exploration plus backward induction for loopy games |
| `quotient.py` | bisimulation quotients -- the floor for any sound abstraction |
| `report.py` | JSON and markdown output, shared by every experiment |

Conventions worth knowing before changing anything:

* A state is a single integer. Slot values encode square and piece type; a
  captured piece takes value 0 and a promoted pawn changes the type in its own
  slot. Changing the encoding invalidates any persisted table.
* Values are **always** from the side to move's perspective. This is what makes
  the colour-swap symmetry value-preserving.
* Draws are the fixpoint complement: a state is drawn exactly when the backward
  induction never labels it. This is the loopy-game convention and it is why
  states carry no move history.
* No castling, no en passant, no fifty-move rule. Double pawn steps default off.
  The reasoning is in the `rules.py` module docstring; do not add them casually.

## Adding an experiment

1. `experiments/expNNN_short_name/` with `run.py`, `README.md`, `results.md`.
2. `run.py` imports from `src/solvingchess`, takes a state budget, and calls
   `report.save`.
3. `README.md` states the question, the method, and what would count as a
   negative result.
4. `results.md` holds the pasted table plus interpretation, limitations, and the
   next hypothesis.
5. Register it in `docs/roadmap.md` and the corpus status table.

## Adding to the research corpus

Notes are numbered and each must:

1. state a claim precisely enough that it could be false;
2. give a small worked example;
3. name the experiment that tests it, or say that none exists;
4. record limitations, including the ones that hurt;
5. end with a next hypothesis.

Separate **established** results (cite them), **our measurements** (link the
results file) and **conjecture** (label it).

## Anti-patterns

* Assuming higher dimensions simplify anything. The arithmetic is in
  `research/04`: dimension multiplies the symmetry group by a constant and the
  state space exponentially in piece count. That is a losing trade and it is
  measured, not guessed.
* Replacing mathematical investigation with a bigger computation.
* Treating playing strength as partial progress toward a solution.
* Rewriting the solver for speed when the blocked thing is an idea, not a table
  size.
