"""Board-size-independent positional features.

The point of these is transfer. A feature like "the defending king is on square
a1" is useless across board sizes; a feature like "the defending king can reach
under 10% of the board" means the same thing on 4x4 and on 8x8. Every feature
here is either a boolean, a small capped distance, or a bucketed *fraction* of
the board, so a rule fitted on one geometry can be evaluated on another without
retraining.

The set is deliberately small and deliberately made of things a human would say
about an endgame -- confinement, opposition, the king on the edge, a piece en
prise. If a rule built from these predicts values on a board it was never fitted
to, that is evidence the concept is size-independent. If it does not, the
concept was an artefact of the training geometry, which is exactly what
``research/07-scaling-and-proof-strategy.md`` warns about.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import KING, PAWN, WHITE
from .rules import CAPTURED, Rules

FEATURE_NAMES = (
    "in_check",
    "stm_is_stronger",
    "king_distance",
    "defender_edge_distance",
    "defender_corner_distance",
    "opposition",
    "mobility_bucket",
    "confinement_bucket",
    "confinement_absolute",
    "attacker_piece_en_prise",
    "slider_cuts_between_kings",
    "defender_has_material",
)

# Human-readable value labels, used when a learned rule is printed.
FEATURE_VALUES = {
    "opposition": {0: "none", 1: "direct", 2: "distant"},
    "mobility_bucket": {0: "0", 1: "1", 2: "2", 3: "3-4", 4: "5-8", 5: "9+"},
    "confinement_bucket": {0: "<5%", 1: "<10%", 2: "<20%", 3: "<40%", 4: ">=40%"},
    "confinement_absolute": {0: "<=1 sq", 1: "<=2 sq", 2: "<=4 sq", 3: "<=8 sq",
                             4: "<=16 sq", 5: ">16 sq"},
}

# Two rival normalisations of the same underlying quantity, kept side by side so
# that experiment 004 can ask which one is the size-independent concept: is a
# king "confined" when it holds a small *share* of the board, or a small
# *number of squares* regardless of how big the board is?
CONFINEMENT_FRACTION = "confinement_bucket"
CONFINEMENT_ABSOLUTE = "confinement_absolute"


def _bucket_mobility(n: int) -> int:
    if n <= 2:
        return n
    if n <= 4:
        return 3
    if n <= 8:
        return 4
    return 5


def _bucket_fraction(fraction: float) -> int:
    for i, edge in enumerate((0.05, 0.10, 0.20, 0.40)):
        if fraction < edge:
            return i
    return 4


def _bucket_count(count: int) -> int:
    for i, edge in enumerate((1, 2, 4, 8, 16)):
        if count <= edge:
            return i
    return 5


@dataclass
class FeatureExtractor:
    """Computes the feature vector for states of one universe."""

    rules: Rules

    def __post_init__(self) -> None:
        rules = self.rules
        counts = [0, 0]
        for colour, ptype in rules.material:
            if ptype != KING:
                counts[colour] += 1
        # The "attacker" is the side with more non-king material; ties resolve to
        # White so the feature is well defined for symmetric material.
        self.stronger = WHITE if counts[WHITE] >= counts[1 - WHITE] else 1 - WHITE
        self.counts = counts

    # ------------------------------------------------------------------ helpers

    def _confinement(self, defender_king: int, defender: int, squares, types, occ) -> float:
        """Fraction of the board the defending king can reach, ignoring replies.

        Flood fill over squares that are neither attacked by the attacker nor
        occupied by an attacker piece. This is the classic "box" the stronger
        side draws around a lone king, expressed as a board fraction so it means
        the same thing at every size.
        """
        rules = self.rules
        attacker = 1 - defender
        seen = {defender_king}
        stack = [defender_king]
        while stack:
            sq = stack.pop()
            for nxt in rules._king_tbl[sq]:
                if nxt in seen:
                    continue
                slot = occ[nxt]
                if slot >= 0 and rules.material[slot][0] == attacker:
                    continue
                if rules.attacked(nxt, attacker, squares, types, occ):
                    continue
                seen.add(nxt)
                stack.append(nxt)
        return len(seen)

    def _opposition(self, a: int, b: int) -> int:
        """0 none, 1 direct opposition, 2 distant opposition."""
        geo = self.rules.geometry
        df = abs(geo.file_of(a) - geo.file_of(b))
        dr = abs(geo.rank_of(a) - geo.rank_of(b))
        aligned = df == 0 or dr == 0 or df == dr
        if not aligned:
            return 0
        gap = max(df, dr)
        if gap == 2:
            return 1
        return 2 if gap % 2 == 0 else 0

    # ------------------------------------------------------------------ extract

    def extract(self, state: int) -> tuple:
        rules = self.rules
        geo = rules.geometry
        squares, types, stm = rules.decode(state)
        occ = rules.occupancy(squares)

        # Which side is the attacker *in this state*: material can vanish, so
        # recount rather than trusting the signature.
        alive = [0, 0]
        for slot, sq in enumerate(squares):
            if sq != CAPTURED and types[slot] != KING:
                alive[rules.material[slot][0]] += 1
        attacker = self.stronger if alive[self.stronger] >= alive[1 - self.stronger] \
            else 1 - self.stronger
        defender = 1 - attacker

        wk = squares[rules._king_slot[attacker]]
        bk = squares[rules._king_slot[defender]]

        df = abs(geo.file_of(wk) - geo.file_of(bk))
        dr = abs(geo.rank_of(wk) - geo.rank_of(bk))
        king_distance = min(4, max(df, dr))

        f = geo.file_of(bk)
        r = geo.rank_of(bk)
        edge_distance = min(3, min(f, geo.files - 1 - f, r, geo.ranks - 1 - r))
        corner_distance = min(4, min(
            max(f, r),
            max(geo.files - 1 - f, r),
            max(f, geo.ranks - 1 - r),
            max(geo.files - 1 - f, geo.ranks - 1 - r),
        ))

        mobility = _bucket_mobility(len(rules.successors(state)))
        reachable = self._confinement(bk, defender, squares, types, occ)

        en_prise = 0
        for slot, sq in enumerate(squares):
            if sq == CAPTURED or types[slot] == KING:
                continue
            if rules.material[slot][0] != attacker:
                continue
            if max(abs(geo.file_of(sq) - f), abs(geo.rank_of(sq) - r)) == 1:
                if not rules.attacked(sq, attacker, squares, types, occ):
                    en_prise = 1
                    break

        cuts = 0
        lo_f, hi_f = sorted((geo.file_of(wk), f))
        lo_r, hi_r = sorted((geo.rank_of(wk), r))
        for slot, sq in enumerate(squares):
            if sq == CAPTURED or types[slot] in (KING, PAWN):
                continue
            if rules.material[slot][0] != attacker:
                continue
            sf, sr = geo.file_of(sq), geo.rank_of(sq)
            if lo_f < sf < hi_f or lo_r < sr < hi_r:
                cuts = 1
                break

        return (
            int(rules.in_check(state)),
            int(stm == attacker),
            king_distance,
            edge_distance,
            corner_distance,
            self._opposition(wk, bk),
            mobility,
            _bucket_fraction(reachable / geo.nsq),
            _bucket_count(reachable),
            en_prise,
            cuts,
            int(alive[defender] > 0),
        )

    def extract_many(self, states) -> list:
        return [self.extract(s) for s in states]
