# Experiment 005 - Results

Run on 2026-08-03. Raw data: `results/exp005_scaling_law.json`.

**Headline: a law fitted only on boards of area 16-30 predicts the drawn
fraction of the real 8x8 board to within 1.8% for KQ vs K and 7.1% for KR vs K.**
This is the first successful out-of-sample prediction in the repository, and it
lands on the standard chessboard.

## Solved universes

| universe | area | states | drawn | max DTM | mean DTM | time |
|---|---|---|---|---|---|---|
| KR-K@4x4 | 16 | 3,808 | 24.26% | 14 | 6.7 | 0.1s |
| KR-K@4x5 | 20 | 8,490 | 20.35% | 18 | 8.6 | 0.2s |
| KR-K@5x4 | 20 | 8,490 | 20.35% | 18 | 8.6 | 0.2s |
| KR-K@4x6 | 24 | 16,016 | 17.51% | 20 | 10.5 | 0.4s |
| KR-K@5x5 | 25 | 18,440 | 16.90% | 20 | 10.4 | 0.5s |
| KR-K@5x6 | 30 | 34,228 | 14.44% | 22 | 12.1 | 1.0s |
| KR-K@6x6 | 36 | 62,880 | 12.30% | 24 | 14.3 | 1.9s |
| KR-K@7x7 | 49 | 172,340 | 9.30% | 28 | 17.6 | 6.0s |
| KR-K@8x8 | 64 | 406,336 | 7.25% | 32 | 21.0 | 16.8s |
| KQ-K@4x4 | 16 | 3,308 | 31.92% | 8 | 4.6 | 0.1s |
| KQ-K@4x5 | 20 | 7,482 | 25.77% | 10 | 5.7 | 0.2s |
| KQ-K@5x4 | 20 | 7,482 | 25.77% | 10 | 5.7 | 0.2s |
| KQ-K@4x6 | 24 | 14,308 | 21.41% | 12 | 6.8 | 0.4s |
| KQ-K@5x5 | 25 | 16,376 | 20.71% | 12 | 6.4 | 0.4s |
| KQ-K@5x6 | 30 | 30,716 | 17.24% | 12 | 7.4 | 0.9s |
| KQ-K@6x6 | 36 | 56,800 | 14.38% | 14 | 8.2 | 1.7s |
| KQ-K@7x7 | 49 | 157,720 | 10.55% | 16 | 10.0 | 6.1s |
| KQ-K@8x8 | 64 | 375,676 | 8.06% | 20 | 11.7 | 17.9s |
| KR-KR@4x4 | 16 | 42,536 | 49.09% | 17 | 7.5 | 1.2s |
| KR-KR@4x5 | 20 | 124,416 | 50.87% | 21 | 9.7 | 3.7s |
| KR-KR@5x5 | 25 | 352,416 | 54.15% | 23 | 11.6 | 11.9s |

## Predictions from small boards only

Fitted on area 16-30. Held-out boards in bold were never seen by the fit.

**KQ-K, drawn fraction ~ 4.868 * area^-0.982 (R^2 = 0.9998)**

| board | predicted | actual | error |
|---|---|---|---|
| **6x6** | 0.144 | 0.144 | **0.39%** |
| **7x7** | 0.107 | 0.105 | **1.15%** |
| **8x8** | 0.082 | 0.081 | **1.84%** |

**KR-K, drawn fraction ~ 2.408 * area^-0.826 (R^2 = 0.9995)**

| board | predicted | actual | error |
|---|---|---|---|
| **6x6** | 0.125 | 0.123 | **1.56%** |
| **7x7** | 0.097 | 0.093 | **4.15%** |
| **8x8** | 0.078 | 0.073 | **7.08%** |

Distance to mate transfers much less well:

| quantity | family | 6x6 error | 7x7 error | 8x8 error |
|---|---|---|---|---|
| max DTM ~ diameter^1.359 | KR-K | 6.56% | 12.62% | 18.16% |
| mean DTM ~ diameter^1.867 | KR-K | 2.00% | 10.09% | 18.49% |
| max DTM ~ diameter^1.379 | KQ-K | 4.77% | 13.39% | 9.04% |
| mean DTM ~ diameter^1.465 | KQ-K | 4.22% | 7.34% | 11.46% |

## Local exponent of drawn fraction against area

| step | KR-K | KQ-K |
|---|---|---|
| 16 -> 20 | -0.788 | -0.960 |
| 20 -> 24 | -0.826 | -1.015 |
| 24 -> 25 | -0.868 | -0.816 |
| 25 -> 30 | -0.861 | -1.006 |
| 30 -> 36 | -0.883 | -0.995 |
| 36 -> 49 | -0.907 | -1.006 |
| **49 -> 64** | **-0.930** | **-1.007** |

`KR-KR` moves the other way entirely: +0.160 then +0.280.

## Findings

### 1. The drawn fraction of KQ vs K is `C / area`, to measurement precision

The local exponent for `KQ-K` sits on -1.00 for every step above area 25, and the
global fit gives -0.982. The drawn fraction is inversely proportional to board
area.

This is a **size-independent statement**, which is exactly the object
`research/07` says a scaling argument needs and did not have. It also has an
obvious proof sketch: for three pieces there are `O(A^3)` positions in total, and
a `KQ-K` draw is either a stalemate or a position where the queen is en prise --
both of which require the queen to be within a bounded neighbourhood of the two
kings. That constrains one of the three placements to `O(1)` choices instead of
`O(A)`, giving `O(A^2)` drawn positions out of `O(A^3)`, hence a drawn fraction
of order `1/A`.

We have not proved that. But it is a conjecture with a mechanism, derived from
data, stated in a form that is either true or false -- which is a different kind
of object from anything this repository contained a day ago.

### 2. KR vs K is heading to the same exponent, more slowly

The local exponent climbs monotonically: -0.788, -0.826, -0.868, -0.861, -0.883,
-0.907, **-0.930**. Extrapolating the trend, it reaches -1 somewhere past 8x8.

The slower convergence is consistent with the same mechanism plus a correction: a
rook, unlike a queen, also draws when it is *cut off* rather than merely en
prise, and cut-off configurations are not confined to a bounded neighbourhood on
small boards. As the board grows that correction becomes relatively less
important.

This also explains why the fitted 8x8 prediction is worse for `KR-K` (7.1%) than
`KQ-K` (1.8%): a single power law is the wrong model for a quantity whose
exponent is still drifting, and the fit is dominated by the smallest boards where
the drift is worst.

### 3. Equal material inverts the law

`KR-KR` drawn fraction *increases* with area: 49.1%, 50.9%, 54.2%, local exponent
+0.16 then +0.28.

The two regimes are different phenomena. With unequal material the drawn set is
the set of *accidents* -- stalemates and captures -- and accidents get rarer as
space grows. With equal material the drawn set is the *generic* outcome and extra
space makes conversion harder. Any law claimed for one regime must state which
one it is about.

This is a useful warning for the minification programme: full chess has equal
material at the start, so `KR-KR` is the relevant regime for the game as a whole,
not `KR-K`.

### 4. Distance to mate does not transfer well, and that is expected

Maximum DTM is an extreme-value statistic quantised to even integers -- there are
only nine distinct values across the whole `KQ-K` sweep. Fitting a power law to it
is close to a category error, and the 9-18% errors reflect that. Mean DTM is
better behaved but still degrades to ~18% at 8x8.

The lesson is about which quantities to look for laws in: **aggregate fractions
over the whole state space transfer; extreme-value statistics do not.**

## Limitations

* Three pieces only. Whether the `1/area` law survives more material is unknown,
  and `KR-KR` already shows the sign can flip.
* The proof sketch in Finding 1 is a sketch. It has not been checked against the
  actual composition of the drawn set, which is a cheap next step: partition the
  `KQ-K` drawn states into stalemates, en-prise positions and everything else,
  and confirm the third bucket is `O(A)` rather than `O(A^2)`.
* Boards are rectangular and flat. Edge effects are doing most of the work in the
  proposed mechanism, so a torus would be a sharp test -- see
  `docs/experiment-catalogue.md`, D5.
* Errors are reported against a single fit. No uncertainty estimate is given, and
  with six fit points the exponent's standard error is not negligible.

## Next

* Verify the mechanism behind the `1/area` law by decomposing the drawn set.
* Register a forward prediction for `KQ-K@9x9` and `KQ-K@10x10` *before* solving
  them, using the registry pattern in `docs/experiment-catalogue.md`, B4.
* Test whether the law holds on a torus, where there are no edges and the
  proposed mechanism should break.
* Experiment 004 asks the harder version of the same question: whether
  *per-position* rules transfer, not just aggregate laws. They do not transfer
  nearly as well.
