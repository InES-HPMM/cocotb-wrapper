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

class AxiStreamFrame:
    def __init__(
        self,
        tdata=...,
        tkeep=...,
        tid=...,
        tdest=...,
        tuser=...,
        tx_complete=...,
    ) -> None: ...
    def normalize(self):  # -> None:
        ...
    def compact(self):  # -> None:
        ...
    def handle_tx_complete(self):  # -> None:
        ...
    def __eq__(self, other) -> bool: ...
    def __repr__(self):  # -> str:
        ...
    def __len__(self):  # -> int:
        ...
    def __iter__(self):  # -> Iterator[int] | Iterator[Any]:
        ...
    def __bytes__(self):  # -> bytes:
        ...

class AxiStreamBus(Bus):
    _signals = ...
    _optional_signals = ...
    def __init__(self, entity=..., prefix=..., **kwargs) -> None: ...
    @classmethod
    def from_entity(cls, entity, **kwargs):  # -> Self:
        ...
    @classmethod
    def from_prefix(cls, entity, prefix, **kwargs):  # -> Self:
        ...

class AxiStreamBase(Reset):
    _signals = ...
    _optional_signals = ...
    _type = ...
    _init_x = ...
    _valid_init = ...
    _ready_init = ...
    def __init__(
        self,
        bus,
        clock,
        reset=...,
        reset_active_level=...,
        byte_size=...,
        byte_lanes=...,
        *args,
        **kwargs,
    ) -> None: ...
    def count(self):  # -> int:
        ...
    def empty(self):  # -> bool:
        ...
    def clear(self):  # -> None:
        ...

class AxiStreamPause:
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

class AxiStreamSource(AxiStreamBase, AxiStreamPause):
    _type = ...
    _init_x = ...
    _valid_init = ...
    _ready_init = ...
    def __init__(
        self,
        bus,
        clock,
        reset=...,
        reset_active_level=...,
        byte_size=...,
        byte_lanes=...,
        *args,
        **kwargs,
    ) -> None: ...
    async def send(self, frame):  # -> None:
        ...
    def send_nowait(self, frame):  # -> None:
        ...
    async def write(self, data):  # -> None:
        ...
    def write_nowait(self, data):  # -> None:
        ...
    def full(self):  # -> bool:
        ...
    def idle(self):  # -> bool:
        ...
    async def wait(self):  # -> None:
        ...

class AxiStreamMonitor(AxiStreamBase):
    _type = ...
    _init_x = ...
    _valid_init = ...
    _ready_init = ...
    def __init__(
        self,
        bus,
        clock,
        reset=...,
        reset_active_level=...,
        byte_size=...,
        byte_lanes=...,
        *args,
        **kwargs,
    ) -> None: ...
    async def recv(self, compact=...): ...
    def recv_nowait(self, compact=...): ...
    async def read(self, count=...):  # -> list[Any]:
        ...
    def read_nowait(self, count=...):  # -> list[Any]:
        ...
    def idle(self):  # -> bool:
        ...
    async def wait(self, timeout=..., timeout_unit=...):  # -> None:
        ...

class AxiStreamSink(AxiStreamMonitor, AxiStreamPause):
    _type = ...
    _init_x = ...
    _valid_init = ...
    _ready_init = ...
    def __init__(
        self,
        bus,
        clock,
        reset=...,
        reset_active_level=...,
        byte_size=...,
        byte_lanes=...,
        *args,
        **kwargs,
    ) -> None: ...
    def full(self):  # -> bool:
        ...
