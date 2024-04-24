
from typing import Union
from cocotb.handle import _value_limits, _Limits, ModifiableObject, ConstantObject
from cocotb.binary import BinaryValue

def _get_binary_value(vector: Union[BinaryValue, ModifiableObject, ConstantObject]) -> BinaryValue:
    if isinstance(vector, (ModifiableObject, ConstantObject)):
        return vector.value
    elif isinstance(vector, (BinaryValue)):
        return vector
    else: raise ValueError(f"vector should be of type BinaryValue, ModifiableObject, ConstantObject but is of type {type(vector)}")
     


def vmin(vector: Union[BinaryValue, ModifiableObject, ConstantObject], signed: bool = False)->int:
    """Uses cocotb functionality to determine the min integer that can be represented by the given bit vector

    Args:
        vector (Union[BinaryValue, ModifiableObject, ConstantObject]): the vector as one of the specified cocotb handles
        signed (bool, optional): Specifies whether the given bit vector is interpreted as signed (results in negative min value) or unsigned (0 or positive value) integer. Defaults to False.

    Returns:
        int: The min integer that can be represented by the given bit vector
    """
    return _value_limits(_get_binary_value(vector).n_bits, _Limits.SIGNED_NBIT if signed else _Limits.UNSIGNED_NBIT)[0]


def vmax(vector: Union[BinaryValue, ModifiableObject, ConstantObject], signed: bool = False, zero_based:bool=True):
    """Uses cocotb functionality to determine the max integer that can be represented by the given bit vector

    Args:
        vector (Union[BinaryValue, ModifiableObject, ConstantObject]): the vector as one of the specified cocotb handles
        signed (bool, optional): Specifies whether the given bit vector is interpreted as signed or unsigned integer. Defaults to False.
        zero_based (bool, optional): Returns the actual max value ((2**N)-1) for zero_based==True or the count of representable numbers (2**N) for zero_based==false. Defaults to True.

    Returns:
        int: The max integer that can be represented by the given bit vector
    """
    return _value_limits(_get_binary_value(vector).n_bits, _Limits.SIGNED_NBIT if signed else _Limits.UNSIGNED_NBIT)[1] + int(not zero_based)

def vrange(vector: Union[BinaryValue, ModifiableObject, ConstantObject], signed: bool = False):
    """Create a python range object using the min and non-zero-based max value of the given vector

    Args:
        vector (Union[BinaryValue, ModifiableObject, ConstantObject]): the vector as one of the specified cocotb handles
        signed (bool, optional): Specifies whether the given bit vector is interpreted as signed or unsigned integer. Defaults to False.

    Returns:
        int: A range object that will iterate from the vectors min to its zero-based max value
    """
    bin_val = _get_binary_value(vector)
    return range(vmin(bin_val, signed), vmax(bin_val, signed, zero_based=False))