import random
from typing import Callable, Dict, Generic, TypeVar, Tuple, Union
import cocotb
from cocotb.handle import HierarchyObject
import pathlib
import threading

import cocotb_wrapper as ctw
from cocotb_wrapper.testbench import TestContext
from cocotb_wrapper import timer, check, scheduler
from cocotb_wrapper.clock import Clock
from cocotb_wrapper.models import *
from cocotb_wrapper.log import logging
from .const import Constants
from .models import *


class TestContext(ctw.TestContext[Constants]):
    def __init__(self, gm: BlockBuffer, const: Constants, clk_cfg: ClockConfig = None, rst_cfg: ResetConfig = None, valid_cfg: ValidationConfig = None, teardown_cfg: TeardownConfig = None, ctx: ctw.TestContext = None) -> None:
        super().__init__(const=const, ctx=ctx)
        self.gm = gm
        self.cycle_count = 0

    def reset_inputs(self):
        self.gm.wr_data_i = [0 for i in range(self.const.G_BLOCK_DEPTH)]
        self.gm.wr_en_i = False
        self.dut.wr_data_i.value = [0 for i in range(self.const.G_BLOCK_DEPTH)]
        self.dut.wr_en_i.value = 0

    def set_input(self, data_count: int):
        """writes a block of random data followed by a terminator sequence to the dut input ports but doesn't advance in time

        Args:
            data_count (int): the number of cells to fill in the input block
        """
        assert data_count < self.const.G_BLOCK_DEPTH, f"data_count {data_count} exceeds block_depth {self.const.G_BLOCK_DEPTH}"
        max_data_value = 2 ** (self.const.G_BLOCK_WIDTH // 2)  # only half of the block width is reserved for data, the other half is reserved for control characters like the sequence terminator
        data = random.sample(range(max_data_value), data_count)
        data.append(self.const.sequence_terminator)
        for i in range(self.const.G_BLOCK_DEPTH - data_count - 1):
            data.append(0)

        logging.info(f"writing {[hex(x) for x in data]}")

        self.gm.wr_data_i = list(data)
        self.gm.wr_en_i = True

        # dut list assignment starts by mapping the last python list element to the dut list index 0 and so forth. Therefore python list need to be reversed befor assignment
        self.dut.wr_data_i.value = list(reversed(data))
        self.dut.wr_en_i.value = 1

    async def check_output(self, cycle_count, reset_inputs):
        for i in range(cycle_count):

            self.gm.tick()
            await timer.edge_trigger(self.clk, EdgeType.falling)
            self.cycle_count += 1
            logging.info(f"clock cycle #{self.cycle_count}")

            logging.debug(f"GM reading {hex(self.dut.rd_data_o.value)}")
            logging.debug(f"GM buffer {[[y for y in b.data] for b in self.gm.buffer]}")
            logging.debug(f"GM buffer tail {self.gm.tail}")
            logging.debug(f"GM buffer head {self.gm.head}")
            logging.debug(f"GM buffer current block cell index {self.gm.buffer[self.gm.tail].index}")
            logging.debug(f"GM buffer current block full {self.gm.buffer[self.gm.tail].full}")
            logging.debug(f"GM buffer current block data {self.gm.buffer[self.gm.tail].data[self.gm.buffer[self.gm.tail].index]}")

            self.validate(check.compare("wr_en_i", self.dut.wr_en_i, self.gm.wr_en_i))
            for act, exp, i in zip(reversed(self.dut.wr_data_i.value), self.gm.wr_data_i, range(self.const.G_BLOCK_DEPTH)):
                self.validate(check.compare_hex(f"wr_data_i[{i}]", act, exp))
            self.validate(check.compare_hex("rd_data_o", self.dut.rd_data_o, self.gm.get_rd_data()))
            self.validate(check.compare("rd_valid_o", self.dut.rd_valid_o, self.gm.get_rd_valid()))
            self.validate(check.compare("empty_o", self.dut.empty_o, self.gm.is_empty()))
            self.validate(check.compare("full_o", self.dut.full_o, self.gm.is_full()))
            self.validate(check.compare("fill_count_o", self.dut.fill_count_o, self.gm.get_fill_count()))

            if reset_inputs:
                self.reset_inputs()


tb = ctw.Testbench(
    pathlib.Path(__file__).parent.resolve().name,
    ClockConfig("clk", 20, Unit.ns),
    ResetConfig("rst_n", 200, Unit.ns, EdgeType.falling, True),
    ValidationConfig(0, False),
    TeardownConfig(5, True),
)


@tb.register_setup()
async def setup(ctx: ctw.TestContext, args: list, kwargs: dict) -> TestContext:
    constants = Constants(ctx.dut)
    ctx = TestContext(gm=BlockBuffer(constants), const=constants, ctx=ctx)  # create custom test context from the default test context of the testbench
    ctx.reset_inputs()
    await ctx.reset()
    return ctx  # return the custom test context to force the testbench to use it


@tb.register_test(skip=True)
async def sandbox(ctx: TestContext):
    """Sanbox for debugging"""

    ctx.set_input(5)
    await ctx.check_output(ctx.const.G_BLOCK_DEPTH + 1, True)


@tb.register_test()
async def single_block_rw(ctx: TestContext):
    """Feed a single block into the buffer and check the output until the entire block is serialized"""
    ctx.set_input(ctx.const.G_BLOCK_DEPTH - 1)
    await ctx.check_output(ctx.const.G_BLOCK_DEPTH + 1, True)


@tb.register_test()
async def random_stress_test(ctx: TestContext):
    """Repeatedly write random length of random data and read for random amount of cycles to simulate real-worls scenario"""

    for i in range(1000):
        ctx.set_input(random.randrange(0, ctx.const.G_BLOCK_DEPTH))
        await ctx.check_output(random.randrange(0, 2 * ctx.const.G_BLOCK_DEPTH), True)


@tb.register_test()
async def overflow(ctx: TestContext):
    """Overflow the buffers block count to ensure that no unprocessed blocks are overridden"""
    insert_block_count = ctx.const.G_BLOCK_COUNT + 1
    insert_cell_count = 10
    for i in range(insert_block_count):
        ctx.set_input(insert_cell_count)
        await ctx.check_output(1, True)

    await ctx.check_output((insert_block_count - 1) * insert_cell_count - insert_block_count, True)
