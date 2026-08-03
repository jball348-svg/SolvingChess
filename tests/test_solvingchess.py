"""Correctness tests for the micro-chess kernel.

The load-bearing tests are the *known-answer* ones: our solver has to reproduce
the published maximum distance-to-mate for KQ vs K (10 moves) and KR vs K (16
moves) on a full 8x8 board. Those two numbers pin down move generation, check
and stalemate detection, and the backward induction all at once.

Run with ``pytest -q`` (or ``python tests/test_solvingchess.py`` for a plain run).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from solvingchess.geometry import (
    BISHOP, BLACK, Geometry, KING, KNIGHT, PAWN, QUEEN, ROOK, WHITE,
)
from solvingchess.quotient import bisimulation_quotient
from solvingchess.rules import Rules
from solvingchess.solver import DRAW, solve_material, solve_variant
from solvingchess.symmetry import SymmetryGroup
from solvingchess.variants import (
    endgame_variant, gardner_5x5, material_from_string, singleton_variant,
)


# --------------------------------------------------------------------- geometry

def test_square_roundtrip():
    g = Geometry(5, 7)
    assert g.nsq == 35
    for sq in range(g.nsq):
        assert g.square(g.file_of(sq), g.rank_of(sq)) == sq


def test_ray_table_stops_at_edge():
    g = Geometry(4, 4)
    rays = g.ray_table(((1, 0), (-1, 0)))
    assert rays[g.square(0, 0)][0] == (1, 2, 3)
    assert rays[g.square(0, 0)][1] == ()


# ------------------------------------------------------------------- encoding

def test_encode_decode_roundtrip():
    rules = Rules(Geometry(4, 4), material_from_string("KQ-KR"))
    squares, types = [0, 5, 15, 9], [KING, QUEEN, KING, ROOK]
    for stm in (WHITE, BLACK):
        state = rules.encode(squares, types, stm)
        back_sq, back_ty, back_stm = rules.decode(state)
        assert (back_sq, back_ty, back_stm) == (squares, types, stm)


def test_capture_is_reversible_in_encoding():
    rules = Rules(Geometry(4, 4), material_from_string("KR-K"))
    state = rules.parse("""
        . . . .
        . . k .
        . R . .
        K . . .
    """)
    assert rules.is_legal_state(state)
    assert any(rules.decode(s)[0][1] == -1 for s in rules.successors(state)) is False


# ------------------------------------------------------------ move generation

def test_gardner_opening_move_count():
    """5x5 minichess with no double pawn step: five pushes plus two knight moves."""
    g = gardner_5x5()
    assert len(g.rules.successors(g.start)) == 7


def test_back_rank_mate_is_detected():
    rules = Rules(Geometry(4, 4), material_from_string("KR-K"))
    state = rules.parse("""
        . . k .
        . . . .
        . . . R
        . . K .
    """, side_to_move=BLACK)
    assert not rules.is_checkmate(state)  # black king still has escape squares
    mate = rules.parse("""
        k . . R
        . . . .
        . K . .
        . . . .
    """, side_to_move=BLACK)
    assert rules.in_check(mate)
    assert rules.is_checkmate(mate)


def test_stalemate_is_not_checkmate():
    rules = Rules(Geometry(4, 4), material_from_string("KQ-K"))
    state = rules.parse("""
        k . . .
        . . Q .
        . . . .
        . . K .
    """, side_to_move=BLACK)
    assert not rules.in_check(state)
    assert rules.is_stalemate(state)


def test_pawn_promotes_and_cannot_double_step():
    rules = Rules(Geometry(4, 4), material_from_string("KP-K"))
    state = rules.parse("""
        . . . k
        . P . .
        . . . .
        K . . .
    """)
    pawn_slot = 1  # material is (white K, white P, black K)
    promoted = {rules.decode(s)[1][pawn_slot] for s in rules.successors(state)
                if rules.decode(s)[1][pawn_slot] != PAWN}
    assert promoted == {QUEEN, ROOK, BISHOP, KNIGHT}

    home = rules.parse("""
        . . . k
        . . . .
        . P . .
        K . . .
    """)
    pawn_targets = {rules.decode(s)[0][1] for s in rules.successors(home)}
    assert rules.geometry.square(1, 2) in pawn_targets
    assert rules.geometry.square(1, 3) not in pawn_targets  # no double step


def test_king_may_not_move_into_check():
    rules = Rules(Geometry(4, 4), material_from_string("KR-K"))
    state = rules.parse("""
        . . . .
        . k . .
        . . . .
        K . R .
    """, side_to_move=BLACK)
    for successor in rules.successors(state):
        assert not rules.in_check(successor, BLACK)


# -------------------------------------------------------------- known answers

def test_kqk_maximum_dtm_on_full_board():
    """Published result: KQ vs K is a mate in at most 10 moves."""
    rules = endgame_variant("KQ-K", 8, 8).rules
    solution = solve_material(rules, max_states=1_000_000)
    _, plies = solution.longest_win()
    assert plies == 20


def test_krk_maximum_dtm_on_full_board():
    """Published result: KR vs K is a mate in at most 16 moves."""
    rules = endgame_variant("KR-K", 8, 8).rules
    solution = solve_material(rules, max_states=1_000_000)
    _, plies = solution.longest_win()
    assert plies == 32


def test_lone_kings_are_always_drawn():
    solution = solve_material(endgame_variant("K-K", 5, 5).rules)
    assert solution.counts()["draw"] == solution.n_states


def test_knight_alone_cannot_mate():
    solution = solve_material(endgame_variant("KN-K", 5, 5).rules)
    assert solution.counts()["win"] == 0


# --------------------------------------------------------------- symmetry

def test_symmetry_group_orders():
    assert SymmetryGroup(endgame_variant("K-K", 4, 4).rules).order == 16   # D4 x colour
    assert SymmetryGroup(endgame_variant("KR-K", 4, 4).rules).order == 8   # D4 only
    assert SymmetryGroup(endgame_variant("KR-K", 4, 6).rules).order == 4   # D2 only
    assert SymmetryGroup(endgame_variant("KP-K", 4, 4).rules).order == 2   # file mirror


def test_symmetry_preserves_value():
    rules = endgame_variant("KR-K", 4, 4).rules
    solution = solve_material(rules)
    group = SymmetryGroup(rules)
    checked, violations = group.verify(solution)
    assert checked == solution.n_states
    assert violations == 0


def test_canonicalised_solve_agrees_with_raw_solve():
    variant = endgame_variant("KQ-K", 4, 4)
    group = SymmetryGroup(variant.rules)
    raw = solve_material(variant.rules)
    quotient = solve_material(variant.rules, canonical=group.canonical)
    assert quotient.n_states < raw.n_states
    for state in raw.states[:500]:
        assert quotient.value_of(group.canonical(state)) == raw.value_of(state)


# --------------------------------------------------------------- quotient

def test_bisimulation_is_at_most_symmetry():
    rules = endgame_variant("KR-K", 4, 4).rules
    solution = solve_material(rules)
    group = SymmetryGroup(rules)
    orbits = len({group.canonical(s) for s in solution.states})
    assert bisimulation_quotient(solution, label="wdl").n_blocks <= orbits


# --------------------------------------------------------------- variants

def test_singleton_start_positions_are_legal_and_mirrored():
    for files, ranks, types in [(4, 4, (KING, QUEEN)), (5, 5, (KING, QUEEN, ROOK))]:
        variant = singleton_variant(files, ranks, types)
        rules = variant.rules
        assert rules.is_legal_state(variant.start)
        squares, _, _ = rules.decode(variant.start)
        white_king = squares[rules._king_slot[WHITE]]
        black_king = squares[rules._king_slot[BLACK]]
        assert rules.geometry.file_of(white_king) == rules.geometry.file_of(black_king)


def test_singleton_kq_is_drawn_on_small_boards():
    for files, ranks in [(3, 3), (4, 4)]:
        variant = singleton_variant(files, ranks, (KING, QUEEN))
        group = SymmetryGroup(variant.rules)
        solution = solve_variant(variant, canonical=group.canonical, max_states=200_000)
        assert solution.value_of(solution.roots[0]) == DRAW


if __name__ == "__main__":
    import traceback
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception:
                failures += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    sys.exit(1 if failures else 0)
