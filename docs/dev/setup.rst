.. _setup:

*****************
Development Setup
*****************

This project is built with `uv <https://github.com/astral-sh/uv>`_. Setting up
development environment is very easy once you have uv installed. Run

.. code-block:: bash

   uv sync --group=dev,docs

which creates a virtual environment with the necessary tools for development and
to generate the documentation. You are now free to either run commands through
``uv run <command>`` or create a virtual environment with

.. code-block:: bash

   uv venv

Be sure to run checks before commiting anything by running `basedpyright`,
`ruff check`, and `ruff format` manually, or by invoking `just check` and
`just fmt`.
