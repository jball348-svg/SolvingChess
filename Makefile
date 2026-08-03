.PHONY: help install test test-quick exp001 exp002 exp003 experiments clean

PYTHON ?= python3
export PYTHONPATH := src

help:
	@echo "install     install dependencies"
	@echo "test        full test suite, including 8x8 known-answer checks (~1 min)"
	@echo "test-quick  skip the 8x8 known-answer checks"
	@echo "exp001      symmetry compression"
	@echo "exp002      minification ladder (~20 min at default budget)"
	@echo "exp003      structure gap"
	@echo "experiments run all three"
	@echo "clean       remove caches"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest tests -q 2>/dev/null || $(PYTHON) tests/test_solvingchess.py

test-quick:
	$(PYTHON) -m pytest tests -q -k "not full_board" 2>/dev/null \
		|| $(PYTHON) tests/test_solvingchess.py

exp001:
	$(PYTHON) experiments/exp001_symmetry_compression/run.py

exp002:
	$(PYTHON) experiments/exp002_minification_ladder/run.py

exp003:
	$(PYTHON) experiments/exp003_quotient_gap/run.py

experiments: exp001 exp002 exp003

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
