"""Value-preserving quotients of a solved state graph.

Symmetry reduction is one way to collapse a game graph, but it is not the only
one and it is certainly not the best one. Two positions can be behaviourally
identical without any board transformation relating them.

The coarsest value-preserving collapse is the **bisimulation quotient**: refine
the partition of states until every block has a well-defined set of successor
blocks, starting from a partition that already separates wins, draws and losses.
The fixpoint is the smallest graph that still answers every question the
original answers about play, so its size is a *lower bound* on any sound
abstraction -- including every symmetry group, present or undiscovered.

The gap between the symmetry quotient and the bisimulation quotient is therefore
a direct measurement of how much structure symmetry alone is missing.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class QuotientResult:
    n_states: int
    n_blocks: int
    rounds: int
    block_of: np.ndarray

    @property
    def ratio(self) -> float:
        return self.n_states / self.n_blocks if self.n_blocks else float("nan")

    @property
    def compression(self) -> float:
        return 100.0 * (1.0 - self.n_blocks / self.n_states) if self.n_states else 0.0


def bisimulation_quotient(solution, label="wdl", max_rounds: int = 200) -> QuotientResult:
    """Coarsest partition that refines ``label`` and is stable under moves.

    ``label`` is ``"wdl"`` (win/draw/loss only) or ``"dtm"`` (also separates
    distance to mate, which is a much finer and therefore much weaker collapse).
    """
    n = solution.n_states
    if label == "wdl":
        initial = solution.value.astype(np.int64)
    elif label == "dtm":
        initial = solution.value.astype(np.int64) * (int(solution.dtm.max()) + 2) \
            + (solution.dtm.astype(np.int64) + 1)
    else:
        raise ValueError(f"unknown label {label!r}")

    _, block_of = np.unique(initial, return_inverse=True)
    block_of = block_of.astype(np.int64)

    succ_start = solution.succ_start.tolist()
    succ_flat = solution.succ_flat.tolist()

    rounds = 0
    for rounds in range(1, max_rounds + 1):
        current = block_of.tolist()
        signatures = []
        for i in range(n):
            children = {current[succ_flat[k]]
                        for k in range(succ_start[i], succ_start[i + 1])}
            signatures.append((current[i], frozenset(children)))
        lookup: dict = {}
        new = np.empty(n, dtype=np.int64)
        for i, sig in enumerate(signatures):
            b = lookup.get(sig)
            if b is None:
                b = len(lookup)
                lookup[sig] = b
            new[i] = b
        if len(lookup) == len(set(current)):
            block_of = new
            break
        block_of = new

    return QuotientResult(
        n_states=n,
        n_blocks=int(block_of.max()) + 1 if n else 0,
        rounds=rounds,
        block_of=block_of,
    )


def symmetry_quotient_size(solution, group) -> int:
    """How many orbits the symmetry group carves the solved state set into."""
    return len({group.canonical(state) for state in solution.states})
