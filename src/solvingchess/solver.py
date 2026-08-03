"""Exact solver for micro-chess universes.

The solver works in two phases.

1. **Explore.** Walk the state graph forward from a set of roots, assigning each
   reachable state a dense integer id and recording every edge. Captures and
   promotions are ordinary moves here, so a single exploration covers the whole
   sub-material tree without special casing.

2. **Back up.** Run the standard backward-induction ("retrograde") pass for
   loopy games over the reversed edge set. Checkmates seed the frontier as
   losses; a state is a win as soon as one successor is a loss, and a loss only
   once *every* successor is a win. Whatever the fixpoint never labels is a draw
   -- that is the loopy-game convention that infinite play is drawn, and it is
   what makes it safe to leave repetition history out of the state.

Values are always stated from the perspective of the side to move.
"""

from __future__ import annotations

import time
from array import array
from collections import deque
from dataclasses import dataclass
from itertools import permutations

import numpy as np

from .rules import Rules

UNKNOWN, WIN, LOSS, DRAW = 0, 1, 2, 3
VALUE_NAME = {UNKNOWN: "unknown", WIN: "win", LOSS: "loss", DRAW: "draw"}


class StateBudgetExceeded(RuntimeError):
    """Raised when exploration passes the configured state ceiling."""


@dataclass
class Solution:
    """A fully solved state graph."""

    rules: Rules
    states: list           # id -> encoded state
    index: dict            # encoded state -> id
    value: np.ndarray      # id -> UNKNOWN/WIN/LOSS/DRAW
    dtm: np.ndarray        # id -> distance to mate in plies (-1 when drawn)
    succ_start: np.ndarray
    succ_flat: np.ndarray
    roots: list
    explore_seconds: float = 0.0
    solve_seconds: float = 0.0
    canonicalised: bool = False

    @property
    def n_states(self) -> int:
        return len(self.states)

    @property
    def n_edges(self) -> int:
        return int(self.succ_flat.size)

    def value_of(self, state: int):
        i = self.index.get(state)
        return None if i is None else int(self.value[i])

    def dtm_of(self, state: int):
        i = self.index.get(state)
        return None if i is None else int(self.dtm[i])

    def successors_of(self, state: int) -> list:
        i = self.index[state]
        lo, hi = self.succ_start[i], self.succ_start[i + 1]
        return [self.states[j] for j in self.succ_flat[lo:hi]]

    def counts(self) -> dict:
        return {
            VALUE_NAME[v]: int((self.value == v).sum())
            for v in (WIN, LOSS, DRAW, UNKNOWN)
        }

    def best_move(self, state: int):
        """A value-optimal successor: win fastest, else survive longest."""
        i = self.index[state]
        if self.value[i] == DRAW:
            for s in self.successors_of(state):
                if self.value_of(s) == DRAW:
                    return s
            return None
        options = [(self.value_of(s), self.dtm_of(s), s) for s in self.successors_of(state)]
        if not options:
            return None
        if self.value[i] == WIN:
            losing = [o for o in options if o[0] == LOSS]
            return min(losing, key=lambda o: o[1])[2]
        return max(options, key=lambda o: o[1])[2]

    def principal_variation(self, state: int, limit: int = 200) -> list:
        line, seen = [state], {state}
        for _ in range(limit):
            nxt = self.best_move(line[-1])
            if nxt is None or nxt in seen:
                break
            line.append(nxt)
            seen.add(nxt)
        return line

    def longest_win(self):
        """The state with the largest distance to mate, and that distance."""
        finite = np.where(self.dtm >= 0, self.dtm, -1)
        if finite.max() < 0:
            return None, -1
        i = int(finite.argmax())
        return self.states[i], int(finite[i])


# --------------------------------------------------------------------- explore

def explore(rules: Rules, roots, canonical=None, max_states: int | None = 5_000_000,
            progress: int = 0):
    """Collect the reachable state graph.

    ``canonical`` optionally maps a state to a representative of its symmetry
    orbit; passing one explores the quotient graph directly, which is sound
    because the symmetry group is a game automorphism (see :mod:`symmetry`).
    """
    started = time.perf_counter()
    index: dict = {}
    states: list = []
    succ_flat = array("i")
    succ_start = [0]

    def intern(state: int) -> int:
        key = canonical(state) if canonical else state
        i = index.get(key)
        if i is None:
            i = len(states)
            index[key] = i
            states.append(key)
        return i

    root_ids = [intern(r) for r in roots]

    # Expand in id order so that CSR row `i` always belongs to state id `i`.
    cursor = 0
    while cursor < len(states):
        for child in rules.successors(states[cursor]):
            succ_flat.append(intern(child))
        succ_start.append(len(succ_flat))
        cursor += 1
        if max_states is not None and len(states) > max_states:
            raise StateBudgetExceeded(
                f"{rules.signature()} exceeded {max_states:,} states"
            )
        if progress and cursor % progress == 0:
            print(f"    expanded {cursor:,} / discovered {len(states):,}", flush=True)

    return (
        states,
        index,
        np.array(succ_start, dtype=np.int64),
        np.frombuffer(succ_flat, dtype=np.int32).copy(),
        root_ids,
        time.perf_counter() - started,
    )


# --------------------------------------------------------------------- back up

def backward_induction(rules: Rules, states, succ_start, succ_flat):
    """Label every state WIN/LOSS/DRAW from the side-to-move's perspective."""
    n = len(states)
    value = np.zeros(n, dtype=np.uint8)
    dtm = np.full(n, -1, dtype=np.int32)
    degree = np.diff(succ_start).astype(np.int32)
    remaining = degree.copy()

    # Reverse adjacency in CSR form: sort edges by destination, which is a
    # counting sort done entirely inside numpy.
    pred_count = np.bincount(succ_flat, minlength=n)
    pred_start = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(pred_count, out=pred_start[1:])
    src = np.repeat(np.arange(n, dtype=np.int32), degree)
    pred_flat = src[np.argsort(succ_flat, kind="stable")]

    queue = deque()
    for i in range(n):
        if degree[i] == 0:
            if rules.in_check(states[i]):
                value[i] = LOSS   # checkmate: the side to move has lost
            else:
                value[i] = DRAW   # stalemate
            dtm[i] = 0
            if value[i] == LOSS:
                queue.append(i)

    pred_start_l = pred_start.tolist()
    pred_flat_l = pred_flat.tolist()
    value_l = value.tolist()
    dtm_l = dtm.tolist()
    remaining_l = remaining.tolist()

    while queue:
        node = queue.popleft()
        node_value = value_l[node]
        node_dtm = dtm_l[node]
        for k in range(pred_start_l[node], pred_start_l[node + 1]):
            parent = pred_flat_l[k]
            if value_l[parent]:
                continue
            if node_value == LOSS:
                value_l[parent] = WIN
                dtm_l[parent] = node_dtm + 1
                queue.append(parent)
            else:  # node is a WIN for its mover, i.e. bad news for the parent
                remaining_l[parent] -= 1
                if remaining_l[parent] == 0:
                    value_l[parent] = LOSS
                    dtm_l[parent] = node_dtm + 1
                    queue.append(parent)

    value = np.array(value_l, dtype=np.uint8)
    dtm = np.array(dtm_l, dtype=np.int32)
    value[value == UNKNOWN] = DRAW   # never resolved => infinite play => draw
    dtm[value == DRAW] = -1
    return value, dtm


def solve(rules: Rules, roots, canonical=None, max_states: int | None = 5_000_000,
          progress: int = 0) -> Solution:
    states, index, succ_start, succ_flat, root_ids, explore_seconds = explore(
        rules, roots, canonical=canonical, max_states=max_states, progress=progress
    )
    started = time.perf_counter()
    value, dtm = backward_induction(rules, states, succ_start, succ_flat)
    return Solution(
        rules=rules,
        states=states,
        index=index,
        value=value,
        dtm=dtm,
        succ_start=succ_start,
        succ_flat=succ_flat,
        roots=[states[i] for i in root_ids],
        explore_seconds=explore_seconds,
        solve_seconds=time.perf_counter() - started,
        canonicalised=canonical is not None,
    )


# ----------------------------------------------------------------------- roots

def all_legal_states(rules: Rules, limit: int | None = None):
    """Every legal placement of the full material signature, both sides to move.

    This is the tablebase seeding: solving from here labels not just these
    positions but everything reachable from them, including all sub-material.
    """
    nsq = rules.geometry.nsq
    types = [t for _, t in rules.material]
    produced = 0
    for combo in permutations(range(nsq), rules.nslots):
        squares = list(combo)
        for stm in (0, 1):
            state = rules.encode(squares, types, stm)
            if rules.is_legal_state(state):
                yield state
                produced += 1
                if limit is not None and produced >= limit:
                    return


def solve_variant(variant, canonical=None, max_states: int | None = 5_000_000,
                  progress: int = 0) -> Solution:
    """Solve a variant from its designated start position."""
    return solve(variant.rules, [variant.start], canonical=canonical,
                 max_states=max_states, progress=progress)


def solve_material(rules: Rules, canonical=None, max_states: int | None = 5_000_000,
                   progress: int = 0) -> Solution:
    """Build a full tablebase for a material signature."""
    return solve(rules, all_legal_states(rules), canonical=canonical,
                 max_states=max_states, progress=progress)
