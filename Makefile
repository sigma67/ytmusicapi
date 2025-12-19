.PHONY: help install dev-install test test-cov lint format type-check clean build docs

help:
	@echo "ytmusicapi - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install production dependencies"
	@echo "  dev-install   Install development dependencies"
	@echo ""
	@echo "Quality:"
	@echo "  lint          Run ruff linter"
	@echo "  format        Format code with ruff"
	@echo "  format-check  Check code formatting"
	@echo "  type-check    Run mypy type checker"
	@echo "  pre-commit    Run pre-commit checks"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         Remove build artifacts"
	@echo "  build         Build package"
	@echo "  docs          Build documentation"

install:
	pdm install --prod

dev-install:
	pdm install
	pre-commit install

test:
	pdm run pytest

test-cov:
	pdm run pytest --cov --cov-report=html --cov-report=term

lint:
	pdm run ruff check ytmusicapi tests

format:
	pdm run ruff format ytmusicapi tests

format-check:
	pdm run ruff format --check ytmusicapi tests

type-check:
	pdm run mypy --install-types --non-interactive

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	pdm build

docs:
	cd docs && make html
