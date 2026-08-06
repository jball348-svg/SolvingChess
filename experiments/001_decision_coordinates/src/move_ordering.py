def order_moves(board, moves):
    """
    Defines the ordering of the decision space.

    Currently:
    - Sort moves by UCI notation.

    This is deliberately isolated so future experiments
    can replace the ordering logic.
    """

    return sorted(
        moves,
        key=lambda move: move.uci()
    )
