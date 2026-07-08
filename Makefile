.PHONY: test test-cov lint typecheck e2e install clean

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=cpa_harness --cov-report=term-missing --cov-fail-under=80

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

typecheck:
	mypy src/cpa_harness/

e2e:
	RUN_E2E=1 pytest tests/e2e/

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov/ build/ dist/
	find . -type d -name __pycache__ -exec rm -rf {} +
