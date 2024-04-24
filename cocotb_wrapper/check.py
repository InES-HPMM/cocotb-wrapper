from enum import Enum
from typing import Any, Callable, Union
from cocotb_wrapper.log import logging
from cocotb.handle import SimHandleBase
from cocotb.binary import BinaryValue


def _get_val(val: any) -> any:
    """used to extract the comparable value from multiple cocotb handle types.

    Args:
        val (any): accepts any type

    Returns:
        any: returns val if no rule for val's type is implemented
    """
    out = val
    if isinstance(val, SimHandleBase):
        out = val.value

    if isinstance(out, BinaryValue):
        try:
            out = out.integer
        except Exception:
            out = str(out)
    return out


def compare_sim(actual: SimHandleBase, expected: int, format: Callable[[int], str] = str, name: str = None) -> bool:
    """compare the value of a cocotb handle with an expected value. in case of mismatch, it logs the name and values in the given format and returns false

    Args:
        actual (SimHandleBase): sim handle that holds the value to compare
        expected (int): expected value of the sim handle
        format (Callable[[int], str], optional): format of the value when logged in case of error. Defaults to str.
        name (str, optional): prefix of the error log. sim handle repr is used if unspecified.

    Returns:
        bool: True if actual and expected match
    """
    return _compare_format(repr(actual) if name == None else name, _get_val(actual), expected, format)


def compare(name: str, actual: Any, expected: int) -> bool:
    """compares two int values. in case of mismatch, it logs the name and values in int format and returns false

    Args:
        name (str): name of the value to compare
        actual (Any): value of the DUT, accepts cocotb handles (see _get_val for implemented value extractions)
        expected (int): expected value or value of the GM

    Returns:
        bool: True if actual and expected match
    """
    return _compare_format(name, _get_val(actual), expected, str)


def compare_hex(name: str, actual: Any, expected: int) -> bool:
    """compares two int values. in case of mismatch, it logs the name and values in hex format and returns false

    Args:
        name (str): name of the value to compare
        actual (Any): value of the DUT, accepts cocotb handles (see _get_val for implemented value extractions)
        expected (int): expected value or value of the GM

    Returns:
        bool: True if actual and expected match
    """
    return _compare_format(name, _get_val(actual), expected, hex)


def compare_bin(name: str, actual: Any, expected: int) -> bool:
    """compares two int values. in case of mismatch, it logs the name and values in binary format and returns false

    Args:
        name (str): name of the value to compare
        actual (Any): value of the DUT, accepts cocotb handles (see _get_val for implemented value extractions)
        expected (int): expected value or value of the GM

    Returns:
        bool: True if actual and expected match
    """
    return _compare_format(name, _get_val(actual), expected, bin)


def compare_format(name: str, actual: Any, expected: int, format: Callable[[int], str]) -> bool:
    """compares two int values. in case of mismatch, it logs the name and values in the given format and returns false

    Args:
        name (str): name of the value to compare
        actual (Any): value of the DUT, accepts cocotb handles (see _get_val for implemented value extractions)
        expected (int): expected value or value of the GM

    Returns:
        bool: True if actual and expected match
    """
    return _compare_format(name, _get_val(actual), expected, format)


def _compare_format(name: str, actual: int, expected: int, format: Callable[[int], str]) -> bool:
    """compares two int values. in case of mismatch, it logs the name and values in the given format and returns false

    Args:
        name (str): name of the value to compare
        actual (int): value of the DUT
        expected (int): expected value or value of the GM

    Returns:
        bool: True if actual and expected match
    """
    try:
        return soft_assert(name, actual == expected, format(actual), format(expected))
    except Exception:
        # for undefined signal states the cocotb handles may contain values that can not be cast to int. in such cases the dut value is printed as string
        return soft_assert(name, actual == expected, str(actual), format(expected))


def compare_str(name: str, actual: str, expected: str) -> bool:
    """compares two string values. in case of mismatch, it logs the name and values and returns false

    Args:
        name (str): name of the value to compare
        actual (str): value of the DUT
        expected (str): expected value or value of the GM

    Returns:
        bool: True if actual and expected match
    """
    return soft_assert(name, _get_val(actual) == expected, _get_val(actual), expected)


def compare_enum(enum: Enum, actual: int, expected: int) -> bool:
    """compares two int values. in case of mismatch, it logs the enum names retrieved using the int values and returns false

    Args:
        enum (Enum): the enum whose values are under consideration
        actual (int): value of the DUT
        expected (int): expected value or value of the GM

    Returns:
        bool: True if actual and expected match
    """
    return soft_assert(enum.__name__, actual == expected, enum(_get_val(actual)).name, enum(expected).name)


def soft_assert(name: str, predicate: bool, actual: str, expected: str):
    """asserts the resolved predicate in a try catch and logs the assert error if the predicate is False"""
    try:
        assert predicate, f"{name} doesn't match! DUT: {_get_val(actual)}, GM: {expected}"
        return True
    except Exception as ex:
        logging.error(ex)
        return False


def compare_bit_stream(name: str, bit_stream_act: Union[str, list], bit_stream_exp: Union[str, list], max_bit_error_count: int = 0) -> bool:
    """compares two bit streams. in case of mismatch, it logs the name and values and returns false

    Args:
        name (str): name of the bit streams to compare
        bit_stream_act (Union[str, list]): the bit stream of the DUT
        bit_stream_exp (Union[str, list]): the expected bit stream

    Returns:
        bool: true if the bit streams match
    """

    def log_mismatch(log_func: Callable[[str], None],bit_error_indexes:list, bit_stream_act: Union[str, list], bit_stream_exp: Union[str, list]):
        log_func( f"{name} bit streams don't match at indexes: {bit_error_indexes}")
        log_func(f"DUT: {bit_stream_act}, length: {len(bit_stream_act)}")
        log_func(f"GM : {bit_stream_exp}, length: {len(bit_stream_exp)}")

    valid = True
    bit_error_indexes = []
    try:
        for i in range(len(bit_stream_exp)):
            if bit_stream_act[i] != bit_stream_exp[i]:
                bit_error_indexes.append(i)
    except Exception as ex:
        logging.error(ex)
        valid = False
    
    log_func = logging.error if len(bit_error_indexes) > max_bit_error_count or not valid else logging.warning
    if not valid or len(bit_error_indexes) > 0:
        log_mismatch(log_func, bit_error_indexes, bit_stream_act, bit_stream_exp)

    return valid, len(bit_error_indexes), bit_error_indexes
