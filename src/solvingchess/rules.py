"""Move generation for parameterised micro-chess universes.

A universe is fixed by a :class:`Rules` object: a board geometry plus a
*material signature* -- an ordered list of ``(colour, piece_type)`` slots. The
signature never changes length; a captured piece simply goes to the "off board"
value, and a promoting pawn changes the type stored in its own slot.

State encoding
--------------
A state is a single Python ``int``::

    state = side_to_move + 2 * sum_i (v_i * R**i)

where the slot value ``v_i`` is ``0`` when that piece has been captured, and
``1 + square * NTYPE + piece_type`` otherwise, and ``R = 1 + nsq * NTYPE``.

Integers are used rather than tuples because they hash in constant time and are
compact enough to hold several million of them in a dict.

Rules that are deliberately omitted (and why)
---------------------------------------------
* **Castling** -- undefined on boards without the standard back rank layout, and
  absent from every published minichess variant we mirror.
* **En passant** -- follows from double pawn steps, which default to off. Turn
  ``pawn_double_step`` on only for geometries where you have re-derived it.
* **Fifty-move / threefold repetition** -- the solver uses the standard
  loopy-game convention that infinite play is a draw, which gives the same
  win/draw/loss classification without carrying history in the state. See
  ``research/07-scaling-and-proof-strategy.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .geometry import (
    BISHOP, BLACK, Geometry, KING, KING_STEPS, KNIGHT, KNIGHT_STEPS, NTYPE,
    PAWN, PIECE_LETTER, QUEEN, ROOK, WHITE,
)

CAPTURED = -1


@dataclass(frozen=True)
class Rules:
    """A complete micro-chess universe."""

    geometry: Geometry
    material: tuple[tuple[int, int], ...]
    promotions: tuple[int, ...] = (QUEEN, ROOK, BISHOP, KNIGHT)
    pawn_double_step: bool = False

    # Derived tables, filled in by __post_init__ (frozen => object.__setattr__).
    _radix: int = field(default=0, init=False, compare=False, repr=False)
    _powers: tuple = field(default=(), init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        radix = 1 + self.geometry.nsq * NTYPE
        object.__setattr__(self, "_radix", radix)
        object.__setattr__(
            self, "_powers", tuple(radix ** i for i in range(len(self.material)))
        )
        object.__setattr__(self, "_king_slot", (
            self._find_king(WHITE), self._find_king(BLACK),
        ))
        g = self.geometry
        object.__setattr__(self, "_king_tbl", g.step_table(KING_STEPS))
        object.__setattr__(self, "_knight_tbl", g.step_table(KNIGHT_STEPS))
        object.__setattr__(self, "_rays", g.ray_table(KING_STEPS))
        object.__setattr__(self, "_pawn_atk", (g.pawn_attacks(WHITE), g.pawn_attacks(BLACK)))

    def _find_king(self, colour: int) -> int:
        for i, (c, t) in enumerate(self.material):
            if c == colour and t == KING:
                return i
        raise ValueError(f"material signature has no {['white', 'black'][colour]} king")

    @property
    def nslots(self) -> int:
        return len(self.material)

    def signature(self) -> str:
        """Human label such as ``KQ-KR`` (white material, black material)."""
        sides = ["", ""]
        for colour, ptype in self.material:
            sides[colour] += PIECE_LETTER[ptype]
        return f"{sides[WHITE]}-{sides[BLACK]}"

    # ------------------------------------------------------------- encoding

    def encode(self, squares, types, side_to_move: int) -> int:
        """Pack per-slot squares/types plus side to move into one integer."""
        total = 0
        for i, (sq, ty) in enumerate(zip(squares, types)):
            v = 0 if sq == CAPTURED else 1 + sq * NTYPE + ty
            total += v * self._powers[i]
        return side_to_move + 2 * total

    def decode(self, state: int):
        """Return ``(squares, types, side_to_move)``. Captured slots use -1."""
        stm = state & 1
        rest = state >> 1
        radix = self._radix
        squares, types = [], []
        for _ in range(self.nslots):
            v = rest % radix
            rest //= radix
            if v == 0:
                squares.append(CAPTURED)
                types.append(CAPTURED)
            else:
                v -= 1
                squares.append(v // NTYPE)
                types.append(v % NTYPE)
        return squares, types, stm

    def occupancy(self, squares):
        """Square -> slot index, or -1 when empty."""
        occ = [-1] * self.geometry.nsq
        for i, sq in enumerate(squares):
            if sq != CAPTURED:
                occ[sq] = i
        return occ

    # -------------------------------------------------------------- attacks

    def attacked(self, target: int, by_colour: int, squares, types, occ) -> bool:
        """Is ``target`` attacked by any piece of ``by_colour``?"""
        material = self.material

        for sq in self._knight_tbl[target]:
            s = occ[sq]
            if s >= 0 and material[s][0] == by_colour and types[s] == KNIGHT:
                return True

        for sq in self._king_tbl[target]:
            s = occ[sq]
            if s >= 0 and material[s][0] == by_colour and types[s] == KING:
                return True

        # A pawn of `by_colour` attacks `target` from the squares that a pawn of
        # the opposite colour standing on `target` would itself attack.
        for sq in self._pawn_atk[1 - by_colour][target]:
            s = occ[sq]
            if s >= 0 and material[s][0] == by_colour and types[s] == PAWN:
                return True

        rays = self._rays[target]
        for d in range(8):
            straight = d < 4  # first four directions are orthogonal
            for sq in rays[d]:
                s = occ[sq]
                if s < 0:
                    continue
                if material[s][0] == by_colour:
                    ty = types[s]
                    if ty == QUEEN or ty == (ROOK if straight else BISHOP):
                        return True
                break  # first blocker in this direction ends the scan
        return False

    def in_check(self, state: int, colour: int | None = None) -> bool:
        squares, types, stm = self.decode(state)
        colour = stm if colour is None else colour
        occ = self.occupancy(squares)
        king_sq = squares[self._king_slot[colour]]
        return self.attacked(king_sq, 1 - colour, squares, types, occ)

    # ---------------------------------------------------------------- moves

    def successors(self, state: int) -> list[int]:
        """All states reachable by one legal move. Empty list means terminal."""
        squares, types, stm = self.decode(state)
        occ = self.occupancy(squares)
        material = self.material
        king_slot = self._king_slot[stm]
        out: list[int] = []

        def emit(slot: int, dest: int, new_type: int | None = None) -> None:
            """Apply slot->dest, keep it only if our own king ends up safe."""
            victim = occ[dest]
            if victim >= 0 and material[victim][0] == stm:
                return
            old_sq, old_ty = squares[slot], types[slot]
            squares[slot] = dest
            if new_type is not None:
                types[slot] = new_type
            occ[old_sq] = -1
            occ[dest] = slot
            v_sq = None
            if victim >= 0:
                v_sq, squares[victim] = squares[victim], CAPTURED

            king_sq = squares[king_slot]
            if not self.attacked(king_sq, 1 - stm, squares, types, occ):
                out.append(self.encode(squares, types, 1 - stm))

            if victim >= 0:
                squares[victim] = v_sq
            squares[slot], types[slot] = old_sq, old_ty
            occ[dest] = victim
            occ[old_sq] = slot

        for slot, (colour, _) in enumerate(material):
            if colour != stm:
                continue
            sq = squares[slot]
            if sq == CAPTURED:
                continue
            ty = types[slot]

            if ty == KING:
                for dest in self._king_tbl[sq]:
                    emit(slot, dest)
            elif ty == KNIGHT:
                for dest in self._knight_tbl[sq]:
                    emit(slot, dest)
            elif ty == PAWN:
                self._pawn_moves(slot, sq, stm, squares, occ, emit)
            else:
                dirs = range(8) if ty == QUEEN else (range(4) if ty == ROOK else range(4, 8))
                rays = self._rays[sq]
                for d in dirs:
                    for dest in rays[d]:
                        blocker = occ[dest]
                        if blocker >= 0:
                            if material[blocker][0] != stm:
                                emit(slot, dest)
                            break
                        emit(slot, dest)
        return out

    def _pawn_moves(self, slot, sq, stm, squares, occ, emit) -> None:
        geo = self.geometry
        push = geo.pawn_push(stm)
        promo_rank = geo.promotion_rank(stm)
        home_rank = 1 if stm == WHITE else geo.ranks - 2

        forward = sq + push
        if 0 <= forward < geo.nsq and occ[forward] < 0:
            if geo.rank_of(forward) == promo_rank:
                for ty in self.promotions:
                    emit(slot, forward, ty)
            else:
                emit(slot, forward)
                if self.pawn_double_step and geo.rank_of(sq) == home_rank:
                    double = forward + push
                    if 0 <= double < geo.nsq and occ[double] < 0:
                        emit(slot, double)

        for dest in self._pawn_atk[stm][sq]:
            victim = occ[dest]
            if victim >= 0 and self.material[victim][0] != stm:
                if geo.rank_of(dest) == promo_rank:
                    for ty in self.promotions:
                        emit(slot, dest, ty)
                else:
                    emit(slot, dest)

    # ------------------------------------------------------------- validity

    def is_legal_state(self, state: int) -> bool:
        """A state is legal when both kings are on board and the side that just
        moved is not left in check (kings also may not stand adjacent)."""
        squares, types, stm = self.decode(state)
        seen = set()
        for i, sq in enumerate(squares):
            if sq == CAPTURED:
                continue
            if sq in seen:
                return False
            seen.add(sq)
        for slot in self._king_slot:
            if squares[slot] == CAPTURED:
                return False
        occ = self.occupancy(squares)
        waiting = 1 - stm
        return not self.attacked(
            squares[self._king_slot[waiting]], stm, squares, types, occ
        )

    def is_checkmate(self, state: int) -> bool:
        return not self.successors(state) and self.in_check(state)

    def is_stalemate(self, state: int) -> bool:
        return not self.successors(state) and not self.in_check(state)

    # ---------------------------------------------------------------- pretty

    def render(self, state: int) -> str:
        squares, types, stm = self.decode(state)
        geo = self.geometry
        grid = [["." for _ in range(geo.files)] for _ in range(geo.ranks)]
        for slot, sq in enumerate(squares):
            if sq == CAPTURED:
                continue
            letter = PIECE_LETTER[types[slot]]
            grid[geo.rank_of(sq)][geo.file_of(sq)] = (
                letter if self.material[slot][0] == WHITE else letter.lower()
            )
        rows = [f"{r + 1} " + " ".join(grid[r]) for r in reversed(range(geo.ranks))]
        files = "  " + " ".join(chr(ord("a") + f) for f in range(geo.files))
        return "\n".join(rows + [files, f"{'White' if stm == WHITE else 'Black'} to move"])

    def parse(self, board: str, side_to_move: int = WHITE) -> int:
        """Build a state from an ASCII diagram (top row = highest rank)."""
        rows = [r.split() for r in board.strip().splitlines()]
        rows.reverse()
        geo = self.geometry
        squares = [CAPTURED] * self.nslots
        types = [CAPTURED] * self.nslots
        used = set()
        for r, row in enumerate(rows):
            for f, cell in enumerate(row):
                if cell == ".":
                    continue
                colour = WHITE if cell.isupper() else BLACK
                ptype = PIECE_LETTER.index(cell.upper())
                for slot, (c, t) in enumerate(self.material):
                    if slot in used or c != colour:
                        continue
                    if t == ptype or (t == PAWN and ptype in self.promotions):
                        squares[slot], types[slot] = geo.square(f, r), ptype
                        used.add(slot)
                        break
                else:
                    raise ValueError(f"no free slot for {cell}")
        return self.encode(squares, types, side_to_move)
