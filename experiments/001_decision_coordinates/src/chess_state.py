import chess


def get_legal_moves(board):
    """
    Returns all legal moves from a chess position.
    """

    return list(board.legal_moves)


def get_fen(board):
    """
    Returns the FEN representation of a position.
    """

    return board.fen()
