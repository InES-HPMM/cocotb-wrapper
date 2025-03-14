build:
   uv build

build-docs:
    uv run sphinx-build -a -b html docs/ docs/_build

check:
    uv run basedpyright --level error
    uv run ruff check --no-fix
    uv run ruff format --check

format:
    uv run ruff format

lint:
    uv run ruff check
    
sync:
    uv sync --group dev --group docs

type-check:
    uv run basedpyright
    

