"""Run the symmetry compression experiment."""

from enumerate_positions import generate_positions
from symmetry_groups import all_symmetries


def find_classes(positions, size=4):
    """Group states into D4 equivalence classes."""
    classes = {}

    for position in positions:
        canonical = min(all_symmetries(position, size))
        classes.setdefault(canonical, []).append(position)

    return classes


if __name__ == "__main__":
    positions = generate_positions(4)
    classes = find_classes(positions)

    orbit_sizes = [len(v) for v in classes.values()]
    raw = len(positions)
    reduced = len(classes)
    compression = (1 - reduced / raw) * 100

    print("Experiment: K vs K on 4x4 board")
    print(f"Raw states: {raw}")
    print(f"Symmetry classes: {reduced}")
    print(f"Compression: {compression:.2f}%")
    print(f"Average orbit size: {sum(orbit_sizes) / len(orbit_sizes):.2f}")
    print(f"Largest orbit: {max(orbit_sizes)}")
    print(f"Smallest orbit: {min(orbit_sizes)}")
