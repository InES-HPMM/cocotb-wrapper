build:
   uv build

build-docs: sync-docs
    uv run sphinx-build -a -b html docs/ docs/_build

check: sync-all
    uv run basedpyright --level error
    uv run ruff check
    uv run ruff format

sync-all:
    uv sync --group dev --group docs

sync-docs:
    uv sync --group docs

