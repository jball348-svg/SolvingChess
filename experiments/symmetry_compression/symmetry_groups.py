"""Dihedral symmetry group D4 transformations for a square board."""


def rotate90(square, size):
    x, y = square
    return (size - 1 - y, x)


def reflect_horizontal(square, size):
    x, y = square
    return (x, size - 1 - y)


def transform_position(position, transform, size=4):
    """Apply a named D4 transformation to a position."""
    white, black = position

    def apply(square):
        if transform == "identity":
            return square
        if transform == "rotate90":
            return rotate90(square, size)
        if transform == "rotate180":
            return rotate90(rotate90(square, size), size)
        if transform == "rotate270":
            return rotate90(rotate90(rotate90(square, size), size), size)
        if transform == "reflect_horizontal":
            return reflect_horizontal(square, size)
        if transform == "reflect_vertical":
            x, y = square
            return (size - 1 - x, y)
        if transform == "reflect_diagonal":
            return (square[1], square[0])
        if transform == "reflect_anti_diagonal":
            x, y = square
            return (size - 1 - y, size - 1 - x)
        raise ValueError(transform)

    return (apply(white), apply(black))


TRANSFORMS = [
    "identity",
    "rotate90",
    "rotate180",
    "rotate270",
    "reflect_horizontal",
    "reflect_vertical",
    "reflect_diagonal",
    "reflect_anti_diagonal",
]


def all_symmetries(position, size=4):
    """Return all equivalent positions under D4."""
    return [transform_position(position, t, size) for t in TRANSFORMS]
