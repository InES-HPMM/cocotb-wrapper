# ============================================================
#   _____       ______  _____
#  |_   _|     |  ____|/ ____|
#    | |  _ __ | |__  | (___    Institute of Embedded Systems
#    | | | '_ \|  __|  \___ \   Zurich University of
#   _| |_| | | | |____ ____) |  Applied Sciences
#  |_____|_| |_|______|_____/   8401 Winterthur, Switzerland
# ============================================================

"""Provide a wrapper classes around `cocotbext-axi <https://github.com/alexforencich/cocotbext-axi>`_."""

from __future__ import annotations

__author__ = "Thierry Delafontaine"
__mail__ = "deaa@zhaw.ch"
__copyright__ = "2022 ZHAW Institute of Embedded Systems"
__date__ = "2022-12-20"

from collections.abc import Iterator
from enum import IntEnum, IntFlag
from itertools import cycle
from random import getrandbits

import cocotbext.axi as axi
from cocotb.handle import HierarchyObject
from cocotb.log import SimLog
from cocotb.triggers import Event


def bits_to_bytes(b: int) -> int:
    """Convert a number of bits to bytes.

    Args:
        b: The number of bits

    Returns:
        The number of bytes
    """
    return (b + 7) // 8


class AxiBurstType(IntEnum):
    """The burst type used during the AXI write transaction."""

    FIXED = 0b00
    """A fixed size burst.

    In a fixed size burst :footcite:`AmbaAxiAndAcArmLimited2021`

    * The address is the same for every transfer in the burst.
    * The byte lanes that are valid are constant for all beats in the burst.
      However, within those byte lanes, the actual bytes that thave **WSTRB**
      asserted can differ for each beat in the burst.
    """
    INCR = 0b01
    """An incrementing burst.

    In an incrementing burst, the address for each tranfer in the burst is an
    increment of the address for the previous transfer. The inceremnnt value
    depends on the size of the transfer. For example, for an aligned start
    address, the address for each trasnfer in a burst with a size of 4 bytes is
    the previous address plus four. :footcite:`AmbaAxiAndAcArmLimited2021`
    """

    WRAP = 0b10
    """A wrapping burst.

    A wrapping burst is similar to an incrementing burst, except  that the
    address wraps around to a lower address if an upper  address limit is
    reached.

    The following restrictions apply to wrapping bursts:

    * The start address must be aligned to the size of each transfer.
    * the length of the burst must be 2, 4, 8, or 16 transfers.

    The behavior of a wrapping burst is:

    * The lowest address that is used by the burst is aligned to the total size
      of the adat to be transferred, that is, to ((size of each transfer in the
      burst) x (number of transfers in the burst)). This address is
      defined as the *wrap boundary*.
    * After each transfer, the address increments in the same way as for an INCR
      burst. However, if this inceremented address is ((wrap boundary) +
      (total size of data to be transferred)), then the address wraps round to
      the wrap boundary.
    * The first transfer in the burst can use an address that is higher than the
      wrap boundary, subject to the restrictions that apply to wrapping
      bursts. The address wraps for any WRAP burst when the first address is
      higher than the wrap boundary.

    This burst type is used for cache line accesses.
    :footcite:`AmbaAxiAndAcArmLimited2021`
    """


class AxiBurstSize(IntEnum):
    """The number of bytes in each data transfer in a write transaction.

    The burst size must be a power of 2, that is 1, 2, 4, 8, 16, 32, 64, or 128
    bytes. :footcite:`AmbaAxiAndAcArmLimited2021`
    """

    SIZE_1 = 0b000
    """A burst size of 1."""
    SIZE_2 = 0b001
    """A burst size of 2."""
    SIZE_4 = 0b010
    """A burst size of 4."""
    SIZE_8 = 0b011
    """A burst size of 8."""
    SIZE_16 = 0b100
    """A burst size of 16."""
    SIZE_32 = 0b101
    """A burst size of 32."""
    SIZE_64 = 0b110
    """A burst size of 64."""
    SIZE_128 = 0b111
    """A burst size of 128."""


class AxiLockType(IntEnum):
    """The AXI Lock type supported by AXI3.

    AXI4 does not support locked transactions. In AXI3 the **AxLOCK** signals
    specify normal, exclusive, and locked accesses.
    :footcite:`AmbaAxiAndAcArmLimited2021`
    """

    NORMAL = 0b0
    """Normal access."""
    EXCLUSIVE = 0b1
    """Exclusize access."""


class AxiCacheBit(IntFlag):
    """The different bits of the **AxCACHE** attribute.

    The **AxCACHE** signals specify the Bufferabel, Modifiable, and Allocate
    attributes of the transaction. :footcite:`AmbaAxiAndAcArmLimited2021`
    """

    B = 0b0001
    """Bufferable bit.

    When this bit is asserted, the interconnect, or any component, can delay the
    transaction reaching its final destination for any number of cycles.
    :footcite:`AmbaAxiAndAcArmLimited2021`
    """
    M = 0b0010
    """Modifiable bit.

    When this bit is asserted the characteristics of the transaction can be
    modified. :footcite:`AmbaAxiAndAcArmLimited2021`
    """
    RA = 0b0100
    """Read-Allocate bit.

    When this bit is asserted, read allocation of the transaction is recomended
    but is not mandatory. The `RA` bit must be asserted if the `M` bit
    deasserted. :footcite:`AmbaAxiAndAcArmLimited2021`
    """
    WA = 0b1000
    """Write-Allocate bit.

    When this bit is asserted, write allocation of the transaction is recomended
    but is not mandatory. The `WA` bit must be asserted if the `M` bit
    deasserted. :footcite:`AmbaAxiAndAcArmLimited2021`
    """


class AxiProt(IntFlag):
    """The permission signals that can be used to protect against illegal transactions."""

    PRIVILEGED = 0b001
    """Privileged access."""
    NONSECURE = 0b010
    """Non-secure access."""
    INSTRUCTION = 0b100
    """Instruction access.

    If this bit is not asserted then the access is a data access.
    """


class AxiResp(IntEnum):
    """The response signals."""

    OKAY = 0b00
    """Normal access success.

    Indicates that a normal access has been successful. Can laso indicate theat
    an aexclusie access has failed. :footcite:`AmbaAxiAndAcArmLimited2021`
    """
    EXOKAY = 0b01
    """Exclusive access okay.

    Indicates that a either the read or write access of an exclusive access has
    been successful. :footcite:`AmbaAxiAndAcArmLimited2021`
    """
    SLVERR = 0b10
    """Subordinate error.

    Used when the access has reached the Subordinate successfully, but the
    Subordinate wishes to return an error condition to the originating Manager.
    :footcite:`AmbaAxiAndAcArmLimited2021`
    """
    DECERR = 0b11
    """Decode error.

    Generated, typically by an interconnect component, to indicate that there is
    no Subordinate at the transaction address.
    :footcite:`AmbaAxiAndAcArmLimited2021`
    """


class AxiMaster:
    """A Wrapper around `cocotbext-axi AXI <https://github.com/alexforencich/cocotbext-axi#axi-and-axi-lite-master>`_.

    Todo:
        Add a usage example.
    """

    def __init__(
        self,
        bus_prefix: str,
        clk: str,
        rst: str,
        reset_active_level: int,
        max_burst_length: int = 256,
    ):
        """Initialize an instance.

        Args:
            bus_prefix: The prefix of signals belonging to the source bus
            clk: The name of the clock
            rst: The name of the reset
            reset_active_level: 1 if active high 0 if active low
            max_burst_length: The maximum burst length in cycles (1 - 256).
        """
        self._bus_prefix = bus_prefix
        self._clk = clk
        self._rst = rst
        self._reset_active_level = reset_active_level
        self._max_burst_length = max_burst_length
        self._log = SimLog(self._bus_prefix)

    def setup(self, dut: HierarchyObject) -> None:
        """Setup the AXI source.

        Args:
            dut: The device under test

        Raises:
            AttributeError: If `dut` does not contain the handles of given with
                `clk` and `rst`.
        """
        self._bus = axi.AxiMaster(
            bus=axi.AxiBus.from_prefix(dut, self._bus_prefix),
            clock=getattr(dut, self._clk),
            reset=getattr(dut, self._rst),
            reset_active_level=bool(self._reset_active_level),
            max_burst_length=self._max_burst_length,
        )

    async def write(
        self,
        address: int,
        data: bytes,
        id: int | None = None,
        burst: AxiBurstType = AxiBurstType.INCR,
        burst_size: AxiBurstSize | None = None,
        lock: AxiLockType = AxiLockType.NORMAL,
        cache: AxiCacheBit = AxiCacheBit.B & AxiCacheBit.M,
        prot: AxiProt = AxiProt.NONSECURE,
        qos: int = 0,
        region: int = 0,
        user: int = 0,
        wuser: int = 0,
    ) -> axi.axi_master.AxiWriteResp:
        """Write `data` to the `address`.

        Args:
            address: The write address
            data: The write data
            id: The AXI burst ID
            burst: The AXI burst type
            burst_size: The AXI burst size
            lock: The AXI lock type
            cache: The AXI cache bits
            prot: The AXI protection flag
            qos: The AXI quality of service field
            region: The AXI region field
            user: The AXI user signal
            wuser: The AXI write user signal

        Returns:
            The response to the write operation
        """
        return await self._bus.write(
            address,
            data,
            id=id,
            burst=burst,
            burst_size=burst_size,
            lock=lock,
            cache=cache,
            prot=prot,
            qos=qos,
            region=region,
            user=user,
            wuser=wuser,
        )

    async def read(
        self,
        address: int,
        length: int,
        id: int | None = None,
        burst: AxiBurstType = AxiBurstType.INCR,
        burst_size: AxiBurstSize | None = None,
        lock: AxiLockType = AxiLockType.NORMAL,
        cache: AxiCacheBit = AxiCacheBit.B & AxiCacheBit.M,
        prot: AxiProt = AxiProt.NONSECURE,
        qos: int = 0,
        region: int = 0,
        user: int = 0,
        wuser: int = 0,
    ) -> axi.axi_master.AxiReadResp:
        """Read `length` bytes from `address`.

        Args:
            address: The read start address
            length: The read size in bytes
            id: The AXI burst ID. Defaults to `None` which assigns an ID
                automatically
            burst: The AXI burst type
            burst_size: The AXI burst size
            lock: The AXI lock type
            cache: The AXI cache bits enables buffering
            prot: The AXI protection flag
            qos: The AXI quality of service field
            region: The AXI region field
            user: The AXI user signal
            wuser: The AXI write user signal

        Returns:
            The response to the read operation, which also contains the data in
            the `data` attribute
        """
        return await self._bus.read(
            address,
            length,
            burst=burst,
            burst_size=burst_size,
            lock=lock,
            cache=cache,
            prot=prot,
            qos=qos,
            region=region,
            user=user,
            wuser=wuser,
        )

    def set_idle_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the write bus lanes given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        for channel in [
            self._bus.write_if.aw_channel,
            self._bus.write_if.w_channel,
            self._bus.read_if.ar_channel,
        ]:
            channel.set_pause_generator(generator)

    def set_backpressure_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the read bus lanes given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        for channel in [
            self._bus.write_if.b_channel,
            self._bus.read_if.r_channel,
        ]:
            channel.set_pause_generator(generator)

    def disable(self) -> None:
        """Disable the AXI master interface."""
        self.set_idle_generator(cycle([1]))
        self.set_backpressure_generator(cycle([1]))

    def enable(self) -> None:
        """Enable the AXI master interface."""
        self.set_idle_generator(cycle([0]))
        self.set_backpressure_generator(cycle([0]))


class AxiRam:
    """A Wrapper around `cocotbext-axi AXI RAM <https://github.com/alexforencich/cocotbext-axi#axi-and-axi-lite-ram>`_.

    Todo:
        Add a usage example.
    """

    def __init__(
        self,
        bus_prefix: str,
        clk: str,
        rst: str,
        reset_active_level: int,
        size: int,
    ):
        """Initialize an instance.

        Args:
            bus_prefix: The prefix of signals belonging to the source bus
            tdata_width_bits: The width of `tdata` in bits
            clk: The name of the clock
            rst: The name of the reset
            reset_active_level: 1 if active high 0 if active low
            size: The memory size in bytes
        """
        self._bus_prefix = bus_prefix
        self._clk = clk
        self._rst = rst
        self._reset_active_level = bool(reset_active_level)
        self._size = size
        self._log = SimLog(self._bus_prefix)

    def setup(self, dut: HierarchyObject) -> None:
        """Setup the AXI RAM.

        Args:
            dut: The device under test

        Raises:
            AttributeError: If `dut` does not contain the handles of given
                with `clk` and `rst`.
        """
        self._ram = axi.AxiRam(
            bus=axi.AxiBus.from_prefix(dut, self._bus_prefix),
            clock=getattr(dut, self._clk),
            reset=getattr(dut, self._rst),
            reset_active_level=self._reset_active_level,
            size=self._size,
        )

    def write(self, address: int, data: bytes) -> None:
        """Write `data` to the `address`.

        Args:
            address: The write address
            data: The write data
        """
        self._ram.write(address, data)

    def read(self, address: int, length: int) -> bytes:
        """Read `length` bytes from `address`.

        Args:
            address: The read start address
            length: The read size in bytes

        Returns:
            The content of the RAM at `address`
        """
        return bytes(self._ram.read(address, length))

    def hexdump(self, address: int, length: int, prefix: str = "RAM") -> None:
        """Dump the content of the RAM to the stdout.

        Args:
            address: The read start address
            length: The read size in bytes
            prefix: A prefix to each output line
        """
        self._ram.hexdump(address, length, prefix)

    def set_idle_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the write bus lanes given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        for channel in [
            self._ram.write_if.b_channel,
            self._ram.read_if.r_channel,
        ]:
            channel.set_pause_generator(generator)

    def set_backpressure_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the read bus lanes given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        for channel in [
            self._ram.write_if.aw_channel,
            self._ram.write_if.w_channel,
            self._ram.read_if.ar_channel,
        ]:
            channel.set_pause_generator(generator)

    def disable(self) -> None:
        """Disable the AXI RAM."""
        self.set_idle_generator(cycle([1]))
        self.set_backpressure_generator(cycle([1]))

    def enable(self) -> None:
        """Enable the AXI RAM."""
        self.set_idle_generator(cycle([0]))
        self.set_backpressure_generator(cycle([0]))


class RandomAxiPayloadGenerator:
    """A generator class that gives back a random payload.

    Todo:
        Add a usage example.
    """

    def __init__(self, data_width_bits: int):
        """Initialize an instance.

        Args:
            data_width_bits: The width of each value in bits
        """
        self._data_width_bits = data_width_bits

    def get_payload(self) -> bytes:
        """Get a random payload.

        Returns:
            The random payload
        """
        return getrandbits(self._data_width_bits).to_bytes(
            bits_to_bytes(self._data_width_bits), byteorder="big"
        )


class AxiLiteMaster:
    """A wrapper class around `cocotbext-axi AXI-Lite Master <https://github.com/alexforencich/cocotbext-axi#axi-and-axi-lite-master>`_.

    Todo:
        Add a usage example.
    """

    def __init__(
        self,
        bus_prefix: str,
        clk: str,
        rst: str,
        reset_active_level: int,
    ):
        """Initialize an instance.

        Args:
            bus_prefix: The prefix of signals belonging to the source bus
            clk: The name of the clock
            rst: The name of the reset
            reset_active_level: 1 if active high 0 if active low
        """
        self._bus_prefix = bus_prefix
        self._clk = clk
        self._rst = rst
        self._reset_active_level = reset_active_level
        self._log = SimLog(self._bus_prefix)

    def setup(self, dut: HierarchyObject) -> None:
        """Setup the AXI-Lite source.

        Args:
            dut: The device under test

        Raises:
            AttributeError: If `dut` does not contain the handles of given
                with `clk` and `rst`.
        """
        self._bus = axi.AxiLiteMaster(
            bus=axi.AxiLiteBus.from_prefix(dut, self._bus_prefix),
            clock=getattr(dut, self._clk),
            reset=getattr(dut, self._rst),
            reset_active_level=bool(self._reset_active_level),
        )

    async def write(
        self,
        address: int,
        data: bytes,
        prot: AxiProt = AxiProt.NONSECURE,
    ) -> axi.axil_master.AxiLiteWriteResp:
        """Write `data` to the `address`.

        Args:
            address: The write address
            data: The write data
            prot: The AXI protection flag

        Returns:
            The response to the write operation
        """
        return await self._bus.write(address, data, prot=prot)

    async def read(
        self,
        address: int,
        length: int,
        prot: AxiProt = AxiProt.NONSECURE,
    ) -> axi.axil_master.AxiLiteReadResp:
        """Read `length` bytes from `address`.

        Args:
            address: The read start address
            length: The read size in bytes
            prot: The AXI protection flag

        Returns:
            The response to the read operation, which also contains the data in
                the `data` attribute
        """
        return await self._bus.read(address, length, prot=prot)

    def set_idle_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the write bus lanes given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        for channel in [
            self._bus.write_if.aw_channel,
            self._bus.write_if.w_channel,
            self._bus.read_if.ar_channel,
        ]:
            channel.set_pause_generator(generator)

    def set_backpressure_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the read bus lanes given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        for channel in [
            self._bus.write_if.b_channel,
            self._bus.read_if.r_channel,
        ]:
            channel.set_pause_generator(generator)

    def disable(self) -> None:
        """Disable the AXI-Lite master interface."""
        self.set_idle_generator(cycle([1]))
        self.set_backpressure_generator(cycle([1]))

    def enable(self) -> None:
        """Enable the AXI-Lite master interface."""
        self.set_idle_generator(cycle([0]))
        self.set_backpressure_generator(cycle([0]))


class AxiLiteRam:
    """A Wrapper around `cocotbext-axi AXI-Lite RAM <https://github.com/alexforencich/cocotbext-axi#axi-and-axi-lite-ram>`_.

    Todo:
        Add a usage example.
    """

    def __init__(
        self,
        bus_prefix: str,
        clk: str,
        rst: str,
        reset_active_level: int,
        size: int,
    ):
        """Initialize an instance.

        Args:
            bus_prefix: The prefix of signals belonging to the source bus
            tdata_width_bits: The width of `tdata` in bits
            clk: The name of the clock
            rst: The name of the reset
            reset_active_level: 1 if active high 0 if active low
            size: The memory size in bytes
        """
        self._bus_prefix = bus_prefix
        self._clk = clk
        self._rst = rst
        self._reset_active_level = bool(reset_active_level)
        self._size = size
        self._log = SimLog(self._bus_prefix)

    def setup(self, dut: HierarchyObject) -> None:
        """Setup the AXI-Lite RAM.

        Args:
            dut: The device under test

        Raises:
            AttributeError: If `dut` does not contain the handles of given
                with `clk` and `rst`.
        """
        self._ram = axi.AxiLiteRam(
            bus=axi.AxiLiteBus.from_prefix(dut, self._bus_prefix),
            clock=getattr(dut, self._clk),
            reset=getattr(dut, self._rst),
            reset_active_level=self._reset_active_level,
            size=self._size,
        )

    def write(self, address: int, data: bytes) -> None:
        """Write `data` to the `address`.

        Args:
            address: The write address
            data: The write data
        """
        self._ram.write(address, data)

    def read(self, address: int, length: int) -> bytes:
        """Read `length` bytes from `address`.

        Args:
            address: The read start address
            length: The read size in bytes

        Returns:
            The content of the RAM at `address`
        """
        return bytes(self._ram.read(address, length))

    def hexdump(self, address: int, length: int, prefix: str = "RAM") -> None:
        """Dump the content of the RAM to the stdout.

        Args:
            address: The read start address
            length: The read size in bytes
            prefix: A prefix to each output line
        """
        self._ram.hexdump(address, length, prefix)

    def set_idle_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the write bus lanes given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        for channel in [
            self._ram.write_if.b_channel,
            self._ram.read_if.r_channel,
        ]:
            channel.set_pause_generator(generator)

    def set_backpressure_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the read bus lanes given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        for channel in [
            self._ram.write_if.aw_channel,
            self._ram.write_if.w_channel,
            self._ram.read_if.ar_channel,
        ]:
            channel.set_pause_generator(generator)

    def disable(self) -> None:
        """Disable the AXI-Lite RAM."""
        self.set_idle_generator(cycle([1]))
        self.set_backpressure_generator(cycle([1]))

    def enable(self) -> None:
        """Enable the AXI-Lite RAM."""
        self.set_idle_generator(cycle([0]))
        self.set_backpressure_generator(cycle([0]))


class RandomAxiLitePayloadGenerator:
    """A generator class that gives back a random payload.

    Todo:
        Add a usage example.
    """

    def __init__(self, data_width_bits: int):
        """Initialize an instance.

        Args:
            data_width_bits: The width of each value in bits
        """
        self._data_width_bits = data_width_bits

    def get_payload(self) -> bytes:
        """Get a random payload.

        Returns:
            The random payload
        """
        return getrandbits(self._data_width_bits).to_bytes(
            bits_to_bytes(self._data_width_bits), byteorder="big"
        )


class AxiStreamSource:
    """A wrapper class around `cocotbext-axi AXI-Stream source <https://github.com/alexforencich/cocotbext-axi#axi-stream>`_.

    Todo:
        Add a usage example.
    """

    def __init__(
        self,
        bus_prefix: str,
        tdata_width_bits: int,
        clk: str,
        rst: str,
        reset_active_level: int,
    ):
        """Initialize an instance.

        Args:
            bus_prefix: The prefix of signals belonging to the source bus
            tdata_width_bits: The width of `tdata` in bits
            clk: The name of the clock
            rst: The name of the reset
            reset_active_level: 1 if active high 0 if active low
        """
        self._bus_prefix = bus_prefix
        self._tdata_width_bits = tdata_width_bits
        self._clk = clk
        self._rst = rst
        self._reset_active_level = reset_active_level
        self._log = SimLog(self._bus_prefix)

    def setup(self, dut: HierarchyObject) -> None:
        """Setup the AXI-Stream source.

        Args:
            dut: The device under test

        Raises:
            AttributeError: If `dut` does not contain the handles of given
                with `clk` and `rst`.
        """
        self._bus = axi.AxiStreamSource(
            bus=axi.AxiStreamBus.from_prefix(dut, self._bus_prefix),
            clock=getattr(dut, self._clk),
            reset=getattr(dut, self._rst),
            reset_active_level=bool(self._reset_active_level),
            byte_lanes=bits_to_bytes(self._tdata_width_bits),
        )

    async def write(
        self, frame_data: bytes, event: Event | None = None
    ) -> None:
        """Write an AXI-Stream frame.

        Args:
            frame_data: The frame data
            event: An :class:`~cocotb.triggers.Event` object to await the
                completion of the frame transmission. The event gets triggered
                when the frame has been transmitted
        """
        frame = axi.AxiStreamFrame(frame_data, tx_complete=event)
        await self._bus.write(frame)

    def set_pause_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the bus given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        self._bus.set_pause_generator(generator)

    def disable(self) -> None:
        """Disable the AXI-Stream source."""
        self._bus.set_pause_generator(cycle([1]))

    def enable(self) -> None:
        """Enable the AXI-Stream source."""
        self._bus.set_pause_generator(cycle([0]))


class AxiStreamSink:
    """A Wrapper around `cocotbext-axi AXI-Stream sink <https://github.com/alexforencich/cocotbext-axi#axi-stream>`_.

    Todo:
        Add a usage example.
    """

    def __init__(
        self,
        bus_prefix: str,
        tdata_width_bits: int,
        clk: str,
        rst: str,
        reset_active_level: int,
    ):
        """Initialize an instance.

        Args:
            bus_prefix: The prefix of signals belonging to the source bus
            tdata_width_bits: The width of `tdata` in bits
            clk: The name of the clock
            rst: The name of the reset
            reset_active_level: 1 if active high 0 if active low
        """
        self._bus_prefix = bus_prefix
        self._tdata_width_bits = tdata_width_bits
        self._clk = clk
        self._rst = rst
        self._reset_active_level = bool(reset_active_level)
        self._log = SimLog(self._bus_prefix)

    def setup(self, dut: HierarchyObject) -> None:
        """Setup the AXI-Stream sink.

        Args:
            dut: The device under test

        Raises:
            AttributeError: If `dut` does not contain the handles of given
                with `clk` and `rst`.
        """
        self._bus = axi.AxiStreamSink(
            bus=axi.AxiStreamBus.from_prefix(dut, self._bus_prefix),
            clock=getattr(dut, self._clk),
            reset=getattr(dut, self._rst),
            reset_active_level=self._reset_active_level,
            byte_lanes=bits_to_bytes(self._tdata_width_bits),
        )

    async def read(self) -> bytes:
        """Read an AXI-Stream frame.

        Returns:
            The frame data
        """
        frame = await self._bus.recv()
        return frame.tdata  # type: ignore[no-any-return]

    def set_pause_generator(self, generator: Iterator[int]) -> None:
        """Toggle pauses on the bus given a generator function.

        Args:
            generator: A signal generator for the tready flag. The tready signal
                will be low if the Iterator yields a ``'1'``
        """
        self._bus.set_pause_generator(generator)

    def disable(self) -> None:
        """Disable the AXI-Stream sink."""
        self.set_pause_generator(cycle([1]))

    def enable(self) -> None:
        """Enable the AXI-Stream sink."""
        self.set_pause_generator(cycle([0]))


class RandomAxiStreamPayloadGenerator:
    """A generator class that gives back a random payload.

    Todo:
        Add a usage example.
    """

    def __init__(self, frame_length: int, data_width_bits: int):
        """Initialize an instance.

        Args:
            frame_length: The length of the frame
            data_width_bits: The width of each value in bits
        """
        self._frame_length = frame_length
        self._data_width_bits = data_width_bits

    def get_payload(self) -> bytes:
        """Get a random payload.

        Returns:
            The random payload
        """
        return b"".join(
            [
                getrandbits(self._data_width_bits).to_bytes(
                    bits_to_bytes(self._data_width_bits), byteorder="big"
                )
                for _ in range(self._frame_length)
            ]
        )
