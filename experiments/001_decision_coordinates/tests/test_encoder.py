import chess

from src.encoder import encode_position


def test_initial_position():

    board = chess.Board()

    move = chess.Move.from_uci("e2e4")

    result = encode_position(
        board,
        move
    )

    assert result["deg_plus"] == 20

    assert result["chosen_edge"] > 0
