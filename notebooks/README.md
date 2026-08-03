# Notebooks

Exploratory work that is not yet a numbered experiment. Anything that produces a
result worth quoting should graduate into `experiments/` with a `run.py`, so it
can be re-run and so its numbers land in `results/`.

```python
import sys; sys.path.insert(0, "../src")
from solvingchess.variants import endgame_variant
from solvingchess.solver import solve_material

tb = solve_material(endgame_variant("KR-K", 4, 4).rules)
print(tb.counts())
print(tb.rules.render(tb.longest_win()[0]))
```

Useful things to look at interactively:

* `Solution.principal_variation(state)` -- the optimal line from any position,
  which is the fastest way to sanity-check a solved universe by eye.
* `Solution.longest_win()` -- the hardest position in a table. Rendering it
  usually explains the whole endgame.
* `SymmetryGroup(rules).describe()` -- which symmetries survive for a given
  material signature, and why.
* `quotient.bisimulation_quotient(solution).block_of` -- block membership per
  state. Characterising the `KP-K@4x4` blocks is the open task from experiment
  003 and is well suited to a notebook.
