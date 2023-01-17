.PHONY: build test lint run publish


build:
	poetry install
	poetry build

lint:
	python -m black typest/ -l 80
	python -m black tests/ -l 100

test: TEST_PATH=tests
test: build
	poetry run python -m pytest $(TEST_PATH)

run: build
	poetry run python -m typest tests/cases

publish: test
	poetry publish
