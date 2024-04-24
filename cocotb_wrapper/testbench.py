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
import threading


__author__ = "Thierry Delafontaine"
__mail__ = "deaa@zhaw.ch"
__copyright__ = "2022 ZHAW Institute of Embedded Systems"
__date__ = "2024-02-27"

from collections.abc import Awaitable
from functools import wraps
from typing import Callable, Dict, Generic, Tuple, TypeVar, Union

from cocotb import start_soon, test
from cocotb.handle import HierarchyObject
from cocotb.log import SimLog
from cocotb.triggers import RisingEdge, Timer
from cocotb_wrapper.clock import Clock
from cocotb_wrapper.const import Constants
from cocotb_wrapper.models import *
from cocotb_wrapper.log import logging
import cocotb_wrapper.timer as timer


class Testbench:
    """A cocotb testbench."""

    _clk_config: ClockConfig
    _rst_config: ResetConfig

    def __init__(
        self,
        name: str,
        clk_cfg: ClockConfig = None,
        rst_cfg: ResetConfig = None,
        valid_cfg: ValidationConfig = None,
        teardown_cfg: TeardownConfig = None,
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
        self._clk_dict = {}
        self._clk_config = clk_cfg
        self._rst_config = rst_cfg
        self._valid_cfg = valid_cfg.default_to(ValidationConfig(0, True))
        self._teardown_cfg = teardown_cfg.default_to(TeardownConfig(0, True))
        self._log = SimLog(self.name)

        self._setup: Callable[[HierarchyObject, list, dict], Awaitable[None]] | None = None
        self._teardown: Callable[[HierarchyObject, list, dict], Awaitable[None]] | None = None

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
        clk_cfg: ClockConfig = None,
        rst_cfg: ResetConfig = None,
        valid_cfg: ValidationConfig = None,
        teardown_cfg: TeardownConfig = None,
        *args,
        **kwargs,
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

        def decorator(f: Callable[[HierarchyObject], Awaitable[None]]) -> Callable[[HierarchyObject], Awaitable[None]]:
            """Register the function as a cocotb test.

            Args:
                f: The decorated function

            Returns:
                The input function `f`
            """

            @wraps(f)
            async def _test_function(dut: HierarchyObject) -> None:
                ctx = TestContext(
                    dut,
                    Constants(dut),
                    self._clk_config if clk_cfg is None else clk_cfg,
                    self._rst_config if rst_cfg is None else rst_cfg,
                    self._valid_cfg if valid_cfg is None else valid_cfg.default_to(self._valid_cfg),
                    self._teardown_cfg if teardown_cfg is None else teardown_cfg.default_to(self._teardown_cfg),
                )
                ctx = await self._get_setup_function()(ctx, args, kwargs) or ctx
                msg = "Test aborted. Setup function didn't return a valid test context. Setup function must create and return an instance of TestContext or a subclass of TestContext."
                assert ctx is not None, msg
                assert issubclass(type(ctx), TestContext), msg
                self._log.debug("Setup completed")
                await f(ctx)
                self._log.debug("Test finished")
                await self._get_teardown_function()(ctx, args, kwargs)
                self._log.debug("Teardown completed")

            test = _Test(test_function=_test_function, test_id=self._get_new_test_id(), timeout_time=timeout_time, timeout_unit=timeout_unit, expect_fail=expect_fail, expect_error=expect_error, skip=skip, stage=stage)
            self._log.debug(
                "Registered %s to module %s",
                test.__call__.__name__,
                test.__call__.__module__,
            )
            return test.__call__

        return decorator

    async def reset(self, dut: HierarchyObject, time: int, units: Unit, clk: Clock = None, edge: EdgeType = EdgeType.none) -> None:
        """Reset the DUT.

        Args:
            dut: The device under test
            time: The time to hold the reset
            units: The unit of the time value
            clk: The clock used for post reset edge synchronization
            edge: The clock edge to synchronize to after reset
        """
        if hasattr(self, "_rst_name"):
            getattr(dut, self._rst_name).setimmediatevalue(1 if self.reset_active_level else 0)
            await Timer(time, units=units.name)
            getattr(dut, self._rst_name).value = 0 if self.reset_active_level else 1
            await RisingEdge(getattr(dut, self._rst_name))
            getattr(dut, self._rst_name)._log.debug("Reset complete")

            if clk is not None:
                await timer.edge_trigger(clk, edge)
        else:
            self._log.debug("Reset not available")

    def add_clk(self, dut: HierarchyObject, name: str, period: float, units: Unit, main: bool = False, start: bool = False) -> None:

        self._clk_dict[name] = Clock(getattr(dut, name), name, period, units)
        self.__setattr__(name, self._clk_dict[name])
        if main:
            self.clk = self._clk_dict[name]
        if start:
            self.start_clk(name)

    def start_clk(self, name: str = None) -> None:
        """Start the clock.

        Args:
            name: Name of the clock to start. If None, all clocks are started
        """
        if name is None:
            if not self._clk_dict:
                self._log.error("No clocks available")
            else:
                for _, clk in self._clk_dict.items():
                    start_soon(clk.start())

        elif name in self._clk_dict:
            start_soon(self._clk_dict[name].start())
        else:
            self._log.error(f"Clock {name} not available")

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

        def decorator(f: Callable[[HierarchyObject], Awaitable[object]]) -> Callable[[HierarchyObject], Awaitable[object]]:
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

    async def _default_setup(self, ctx: TestContext, args: list, kwargs: dict) -> TestContext:
        """Set up the testbench.

        This function is the default setup function and is executed if no other
        setup function is registered.

        Args:
            dut: The device under test
            args: The informal arguments passed to the test function decorator
            kwargs: The keyword arguments passed to the test function decorator
        """

        clk_conf = kwargs.get("clk_cfg", self._clk_config)
        if clk_conf is None:
            raise ValueError("No clock configuration available")
        rst_conf = kwargs.get("clk_cfg", self._rst_config)
        if self._rst_config is None:
            raise ValueError("No reset configuration available")

        await ctx.reset(rst_conf, ctx.clk)
        return ctx

    async def _default_teardown(self, ctx: TestContext, args: list, kwargs: dict) -> None:
        """Teardown the testbench.

        This function is the default teardown function and is executed if no
        other teardown function is registered.

        Args:
            dut: The device under test
            args: The informal arguments passed to the test function decorator
            kwargs: The keyword arguments passed to the test function decorator
        """
        teardown_delay_cycles = ctx.teardown_cfg.delay_cycles
        if teardown_delay_cycles > 0:
            if ctx.clk is None:
                logging.warning("No clock available for teardown delay")
            await timer.delay(teardown_delay_cycles, clk=ctx.clk)

        if ctx.teardown_cfg.assert_valid:
            ctx.assert_valid(AssertConfig())
        await ctx.reset()

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
    ) -> Callable[[HierarchyObject], Awaitable[TestContext]]:
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
    ) -> Callable[[TestContext], Awaitable[None]]:
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


TConst = TypeVar("TConst")


class TestContext(Generic[TConst]):
    _error_count: int
    _error_msgs: Dict[int, str]
    _thread_lock: threading.Lock
    _log: SimLog
    _clk_dict: Dict[str, Clock]
    _clk_config: ClockConfig
    _rst_config: ResetConfig

    clk: Clock
    const: TConst
    valid_cfg: ValidationConfig
    teardown_cfg: TeardownConfig
    dut: HierarchyObject

    def __init__(self, dut: HierarchyObject = None, const: TConst = None, clk_cfg: ClockConfig = None, rst_cfg: ResetConfig = None, valid_cfg: ValidationConfig = None, teardown_cfg: TeardownConfig = None, ctx: TestContext = None) -> None:
        self._error_count = 0
        self._error_msgs = {}
        self._clk_dict = {}
        self._thread_lock = threading.Lock()
        self._log = SimLog(type(self).__name__)

        def first_not_none(values: list, error_msg: str = None):
            for val in values:
                if val is not None:
                    return val
            if error_msg is not None:
                assert False, error_msg
            else:
                return None

        self.dut = first_not_none([dut, ctx.dut if ctx is not None else None], f"{type(self).__name__} has been initialized without providing a DUT reference and no DUT reference was found in the provided context")
        self.const = first_not_none([const, ctx.const if ctx is not None else None], f"{type(self).__name__} has been initialized without providing a {TConst.__name__} reference and no {TConst.__name__} reference was found in the provided context")

        self._clk_config = first_not_none([clk_cfg, ctx._clk_config if ctx is not None else None])
        self._rst_config = first_not_none([rst_cfg, ctx._rst_config if ctx is not None else None])

        self.valid_cfg = ValidationConfig()
        self.teardown_cfg = TeardownConfig()
        self.valid_cfg.default_to(valid_cfg)
        self.teardown_cfg.default_to(teardown_cfg)
        if ctx is not None:
            self.valid_cfg.default_to(ctx.valid_cfg)
            self.teardown_cfg.default_to(ctx.teardown_cfg)

        if self._clk_config is not None:
            self.add_clk(self._clk_config, main=True, start=True)

    def add_clk(self, clk_cfg: ClockConfig, main: bool = False, start: bool = False) -> None:
        self._clk_dict[clk_cfg.name] = Clock(getattr(self.dut, clk_cfg.name), clk_cfg.name, clk_cfg.period, clk_cfg.units)
        self.__setattr__(clk_cfg.name, self._clk_dict[clk_cfg.name])
        if main:
            self.clk = self._clk_dict[clk_cfg.name]
        if start:
            self.start_clk(clk_cfg.name)

    def start_clk(self, name: str = None):
        if name:
            self._clk_dict[name].start_soon()
        else:
            for clk in self._clk_dict.values():
                clk.start_soon()

    def stop_clk(self, name: str = None):
        if name:
            self._clk_dict[name].stop()
        else:
            for clk in self._clk_dict.values():
                clk.stop()

    async def reset(self, config: ResetConfig = None, clk: Clock = None) -> None:
        """Reset the DUT.

        Args:
            dut: The device under test
            time: The time to hold the reset
            units: The unit of the time value
            clk: The clock used for post reset edge synchronization
            edge: The clock edge to synchronize to after reset
        """
        if config is not None:
            rst_conf = config
        elif self._rst_config is not None:
            rst_conf = self._rst_config
        else:
            self._log.debug("No reset configuration available")
            return

        if clk is not None:
            rst_clk = clk
        elif self.clk is not None:
            rst_clk = self.clk
        else:
            rst_clk = None

        rst_signal: HierarchyObject = getattr(self.dut, rst_conf.name)

        self.reset_inputs()
        rst_signal.setimmediatevalue(0 if rst_conf.active_low else 1)
        await timer.delay(rst_conf.duration, rst_conf.units, rst_clk)
        rst_signal.value = 1 if rst_conf.active_low else 0
        await timer.edge_trigger(rst_clk, EdgeType.any)
        rst_signal._log.debug("Reset complete")

        if rst_clk is not None:
            await timer.edge_trigger(rst_clk, rst_conf.edge)

    def reset_inputs(self):
        pass

    def validate(self, predicate: bool, error_msg: str = None, severity: Severity = Severity.error) -> bool:
        if not predicate:
            with self._thread_lock:
                self._error_count += 1
                if error_msg is not None:
                    self._error_msgs[self._error_count] = error_msg
            if severity == Severity.fatal:
                self._report_failure(f"{error_msg}", log=False)
            elif not self.is_valid() and self.valid_cfg.break_if_exceeded:
                self._report_failure(f"Max Error Count Exceeded: {error_msg}", log=False)
            else:
                logging.error(error_msg)
        return predicate

    def is_valid(self) -> bool:
        return self._error_count <= self.valid_cfg.max_error_count

    def assert_valid(self, config: AssertConfig = None) -> Union[Tuple[bool, str], None]:
        if config is None:
            config = AssertConfig()
        if self.is_valid():
            return True, self._report_success(not config.silent)
        else:
            return False, self._report_failure("Test context valid assertion failed", config.soft and not config.silent, raise_exception=not config.soft)

    def _report_success(self, log: bool = True) -> str:
        report_msg = ""
        if self._error_count > 0:
            report_msg += f"Test succeeded with {self._error_count} errors"
            if self.valid_cfg.max_error_count > 0:
                report_msg += f" (max allowed error count: {self.valid_cfg.max_error_count})"
            if len(self._error_msgs) > 0:
                report_msg += self._get_error_msgs_report()
            if log:
                logging.warning(report_msg)
        else:
            report_msg += "Test succeeded without errors"
            if log:
                logging.info(report_msg)

        return report_msg

    def _report_failure(self, error_msg: str = None, log: bool = True, raise_exception: bool = True) -> str:
        report_msg = f"Test failed with {self._error_count} errors"
        if len(self._error_msgs) > 0:
            report_msg += self._get_error_msgs_report()
        if error_msg:
            report_msg += f"\nBreaking error: {error_msg}"
        if log:
            logging.fatal(report_msg)
        if raise_exception:
            assert False, report_msg  # assert is used here because cocotb test wrapper by default listen for AssertionError exceptions to mark a test as failed
        return report_msg

    def _get_error_msgs_report(self, prefix_newline: bool = True) -> str:
        report_msg = "\n" if prefix_newline else ""
        report_msg += "error messages:"
        for i, msg in self._error_msgs.items():
            report_msg += f"\n{i}: {msg}"
        return report_msg
