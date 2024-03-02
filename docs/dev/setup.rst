.. _setup:

*****************
Development Setup
*****************

This project is built with `poetry <https://python-poetry.org/>`_. Setting up
development environment is very easy once you have poetry installed. Run

.. code-block:: bash

   poetry install --with=dev,docs

which creates a virtual environment with the necessary tools for development and
to generate the documentation. You are now free to either run commands through
``poetry run <command>`` or spawn a shell within the virtual environment with

.. code-block:: bash

   poetry shell

Be sure to install `pre-commit <https://pre-commit.com/>`_ and the hooks before
commiting anything.

.. code-block:: bash

   pre-commit install

This automatically checks your code before a commit and makes sure that it
complies with the rest of the code.
