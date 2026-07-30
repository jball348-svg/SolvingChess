# Experiment 001

# Symmetry Compression in a Tiny Chess Universe

## Question

Can mathematical symmetry reduce the apparent complexity of chess state spaces?

## Method

A 4x4 king-versus-king universe was generated. Legal positions were reduced under the dihedral symmetry group of the square:

\[
D_4
\]

Each position was mapped to a canonical representative of its equivalence class.

## Results

Expected:

```
Raw states: 78
Reduced states: 13
Compression: 83.33%
```

## Interpretation

This does not solve chess.

It demonstrates that:

- coordinate representations contain redundancy
- group theory can collapse equivalent states
- quotient representations may provide computational advantages

## Next experiments

### Experiment 002

Add King + Rook + King.

Questions:

- Does symmetry still compress?
- Does compression preserve tactical meaning?

### Experiment 003

Create the state transition graph:

\[
G=(V,E)
\]

Compare the original graph with the quotient graph:

\[
G/D_4
\]

Measure:

- graph size reduction
- shortest paths
- distance-to-mate preservation

### Experiment 004

Extend to 4D:

\[
\{1,...,8\}^4
\]

Study hypercube symmetries and orbit sizes.
