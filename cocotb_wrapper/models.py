from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, List, TypeVar
import cocotb_wrapper.convert as conv
from cocotb.handle import SimHandle
import queue


class EdgeType(Enum):
    none = 0
    rising = 1
    falling = 2
    any = 3


class Unit(Enum):
    step = 0
    fs = 1
    ps = 2
    ns = 3
    us = 4
    ms = 5
    sec = 6
    cycle = 7
    edge = 8


class Severity:
    error = 0
    fatal = 1


TChild = TypeVar("TChild")


class Defaultable(Generic[TChild]):
    def default_to(self, obj: TChild):
        if obj is not None:
            for key, value in self.__dict__.items():
                if value is None:
                    setattr(self, key, obj.__dict__[key])
        return self

    def set_from(self, obj: TChild):
        if obj is not None:
            for key, value in obj.__dict__.items():
                setattr(self, key, value)
        return self


class ClockConfig:
    def __init__(self, name: str, period: float, units: Unit) -> None:
        self.name = name
        self.period = period
        self.units = units


class ResetConfig:
    def __init__(self, name: str, duration: int, units: Unit, edge: EdgeType = EdgeType.none, active_low: bool = False) -> None:
        self.name = name
        self.duration = duration
        self.units = units
        self.edge = edge
        self.active_low = active_low


class AssertConfig:
    def __init__(self, silent: bool = False, soft: bool = False) -> None:
        self.silent = silent
        self.soft = soft


class ValidationConfig(Defaultable["ValidationConfig"]):
    def __init__(self, max_error_count: int = None, break_if_exceeded: bool = None):
        self.max_error_count = max_error_count
        self.break_if_exceeded = break_if_exceeded


class TeardownConfig(Defaultable["TeardownConfig"]):
    def __init__(self, delay_cycles: int = None, assert_valid: bool = None):
        self.delay_cycles = delay_cycles
        self.assert_valid = assert_valid


@dataclass
class TriggerConfig:
    dut_signal: SimHandle
    edge: EdgeType


class TestContextValidationException(Exception):
    pass


T = TypeVar("T")


class PriorityFifoQueue(queue.PriorityQueue, Generic[T]):
    """a priority queue that includes an insert index with each element to ensure stable fifo queue behavior within elements of the same priority"""

    def __init__(self, maxsize=0):
        super().__init__(maxsize=maxsize)
        self._index = 0

    def put(self, item: T, priority: int = None, block: bool = True, timeout: float = None):
        """packs an item with the given priority and the current index into a tuple and adds it to the queue. Priority can be left empty, if the item has a priority property

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).

        Raises:
            ValueError: raised if no priority was given and the item does not contain a priority property
        """
        if priority != None:
            _item = (priority, self._index, item)
        elif hasattr(item, "priority"):
            _item = (item.priority, self._index, item)
        else:
            raise ValueError("Item must have a priority attribute or a priority must be specified")
        super().put(_item, block=block, timeout=timeout)
        self._index += 1

    def get(self, *args, **kwargs) -> T:
        """gets the highest priority and oldest tuple from the queue and unpacks it to only return the item

        Returns:
            T: the highest priority and oldest item in the queue
        """
        _, _, item = super().get(*args, **kwargs)
        return item

    def has_item_of_priority(self, priority: int) -> bool:
        """iterates the queue until first item of the given priority is found

        Args:
            priority (int): the priority to search for

        Returns:
            bool: true if item of priority is found
        """
        for item_prio, _, _ in self.queue:
            if item_prio == priority:
                return True
        return False
