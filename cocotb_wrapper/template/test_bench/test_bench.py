import pathlib

import cocotb_wrapper as ctw
from cocotb_wrapper import timer, check, scheduler
from cocotb_wrapper.models import *
from cocotb_wrapper.const import Constants
from cocotb_wrapper.log import logging

tb = ctw.Testbench(
    pathlib.Path(__file__).parent.resolve().name,
    ClockConfig("clk", 20, Unit.ns),
    ResetConfig("rst_n", 200, Unit.ns, EdgeType.falling, True),
    ValidationConfig(max_error_count=0, break_if_exceeded=True),
    TeardownConfig(delay_cycles=0, assert_valid=True),
)


# class MyConstants(ctw.Constants):
#     def __init__(self, dut: HierarchyObject) -> None:
#         super().__init__(dut)
#         self.my_target_state = 3


# class MyTestContext(ctw.TestContext[MyConstants]):
#     def __init__(self, const: MyConstants, ctx: ctw.TestContext) -> None:
#         super().__init__(const=const, ctx=ctx)
#         self.my_state_tracker = 0


# @tb.register_setup()
# async def setup(ctx: ctw.TestContext, args: list, kwargs: dict) -> ctw.TestContext:
#     # The testbench creates a default test context with the DUT, default config and the clock and reset configurations if specified in the testbench constructor
#     # If you need to adjust the config or other parameters, use the corresponding setter methods
#     # If you want to enrich the test context with additional data or methods, derive your own subclass from TestContext, initialize it and return it at the end of the setup function
#     ctx = MyTestContext(MyConstants(ctx.dut), ctx)
#     ctx.add_clk(ClockConfig("clk_half_speed", ctx.clk.period * 2, ctx.clk.unit), start=True)
#     ctx.reset_inputs()  # the default reset_inputs method does nothing, but can be overridden in a custom TestContext subclass
#     await ctx.reset(clk=kwargs.get("rst_clk", ctx.clk))  # keyword arguments of the register_test decorator are passed to the setup function for test specific setup configurations
#     return ctx  # only necessary if you want to use a custom test context


# @tb.register_teardown()
# async def teardown(ctx: ctw.TestContext, args: list, kwargs: dict):
#     if ctx.teardown_cfg.delay_cycles > 0:
#         await timer.delay(ctx.teardown_cfg.delay_cycles, clk=ctx.clk)

#     if ctx.teardown_cfg.assert_valid:
#         ctx.assert_valid(AssertConfig())
#     await ctx.reset()


@tb.register_test(skip=True)
async def sandbox(ctx: ctw.TestContext):
    """Sanbox for debugging"""

    ctx.validate(1 == 1, error_msg="1 is not equal to 1", severity=Severity.fatal)  # if invalid, this would stop the simulation regardless of the break_if_exceeded setting if validation fails
    await timer.delay(10, Unit.ns)  # wait for 10 ns
    logging.info("10 ns later")  # log to test bench logger (uses different log levels than cocotb logger and can be set using pytest --log-cli-level option)
    ctx.validate(2 == 2, error_msg="2 is not equal to 2", severity=Severity.error)  # if invalid, this would not stop the simulation if the break_if_exceeded setting is True
    await timer.delay(10, Unit.ns)  # wait for 10 ns
    logging.info("10 ns later")  # log to test bench logger (uses different log levels than cocotb logger and can be set using pytest --log-cli-level option)
    ctx.validate(check.compare_hex("3==3", 3, 3))  # error message can be omitted as check.compare_hex will log an error message if the comparison fails

    # the default teardown will assert whether the test context is valid and fail the test if it isn't


# @tb.register_test(skip=True)
# async def sandbox_custom(ctx: MyTestContext):
#     """Sanbox for debugging"""

#     for i in range(ctx.const.my_target_state):
#         ctx.my_state_tracker += 1
#         logging.info(f"State tracker: {ctx.my_state_tracker}")
#         await timer.delay(10, Unit.ns)

#     ctx.validate(ctx.my_state_tracker == ctx.const.my_target_state, error_msg=f"State tracker {ctx.my_state_tracker} is not equal to target state {ctx.const.my_target_state}", severity=Severity.error)

#     # the default teardown will assert whether the test context is valid and fail the test if it isn't
