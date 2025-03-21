build:
   uv build

build-docs:
    uv run sphinx-build -a -b html docs/ docs/_build

check:
    uv run basedpyright --level error
    uv run ruff check

fmt:
    uv run ruff format
    
sync:
    uv sync --group dev --group docs
    

