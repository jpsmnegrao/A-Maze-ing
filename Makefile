VENV    := matrix
PYTHON  := $(VENV)/bin/python3
PIP     := $(VENV)/bin/pip
MAIN    := a_maze_ing.py
CONFIG  := config.txt

.PHONY: install wheel run debug clean lint lint-strict

all: install

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install ./mlx-2.2-py3-none-any.whl || $(PIP) install ./mlx-2.2-py3-ubuntu-any.whl
	$(PIP) install -r requirements.txt
	$(PIP) install .

wheel:
	$(PIP) install build
	$(VENV)/bin/python -m build --wheel --outdir .

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf $(VENV) build dist *.egg-info .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f maze.txt

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --strict
