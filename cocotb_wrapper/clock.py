from argparse import ArgumentError
from typing import Callable
from cocotb import start_soon, Task
from cocotb.handle import SimHandleBase

from cocotb_wrapper.models import Unit
import cocotb.clock
from cocotb.triggers import Timer
from cocotb_wrapper.models import *
from cocotb_wrapper.log import logging


class Clock(cocotb.clock.Clock):
    name: str
    unit: Unit
    period: float
    half_period: float

    _cocotb_clock: cocotb.clock.Clock
    _task: Task

    def __init__(self, signal, name:str = "main", period: float = 10, unit: Unit= Unit.ns) -> None:
        self._cocotb_clock = cocotb.clock.Clock(signal, period, unit.name)
        self.name = name
        self.unit = unit
        self.period = period
        self.half_period = period / 2
        self.signal = signal
        self._task = None

    async def start(self):
        await self._cocotb_clock.start()

    def start_soon(self) -> Task:
        if self._task is not None and not self._task.done() and not self._task.cancelled():
             logging.warning(f"Clock {self.name} has already been started.")
             return self._task
        self._task = start_soon(self._cocotb_clock.start())
        return self._task

    def stop(self):
        if self._task is None:
            logging.warning(f"Clock {self.name} has not been started using the start_soon() method and has therefore no access to the task handle")
        elif self._task.cancelled():
            logging.warning(f"Clock {self.name} has has already been canceled")
        elif self._task.done():
            logging.warning(f"Clock {self.name} has already finished executing")
        else:
            self._task.kill()

    def __str__(self) -> str:
        return str(self._cocotb_clock)
    