"""Symmetry groups acting on micro-chess states.

Three kinds of symmetry are available, and which of them actually preserve the
game depends on the material signature:

===========================  ================================================
symmetry                     when it is a game symmetry
===========================  ================================================
mirror across the file axis  always (pawn motion is along ranks)
mirror across the rank axis  only when no pawn is present, *or* when paired
                             with a colour swap
transpose / 90-degree turns  only on a square board with no pawns
colour swap                  only when both sides hold the same material; must
                             be paired with a rank mirror and a side-to-move
                             flip
===========================  ================================================

Getting this wrong silently corrupts a tablebase, so
:meth:`SymmetryGroup.verify` re-checks the group against a solved table by
comparing values across each orbit.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import Geometry, PAWN, WHITE
from .rules import CAPTURED, Rules


def _perm_identity(g: Geometry):
    return tuple(range(g.nsq))


def _perm_mirror_files(g: Geometry):
    return tuple(g.square(g.files - 1 - g.file_of(s), g.rank_of(s)) for s in range(g.nsq))


def _perm_mirror_ranks(g: Geometry):
    return tuple(g.square(g.file_of(s), g.ranks - 1 - g.rank_of(s)) for s in range(g.nsq))


def _perm_transpose(g: Geometry):
    return tuple(g.square(g.rank_of(s), g.file_of(s)) for s in range(g.nsq))


def _compose(p, q):
    """Apply ``q`` then ``p``."""
    return tuple(p[q[s]] for s in range(len(q)))


def _closure(generators, identity):
    """Generate the group spanned by ``generators``."""
    group = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for gen in generators:
            candidate = _compose(gen, current)
            if candidate not in group:
                group.add(candidate)
                frontier.append(candidate)
    return sorted(group)


@dataclass
class SymmetryGroup:
    """The subgroup of board symmetries that preserves a given universe."""

    rules: Rules

    def __post_init__(self) -> None:
        g = self.rules.geometry
        material = self.rules.material
        self.has_pawn = any(t == PAWN for _, t in material)
        self.square_board = g.files == g.ranks

        white = sorted(t for c, t in material if c == WHITE)
        black = sorted(t for c, t in material if c != WHITE)
        self.colour_symmetric = white == black

        identity = _perm_identity(g)
        generators = [_perm_mirror_files(g)]
        if not self.has_pawn:
            generators.append(_perm_mirror_ranks(g))
            if self.square_board:
                generators.append(_perm_transpose(g))
        geometric = _closure(generators, identity)

        elements = [(p, False) for p in geometric]
        if self.colour_symmetric:
            if self.has_pawn:
                # Only a rank mirror converts White's pawn direction into Black's.
                mirror = _perm_mirror_ranks(g)
                elements += [(_compose(mirror, p), True) for p in geometric]
            else:
                elements += [(p, True) for p in geometric]

        self.elements = elements
        self.slot_map = self._colour_pairing() if self.colour_symmetric else None

    def _colour_pairing(self):
        """Slot permutation exchanging each white piece with its black twin."""
        material = self.rules.material
        mapping = [None] * len(material)
        by_type: dict[int, list[int]] = {}
        for slot, (colour, ptype) in enumerate(material):
            if colour == WHITE:
                by_type.setdefault(ptype, []).append(slot)
        cursor: dict[int, int] = {}
        for slot, (colour, ptype) in enumerate(material):
            if colour == WHITE:
                continue
            i = cursor.get(ptype, 0)
            cursor[ptype] = i + 1
            partner = by_type[ptype][i]
            mapping[slot] = partner
            mapping[partner] = slot
        return tuple(mapping)

    @property
    def order(self) -> int:
        return len(self.elements)

    # ------------------------------------------------------------------ apply

    def apply(self, state: int, element) -> int:
        perm, swap = element
        squares, types, stm = self.rules.decode(state)
        n = len(squares)
        new_squares = [CAPTURED] * n
        new_types = [CAPTURED] * n
        target = self.slot_map if swap else range(n)
        for slot in range(n):
            dest = target[slot]
            sq = squares[slot]
            new_squares[dest] = CAPTURED if sq == CAPTURED else perm[sq]
            new_types[dest] = types[slot]
        return self.rules.encode(new_squares, new_types, stm ^ int(swap))

    def _images(self, state: int):
        """Every image of ``state`` under the group, decoding the state once."""
        rules = self.rules
        squares, types, stm = rules.decode(state)
        n = len(squares)
        identity = range(n)
        slot_map = self.slot_map
        for perm, swap in self.elements:
            target = slot_map if swap else identity
            new_squares = [CAPTURED] * n
            new_types = [CAPTURED] * n
            for slot in range(n):
                dest = target[slot]
                sq = squares[slot]
                new_squares[dest] = CAPTURED if sq == CAPTURED else perm[sq]
                new_types[dest] = types[slot]
            yield rules.encode(new_squares, new_types, stm ^ int(swap))

    def orbit(self, state: int) -> set:
        return set(self._images(state))

    def canonical(self, state: int) -> int:
        """The orbit's smallest encoding: a canonical representative."""
        return min(self._images(state))

    # ----------------------------------------------------------------- checks

    def verify(self, solution, sample: int | None = None) -> tuple[int, int]:
        """Check that every orbit in ``solution`` carries a constant value.

        Returns ``(checked, violations)``. A non-zero violation count means the
        group is not a game symmetry for this universe and any compression
        figure derived from it is meaningless.
        """
        import itertools
        states = solution.states
        if sample is not None and sample < len(states):
            step = len(states) // sample
            states = itertools.islice(states, 0, None, max(1, step))
        checked = violations = 0
        for state in states:
            value = solution.value_of(state)
            for image in self._images(state):
                other = solution.value_of(image)
                if other is not None and other != value:
                    violations += 1
            checked += 1
        return checked, violations

    def describe(self) -> str:
        bits = [f"order {self.order}"]
        bits.append("pawnful" if self.has_pawn else "pawnless")
        bits.append("square board" if self.square_board else "rectangular board")
        if self.colour_symmetric:
            bits.append("colour swap available")
        return ", ".join(bits)
