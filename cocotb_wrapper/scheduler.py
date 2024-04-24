import queue
from typing import Callable, List, Tuple
import random
import math
import functools

import cocotb
from cocotb.triggers import RisingEdge
from cocotb.types import Logic
from cocotb.handle import ModifiableObject

from cocotb_wrapper.log import logging
from cocotb_wrapper.clock import Clock
from cocotb_wrapper.models import TriggerConfig, Unit, EdgeType
from cocotb_wrapper import timer, check


class ValidatorResult:
    valid: int
    error_count: int

    def __init__(self):
        self.valid = True
        self.error_count = 0


async def drive_single_pulse(dut_signal: ModifiableObject, value: int = 1, duration: int = 1, unit: Unit = Unit.cycle, clk: Clock = None, start_edge: EdgeType = EdgeType.none, delay_edge: EdgeType = EdgeType.none, reset_value: int = 0):
    """drive the given value to the dut_signal for the given duration and then reset the dut_signal to the given reset_value

    Args:
        dut_signal (ModifiableObject): the target DUT signal or port
        value (int, optional): the value to which the signal is set. Defaults to 1.
        duration (int, optional): the duration of the pulse. Defaults to 1.
        unit (Unit, optional): the unit with which the given duration should be interpreted. Defaults to Unit.cycle.
        clk (Clock, optional): the clock to whose edges the process synchronizes to. Defaults to None.
        start_edge (EdgeType, optional): the edge at which the pulse starts. Defaults to EdgeType.none in which case the pulse is emitted from the time the function is called.
        delay_edge (EdgeType, optional): the edge to synchronize to before resetting the dut_signal. Defaults to EdgeType.none.
        reset_value (int, optional): the value to which the signal is set after the pulse. Defaults to 0.

    """
    if clk.signal == 1 and start_edge == EdgeType.falling:
        await timer.edge_trigger(clk.signal, EdgeType.falling)
    elif clk.signal == 0 and start_edge == EdgeType.rising:
        await timer.edge_trigger(clk.signal, EdgeType.rising)

    dut_signal.value = value
    await timer.delay(duration, unit, clk, delay_edge)
    dut_signal.value = reset_value


async def delay_action(action: Callable, delay: int = 1, unit: Unit = Unit.cycle, clk: Clock = None, edge: EdgeType = EdgeType.none)-> any:
    """wait for the given delay before executing the action

    Args:
        action (Callable): the action to execute
        duration (int, optional): the duration of the pulse. Defaults to 1.
        unit (Unit, optional): the unit with which the given duration should be interpreted. Defaults to Unit.cycle.
        clk (Clock, optional): the clock to whose edges the process synchronizes to. Defaults to None.
        edge (EdgeType, optional): The edge on which the delay should terminate. Defaults to EdgeType.none.
    Returns:
        any: forwards the action return value
    """
    await timer.delay(delay, unit, clk, edge)
    return action()


async def delay_triggered_action(action: Callable, trigger_config: TriggerConfig, timeout: int, unit: Unit = Unit.cycle, clk: Clock = None) -> any:
    """wait until the given trigger fires before executing the action

    Args:
        action (Callable): the action to execute
        trigger_config (TriggerConfig): contains the information required to setup the trigger
        timeout (int): the max delay to wait for before aborting
        unit (Unit, optional): the unit with which the given duration should be interpreted. Defaults to Unit.cycle.
        clk (Clock, optional): the clock to whose edges the process synchronizes to. Defaults to None.

    Returns:
        any: false if the trigger times out, else it forwards the action return value
    """
    triggered = await timer.trigger_with_timeout([trigger_config], timeout, unit, clk)
    if triggered:
        return action()
    else:
        return False


async def validate_bit_stream(sim_handle: ModifiableObject, clk: Clock, data_exp: List[int], edge: EdgeType = EdgeType.rising, init_sync:bool=False) -> bool:
    """checks in realtime if the data sent through the sim_handle handle matches the given data_exp list

    Args:
        sim_handle (ModifiableObject): the sim_handle to validate
        clk (Clock): the clock with which the sim_handles signal is driven
        data_exp (List[int]): the expected output of the sim_handle (one value per clk cycle)
        edge (EdgeType, optional): the edge to which the process synchronizes to before validating the next value. Defaults to EdgeType.rising.
        init_sync (bool, optional): specifies, whether the process synchronizes to the given edge before the first validation. Defaults to False.

    Returns:
        bool: true if the sim_handles output matches the expected data
    """
    bit_stream_act: List[int] = []
    bit_error_indexes: List[int] = []
    valid = True
    if init_sync:
        await timer.edge_trigger(clk, edge)
    for bit in data_exp:
        if not check.compare(f"{repr(sim_handle)}[{len(bit_stream_act)}]", sim_handle, bit):
            valid = False
            bit_error_indexes.append(len(bit_stream_act))
        bit_stream_act.append(sim_handle.value)
        await timer.edge_trigger(clk, edge)

    if not valid:
        logging.error(f"bit streams don't match at indexes: {bit_error_indexes}")
        logging.error(f"GM : {data_exp}, length: {len(data_exp)}")
        logging.error(f"DUT: {bit_stream_act}, length: {len(bit_stream_act)}")
    return valid


async def drive_signal(dut_signal: ModifiableObject, clk: Clock, unit: Unit, value_duration: List[Tuple[int, float, EdgeType]]) -> None:
    """cocotb.coroutine: drive a signal based on the given value_duration instruction list

    Args:
        dut_signal (ModifiableObject): the target DUT signal or port
        clk (Clock): the clock to whose edges the process synchronizes to. if all edges are EdgeType.None and unit is not Unit.cycle, no clock is required.
        unit (Unit): the unit with which the given duration should be interpreted
        value_duration (List[Tuple[int, float, EdgeType]]): Tupel Format:(value, duration, edge). A list of interval instructions, where each Tupel consists of the value to drive, the duration to drive the for, and the edge that should be synchronized to before advancing to the next interval.

    """
    for value, duration, edge in value_duration:
        dut_signal.value = value
        await timer.delay(duration, unit, clk, edge)


async def drive_signal_incremental(dut_signal: ModifiableObject, clk: Clock, value_range: range, value_duration: int = 1, unit: Unit = Unit.cycle, edge: EdgeType = EdgeType.none) -> None:
    """cocotb.coroutine: auto incrementing signal driver for e.g. a counter.

    Args:
        dut_signal (ModifiableObject): the target DUT signal or port
        clk (Clock): the clock to whose edges the process synchronizes to. if edge is EdgeType.None and unit is not Unit.cycle, no clock is required.
        unit (Unit): the unit with which the given duration should be interpreted
        value_range (range): the value range to increment through
        value_duration (int, optional): the constant delay between increments. Defaults to 1.
        edge (EdgeType, optional): the edge to synchronize to before incrementing. Defaults to EdgeType.none.
    """
    for value in value_range:
        dut_signal.value = value
        await timer.delay(value_duration, unit, clk, edge)


async def drive_signal_random(dut_signal: ModifiableObject, clk: Clock, unit: Unit, value_range: range, time_range: range = range(1, 2), edge_choices: List[EdgeType] = [EdgeType.none], out_data: List[int] = None):
    """cocotb.coroutine: drives a random signal until stopped or killed

    Args:
        dut_signal (ModifiableObject): the target DUT signal or port
        clk (Clock): the clock to whose edges the process synchronizes to. if edge is EdgeType.None and unit is not Unit.cycle, no clock is required.
        unit (Unit): the unit with which the given duration should be interpreted
        value_range (range): the value range of which the random values are sampled
        time_range (int, optional): the time range of which the durations are sampled. Defaults to range(1,2).
        edge_choices (List[EdgeType], optional): the list of edge type from which the sync edges are sampled. Defaults to [EdgeType.none].
        out_data (List[int], optional): output list to which the random values are written to for subsequent validation. Defaults to None.
    """
    while True:
        value = random.randrange(value_range.start, value_range.stop)
        if out_data != None:
            out_data.append(value)
        dut_signal.value = value
        await timer.delay(random.randrange(time_range.start, time_range.stop), unit, clk, random.choice(edge_choices))


async def signal_loopback_random_jitter(dut_signal_source: ModifiableObject, dut_signal_target: ModifiableObject, clk_data: Clock, constant_delay: float = 0, max_jitter: int = 0, unit: Unit = Unit.ns) -> None:
    """cocotb.coroutine: creates a loopback between a DUT output and input port or two signals until stopped or killed

    Args:
        dut_signal_source (ModifiableObject): output port / source signal
        dut_signal_target (ModifiableObject): input port / target signal
        clk_data (Clock): The clock that the output signal is synchronized to
        constant_delay (float, optional): The duration by which the signal is delayed before looping back to the input, e.g. to simulate combinatorial logic. Defaults to 0.
        max_jitter (int, optional): The max duration by which the input signal may be off sync to the output signals clock. Jitter is applied randomly and without causing clock drift. Defaults to 0.
        unit (Unit, optional): The time unit for both the delay and jitter parameters. Defaults to Unit.ns.
    """
    assert constant_delay < max_jitter, f"constant delay {constant_delay} needs to be greater or equal than max jitter {max_jitter}"
    loopback_queue = queue.Queue()
    cocotb.start_soon(signal_loopback_receiver(dut_signal_source, clk_data, loopback_queue))
    # delay the start of the loopback sender by the specified constant delay. Afterwards the loopback sender is run once every data_clock cycle (+- jitter)
    await timer.delay(constant_delay, unit)
    jitter_sum = 0
    jitter_sign = 1
    while True:
        delay_duration = clk_data.period
        if max_jitter > 0:
            jitter = random.randint(0, max_jitter)
            if abs(jitter_sum + jitter_sign * jitter) > max_jitter:
                jitter_sign *= -1
            delay_duration += jitter_sign * jitter
            jitter_sum += jitter_sign * jitter
        await signal_loopback_sender(dut_signal_target, loopback_queue, delay_duration, unit)


async def signal_loopback(dut_signal_source: ModifiableObject, dut_signal_target: ModifiableObject, clk_data: Clock, constant_delay: float = 0, unit: Unit = Unit.ns):
    """cocotb.coroutine: creates a loopback between a DUT output and input port or two signals until stopped or killed

    Args:
        dut_signal_source (ModifiableObject): output port / source signal
        dut_signal_target (ModifiableObject): input port / target signal
        clk_data (Clock): The clock that the output signal is synchronized to
        constant_delay (float, optional): The duration by which the signal is delayed before looping back to the input, e.g. to simulate combinatorial logic. Defaults to 0.
        unit (Unit, optional): The time unit for both the delay and jitter parameters. Defaults to Unit.ns.
    """
    loopback_queue = queue.Queue()
    cocotb.start_soon(signal_loopback_receiver(dut_signal_source, clk_data, loopback_queue))
    # delay the start of the loopback sender by the specified constant delay. Afterwards the loopback sender is run once every data_clock cycle
    await timer.delay(constant_delay, unit)
    while True:
        await signal_loopback_sender(dut_signal_target, loopback_queue, clk_data.period, unit)


async def signal_loopback_individual_delays(dut_signal_source: ModifiableObject, dut_signal_target: ModifiableObject, clk_data: Clock, delay_durations: List[float], unit: Unit = Unit.ns):
    """cocotb.coroutine: creates a loopback between a DUT output and input port or two signals that runs until the list of delay durations is fully processed

    Args:
        dut_signal_source (ModifiableObject): output port / source signal
        dut_signal_target (ModifiableObject): input port / target signal
        clk_data (Clock): The clock that the output signal is synchronized to
        constant_delay (List[float]): The list of individual delay with whom each data bit of the output signal should be delayed.
        unit (Unit, optional): The time unit for both the individual delays. Defaults to Unit.ns.
    """
    loopback_queue = queue.Queue()
    receiver = cocotb.start_soon(signal_loopback_receiver(dut_signal_source, clk_data, loopback_queue))
    # the loopback sender awaits the specified delay after writing the value. the first individual delay therefore needs to be awaited before the function call
    await timer.delay(delay_durations[0], unit)
    for delay in delay_durations[1:]:
        await signal_loopback_sender(dut_signal_target, loopback_queue, delay, unit)
    receiver.kill()


async def signal_loopback_receiver(dut_signal_source: ModifiableObject, clk_data: Clock, queue: queue.Queue):
    """cocotb.coroutine: creates a thread that feeds the dut signal status into a cue at every rising edge of the data clock

    Args:
        dut_signal_source (ModifiableObject): The dut signal to read
        clk_data (Clock): The data clock used to trigger reading
        queue (queue.Queue): The queue to write the data into
    """
    while True:
        await timer.edge_trigger(clk_data, EdgeType.rising)
        logging.debug(f"signal loopback: value {dut_signal_source.value} received")
        queue.put(dut_signal_source.value)


async def signal_loopback_sender(dut_signal_target: ModifiableObject, queue: queue.Queue, delay_duration: float, unit: Unit = Unit.ns):
    """awaits the given queue for one value, feeds it to the dut signal, awaits the specified delay and then returns

    Args:
        dut_signal_target (ModifiableObject): The dut signal to write to
        queue (queue.Queue): The queue to read from
        delay_duration (float): The delay between the current and the next return bit (e.g the expected input clock period +- jitter). Don't set this parameter to the constant delay of the loopback as this would result in clock drift.
        unit (Unit, optional): The time unit of the delay duration. Defaults to Unit.ns.
    """
    while queue.empty():
        await timer.delay(1, Unit.ns)
    value = queue.get()
    logging.debug(f"signal loopback: value {value} returned")
    dut_signal_target.value = value
    await timer.delay(delay_duration, unit)
