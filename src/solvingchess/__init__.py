"""SolvingChess: exact micro-chess universes for structural research.

Quick start::

    from solvingchess.variants import endgame_variant
    from solvingchess.solver import solve_material

    v = endgame_variant("KR-K", 4, 4)
    tb = solve_material(v.rules)
    print(tb.counts())
"""

from .geometry import (
    BISHOP, BLACK, Geometry, KING, KNIGHT, PAWN, PIECE_LETTER, QUEEN, ROOK, WHITE,
)
from .rules import Rules
from .solver import DRAW, LOSS, Solution, WIN, solve, solve_material, solve_variant
from .symmetry import SymmetryGroup
from .variants import (
    Variant, endgame_variant, gardner_5x5, singleton_ladder, singleton_variant,
)

__all__ = [
    "BISHOP", "BLACK", "DRAW", "Geometry", "KING", "KNIGHT", "LOSS", "PAWN",
    "PIECE_LETTER", "QUEEN", "ROOK", "Rules", "Solution", "SymmetryGroup",
    "Variant", "WHITE", "WIN", "endgame_variant", "gardner_5x5",
    "singleton_ladder", "singleton_variant", "solve", "solve_material",
    "solve_variant",
]
