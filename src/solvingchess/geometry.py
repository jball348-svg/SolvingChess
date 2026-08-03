"""Board geometry for arbitrary rectangular chess boards.

Everything downstream (move generation, symmetry, indexing) is parameterised by a
:class:`Geometry`, so a 3x3 toy universe and a standard 8x8 board are the same
code path with different constants.

Squares are integers ``0 .. nsq-1`` with ``square = rank * files + file``.
Rank 0 is White's home rank; White pawns move towards increasing rank.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

# Piece types. The integer values are part of the state encoding, so do not
# reorder them without regenerating any persisted tablebases.
KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN = range(6)
NTYPE = 6

PIECE_LETTER = "KQRBNP"
LETTER_TO_PIECE = {c: i for i, c in enumerate(PIECE_LETTER)}

WHITE, BLACK = 0, 1
COLOUR_NAME = ("white", "black")

# Sliding directions as (file_delta, rank_delta).
ORTHOGONAL = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIAGONAL = ((1, 1), (1, -1), (-1, 1), (-1, -1))
KING_STEPS = ORTHOGONAL + DIAGONAL
KNIGHT_STEPS = (
    (1, 2), (2, 1), (2, -1), (1, -2),
    (-1, -2), (-2, -1), (-2, 1), (-1, 2),
)

SLIDER_DIRECTIONS = {
    QUEEN: KING_STEPS,
    ROOK: ORTHOGONAL,
    BISHOP: DIAGONAL,
}


@dataclass(frozen=True)
class Geometry:
    """A rectangular board of ``files`` columns and ``ranks`` rows."""

    files: int
    ranks: int

    # ---------------------------------------------------------------- basics

    @property
    def nsq(self) -> int:
        return self.files * self.ranks

    def square(self, file: int, rank: int) -> int:
        return rank * self.files + file

    def file_of(self, sq: int) -> int:
        return sq % self.files

    def rank_of(self, sq: int) -> int:
        return sq // self.files

    def on_board(self, file: int, rank: int) -> bool:
        return 0 <= file < self.files and 0 <= rank < self.ranks

    def name(self, sq: int) -> str:
        """Algebraic-ish name, e.g. ``a1``. Falls back past 'z' for huge boards."""
        return f"{chr(ord('a') + self.file_of(sq))}{self.rank_of(sq) + 1}"

    def promotion_rank(self, colour: int) -> int:
        return self.ranks - 1 if colour == WHITE else 0

    def pawn_push(self, colour: int) -> int:
        """Square delta for a single pawn push."""
        return self.files if colour == WHITE else -self.files

    # ------------------------------------------------------- attack topology
    # These tables are built once per geometry and shared by every position.

    @lru_cache(maxsize=None)
    def step_table(self, steps: tuple) -> tuple:
        """For each square, the squares reachable by a single ``steps`` hop."""
        table = []
        for sq in range(self.nsq):
            f, r = self.file_of(sq), self.rank_of(sq)
            table.append(tuple(
                self.square(f + df, r + dr)
                for df, dr in steps
                if self.on_board(f + df, r + dr)
            ))
        return tuple(table)

    @lru_cache(maxsize=None)
    def ray_table(self, directions: tuple) -> tuple:
        """For each square, one tuple of squares per direction, ordered outward."""
        table = []
        for sq in range(self.nsq):
            f, r = self.file_of(sq), self.rank_of(sq)
            rays = []
            for df, dr in directions:
                ray, cf, cr = [], f + df, r + dr
                while self.on_board(cf, cr):
                    ray.append(self.square(cf, cr))
                    cf, cr = cf + df, cr + dr
                rays.append(tuple(ray))
            table.append(tuple(rays))
        return tuple(table)

    @lru_cache(maxsize=None)
    def pawn_attacks(self, colour: int) -> tuple:
        """For each square, the squares a pawn of ``colour`` standing there attacks."""
        dr = 1 if colour == WHITE else -1
        table = []
        for sq in range(self.nsq):
            f, r = self.file_of(sq), self.rank_of(sq)
            table.append(tuple(
                self.square(f + df, r + dr)
                for df in (-1, 1)
                if self.on_board(f + df, r + dr)
            ))
        return tuple(table)

    def __str__(self) -> str:
        return f"{self.files}x{self.ranks}"
