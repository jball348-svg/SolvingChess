from chess_state import get_legal_moves, get_fen
from move_ordering import order_moves


def encode_position(board, move):
    """
    Converts a chess position and chosen move
    into decision coordinates.
    """

    legal_moves = get_legal_moves(board)

    ordered_moves = order_moves(
        board,
        legal_moves
    )

    deg_plus = len(ordered_moves)

    chosen_edge = (
        ordered_moves.index(move) + 1
    )

    return {
        "fen": get_fen(board),
        "deg_plus": deg_plus,
        "chosen_edge": chosen_edge
    }
