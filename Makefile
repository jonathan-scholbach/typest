.PHONY: test

lint:
	python -m black typest/ -l 80
	python -m black tests/ -l 100

test:
	poetry run python -m pytest tests
