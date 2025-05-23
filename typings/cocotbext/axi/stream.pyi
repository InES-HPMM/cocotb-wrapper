"""This type stub file was generated by pyright."""

from cocotb_bus.bus import Bus

from .reset import Reset

"""

Copyright (c) 2020 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

class StreamBus(Bus):
    _signals = ...
    _optional_signals = ...
    def __init__(self, entity=..., prefix=..., **kwargs) -> None: ...
    @classmethod
    def from_entity(cls, entity, **kwargs):  # -> Self:
        ...
    @classmethod
    def from_prefix(cls, entity, prefix, **kwargs):  # -> Self:
        ...

class StreamTransaction:
    _signals = ...
    def __init__(self, *args, **kwargs) -> None: ...
    def __repr__(self):  # -> str:
        ...

class StreamBase(Reset):
    _signals = ...
    _optional_signals = ...
    _signal_widths = ...
    _init_x = ...
    _valid_signal = ...
    _valid_init = ...
    _ready_signal = ...
    _ready_init = ...
    _transaction_obj = StreamTransaction
    _bus_obj = StreamBus
    def __init__(
        self, bus, clock, reset=..., reset_active_level=..., *args, **kwargs
    ) -> None: ...
    def count(self):  # -> int:
        ...
    def empty(self):  # -> bool:
        ...
    def clear(self):  # -> None:
        ...

class StreamPause:
    def __init__(self, *args, **kwargs) -> None: ...
    @property
    def pause(self):  # -> bool:
        ...
    @pause.setter
    def pause(self, val):  # -> None:
        ...
    def set_pause_generator(self, generator=...):  # -> None:
        ...
    def clear_pause_generator(self):  # -> None:
        ...

class StreamSource(StreamBase, StreamPause):
    _init_x = ...
    _valid_init = ...
    _ready_init = ...
    def __init__(
        self, bus, clock, reset=..., reset_active_level=..., *args, **kwargs
    ) -> None: ...
    async def send(self, obj):  # -> None:
        ...
    def send_nowait(self, obj):  # -> None:
        ...
    def full(self):  # -> bool:
        ...
    def idle(self):  # -> bool:
        ...
    async def wait(self):  # -> None:
        ...

class StreamMonitor(StreamBase):
    _init_x = ...
    _valid_init = ...
    _ready_init = ...
    def __init__(
        self, bus, clock, reset=..., reset_active_level=..., *args, **kwargs
    ) -> None: ...
    async def recv(self): ...
    def recv_nowait(self): ...
    async def wait(self, timeout=..., timeout_unit=...):  # -> None:
        ...

class StreamSink(StreamMonitor, StreamPause):
    _init_x = ...
    _valid_init = ...
    _ready_init = ...
    def __init__(
        self, bus, clock, reset=..., reset_active_level=..., *args, **kwargs
    ) -> None: ...
    def full(self):  # -> bool:
        ...

def define_stream(
    name,
    signals,
    optional_signals=...,
    valid_signal=...,
    ready_signal=...,
    signal_widths=...,
):  # -> tuple[Any, Any, Any, Any, Any]:
    ...
