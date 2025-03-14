# ============================================================
#   _____       ______  _____
#  |_   _|     |  ____|/ ____|
#    | |  _ __ | |__  | (___    Institute of Embedded Systems
#    | | | '_ \|  __|  \___ \   Zurich University of
#   _| |_| | | | |____ ____) |  Applied Sciences
#  |_____|_| |_|______|_____/   8401 Winterthur, Switzerland
# ============================================================

"""A cocotb testbench.

This module wraps around the :class:`cocotb.test` decorator and facilitates the
use with cocotb testbenches.
"""

from __future__ import annotations

__author__ = "Thierry Delafontaine"
__mail__ = "deaa@zhaw.ch"
__copyright__ = "2022 ZHAW Institute of Embedded Systems"
__date__ = "2024-02-27"

from collections.abc import Awaitable
from functools import wraps
from typing import Callable

from cocotb import (
    start_soon,
    test,  # pyright: ignore[reportAttributeAccessIssue]
)
from cocotb.clock import Clock
from cocotb.handle import HierarchyObject
from cocotb.log import SimLog
from cocotb.triggers import RisingEdge, Timer


class Testbench:
    """A cocotb testbench."""

    def __init__(
        self,
        name: str,
        clk: str | None = None,
        rst: str | None = None,
        reset_active_level: int = 1,
    ):
        """Initialize an instance.

        Args:
            name: The name of the device under test
            clk: The clock signal of the device under test
            rst: The reset signal of the device under test
            reset_active_level: 1 if the reset is active high, else active low
        """
        self._name = name
        self._test_id_counter = 1
        if clk is not None:
            self._clk = clk
        if rst is not None:
            self._rst = rst
        self.reset_active_level = reset_active_level
        self._log = SimLog(self.name)

        self._setup: Callable[[HierarchyObject], Awaitable[None]] | None = None
        self._teardown: Callable[[HierarchyObject], Awaitable[None]] | None = (
            None
        )

    @property
    def name(self) -> str:
        """Get the name of the device under test.

        Returns:
            The name of the device under test
        """
        return self._name

    def register_setup(
        self,
    ) -> Callable[
        [Callable[[HierarchyObject], Awaitable[object]]],
        Callable[[HierarchyObject], Awaitable[object]],
    ]:
        """Make the decorated function the setup function.

        Returns:
            A decorator function
        """
        return self._add_to_instance("_setup")

    def register_teardown(
        self,
    ) -> Callable[
        [Callable[[HierarchyObject], Awaitable[object]]],
        Callable[[HierarchyObject], Awaitable[object]],
    ]:
        """Make the decorated function the teardown function.

        Returns:
            A decorator function
        """
        return self._add_to_instance("_teardown")

    def register_test(
        self,
        timeout_time: int | None = None,
        timeout_unit: str = "step",
        expect_fail: bool = False,
        expect_error: Exception | tuple[Exception, ...] = (),
        skip: bool = False,
        stage: int = 0,
    ) -> Callable[
        [Callable[[HierarchyObject], Awaitable[None]]],
        Callable[[HierarchyObject], Awaitable[None]],
    ]:
        """Decorate a function to register the function as a test.

        Args:
            timeout_time: The duration before a timeout occurs
            timeout_unit: The unit of the timeout time
            expect_fail: Don't mark the test as failed if the test fails.
            expect_error: Mark the test as passed only if the given exception is
                raised
            skip: Skip this test
            stage: Order tests logically into stages, where multiple test can
                share a stage

        Returns:
            A decorator function
        """

        def decorator(
            f: Callable[[HierarchyObject], Awaitable[None]],
        ) -> Callable[[HierarchyObject], Awaitable[None]]:
            """Register the function as a cocotb test.

            Args:
                f: The decorated function

            Returns:
                The input function `f`
            """

            @wraps(f)
            async def _test_function(dut: HierarchyObject) -> None:
                await self._get_setup_function()(dut)
                self._log.debug("Setup completed")
                await f(dut)
                self._log.debug("Test finished")
                await self._get_teardown_function()(dut)
                self._log.debug("Teardown completed")

            test = _Test(
                test_function=_test_function,
                test_id=self._get_new_test_id(),
                timeout_time=timeout_time,
                timeout_unit=timeout_unit,
                expect_fail=expect_fail,
                expect_error=expect_error,
                skip=skip,
                stage=stage,
            )
            self._log.debug(
                "Registered %s to module %s",
                test.__call__.__name__,
                test.__call__.__module__,
            )
            return test.__call__

        return decorator

    async def reset(self, dut: HierarchyObject, time: int, units: str) -> None:
        """Reset the DUT.

        Args:
            dut: The device under test
            time: The time to hold the reset
            units: The unit of the time value
        """
        if hasattr(self, "_rst"):
            getattr(dut, self._rst).setimmediatevalue(
                1 if self.reset_active_level else 0
            )
            await Timer(time, units=units)  # pyright: ignore[reportArgumentType]
            getattr(dut, self._rst).value = 0 if self.reset_active_level else 1
            await RisingEdge(getattr(dut, self._rst))
            getattr(dut, self._rst)._log.debug("Reset complete")
        else:
            self._log.debug("Reset not available")

    def start_clk(
        self, dut: HierarchyObject, period: int, units: str = "ns"
    ) -> None:
        """Start the clock.

        Args:
            dut: The device under test
            period: The clock period. Must convert to an even number of
                timesteps
            units: One of ``'step'``, ``'fs'``, ``'ps'``, ``'ns'``, ``'us'``,
                ``'ms'``, ``'sec'``. When units is ``'step'``, the timestep is
                determined by the simulator (see
                :make:var:`COCOTB_HDL_TIMEPRECISION`)
        """
        if hasattr(self, "_clk"):
            start_soon(
                Clock(
                    getattr(dut, self._clk), period=period, units=units
                ).start()
            )
        else:
            self._log.debug("Clock not available")

    def _add_to_instance(
        self,
        name: str,
    ) -> Callable[
        [Callable[[HierarchyObject], Awaitable[object]]],
        Callable[[HierarchyObject], Awaitable[object]],
    ]:
        """Add the decorated function to the instance.

        Args:
            name: The name of the instance method

        Returns:
            A decorator function
        """

        def decorator(
            f: Callable[[HierarchyObject], Awaitable[object]],
        ) -> Callable[[HierarchyObject], Awaitable[object]]:
            """Make the decorated function a method of the testbench.

            Args:
                f: The decorated function

            Returns:
                The same function
            """
            setattr(self, name, f)
            self._log.debug("Added %s to %s.%s", f.__name__, self.name, name)

            return f

        return decorator

    async def _default_setup(self, dut: HierarchyObject) -> None:
        """Set up the testbench.

        This function is the default setup function and is executed if no other
        setup function is registered.

        Args:
            dut: The device under test
        """
        self.start_clk(dut, period=2, units="ns")
        await self.reset(dut, time=2, units="ns")

    async def _default_teardown(self, dut: HierarchyObject) -> None:
        """Teardown the testbench.

        This function is the default teardown function and is executed if no
        other teardown function is registered.

        Args:
            dut: The device under test
        """
        await self.reset(dut, time=2, units="ns")

    def _get_new_test_id(self) -> int:
        """Get a new test ID.

        Returns:
            A new unique test ID
        """
        new_test_id = self._test_id_counter
        self._test_id_counter += 1
        return new_test_id

    def _get_setup_function(
        self,
    ) -> Callable[[HierarchyObject], Awaitable[None]]:
        """Get the setup function.

        Returns:
            The testbenches setup function
        """
        if self._setup is not None:
            return self._setup
        else:
            return self._default_setup

    def _get_teardown_function(
        self,
    ) -> Callable[[HierarchyObject], Awaitable[None]]:
        """Get the teardown function.

        Returns:
            The testbenches teardown function
        """
        if self._teardown is not None:
            return self._teardown
        else:
            return self._default_teardown


class _Test:
    """A single test of a testbench.

    This class is not intended to be instantiated directly. Instead use
    :class:`~cocotb_wrapper.testbench.Testbench` to create a testbench and
    register tests with
    :meth:`~cocotb_wrapper.testbench.Testbench.register_test`.
    """

    def __init__(
        self,
        test_function: Callable[[HierarchyObject], Awaitable[None]],
        test_id: int = 1,
        timeout_time: int | None = None,
        timeout_unit: str = "step",
        expect_fail: bool = False,
        expect_error: Exception | tuple[Exception, ...] = (),
        skip: bool = False,
        stage: int = 0,
    ):
        """Initialize an instance.

        Args:
            test_function: The test function
            test_id: The test identifier
            timeout_time: The duration before a timeout occurs
            timeout_unit: The unit of the timeout time
            expect_fail: Don't mark the test as failed if the test fails.
            expect_error: Mark the test as passed only if the given exception is
                raised
            skip: Skip this test
            stage: Order tests logically into stages, where multiple test can
                share a stage
        """
        self._log = SimLog(test_function.__name__)

        @wraps(test_function)
        async def _test_function(dut: HierarchyObject) -> None:
            try:
                dut.test_id.value = self._test_id
                self._log.debug("'Set test_id' to %s", self._test_id)
            except AttributeError:
                self._log.debug("No 'test_id' signal found in DUT")
            await test_function(dut)

        self.__call__: Callable[[HierarchyObject], Awaitable[None]] = test(
            timeout_time=timeout_time,
            timeout_unit=timeout_unit,
            expect_fail=expect_fail,
            expect_error=expect_error,
            skip=skip,
            stage=stage,
        )(_test_function)
        self._test_id = test_id
