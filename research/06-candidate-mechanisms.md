# 06 - Candidate mechanisms

Ten routes to a solution, ranked by *expected information per unit of effort*
rather than by how exciting they sound. Each entry states the mechanism, the
smallest experiment that would produce evidence for or against it, and the
reason it might fail.

The ranking is deliberate. Mechanisms 1-4 are cheap and decisive; 5-7 are the
research-grade middle; 8-10 are long shots kept because their payoff is
qualitatively different.

---

## 1. Maximal value-preserving abstraction (bisimulation)

**Mechanism.** Collapse states that behave identically under play, not merely
states related by a board transformation. The coarsest such collapse is
computable on any solved universe by partition refinement, and it is a hard floor
for every sound abstraction that exists or could exist.

**Why it comes first.** It converts the entire "wrong mathematical space"
hypothesis from a slogan into a number. If the bisimulation quotient is barely
smaller than the symmetry quotient, no undiscovered representation is hiding
anything and several other mechanisms below are dead on arrival.

**Experiment.** `experiments/exp003_quotient_gap` -- built, runs today.

**Failure mode.** The quotient is computed *from* the values, so it cannot be
used to avoid solving. It bounds what is possible; it does not deliver it.

---

## 2. Scaling laws across universe families

**Mechanism.** Treat board size and material as continuous-ish parameters and
measure how solved quantities behave: drawn fraction, maximum distance to mate,
state count, structure gap. A quantity with a clean law across a family is a
candidate for something provable; a quantity that jumps around is not.

**Why it matters.** This is the only mechanism that directly attacks the
transfer problem (note 07). Everything else produces facts about one universe.

**Experiment.** Extend `exp002` to a full grid of board sizes and material
signatures, and fit. Partly built -- the ladder exists, the grid does not.

**Failure mode.** Small-board effects (edge dominance, kings never far apart)
may dominate at every size we can reach, so any law we fit is a law about tiny
boards.

---

## 3. Ultra-weak arguments: strategy stealing and pairing

**Mechanism.** Prove the value without a strategy. Strategy stealing proves the
first player cannot lose in games where an extra move never hurts; pairing
strategies prove draws by matching the opponent's resources.

**Why chess resists.** Both classical techniques break on chess for identifiable
reasons: chess has draws (so "cannot lose" is not "wins"), and zugzwang means an
extra move genuinely can hurt, which is exactly the hypothesis strategy stealing
needs.

**Experiment.** Test the *premise* rather than the conclusion. On solved
universes, measure the frequency of zugzwang -- states where the side to move
would prefer to pass. If zugzwang is vanishingly rare outside pawn endgames, a
strategy-stealing argument modulo a characterised exceptional set becomes
conceivable. Cheap to run on existing tables; not yet built.

**Failure mode.** Zugzwang is probably common enough on cramped boards to kill
it, and the exceptional set is probably not characterisable.

---

## 4. Mirroring and pairing strategies for the drawing side

**Mechanism.** A specialisation of 3 that suits chess's draw-richness. Rather
than proving White wins, prove **Black can always draw** by maintaining an
invariant -- a matching between White's threats and Black's answers preserved by
every move.

**Why it is attractive.** It targets the value chess is believed to have, and
"maintain an invariant" is a finite, checkable claim. It also sidesteps the need
for a strategy that is short: the invariant is the strategy.

**Experiment.** On solved micro-universes that are drawn, ask whether the drawn
region is closed under a *small* set of predicates -- can the set of drawn states
be described by a handful of conditions, each preserved by the drawing side's
best reply? Directly checkable against exp002's tables. Not built.

**Failure mode.** The invariant may exist but be as large as the table.

---

## 5. Learned invariants validated against ground truth

**Mechanism.** Fit cheap positional features to predict exact values on solved
universes, then test the fitted function on universes it was **not** fitted to.
This is the only mechanism here that gets an unambiguous verdict, because we
have exact labels for the entire state space rather than a sample.

**Why it is different from engine evaluation.** An engine's evaluation is judged
by playing strength. A candidate invariant is judged by whether it is *exactly*
constant on the classes it claims to describe. Those are different standards and
only the second is evidence of structure.

**Experiment.** Phase 3 of note 05. Fit on `KR-K@4x4`, test on `KR-K@5x5` and
`KR-K@4x6`. Not built; the highest-value unbuilt experiment in the repository.

**Failure mode.** The features that work are board-size specific, and nothing
transfers. That is itself an informative result and is why this is ranked high.

---

## 6. Decomposition and combinatorial game theory

**Mechanism.** Conway-style theory decomposes a game into independent components
and gives each a value in a group, so the whole is the sum of its parts. This
turns exponential search into arithmetic where it applies.

**Why chess mostly resists.** Chess is *loopy* (positions repeat) and *global*
(a piece anywhere may bear on any square), so the standard theory does not apply
off the shelf. But chess endgames sometimes decompose in practice -- separated
pawn races, opposite-wing play -- and the literature on chess endgames as
combinatorial games (Elkies) shows values like `*` and `1/2` really do appear.

**Experiment.** Build universes that are *forced* to decompose: two pawn chains
separated by a wall of blocked files, so no piece can cross. Solve exactly and
check whether the game value equals the CGT sum of the components. If it does,
we have a compositional handle on a chess-like game.

**Failure mode.** Constructing genuine independence in chess needs artificial
constraints, and results about artificially decomposable chess may say nothing
about chess.

---

## 7. Certificate compression: from table to rule

**Mechanism.** Solve exactly, then compress the solution into a decision
procedure -- a set of rules that reproduces the table. Measure the compression.
A solved game whose table compresses to a page is *understood*; one that does not
is merely *computed*.

**Why it is the real test of the founding hypothesis.** Both prior solved games
(checkers, Gardner) produced oracles, not theorems. If micro-chess tables
compress well under, say, decision-list or BDD encodings, the "hidden structure"
claim gets its first positive evidence. If they resist compression at 10^5
states, the claim is in serious trouble.

**Experiment.** Take the `KR-K@4x4` table and fit a minimal decision list over
simple predicates (opposition, king distance, rook alignment, edge proximity).
Report exact accuracy and description length. Not built.

**Failure mode.** Near-perfect rules with a stubborn 1% exceptional set. In a
proof, 1% wrong is 100% wrong.

---

## 8. Retrograde analysis with better indexing

**Mechanism.** Not a structural idea -- an engineering one. Our current solver
holds an explicit state graph in a Python dict at roughly 20,000 states per
second. A bitboard move generator over a dense integer index with numpy-vectorised
retrograde passes is a realistic 100-1000x, which is two to three extra rungs of
the ladder.

**Why it is on the list.** Every structural experiment above is bounded by how
much ground truth we have. Two extra rungs improve *all* of them, which is a
better return than most of the clever ideas.

**Experiment.** Reimplement `solve_material` over a dense material index with
numpy retrograde passes; validate against the existing known-answer tests.

**Failure mode.** None conceptually; it is a known technique. The risk is that
it eats the time that should go into mechanisms 1-5.

---

## 9. Spectral and topological structure of the state graph

**Mechanism.** Treat the solved state graph as a geometric object: spectral gap,
community structure, the boundary between won and drawn regions, whether that
boundary is thin.

**Why it might matter.** If the won/drawn boundary is a thin, well-behaved
surface, a small certificate for "which side of the boundary am I on" is
plausible, which feeds mechanism 7. If the regions interleave fractally, no short
certificate exists and several mechanisms above die at once.

**Experiment.** For each solved universe, compute the boundary set -- drawn
states with a won neighbour -- as a fraction of the whole, and its growth across
the ladder. Cheap on existing tables. Not built.

**Failure mode.** Graph spectra are easy to compute and hard to interpret. There
is a real risk of producing numbers nobody can act on, which is why this sits
below the mechanisms with sharp verdicts.

---

## 10. Higher-dimensional embeddings

**Mechanism.** Note 04's programme: use dimension as a parameter and look for
quantities invariant across 2D, 3D and 4D.

**Why it is ranked last despite being the repository's original theme.** The
arithmetic in note 04 is unfavourable and now measured rather than guessed:
raising the dimension multiplies the symmetry group by a constant while
multiplying the state space exponentially in piece count. As a route to
compression it is a losing trade. Its only defensible use is as an extra axis for
mechanism 2's invariance testing, and there are cheaper axes -- board width,
board height, aspect ratio -- that we have not exhausted.

**Experiment.** The 2D precondition in note 04: check that the target quantities
follow a clean law across 2D rectangles first. If they do not, skip the 4D
refactor entirely.

**Failure mode.** Substantial engineering cost for a mechanism whose upside is
already bounded.

---

## What to build next, in order

1. Run `exp003` and read the structure gap. It gates mechanisms 5, 7 and 9.
2. Build the invariant-transfer experiment (mechanism 5). Highest information
   per unit effort of anything unbuilt.
3. Build the zugzwang census (mechanism 3) -- one afternoon, and it decides
   whether the ultra-weak route is worth thinking about at all.
4. Only then consider the solver rewrite (mechanism 8), and only if a specific
   experiment is blocked on table size.
