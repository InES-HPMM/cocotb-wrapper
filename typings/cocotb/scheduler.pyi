"""This type stub file was generated by pyright."""

from collections.abc import Coroutine
from typing import Any, Callable, Union

import cocotb
import cocotb.decorators
from cocotb._deprecation import deprecated
from cocotb.task import Task

"""Coroutine scheduler.

FIXME: We have a problem here.  If a coroutine schedules a read-only but we
also have pending writes we have to schedule the ReadWrite callback before
the ReadOnly (and this is invalid, at least in Modelsim).
"""
_profiling = ...
if _profiling:
    _profile = ...
_debug = ...

class InternalError(BaseException):
    """An error internal to scheduler. If you see this, report a bug!"""

    ...

class profiling_context:
    """Context manager that profiles its contents"""
    def __enter__(self):  # -> None:
        ...
    def __exit__(self, *excinfo):  # -> None:
        ...

class external_state:
    INIT = ...
    RUNNING = ...
    PAUSED = ...
    EXITED = ...

@cocotb.decorators.public
class external_waiter:
    def __init__(self) -> None: ...
    @property
    def result(self): ...
    def thread_done(self):  # -> None:
        ...
    def thread_suspend(self):  # -> None:
        ...
    def thread_start(self):  # -> None:
        ...
    def thread_resume(self):  # -> None:
        ...
    def thread_wait(self):  # -> int:
        ...

class Scheduler:
    """The main scheduler.

    Here we accept callbacks from the simulator and schedule the appropriate
    coroutines.

    A callback fires, causing the :any:`react` method to be called, with the
    trigger that caused the callback as the first argument.

    We look up a list of coroutines to schedule (indexed by the trigger) and
    schedule them in turn.

    .. attention::

       Implementors should not depend on the scheduling order!

    Some additional management is required since coroutines can return a list
    of triggers, to be scheduled when any one of the triggers fires.  To
    ensure we don't receive spurious callbacks, we have to un-prime all the
    other triggers when any one fires.

    Due to the simulator nuances and fun with delta delays we have the
    following modes:

    Normal mode
        - Callbacks cause coroutines to be scheduled
        - Any pending writes are cached and do not happen immediately

    ReadOnly mode
        - Corresponds to ``cbReadOnlySynch`` (VPI) or ``vhpiCbRepEndOfTimeStep``
          (VHPI).  In this state we are not allowed to perform writes.

    Write mode
        - Corresponds to ``cbReadWriteSynch`` (VPI) or ``vhpiCbRepLastKnownDeltaCycle`` (VHPI)
          In this mode we play back all the cached write updates.

    We can legally transition from Normal to Write by registering a :class:`~cocotb.triggers.ReadWrite`
    callback, however usually once a simulator has entered the ReadOnly phase
    of a given timestep then we must move to a new timestep before performing
    any writes.  The mechanism for moving to a new timestep may not be
    consistent across simulators and therefore we provide an abstraction to
    assist with compatibility.


    Unless a coroutine has explicitly requested to be scheduled in ReadOnly
    mode (for example wanting to sample the finally settled value after all
    delta delays) then it can reasonably be expected to be scheduled during
    "normal mode" i.e. where writes are permitted.
    """

    _MODE_NORMAL = ...
    _MODE_READONLY = ...
    _MODE_WRITE = ...
    _MODE_TERM = ...
    _next_time_step = ...
    _read_write = ...
    _read_only = ...
    _timer1 = ...
    def __init__(self, handle_result: Callable[[Task], None]) -> None: ...
    def react(self, trigger):  # -> None:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    def unschedule(self, coro):  # -> None:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    def queue(self, coroutine):  # -> None:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    def queue_function(self, coro):
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    def run_in_executor(
        self, func, *args, **kwargs
    ):  # -> CoroutineType[Any, Any, Any]:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    @staticmethod
    def create_task(coroutine: Any) -> Task:
        """Check to see if the given object is a schedulable coroutine object and if so, return it."""
        ...

    @deprecated("This method is now private.")
    def add(self, coroutine: Union[Task, Coroutine]) -> Task: ...
    def start_soon(self, coro: Union[Coroutine, Task]) -> Task:
        """Schedule a coroutine to be run concurrently, starting after the current coroutine yields control.

        In contrast to :func:`~cocotb.fork` which starts the given coroutine immediately, this function
        starts the given coroutine only after the current coroutine yields control.
        This is useful when the coroutine to be forked has logic before the first
        :keyword:`await` that may not be safe to execute immediately.

        .. versionadded:: 1.5
        """
        ...

    def add_test(self, test_coro):  # -> None:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    def schedule(self, coroutine, trigger=...):  # -> None:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    def finish_test(self, exc):  # -> None:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    def finish_scheduler(self, exc):  # -> None:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...

    def cleanup(self):  # -> None:
        """.. deprecated:: 1.5
        This function is now private.
        """
        ...
