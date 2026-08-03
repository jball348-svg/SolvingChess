"""Named micro-chess universes.

Two families matter for this project.

**Endgame universes** (``KQ-K``, ``KR-K``, ...) are the classical tablebase
material signatures on a shrunken board. They are the rungs of the scaling
ladder in ``experiments/exp002_minichess_ladder``.

**Singleton Chess** is the construction proposed for this repository: shrink the
board *and* allow at most one piece of each type per side, so that the game keeps
every piece's movement geometry -- the thing that makes chess chess -- while
deleting the multiplicity that makes it astronomically large.

The maximal member of the family is::

    Singleton Chess 5x5   back rank R N B Q K, one pawn each, 12 pieces

which is Gardner's 5x5 minichess with four of the five pawns per side removed.
Smaller members drop piece types from the right of the sequence
``K, Q, R, B, N, P``, giving a ladder of universes that differ from full chess in
exactly one controlled way.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import (
    BISHOP, BLACK, Geometry, KING, KNIGHT, LETTER_TO_PIECE, PAWN, PIECE_LETTER,
    QUEEN, ROOK, WHITE,
)
from .rules import CAPTURED, Rules

# Order in which piece types are added as a singleton universe grows.
SINGLETON_ORDER = (KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN)

# Where non-king pieces prefer to sit on the back rank, mirroring Gardner's 5x5.
BACK_RANK_PREFERENCE = (ROOK, KNIGHT, BISHOP, QUEEN, KING)


@dataclass(frozen=True)
class Variant:
    """A universe plus a designated starting state."""

    name: str
    rules: Rules
    start: int
    description: str = ""

    @property
    def geometry(self) -> Geometry:
        return self.rules.geometry

    def __str__(self) -> str:
        return self.name


def material_from_string(spec: str) -> tuple[tuple[int, int], ...]:
    """``"KQ-KR"`` -> white K,Q and black K,R as ordered colour/type slots."""
    white, _, black = spec.partition("-")
    slots = [(WHITE, LETTER_TO_PIECE[c]) for c in white]
    slots += [(BLACK, LETTER_TO_PIECE[c]) for c in black]
    return tuple(slots)


def endgame_variant(spec: str, files: int, ranks: int, start=None) -> Variant:
    """An endgame universe such as ``KR-K``; ``start`` is a state or ASCII board."""
    rules = Rules(Geometry(files, ranks), material_from_string(spec))
    if start is None:
        state = _default_endgame_start(rules)
    elif isinstance(start, str):
        state = rules.parse(start)
    else:
        state = start
    return Variant(f"{spec}@{files}x{ranks}", rules, state, f"{spec} on {files}x{ranks}")


def _default_endgame_start(rules: Rules) -> int:
    """Corner the weaker king and spread everything else, deterministically.

    Endgame universes are usually solved over *all* legal placements rather than
    from one root, so this only needs to be a legal, reproducible position.
    """
    geo = rules.geometry
    squares = [CAPTURED] * rules.nslots
    types = [ptype for _, ptype in rules.material]
    # Deterministic sweep: place pieces on a spaced-out subset of squares.
    stride = max(1, geo.nsq // max(1, rules.nslots))
    cursor = 0
    for slot in range(rules.nslots):
        squares[slot] = (cursor * stride) % geo.nsq
        cursor += 1
    used = set()
    for slot in range(rules.nslots):  # repair collisions
        while squares[slot] in used:
            squares[slot] = (squares[slot] + 1) % geo.nsq
        used.add(squares[slot])
    state = rules.encode(squares, types, WHITE)
    if rules.is_legal_state(state):
        return state
    # Fall back to a linear scan for a legal placement.
    from itertools import permutations
    for combo in permutations(range(geo.nsq), rules.nslots):
        candidate = rules.encode(list(combo), types, WHITE)
        if rules.is_legal_state(candidate):
            return candidate
    raise ValueError(f"no legal placement for {rules.signature()} on {geo}")


def singleton_variant(files: int, ranks: int, types=SINGLETON_ORDER,
                      promotions=(QUEEN, ROOK, BISHOP, KNIGHT)) -> Variant:
    """Build a Singleton Chess universe: at most one of each ``type`` per side.

    Non-pawn pieces are laid out on each side's home rank following Gardner's
    ordering; a pawn (if present) sits in front of the king.
    """
    types = tuple(types)
    if KING not in types:
        raise ValueError("a singleton universe needs kings")
    geo = Geometry(files, ranks)

    back = [t for t in BACK_RANK_PREFERENCE if t in types]
    if len(back) > files:
        raise ValueError(f"{len(back)} back-rank pieces do not fit on {files} files")
    has_pawn = PAWN in types
    if has_pawn and ranks < 3:
        raise ValueError("a pawn needs at least three ranks")

    material = tuple([(WHITE, t) for t in types] + [(BLACK, t) for t in types])
    rules = Rules(geo, material, promotions=promotions)

    # Centre the back rank; White on rank 0, Black mirrored on the top rank.
    offset = (files - len(back)) // 2
    squares = [CAPTURED] * rules.nslots
    piece_types = [t for _, t in material]
    for colour in (WHITE, BLACK):
        home = 0 if colour == WHITE else ranks - 1
        pawn_rank = 1 if colour == WHITE else ranks - 2
        # Reflection, not rotation: kings face each other down the same file,
        # exactly as in standard chess.
        for i, t in enumerate(back):
            slot = _slot_of(material, colour, t)
            squares[slot] = geo.square(offset + i, home)
        if has_pawn:
            king_slot = _slot_of(material, colour, KING)
            king_file = geo.file_of(squares[king_slot])
            squares[_slot_of(material, colour, PAWN)] = geo.square(king_file, pawn_rank)

    start = rules.encode(squares, piece_types, WHITE)
    if not rules.is_legal_state(start):
        raise ValueError("generated singleton start position is illegal")

    label = "".join(PIECE_LETTER[t] for t in types)
    return Variant(
        f"singleton-{label}@{files}x{ranks}",
        rules,
        start,
        f"Singleton Chess on {files}x{ranks} with one each of {label} per side",
    )


def _slot_of(material, colour: int, ptype: int) -> int:
    for i, (c, t) in enumerate(material):
        if c == colour and t == ptype:
            return i
    raise KeyError((colour, ptype))


def singleton_ladder(files: int, ranks: int, max_pieces: int | None = None):
    """The ladder of singleton universes from ``K`` up to the largest that fits."""
    out = []
    for n in range(1, len(SINGLETON_ORDER) + 1):
        if max_pieces is not None and 2 * n > max_pieces:
            break
        types = SINGLETON_ORDER[:n]
        try:
            out.append(singleton_variant(files, ranks, types))
        except ValueError:
            break
    return out


# ---------------------------------------------------------------- references

def gardner_5x5() -> Variant:
    """Gardner's minichess: 5x5, full back rank, five pawns a side.

    Included as a reference point for move-generation tests and for size
    comparisons. It is far outside exhaustive-solving range for this codebase.
    """
    geo = Geometry(5, 5)
    order = (ROOK, KNIGHT, BISHOP, QUEEN, KING)
    material = (
        tuple((WHITE, t) for t in order) + tuple((WHITE, PAWN) for _ in range(5))
        + tuple((BLACK, t) for t in order) + tuple((BLACK, PAWN) for _ in range(5))
    )
    rules = Rules(geo, material)
    squares, types = [], [t for _, t in material]
    for f in range(5):
        squares.append(geo.square(f, 0))
    for f in range(5):
        squares.append(geo.square(f, 1))
    for f in range(5):
        squares.append(geo.square(f, 4))
    for f in range(5):
        squares.append(geo.square(f, 3))
    start = rules.encode(squares, types, WHITE)
    return Variant("gardner@5x5", rules, start, "Gardner's 5x5 minichess (reference only)")


CATALOGUE = {
    "KK-4x4": lambda: endgame_variant("K-K", 4, 4),
    "KRK-4x4": lambda: endgame_variant("KR-K", 4, 4),
    "KQK-4x4": lambda: endgame_variant("KQ-K", 4, 4),
    "KRK-5x5": lambda: endgame_variant("KR-K", 5, 5),
    "KQK-5x5": lambda: endgame_variant("KQ-K", 5, 5),
    "KQK-8x8": lambda: endgame_variant("KQ-K", 8, 8),
    "singleton-KQ-4x4": lambda: singleton_variant(4, 4, (KING, QUEEN)),
    "singleton-KQR-5x5": lambda: singleton_variant(5, 5, (KING, QUEEN, ROOK)),
    "singleton-full-5x5": lambda: singleton_variant(5, 5),
    "gardner-5x5": gardner_5x5,
}
