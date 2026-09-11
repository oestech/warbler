.PHONY: setup seed test run

VENV := .venv
PY := $(VENV)/bin/python

setup:
	python3 -m venv $(VENV)
	$(PY) -m pip install -r requirements.txt

seed:
	$(PY) -m app.seed

test:
	$(PY) -m pytest

run:
	$(PY) -m uvicorn app.main:app --port 8000 --reload
