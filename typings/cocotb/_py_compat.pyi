"""This type stub file was generated by pyright."""

import sys

"""
Backports and compatibility shims for newer python features.

These are for internal use - users should use a third party library like `six`
if they want to use these shims in their own code
"""

class nullcontext:
    """Context manager that does no additional processing.
    Used as a stand-in for a normal context manager, when a particular
    block of code is only sometimes used with a normal context manager:

    cm = optional_cm if condition else nullcontext()
    with cm:
        # Perform operation, using optional_cm if condition is True
    """
    def __init__(self, enter_result=...) -> None: ...
    def __enter__(self):  # -> None:
        ...
    def __exit__(self, *excinfo):  # -> None:
        ...

if sys.version_info[:2] >= (3, 7):
    insertion_ordered_dict = ...
else:
    insertion_ordered_dict = ...
