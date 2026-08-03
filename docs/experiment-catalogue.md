# Experiment catalogue

Everything else worth testing, with a sketch of what the code would look like.

`docs/roadmap.md` is the *ordered* list -- what to do next. This is the *complete*
list: twenty-five things that could be measured with the kernel as it stands or
with a modest extension, kept here so that ideas are not lost and so that
choosing what to build next is a choice between known options rather than
whatever occurs to someone that morning.

Each entry gives the question, why it matters, **what would count as a negative
result**, and a Python sketch against the real API. The sketches are
illustrative -- they compile against `src/solvingchess` but have not been run.

Shared preamble for every sketch:

```python
import sys; sys.path.insert(0, "src")
from solvingchess.variants import endgame_variant, singleton_variant
from solvingchess.solver import solve_material, solve_variant, WIN, DRAW, LOSS
from solvingchess.symmetry import SymmetryGroup
from solvingchess import report
```

---

# A. Structure and compression

## A1. Zugzwang census

**Question.** How often would the side to move rather pass?

**Why.** Strategy stealing -- the technique that gives Hex a size-independent
ultra-weak solution -- needs "an extra move never hurts". Zugzwang is precisely
the failure of that premise. If zugzwang is rare and confined to identifiable
material, an ultra-weak argument modulo an exceptional set becomes conceivable.
If it is everywhere, that route is closed and we stop thinking about it.

**Negative result.** Zugzwang frequency above a few percent across all material,
or with no pattern in where it occurs.

```python
def zugzwang_census(rules):
    """A state is zugzwang if passing would give the mover a better value."""
    solution = solve_material(rules)
    # A "pass" is the same position with the side to move flipped.
    counted = zugzwang = 0
    for state in solution.states:
        passed = state ^ 1               # side-to-move lives in bit 0
        here, there = solution.value_of(state), solution.value_of(passed)
        if there is None:
            continue
        counted += 1
        # value is from the mover's perspective, so flip the passed position's
        # value to express it from the original mover's point of view.
        flipped = {WIN: LOSS, LOSS: WIN, DRAW: DRAW}[there]
        if _better(flipped, here):
            zugzwang += 1
    return zugzwang / counted

def _better(a, b):
    order = {LOSS: 0, DRAW: 1, WIN: 2}
    return order[a] > order[b]
```

Run it across the exp002 ladder and report frequency against material and board
size.

## A2. Certificate compression (minimum description length)

**Question.** How short can a rule set be that reproduces a solved table
exactly?

**Why.** This is the sharpest form of the founding hypothesis. A solved game
whose table compresses to a page is *understood*; one that does not is merely
*computed*. Both prior solved games (checkers, Gardner's 5x5) produced oracles,
not theorems.

**Negative result.** Near-perfect rules with a stubborn exceptional set. In a
proof, 1% wrong is 100% wrong.

```python
from solvingchess.features import FEATURE_NAMES, FeatureExtractor
from solvingchess.induction import accuracy, fit

def description_length_curve(rules, depths=range(2, 15)):
    solution = solve_material(rules)
    extractor = FeatureExtractor(rules)
    rows = [extractor.extract(s) for s in solution.states]
    labels = [solution.value_of(s) for s in solution.states]
    curve = []
    for depth in depths:
        tree = fit(rows, labels, len(FEATURE_NAMES), max_depth=depth, min_samples=1)
        curve.append({"depth": depth, "nodes": tree.size(),
                      "exact": accuracy(tree, rows, labels)})
    return curve      # plot nodes against exactness; look for a knee
```

The interesting output is the shape: a sharp knee means a short certificate
exists, a straight line to 100% means the table is being memorised.

## A3. Won/drawn boundary thickness

**Question.** Is the frontier between winning and drawing regions thin and
well-behaved, or fractal?

**Why.** A thin boundary makes a short "which side am I on" certificate
plausible, which feeds A2. Interleaved regions kill several mechanisms at once.

**Negative result.** Boundary fraction that does not shrink as the board grows.

```python
def boundary_fraction(solution):
    frontier = 0
    drawn = 0
    for state in solution.states:
        if solution.value_of(state) != DRAW:
            continue
        drawn += 1
        if any(solution.value_of(t) != DRAW for t in solution.successors_of(state)):
            frontier += 1
    return frontier / drawn
```

Measure across the exp005 board sweep and fit against area.

## A4. Characterise the KP-K bisimulation blocks

**Question.** Experiment 003 found 3,456 behavioural classes over 18,740 states
in `KP-K@4x4` -- a x2.7 improvement on symmetry. What *are* they?

**Why.** This is the single concrete follow-up the measurements point at. If the
blocks correspond to named endgame concepts -- opposition, key squares, the
square of the pawn -- the representation hypothesis has produced a real result on
the one family where the data says to look.

**Negative result.** Blocks that no combination of interpretable features
separates.

```python
from solvingchess.quotient import bisimulation_quotient
from solvingchess.features import FEATURE_NAMES, FeatureExtractor
from solvingchess.induction import accuracy, fit

def explain_blocks(rules):
    solution = solve_material(rules)
    blocks = bisimulation_quotient(solution, label="wdl")
    extractor = FeatureExtractor(rules)
    rows = [extractor.extract(s) for s in solution.states]
    labels = blocks.block_of.tolist()          # predict block id, not value
    tree = fit(rows, labels, len(FEATURE_NAMES), max_depth=10)
    return accuracy(tree, rows, labels), tree  # can features name the blocks?
```

## A5. Stabiliser census

**Question.** Which positions have non-trivial symmetry stabilisers, and are
they strategically special?

**Why.** Experiment 001 showed compression sits at 90-100% of the group-order
ceiling, meaning almost every stabiliser is trivial. The exceptions are exactly
the self-symmetric positions -- kings on a diagonal, mirrored material. Whether
that set carries any strategic meaning is an open and rather appealing question.

**Negative result.** Stabiliser-non-trivial positions have the same value
distribution as everything else, i.e. symmetry of the position says nothing about
the game.

```python
def stabiliser_census(rules):
    solution = solve_material(rules)
    group = SymmetryGroup(rules)
    census = {}
    for state in solution.states:
        size = len(group.orbit(state))
        stabiliser = group.order // size
        census.setdefault(stabiliser, []).append(solution.value_of(state))
    return {k: {"count": len(v), "drawn": v.count(DRAW) / len(v)}
            for k, v in census.items()}
```

## A6. Empirical entropy of a solved table

**Question.** How many bits does a tablebase actually contain, once symmetry and
the value distribution are accounted for?

**Why.** Gives A2 a target. If the empirical entropy of the WDL sequence over
symmetry orbits is 20,000 bits, a 500-node decision tree is a genuine
compression; if it is 2,000 bits, the tree is not doing much.

```python
import math
from collections import Counter

def table_entropy_bits(solution, group):
    orbits = {group.canonical(s): solution.value_of(s) for s in solution.states}
    counts = Counter(orbits.values())
    total = sum(counts.values())
    per_symbol = -sum((c / total) * math.log2(c / total) for c in counts.values())
    return per_symbol * total, total
```

---

# B. Invariants and prediction

## B1. Feature ablation

**Question.** Which single feature carries the transfer in experiment 004?

**Why.** A rule that transfers is only interesting if we can say *why*. Ablation
turns "the model works" into "confinement is the invariant", which is the form a
theorem would take.

**Negative result.** No single feature matters and the transfer comes from a
conjunction of six -- which is still a result, just a less quotable one.

```python
from solvingchess.induction import accuracy, fit

def ablate(train_rows, train_labels, test_rows, test_labels, n_features):
    full = fit(train_rows, train_labels, n_features)
    scores = {"all": accuracy(full, test_rows, test_labels)}
    for drop in range(n_features):
        keep = [i for i in range(n_features) if i != drop]
        tr = [tuple(r[i] for i in keep) for r in train_rows]
        te = [tuple(r[i] for i in keep) for r in test_rows]
        scores[drop] = accuracy(fit(tr, train_labels, len(keep)), te, test_labels)
    return scores
```

## B2. DTM regression instead of WDL classification

**Question.** Can the same features predict *how long* the win takes, not just
that it is a win?

**Why.** WDL is three classes and mostly one of them; DTM is a much harder
target, so a rule that transfers on DTM is far stronger evidence. It also feeds
the scaling law: a per-position DTM predictor implies the aggregate law that
exp005 fits.

**Negative result.** Predictions that transfer in rank order but not in scale --
which would actually be informative, since it would say the *shape* is
size-independent and only a normalisation constant changes.

```python
def dtm_transfer(train_rules, test_rules):
    extractor = FeatureExtractor(train_rules)
    train = solve_material(train_rules)
    won = [s for s in train.states if train.value_of(s) == WIN]
    table = {}                       # feature vector -> mean DTM
    for state in won:
        table.setdefault(extractor.extract(state), []).append(train.dtm_of(state))
    model = {k: sum(v) / len(v) for k, v in table.items()}

    test = solve_material(test_rules)
    tester = FeatureExtractor(test_rules)
    errors = []
    for state in test.states:
        if test.value_of(state) != WIN:
            continue
        predicted = model.get(tester.extract(state))
        if predicted is not None:
            errors.append(abs(predicted - test.dtm_of(state)))
    return sum(errors) / len(errors)
```

## B3. Conserved quantities along optimal play

**Question.** Is there a function constant along the principal variation?

**Why.** This is the literal meaning of "invariant" and the thing physics-style
intuition keeps reaching for. A quantity conserved by optimal play is a candidate
for an inductive hypothesis.

**Negative result.** Nothing is conserved except the value itself, which is
trivially conserved and says nothing.

```python
def conservation_scan(rules, candidates):
    """candidates: dict of name -> function(rules, state) -> hashable"""
    solution = solve_material(rules)
    scores = {name: [0, 0] for name in candidates}
    for state in solution.states[::17]:                 # stride to keep it cheap
        line = solution.principal_variation(state, limit=40)
        for name, fn in candidates.items():
            values = {fn(rules, s) for s in line}
            scores[name][0] += 1
            scores[name][1] += (len(values) == 1)
    return {n: hits / total for n, (total, hits) in scores.items()}
```

Seed `candidates` with parity of king separation, colour of the square the
defending king stands on, and the confinement bucket.

## B4. Prediction registry

**Question.** Are our predictions actually any good, tracked over time?

**Why.** Experiment 005 predicts and scores in one script, which is fine, but the
methodology only has teeth if predictions are recorded *before* the run and
cannot be quietly revised. A registry file makes that mechanical.

```python
# results/predictions.json holds entries written before a solve:
#   {"universe": "KR-K@9x9", "quantity": "draw_fraction",
#    "predicted": 0.058, "made_at": "...", "basis": "exp005 fit"}
def score_registry(path="results/predictions.json"):
    import json
    entries = json.load(open(path))
    for entry in entries:
        if entry.get("actual") is None:
            spec, shape = entry["universe"].split("@")
            files, ranks = map(int, shape.split("x"))
            solution = solve_material(endgame_variant(spec, files, ranks).rules)
            entry["actual"] = solution.counts()["draw"] / solution.n_states
            entry["error"] = abs(entry["actual"] - entry["predicted"]) / entry["actual"]
    json.dump(entries, open(path, "w"), indent=2)
```

## B5. Monte Carlo estimates past the solving frontier

**Question.** Can the scaling law be extended to universes too big to solve?

**Why.** Experiment 005 stops at 8x8 for three pieces. Random sampling of legal
positions plus a bounded search gives a noisy estimate of the drawn fraction far
beyond that, which is enough to test whether the fitted exponent holds where we
cannot enumerate.

**Negative result.** Sampling error swamps the effect, or sampled positions are
not representative of the legal-position distribution.

```python
import random
from solvingchess.solver import all_legal_states, solve

def sampled_draw_fraction(rules, samples=2000, radius=200_000):
    """Solve a bounded neighbourhood around each sampled root."""
    pool = []
    for i, state in enumerate(all_legal_states(rules)):
        if i >= 200_000:
            break
        pool.append(state)
    drawn = 0
    for root in random.sample(pool, samples):
        local = solve(rules, [root], max_states=radius)
        drawn += local.value_of(root) == DRAW
    return drawn / samples
```

---

# C. Game theory and proof technique

## C1. The pass-move variant

**Question.** How much does the value of a universe change if either side may
pass?

**Why.** A cleaner version of A1. In a game where passing is allowed, strategy
stealing applies immediately: the first player can never be worse off. Comparing
the pass-variant value to the real value measures exactly how much of chess's
difficulty is zugzwang.

**Negative result.** The pass variant has wildly different values, meaning
zugzwang is structural rather than exceptional.

Needs a small kernel change: a `Rules` flag adding the null move to
`successors`, guarded so it cannot be played in check and cannot repeat
indefinitely (cap consecutive passes at one per side).

```python
# in rules.py, inside successors(), after normal move generation:
if self.allow_pass and not in_check and not just_passed:
    out.append(self.encode(squares, types, 1 - stm))
```

## C2. Mirroring strategy for the drawing side

**Question.** In a colour-symmetric universe, can the second player draw by
mirroring?

**Why.** This is the most chess-shaped ultra-weak technique available. Chess is
believed drawn; "Black maintains a symmetry-based invariant" is a finite,
checkable claim, and colour-symmetric singleton universes are the natural place
to test it.

**Negative result.** Mirroring fails immediately (it will -- the interesting
question is *where*, and whether the failures are characterisable).

```python
def mirror_strategy_survives(variant, plies=40):
    group = SymmetryGroup(variant.rules)
    solution = solve_variant(variant, canonical=group.canonical)
    state = variant.start
    for ply in range(plies):
        state = solution.best_move(state)          # White plays optimally
        if state is None:
            return ply
        mirrored = group.apply(state, (group.elements[0][0], True))
        if mirrored not in solution.index:          # mirror not legal here
            return ply
        state = mirrored
    return plies
```

## C3. Forced decomposition

**Question.** In a universe engineered so two regions cannot interact, does the
game value equal the combinatorial-game-theory sum of the parts?

**Why.** Decomposition converts exponential search into arithmetic wherever it
applies. Chess mostly resists because it is loopy and global, but endgames do
sometimes decompose in practice.

**Negative result.** Values do not add, meaning even artificially separated chess
is not compositional -- which would close mechanism 6 of `research/06` cleanly.

Needs a kernel extension: blocked squares (a wall). Sketch assumes a
`Geometry(files, ranks, blocked=frozenset(...))`.

```python
def decomposition_test(left, right, combined):
    lv = solve_variant(left).value_of(left.start)
    rv = solve_variant(right).value_of(right.start)
    cv = solve_variant(combined).value_of(combined.start)
    return {"left": lv, "right": rv, "combined": cv}
```

## C4. Weak versus strong solving cost

**Question.** How much cheaper is a weak solution than a strong one, on a
universe where we can compute both?

**Why.** Every route past six pieces goes through weak solving -- it is how
Gardner's 5x5 was done. Measuring the ratio on `singleton-KQR@4x4`, where we have
the strong solution as ground truth, tells us how many extra rungs weak solving
buys before we invest in it.

**Negative result.** The ratio is small, meaning weak solving does not open the
ladder and the top rung stays out of reach.

```python
def proof_number_search(rules, root, budget=5_000_000):
    """Return (value, nodes_expanded). Standard PNS over the move relation."""
    ...

def weak_versus_strong(variant):
    strong = solve_variant(variant, canonical=SymmetryGroup(variant.rules).canonical)
    value, nodes = proof_number_search(variant.rules, variant.start)
    assert value == strong.value_of(variant.start)      # ground-truth check
    return {"strong_states": strong.n_states, "weak_nodes": nodes,
            "ratio": strong.n_states / nodes}
```

## C5. Is classical opposition exactly right?

**Question.** The opposition rule in king-and-pawn endgames is stated as exact
chess theory. On a solved table, is it?

**Why.** If a piece of received human theory is exactly correct on our tables,
that is a worked example of a short certificate for a region of the state space
-- the thing A2 is hunting. If it is nearly-but-not-quite correct, the exceptions
are the interesting object.

```python
def opposition_exactness(rules):
    solution = solve_material(rules)          # KP-K
    extractor = FeatureExtractor(rules)
    agree = total = 0
    for state in solution.states:
        f = extractor.extract(state)
        opposition = f[FEATURE_NAMES.index("opposition")]
        if opposition == 0:
            continue
        total += 1
        agree += solution.value_of(state) == DRAW   # naive form of the rule
    return agree / total, total
```

---

# D. Minification and variant space

## D1. Back-rank ordering sensitivity

**Question.** Does the value of a singleton universe depend on the order of
pieces on the home rank?

**Why.** `research/05` claims Singleton Chess is "essentially the same game" as
chess. If permuting `R N B Q K` changes the value, the claim is weaker than it
sounds and the caveat needs stating loudly.

**Negative result** (here, actually the *bad* result): value changes with
ordering, meaning results are about one arrangement rather than about the family.

```python
from itertools import permutations
from solvingchess.geometry import KING, QUEEN, ROOK

def ordering_sensitivity(files, ranks, types):
    values = {}
    for order in permutations(types):
        variant = singleton_variant(files, ranks, types)
        # requires exposing back-rank order as a parameter of singleton_variant
        group = SymmetryGroup(variant.rules)
        solution = solve_variant(variant, canonical=group.canonical)
        values["".join(map(str, order))] = solution.value_of(variant.start)
    return values
```

## D2. The phase-boundary map

**Question.** Where in (board area, piece count) does the singleton family flip
from drawn to a first-player win?

**Why.** Experiment 002 found one transition: `singleton-KQ` is drawn on 3x3,
4x4 and 5x5, and `singleton-KQR@4x4` is a White win. A boundary curve would be a
genuine theorem about a family of games, even if the family does not contain
chess.

```python
def phase_map(shapes, type_sets, budget=1_200_000):
    grid = {}
    for files, ranks in shapes:
        for types in type_sets:
            try:
                variant = singleton_variant(files, ranks, types)
                group = SymmetryGroup(variant.rules)
                solution = solve_variant(variant, canonical=group.canonical,
                                         max_states=budget)
                grid[(files, ranks, types)] = solution.value_of(variant.start)
            except Exception as exc:
                grid[(files, ranks, types)] = f"unsolved: {exc}"
    return grid
```

## D3. Empirical piece values

**Question.** What are the piece values implied by exactly solved micro-chess,
and do they match the folklore 1/3/3/5/9?

**Why.** Piece values are the most widely used heuristic in chess and they were
derived from play, never from ground truth. Deriving them from exhaustively
solved universes -- and watching them change with board size -- is a clean,
self-contained result that needs no new machinery.

```python
def implied_values(shapes, pieces="QRBNP"):
    out = {}
    for files, ranks in shapes:
        for letter in pieces:
            rules = endgame_variant(f"K{letter}-K", files, ranks).rules
            solution = solve_material(rules)
            counts = solution.counts()
            out[(letter, files, ranks)] = counts["win"] / solution.n_states
    return out    # win rate as a proxy for value; compare orderings, not scales
```

## D4. Rule perturbation -- which rules matter?

**Question.** If a piece's movement set is perturbed slightly, how much do the
measured structural quantities move?

**Why.** Turns "is chess special?" into a measurement. If chess's structural
statistics sit in the middle of the distribution over nearby rule sets, there is
nothing special to find and the search for hidden structure is misdirected. If
they are an outlier, that is the most interesting possible result in this
repository.

**Negative result.** Chess is unremarkable among its neighbours.

```python
from solvingchess.geometry import KNIGHT_STEPS

def perturb_knight(steps):
    """Yield rule sets with one knight jump changed."""
    for i in range(len(steps)):
        for replacement in [(3, 1), (1, 3), (2, 2), (3, 2)]:
            yield steps[:i] + (replacement,) + steps[i + 1:]

def rule_sensitivity(files, ranks):
    baseline = solve_material(endgame_variant("KN-K", files, ranks).rules)
    out = {"chess": baseline.counts()}
    for steps in perturb_knight(KNIGHT_STEPS):
        # requires Geometry to accept custom step sets per piece type
        ...
    return out
```

This one needs the biggest kernel change -- movement sets have to become data
rather than constants -- but it is the change that makes the repository able to
ask comparative questions at all, and it is probably the most valuable single
refactor on this page.

## D5. Board topology variants

**Question.** What happens on a cylinder, a torus, or a board with holes?

**Why.** Board topology is a parameter nobody varies, and it separates "the rules
of chess" from "the shape of the board" more cleanly than adding dimensions does.
A cylindrical board has no edges, which removes the mating net entirely -- a
sharp test of how much of chess's structure is edge effects. Experiment 005 found
drawn fraction scaling as roughly `1/area`, and the obvious explanation is that
draws are edge and corner phenomena; a torus would falsify or confirm that
immediately.

```python
# Geometry gains wrap flags; ray_table and step_table wrap coordinates.
def torus_comparison(files, ranks):
    flat = solve_material(endgame_variant("KR-K", files, ranks).rules)
    torus = solve_material(endgame_variant("KR-K", files, ranks,
                                           wrap=(True, True)).rules)
    return {"flat_draws": flat.counts()["draw"] / flat.n_states,
            "torus_draws": torus.counts()["draw"] / torus.n_states}
```

---

# E. Engineering that unblocks the rest

## E1. Dense-index retrograde solver

Current throughput is roughly 20,000 states/second in pure Python with an
explicit graph. A dense material index plus numpy-vectorised retrograde passes
is a realistic 100-1000x, which is two to three extra rungs of every ladder in
the repository.

```python
def dense_index(rules):
    """state -> integer in [0, nsq**k * 2), with no dict."""
    ...

def retrograde_dense(rules):
    n = 2 * rules.geometry.nsq ** rules.nslots
    value = np.zeros(n, dtype=np.uint8)
    # generate *unmoves* rather than storing predecessors, so memory is O(n)
    # rather than O(edges)
    ...
```

Do this only when a specific experiment is blocked on table size. It is the most
tempting item on this page and the least informative on its own.

## E2. Tablebase persistence and a probe CLI

Solved tables are currently recomputed every run. Persisting them as numpy arrays
keyed by material signature and geometry would make every experiment above
cheaper, and a `probe` command that renders a position with its value and
principal variation is the fastest way to check a result by eye.

```python
def save_table(solution, path): ...
def load_table(path): ...

# python -m solvingchess.probe --universe KR-K@8x8 --fen-ish "K..k/.R../..../...."
```

## E3. n-dimensional geometry

Generalise `Geometry` beyond two axes. Gated on experiment 005: the note in
`research/04` argues dimension is a losing trade for compression and is only
worth building as an extra axis for invariance testing. Given that experiment 005
found clean laws across 2D rectangles, this is now *justified* -- but D5 (board
topology) is the cheaper and sharper version of the same question and should come
first.

---

## How to pick from this list

Prefer, in order:

1. experiments that can come out **against** a claim the repository has already
   made;
2. experiments that produce a **prediction** which a later run can score;
3. experiments that need **no kernel change**;
4. experiments whose result would change what gets built next.

By that test the strongest unbuilt items are **A1** (zugzwang census -- one
afternoon, closes or opens the entire ultra-weak route), **A4** (name the KP-K
blocks -- the concrete follow-up the data points at), and **D4** (rule
perturbation -- the only item that asks whether chess is special at all).
