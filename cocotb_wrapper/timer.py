from typing import List, Tuple, Union
from cocotb.triggers import FallingEdge, RisingEdge, Timer, First, Edge, with_timeout, Trigger
from cocotb.handle import ModifiableObject

from cocotb_wrapper.log import logging
from cocotb_wrapper.clock import Clock
from cocotb_wrapper.models import TriggerConfig, Unit, EdgeType


def convert(duration: int, source_unit: Unit, target_unit: Unit, clk: Clock = None) -> int:
    if source_unit == Unit.cycle or target_unit == Unit.cycle:
        assert clk != None, "clk must be specified if source_unit==cycle or target_unit==cycle"
    if source_unit == Unit.us:
        if target_unit == Unit.cycle:
            if clk.unit == Unit.ns:
                cycles_per_source_unit = 1000 / clk.period
            elif clk.unit == Unit.us:
                cycles_per_source_unit = 1 / clk.period
            return int(duration * cycles_per_source_unit)
        elif target_unit == Unit.ns:
            return duration * 1000
    elif source_unit == Unit.ns:
        if target_unit == Unit.cycle:
            if clk.unit == Unit.ns:
                cycles_per_source_unit = 1 / clk.period
            elif clk.unit == Unit.us:
                cycles_per_source_unit = 0.001 / clk.period
            return int(duration * cycles_per_source_unit)
        elif target_unit == Unit.us:
            return duration * 0.001
    elif source_unit == Unit.cycle:
        return convert(duration * clk.period, clk.unit, target_unit, clk)

    raise NotImplementedError(f"Conversion from {source_unit} to {target_unit} is not implemented")


async def edge_trigger(clk: Union[ModifiableObject, Clock], edge: EdgeType) -> Trigger:
    """awaits the specified edge type using the given clock (EdgeType.none is ignored)

    Args:
        clk (Handle): the DUT signal whose edge to sync to
        edge (EdgeType): the edge to sync to
    """
    if edge != EdgeType.none:
        await get_edge_trigger(clk, edge)


def get_edge_trigger(clk: Union[ModifiableObject, Clock], edge: EdgeType) -> Trigger:
    """awaits the specified edge type using the given clock

    Args:
        clk (Handle): the DUT signal whose edge to sync to
        edge (EdgeType): the edge to sync to
    """
    if isinstance(clk, Clock):
        clk_sim = clk.signal
    else:
        clk_sim = clk

    if edge == edge.rising:
        return RisingEdge(clk_sim)
    elif edge == edge.falling:
        return FallingEdge(clk_sim)
    elif edge == edge.any:
        return Edge(clk_sim)


async def trigger_with_timeout(trigger_configs: Union[TriggerConfig, List[TriggerConfig]], duration: int, unit: Unit = Unit.cycle, clk: Clock = None, post_trigger_sync_edge: EdgeType = EdgeType.none, silent_timeout=False) -> bool:
    delay_duration, delay_unit, delay_edge = await get_delay_specs(duration, unit, clk)
    if isinstance(trigger_configs, list):
        _trigger_configs = trigger_configs
    else:
        _trigger_configs = [trigger_configs]
    try:
        await with_timeout(First(*[get_edge_trigger(tc.dut_signal, tc.edge) for tc in _trigger_configs]), delay_duration, delay_unit.name)
        valid = True
    except TimeoutError as e:
        if not silent_timeout:
            logging.error(f"Trigger First({[repr(t.dut_signal) for t in _trigger_configs]}) timed out after {duration} {unit.name}")
        valid = False
    if clk != None:
        await edge_trigger(clk.signal, post_trigger_sync_edge)
    elif post_trigger_sync_edge != EdgeType.none:
        logging.warning(f"trigger_with_timeout called with post_trigger_sync_edge {post_trigger_sync_edge} requires a clock")
    return valid


async def get_delay_specs(duration: int, unit: Unit = Unit.cycle, clk: Clock = None, edge: EdgeType = EdgeType.none) -> Tuple[int, Unit, EdgeType]:
    assert not (clk == None and unit in (Unit.cycle, Unit.edge)), f"Unit {unit} requires a clock"
    assert not (clk == None and edge != EdgeType.none), f"EdgeType {edge} requires a clock"
    assert not (unit == Unit.edge and edge == EdgeType.none), f"Unit {unit} is not compatible with EdgeType {edge}"

    if unit == Unit.cycle:
        unit = clk.unit
        duration *= clk.period
    elif unit == Unit.edge:
        unit = clk.unit
        if edge == EdgeType.any:
            # set timer delay to accumulation of 1 half_period less that the specified edge count and then synchronize to the specified edge afterwards
            duration = (duration - 1) * clk.half_period
        else:
            # set timer delay to accumulation of 1 period less that the specified edge count and then synchronize to the specified edge afterwards
            duration = (duration - 1) * clk.period
    return duration, unit, edge


async def delay(duration: int, unit: Unit = Unit.cycle, clk: Clock = None, edge: EdgeType = EdgeType.none) -> None:
    """delays the current thread by <duration> times the specified Unit.
    If a clock and edge are specified the thread is synchronized to the specified edge AFTER the delay timer returns (this can extend the total delay over the specified duration)
    For Unit.edge, the process delays for exactly the number of specified edges

    Args:
        duration (int): The amount of specified unit to delay
        unit (Unit, optional): The time unit for the specified duration. Defaults to Unit.cycle.
        clk (Clock, optional): The clock whose period and edges is used to await cycles and terminate on a specific edge. Defaults to None.
        edge (EdgeType, optional): The edge on which the delay should terminate. Defaults to EdgeType.none.
    """
    if duration <= 0:
        return

    duration, unit, edge = await get_delay_specs(duration, unit, clk, edge)

    if duration > 0:
        await Timer(duration, unit.name)

    if clk != None:
        await edge_trigger(clk.signal, edge)
