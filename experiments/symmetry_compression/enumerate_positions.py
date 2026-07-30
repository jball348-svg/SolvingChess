"""Enumerate legal king-versus-king positions on a small board."""


def kings_adjacent(a, b):
    """Return True if two kings are touching."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) == 1


def generate_positions(size=4):
    """Generate all legal white king / black king positions.

    Positions are represented as:
        ((white_x, white_y), (black_x, black_y))
    """
    positions = []

    for wx in range(size):
        for wy in range(size):
            white = (wx, wy)
            for bx in range(size):
                for by in range(size):
                    black = (bx, by)

                    if white == black:
                        continue

                    if kings_adjacent(white, black):
                        continue

                    positions.append((white, black))

    return positions


if __name__ == "__main__":
    print(len(generate_positions(4)))
