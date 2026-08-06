import streamlit as st
import sys
from pathlib import Path

# Allow importing from src
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "src"))

from encoder import encode_position

import chess
import chess.pgn
import io


st.title("Solving Chess - Decision Coordinates")

st.write(
    """
    Paste a PGN game below.

    The app converts each move into:

    FEN → deg+ → chosen edge
    """
)


pgn_text = st.text_area(
    "Paste PGN here",
    height=200
)


if st.button("Analyse"):

    game = chess.pgn.read_game(
        io.StringIO(pgn_text)
    )

    board = game.board()

    results = []


    for move in game.mainline_moves():

        record = encode_position(
            board,
            move
        )

        record["move"] = board.san(move)

        results.append(record)

        board.push(move)


    st.success(
        f"Encoded {len(results)} positions"
    )

    st.dataframe(results)
