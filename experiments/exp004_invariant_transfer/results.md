# Experiment 004 - Results

Run on 2026-08-03. Raw data: `results/exp004_invariant_transfer.json`.

**Headline: per-position rules transfer, but they decay. Every rule fitted on
4x4 loses accuracy monotonically as the board grows, and no feature
normalisation fixes it.** Read alongside experiment 005, which found that an
*aggregate* law transfers almost exactly, the contrast is the most useful thing
this repository has measured.

## Transfer by feature normalisation

`fraction` = confinement as a share of the board. `absolute` = confinement as a
square count. `both` = the learner chooses.

| fitted on | features | evaluated on | nodes | accuracy | baseline | lift | unseen-value fallback |
|---|---|---|---|---|---|---|---|
| KR-K@4x4 | fraction | KR-K@4x4 (train) | 39 | 0.9590 | 0.4128 | +0.9302 | 0.0% |
| KR-K@4x4 | fraction | KR-K@5x5 | 39 | 0.7755 | 0.4492 | +0.5924 | 11.7% |
| KR-K@4x4 | fraction | KR-K@6x6 | 39 | 0.6997 | 0.4719 | +0.4314 | 16.0% |
| KR-K@4x4 | fraction | KR-K@8x8 | 39 | 0.6144 | 0.5001 | +0.2287 | 21.7% |
| KR-K@4x4 | absolute | KR-K@4x4 (train) | 34 | 0.9853 | 0.4128 | +0.9750 | 0.0% |
| KR-K@4x4 | absolute | KR-K@5x5 | 34 | 0.6935 | 0.4492 | +0.4435 | 6.6% |
| KR-K@4x4 | absolute | KR-K@6x6 | 34 | 0.6130 | 0.4719 | +0.2672 | 30.0% |
| KR-K@4x4 | absolute | KR-K@8x8 | 34 | 0.8079 | 0.5001 | +0.6157 | **68.7%** |
| KR-K@4x4 | both | KR-K@8x8 | 35 | 0.8079 | 0.5001 | +0.6157 | **73.7%** |
| KQ-K@4x4 | fraction | KQ-K@4x4 (train) | 34 | 1.0000 | 0.4353 | +1.0000 | 0.0% |
| KQ-K@4x4 | fraction | KQ-K@5x5 | 34 | 0.9502 | 0.4890 | +0.9025 | 6.3% |
| KQ-K@4x4 | fraction | KQ-K@6x6 | 34 | 0.8774 | 0.5154 | +0.7470 | 9.8% |
| KQ-K@4x4 | fraction | KQ-K@8x8 | 34 | 0.7605 | 0.5353 | +0.4847 | 10.6% |
| KQ-K@4x4 | absolute | KQ-K@8x8 | 47 | 0.6680 | 0.5353 | +0.2856 | 38.9% |
| KQ-K@4x4 | both | KQ-K@8x8 | 35 | 0.7196 | 0.5353 | +0.3966 | 19.5% |
| KR-K@4x4 | fraction | KQ-K@5x5 | 39 | 0.8705 | 0.4890 | +0.7467 | 8.2% |
| KR-K@4x4 | fraction | KQ-K@8x8 | 39 | 0.7332 | 0.5353 | +0.4259 | 16.3% |
| KP-K@4x4 | fraction | KP-K@4x4 (train) | 161 | 0.8300 | 0.6370 | +0.5316 | 0.0% |
| KP-K@4x4 | fraction | KP-K@5x5 | 161 | 0.7621 | 0.5962 | +0.4107 | 13.0% |
| KP-K@4x4 | fraction | KP-K@4x6 | 161 | 0.7725 | 0.6069 | +0.4212 | 12.6% |
| KP-K@4x4 | fraction | KP-K@6x6 | 161 | 0.7100 | 0.5683 | +0.3283 | 23.2% |

The full 48-row table, including every `absolute` and `both` transfer, is in the
results JSON.

## Findings

### 1. A near-result that was an artefact

The first run of this experiment reported that `absolute` normalisation
transferred *better* to 8x8 than `fraction` -- 0.808 against 0.614 -- which would
have been a clean and quotable finding about which concept is size-independent.

It was wrong. The fallback instrumentation added afterwards shows that transfer
had a **68.7% unseen-value fallback rate**: on a 4x4 board the top confinement
bucket ("more than 16 squares") is *unreachable*, because the board only has 16
squares. Two thirds of the 8x8 predictions never reached a leaf and were answered
by an internal node's majority class. The rule was not transferring; it was
guessing, and guessing happened to work.

This is recorded prominently because it is the most instructive thing in the run.
A structural claim about chess would have been built on a bucket boundary. The
lesson generalises: **any transfer metric needs an accompanying measure of how
much of the model was actually exercised.**

With fallbacks accounted for, `fraction` is the better normalisation everywhere,
which was prediction 2 and holds.

### 2. Rules beat baseline everywhere, and decay everywhere

Honest numbers, `fraction` features, fallback under 25% throughout:

| fitted on | train | 5x5 | 6x6 | 8x8 |
|---|---|---|---|---|
| KR-K@4x4 | 0.959 | 0.776 | 0.700 | 0.614 |
| KQ-K@4x4 | 1.000 | 0.950 | 0.877 | 0.761 |
| KP-K@4x4 | 0.830 | 0.762 | 0.773 (4x6) | 0.710 |

Never chance -- lift over the majority baseline stays between +0.23 and +0.90.
But the decay is monotone and substantial, and by 8x8 the `KR-K` rule is only 11
points above a coin flip.

So: the features carry real, transferable signal about the game, and they do not
carry a *size-independent* description of it. `research/07`'s option (c) -- a
size-independent invariant verified on small cases -- is not satisfied by
anything in this feature set.

### 3. Concepts are more piece-portable than size-portable

The surprise, and prediction 3 was wrong about it.

A rule fitted on `KR-K@4x4` and applied to **a different piece on a bigger
board** scores 0.871 on `KQ-K@5x5` -- better than the same rule does on
`KR-K@6x6` (0.700), its own family. On 8x8 it scores 0.733 on queens against
0.614 on rooks.

Changing the piece hurts less than changing the board. Confinement, en prise,
edge distance and opposition apparently describe *the defending king's
predicament* rather than anything about the attacking piece -- which is a more
general concept than we expected, and points at where a genuine invariant might
live. It also means the pieces are less important to the structure than the
geometry is, which is an odd and rather chess-specific thing to be able to say.

### 4. Pawns need five times the rule and still do worse

`KP-K@4x4` needs **161 nodes** to reach 83% on its own board, against 34-39 nodes
for 96-100% on the pawnless universes.

This is the same conclusion experiment 003 reached from the other direction:
pawn positions carry structure that geometric features do not capture. Experiment
003 said there is 2.7x more compressible structure in `KP-K` than symmetry finds;
this says our feature vocabulary is not the thing that finds it.

### 5. The learned rule is readable, and it is the human rule

The `fraction` rule on `KR-K@4x4`, in essence:

* if the defending side is to move and the attacking piece is *not* en prise,
  and the king is confined to under 40% of the board -- **lost**;
* if the attacking piece *is* en prise -- **drawn**;
* if the attacking side is to move and the king is confined to under 40% --
  **won**;
* above 40% confinement, it depends on mobility, edge distance and opposition.

That is recognisably the textbook `KR` vs `K` method -- cut the king off, shrink
the box, do not hang the rook -- recovered from a solved table by a 39-node tree
with no chess knowledge supplied. The full tree is printed at the end of the run
output and stored in the results JSON.

The honest caveat: 96% is not a certificate. The remaining 4% is where the
theorem would live.

## Limitations

* Tables above 60,000 states are uniformly subsampled. The 8x8 figures are over
  60,000 of 406,336 states.
* Depth is capped at 6 and minimum leaf size at 30. A deeper tree memorises the
  training board and transfers worse; the cap was not tuned per trial, so the
  numbers are a floor rather than a best effort.
* Only three-piece pawnless universes and one pawnful one. Nothing here has been
  tested where both sides hold material.
* The majority baseline uses the *training* set's majority class, which is the
  right control for transfer but makes the baseline degenerate when the test
  universe has a very different value distribution.

## Next

* The decay curve itself is a measurement. Fit it: does accuracy fall like a
  power of board area, and does it asymptote above baseline or converge to it?
  That distinguishes "the invariant is approximate" from "the invariant is
  fictional".
* Feature ablation (`docs/experiment-catalogue.md`, B1) -- which single feature
  carries the transfer? If it is confinement alone, the invariant has a name.
* Try DTM regression instead of WDL classification
  (`docs/experiment-catalogue.md`, B2). A harder target that transfers would be
  far stronger evidence than an easy one that does not.
* Follow experiment 005's lead instead: aggregate statistics transferred to 1.8%
  where these rules manage 76%. The invariant to hunt may be statistical rather
  than positional.
