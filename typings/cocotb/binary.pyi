"""This type stub file was generated by pyright."""

from enum import Enum

from cocotb._deprecation import deprecated

_RESOLVE_TO_0 = ...
_RESOLVE_TO_1 = ...
_RESOLVE_TO_CHOICE = ...

class _ResolveXToValue(Enum):
    VALUE_ERROR = ...
    ZEROS = ...
    ONES = ...
    RANDOM = ...

resolve_x_to = ...

class _ResolveTable(dict):
    """Translation table class for resolving binary strings.

    For use with :func:`str.translate()`, which indexes into table with Unicode ordinals.
    """
    def __init__(self) -> None: ...
    def __missing__(self, key):  # -> int:
        ...

_resolve_table = ...

def resolve(string): ...

class BinaryRepresentation:
    UNSIGNED = ...
    SIGNED_MAGNITUDE = ...
    TWOS_COMPLEMENT = ...

class BinaryValue:
    """Representation of values in binary format.

    The underlying value can be set or accessed using these aliasing attributes:

        - :attr:`BinaryValue.integer` is an integer
        - :attr:`BinaryValue.signed_integer` is a signed integer
        - :attr:`BinaryValue.binstr` is a string of ``01xXzZ``
        - :attr:`BinaryValue.buff` is a binary buffer of bytes
        - :attr:`BinaryValue.value` is an integer **deprecated**

    For example:

    >>> vec = BinaryValue()
    >>> vec.integer = 42
    >>> print(vec.binstr)
    101010
    >>> print(vec.buff)
    b'*'

    """

    _permitted_chars = ...
    def __init__(
        self,
        value=...,
        n_bits=...,
        bigEndian=...,
        binaryRepresentation=...,
        bits=...,
    ) -> None:
        """Args:
        value (str or int or long, optional): Value to assign to the bus.
        n_bits (int, optional): Number of bits to use for the underlying
            binary representation.
        bigEndian (bool, optional): Interpret the binary as big-endian
            when converting to/from a string buffer.
        binaryRepresentation (BinaryRepresentation): The representation
            of the binary value
            (one of :any:`UNSIGNED`, :any:`SIGNED_MAGNITUDE`, :any:`TWOS_COMPLEMENT`).
            Defaults to unsigned representation.
        bits (int, optional): Deprecated: Compatibility wrapper for :attr:`n_bits`.
        """
        ...

    def assign(self, value):  # -> None:
        """Decides how best to assign the value to the vector.

        Picks from the type of its argument whether to set :attr:`integer`,
        :attr:`binstr`, or :attr:`buff`.

        Args:
            value (str or int or bytes): The value to assign.

        .. versionchanged:: 1.4

            This no longer falls back to setting :attr:`buff` if a :class:`str`
            containing any characters that aren't ``0``, ``1``, ``X`` or ``Z``
            is used, since :attr:`buff` now accepts only :class:`bytes`. Instead,
            an error is raised.
        """
        ...

    _convert_to_map = ...
    _convert_from_map = ...
    _invert_table = ...
    @property
    def integer(self):  # -> Any:
        """The integer representation of the underlying vector."""
        ...

    @integer.setter
    def integer(self, val):  # -> None:
        ...
    @property
    @deprecated("Use `bv.integer` instead.")
    def value(self):  # -> Any:
        """Integer access to the value. **deprecated**"""
        ...

    @value.setter
    @deprecated("Use `bv.integer` instead.")
    def value(self, val):  # -> None:
        ...

    get_value = ...
    set_value = ...
    @property
    def signed_integer(self):  # -> int:
        """The signed integer representation of the underlying vector."""
        ...

    @signed_integer.setter
    def signed_integer(self, val):  # -> None:
        ...

    get_value_signed = ...
    @property
    def is_resolvable(self) -> bool:
        """Return whether the value contains only resolvable (i.e. no "unknown") bits.

        By default the values ``X``, ``Z``, ``U`` and ``W`` are considered unresolvable.
        This can be configured with :envvar:`COCOTB_RESOLVE_X`.

        This is similar to the SystemVerilog Assertion ``$isunknown`` system function
        or the VHDL function ``is_x`` (with an inverted meaning).
        """
        ...

    @property
    def buff(self) -> bytes:
        r"""The value as a binary string buffer.

        >>> BinaryValue("01000001" + "00101111").buff == b"\x41\x2f"
        True

        .. versionchanged:: 1.4
            This changed from :class:`str` to :class:`bytes`.
            Note that for older versions used with Python 2 these types were
            indistinguishable.
        """
        ...

    @buff.setter
    def buff(self, val: bytes):  # -> None:
        ...

    get_buff = ...
    set_buff = ...
    @property
    def binstr(self):  # -> str | Any:
        """The binary representation stored as a string of ``0``, ``1``, and possibly ``x``, ``z``, and other states."""
        ...

    _non_permitted_regex = ...
    @binstr.setter
    def binstr(self, string):  # -> None:
        ...

    get_binstr = ...
    set_binstr = ...
    @property
    def n_bits(self):  # -> None:
        """The number of bits of the binary value."""
        ...

    def hex(self):  # -> str:
        ...
    def __le__(self, other) -> bool: ...
    def __str__(self) -> str: ...
    def __repr__(self):  # -> str | Any:
        ...
    def __bool__(self):  # -> bool:
        """Provide boolean testing of a :attr:`binstr`.

        >>> val = BinaryValue("0000")
        >>> if val:
        ...     print("True")
        ... else:
        ...     print("False")
        False
        >>> val.integer = 42
        >>> if val:
        ...     print("True")
        ... else:
        ...     print("False")
        True

        """
        ...

    def __eq__(self, other) -> bool: ...
    def __int__(self) -> int: ...
    def __long__(self):  # -> Any:
        ...
    def __add__(self, other):  # -> Any:
        ...
    def __iadd__(self, other):  # -> Self:
        ...
    def __radd__(self, other): ...
    def __sub__(self, other):  # -> Any:
        ...
    def __isub__(self, other):  # -> Self:
        ...
    def __rsub__(self, other): ...
    def __mul__(self, other):  # -> Any:
        ...
    def __imul__(self, other):  # -> Self:
        ...
    def __rmul__(self, other): ...
    def __floordiv__(self, other):  # -> Any:
        ...
    def __ifloordiv__(self, other):  # -> Self:
        ...
    def __rfloordiv__(self, other): ...
    def __divmod__(self, other):  # -> tuple[Any, Any]:
        ...
    def __rdivmod__(self, other): ...
    def __mod__(self, other):  # -> Any:
        ...
    def __imod__(self, other):  # -> Self:
        ...
    def __rmod__(self, other): ...
    def __pow__(self, other, modulo=...): ...
    def __ipow__(self, other):  # -> Self:
        ...
    def __rpow__(self, other): ...
    def __lshift__(self, other):  # -> int:
        ...
    def __ilshift__(self, other):  # -> Self:
        """Preserves X values"""
        ...

    def __rlshift__(self, other): ...
    def __rshift__(self, other):  # -> int:
        ...
    def __irshift__(self, other):  # -> Self:
        """Preserves X values"""
        ...

    def __rrshift__(self, other): ...
    def __and__(self, other): ...
    def __iand__(self, other):  # -> Self:
        ...
    def __rand__(self, other): ...
    def __xor__(self, other): ...
    def __ixor__(self, other):  # -> Self:
        ...
    def __rxor__(self, other): ...
    def __or__(self, other): ...
    def __ior__(self, other):  # -> Self:
        ...
    def __ror__(self, other): ...
    def __div__(self, other): ...
    def __idiv__(self, other):  # -> Self:
        ...
    def __rdiv__(self, other): ...
    def __neg__(self):  # -> Any:
        ...
    def __pos__(self):  # -> Any:
        ...
    def __abs__(self):  # -> Any:
        ...
    def __invert__(self):  # -> str | Any:
        """Preserves X values"""
        ...

    def __oct__(self):  # -> str:
        ...
    def __hex__(self):  # -> str:
        ...
    def __index__(self):  # -> Any:
        ...
    def __len__(self):  # -> int:
        ...
    def __getitem__(self, key):  # -> BinaryValue:
        """BinaryValue uses Verilog/VHDL style slices as opposed to Python
        style
        """
        ...

    def __setitem__(self, key, val):  # -> None:
        """BinaryValue uses Verilog/VHDL style slices as opposed to Python style."""
        ...

if __name__ == "__main__": ...
