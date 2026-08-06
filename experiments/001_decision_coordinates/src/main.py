import chess
import chess.pgn

from encoder import encode_position
from output import save_csv


def analyse_game(filename):

    records = []

    with open(filename) as game_file:

        game = chess.pgn.read_game(game_file)


    board = game.board()


    for move in game.mainline_moves():

        record = encode_position(
            board,
            move
        )

        record["move"] = board.san(move)

        records.append(record)

        board.push(move)


    return records



if __name__ == "__main__":

    input_game = "games/sample.pgn"

    output_file = "results/decision_coordinates.csv"


    records = analyse_game(
        input_game
    )


    save_csv(
        records,
        output_file
    )


    print(
        f"Encoded {len(records)} positions"
    )
