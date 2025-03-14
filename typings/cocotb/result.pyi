"""This type stub file was generated by pyright."""

from io import StringIO

def raise_error(obj, msg):  # -> None:
    """Create a :exc:`TestError` exception and raise it after printing a traceback.

    .. deprecated:: 1.3
        Raise a standard Python exception instead of calling this function.
        A stacktrace will be printed by cocotb automatically if the exception is unhandled.

    Args:
        obj: Object with a log method.
        msg (str): The log message.
    """
    ...

def create_error(obj, msg):  # -> TestError:
    """Like :func:`raise_error`, but return the exception rather than raise it,
    simply to avoid too many levels of nested `try/except` blocks.

    .. deprecated:: 1.3
        Raise a standard Python exception instead of calling this function.

    Args:
        obj: Object with a log method.
        msg (str): The log message.
    """
    ...

class ReturnValue(Exception):
    """Helper exception needed for Python versions prior to 3.3.

    .. deprecated:: 1.4
        Use a :keyword:`return` statement instead; this works in all supported versions of Python.
    """
    def __init__(self, retval) -> None: ...

class TestComplete(Exception):
    """Exception showing that the test was completed. Sub-exceptions detail the exit status.

    .. deprecated:: 1.6.0
        The ``stdout`` and ``stderr`` attributes.
    """
    def __init__(self, *args, **kwargs) -> None: ...
    @property
    def stdout(self) -> StringIO: ...
    @stdout.setter
    def stdout(self, new_value: StringIO) -> None: ...
    @property
    def stderr(self) -> StringIO: ...
    @stderr.setter
    def stderr(self, new_value: StringIO) -> None: ...

class ExternalException(Exception):
    """Exception thrown by :class:`cocotb.external` functions."""
    def __init__(self, exception) -> None: ...

class TestError(TestComplete):
    """Exception showing that the test was completed with severity Error.

    .. deprecated:: 1.5
        Raise a standard Python exception instead.
        A stacktrace will be printed by cocotb automatically if the exception is unhandled.
    """
    def __init__(self, *args, **kwargs) -> None: ...

class TestFailure(TestComplete, AssertionError):
    """Exception showing that the test was completed with severity Failure.

    .. deprecated:: 1.6.0
        Use a standard ``assert`` statement instead of raising this exception.
        Use ``expect_fail`` rather than ``expect_error`` with this exception in the
        :class:`cocotb.test` decorator.
    """
    def __init__(self, *args, **kwargs) -> None: ...

class TestSuccess(TestComplete):
    """Exception showing that the test was completed successfully."""

    ...

class SimFailure(TestComplete):
    """Exception showing that the simulator exited unsuccessfully."""

    ...

class SimTimeoutError(TimeoutError):
    """Exception for when a timeout, in terms of simulation time, occurs."""

    ...
