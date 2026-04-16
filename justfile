default:
    @just --list

lint:
    uv run ruff check src/ tests/

format:
    uv run ruff format src/ tests/

typecheck:
    uv run ty check src/

test:
    uv run pytest tests/ -v

all: lint typecheck test

install:
    uv tool install .

sync:
    uv sync --extra dev

clean:
    rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/ __pycache__/ src/__pycache__/ tests/__pycache__/
