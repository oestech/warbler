.PHONY: setup seed test run

setup:
	python -m pip install --user --no-warn-script-location -r requirements.txt

seed:
	python -m app.seed

test:
	python -m pytest

run:
	python -m uvicorn app.main:app --port 8000
