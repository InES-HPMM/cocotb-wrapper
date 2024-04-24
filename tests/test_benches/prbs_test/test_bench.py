import random
import cocotb
from cocotb.handle import HierarchyObject
import pathlib

import cocotb_wrapper as ctw
from cocotb_wrapper import timer, check, scheduler
from cocotb_wrapper.models import *
from cocotb_wrapper.log import logging


class TestContext(ctw.TestContext[ctw.Constants]):
    def reset_dut_inputs(self):
        self.dut.data_i.value = 0

    def setup_signal_loopback(self, data_value_count: int = 0, constant_delay: int = 0, max_data_clk_jitter: int = 0, data_clk_period_drift_ratio: float = 0, data_clk_drift_type: str = "speed_up"):
        data_clk_drift = -1 if data_clk_drift_type == "speed_up" else 1

        if data_value_count > 0:
            data_clk_period = int(self.clk_data.period)
            sample_clk_period = int(self.clk_sample.period)
            # create a list of delays for each data bit for jitter and clock drift simulation
            delay_durations = [data_clk_period for i in range(data_value_count)]

            if max_data_clk_jitter > 0:
                # add random jitter to the data clock without affecting the overall constant delay of the loopback
                jitter_sum = 0
                jitter_sign = 1
                for i in range(data_value_count):
                    jitter = random.randint(0, max_data_clk_jitter)
                    if abs(jitter_sum + jitter_sign * jitter) > max_data_clk_jitter:
                        jitter_sign *= -1
                    delay_durations[i] += jitter_sign * jitter
                    jitter_sum += jitter_sign * jitter

            if data_clk_period_drift_ratio > 0:
                # adjust the delays between data bits to simulate clock drift
                data_cycle_count_before_drift = int(1 / data_clk_period_drift_ratio)
                for i in range(0, data_value_count, data_cycle_count_before_drift):
                    delay_durations[i] += data_clk_drift * sample_clk_period

            return cocotb.start_soon(scheduler.signal_loopback_individual_delays(self.dut.data_o, self.dut.data_i, self.clk_data, delay_durations))
        elif max_data_clk_jitter > 0:
            return cocotb.start_soon(scheduler.signal_loopback_random_jitter(self.dut.data_o, self.dut.data_i, self.clk_data, constant_delay, max_data_clk_jitter))
        else:
            return cocotb.start_soon(scheduler.signal_loopback(self.dut.data_o, self.dut.data_i, self.clk_data, constant_delay))


tb = ctw.Testbench(
    pathlib.Path(__file__).parent.resolve().name,
    ClockConfig("clk_sample", 10, Unit.ns),
    ResetConfig("rst_n", 50, Unit.ns, EdgeType.falling, True),
    ValidationConfig(0, False),
    TeardownConfig(5, True),
)


@tb.register_setup()
async def setup(ctx: ctw.TestContext, args: list, kwargs: dict) -> TestContext:
    ctx = TestContext(ctx=ctx)
    ctx.add_clk(ClockConfig("clk_data", ctx.clk.period * ctx.const.G_SAMPLE_DATA_CLK_RATIO, Unit.ns), start=True)
    await ctx.reset()
    return ctx


@tb.register_test(skip=True)
async def sandbox(ctx: TestContext):
    """Sanbox for debugging"""
    valid = True

    logging.info(f"clk period: {ctx.clk.period}")

    assert valid, "Check Logs for errors"


@tb.register_test(expect_fail=True)
async def error_tracking_test(ctx: TestContext):
    """Ensure that the prbs test can detect bit errors by turning off the loopback process after a while and checking the bit error results"""
    # let loopback run for 5us and then stop it
    rx_tx_loopback = ctx.setup_signal_loopback()
    await timer.delay(5, Unit.us)
    rx_tx_loopback.kill()

    # wait for one BER average cycle to ensure that the bit error result min and max values are updated at least once
    # ctx.dut.bit_error_result_o is updated 1 cycle after mov_avg_output_en is set, so we trigger for the first falling clk_data edge after the mov_avg_output_en falling edge
    ctx.validate(await timer.trigger_with_timeout(TriggerConfig(ctx.dut.mov_avg_output_en, EdgeType.falling), duration=2 ** (ctx.const.G_BER_AVG_CYCLE_DURATION_LOG + 1), clk=ctx.clk_data, post_trigger_sync_edge=EdgeType.falling))

    # all three checks must fail to pass the test
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.avg, 0))
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.max, 0))
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.min, 0))


@tb.register_test()
async def basic_validation_test(ctx: TestContext):
    """Run a simple loopback for a long time and check if the bit error results are zero"""
    rx_tx_loopback = ctx.setup_signal_loopback()
    await timer.delay(1000, Unit.us)
    # wait for the next BER average cycle to ensure that the bit error result min and max values are updated with the most recent data
    ctx.validate(await timer.trigger_with_timeout(TriggerConfig(ctx.dut.mov_avg_output_en, EdgeType.falling), duration=2 ** (ctx.const.G_BER_AVG_CYCLE_DURATION_LOG + 1), clk=ctx.clk_data, post_trigger_sync_edge=EdgeType.falling))
    rx_tx_loopback.kill()
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.avg, 0))
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.max, 0))
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.min, 0))


@tb.register_test()
async def constant_delay_test(ctx: TestContext):
    """Run loopbacks for possible ns delays to simulate different clk misalignments and check if the bit error results are zero"""
    for i in range(ctx.clk_data.period):
        loopback_driver = ctx.setup_signal_loopback(constant_delay=i)
        # wait for one BER average cycle to ensure that the bit error result min and max values are updated at least once
        # ctx.dut.bit_error_result_o is updated 1 cycle after mov_avg_output_en is set, so we trigger for the first falling clk_data edge after the mov_avg_output_en falling edge
        await timer.trigger_with_timeout(TriggerConfig(ctx.dut.mov_avg_output_en, EdgeType.falling), duration=2 ** (ctx.const.G_BER_AVG_CYCLE_DURATION_LOG + 1), clk=ctx.clk_data, post_trigger_sync_edge=EdgeType.falling)
        loopback_driver.kill()
        ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.avg, 0))
        ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.max, 0))
        ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.min, 0))
        await ctx.reset()


@tb.register_test()
async def clk_drift_with_jitter(ctx: TestContext):
    """Tests whether the prbs test can withstand up to +-1 sample clk cycles jitter and clock drift without failing"""
    await ctx.setup_signal_loopback(data_value_count=10**4, data_clk_period_drift_ratio=1 / 100, data_clk_drift_type="speed_up")
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.avg, 0))
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.max, 0))
    ctx.validate(check.compare_sim(ctx.dut.bit_error_result_o.min, 0))
