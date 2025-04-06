build:
   uv build

build-docs:
    uv run sphinx-build -a -b html docs/ docs/_build

check:
    uv run basedpyright --level error
    uv run ruff check

fmt: fmt-md fmt-py

fmt-md:
    prettier --write *.md

fmt-py:
    uv run ruff format
   
sync:
    uv sync --group dev --group docs
    

