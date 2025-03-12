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

Be sure to install `pre-commit <https://pre-commit.com/>`_ and the hooks before
commiting anything.

.. code-block:: bash

   pre-commit install

This automatically checks your code before a commit and makes sure that it
complies with the rest of the code.
