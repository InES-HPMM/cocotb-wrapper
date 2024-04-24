from typing import List


def to_bit_array(data: int, width: int, msb_first: bool = False, repeat_count: int = 1) -> list:
    """converts an integer to a bit array

    Args:
        data (int): int value to convert
        width (int): the desired with of the bit array. if the value to convert requires a larger bit array, excess is cut off
        msb_first (bool, optional): specifies whether conversion is done LSB or MSB first. Defaults to False (LSB first).
        repeat_count (int, optional): specifies bit wise repetition count expected in the resulting list.

    Returns:
        list: list of 0 and 1 items that represent the parameter in binary base
    """
    if msb_first:
        bits = [data >> i & 1 for i in range(width - 1, -1, -1)]
    else:
        bits = [data >> i & 1 for i in range(width)]

    return [b for b in bits for i in range(repeat_count)]


def to_int(data: list, width: int = None, msb_first: bool = False) -> int:
    """converts a bit array into an integer

    Args:
        data (list): the bit array to convert
        msb_first (bool, optional): specifies whether conversion is done LSB or MSB first. Defaults to False (LSB first).

    Returns:
        int: _description_
    """
    val = 0
    if width is None:
        width = len(data)
    data_width = len(data)
    for i in range(data_width):
        val += (data[i] & 1) << (data_width - 1 - i if msb_first else i)

    if width is not None and width > data_width:
        val = val << (width - data_width)
    return val


def to_ints(data: list, chunk_size: int, msb_first: bool = False) -> List[int]:
    """converts a bit array into a list of integers

    Args:
        data (list): the bit array to convert
        chunk_size (int): the number of bits that are converted into one integer
        msb_first (bool, optional): specifies whether conversion is done LSB or MSB first. Defaults to False (LSB first).

    Returns:
        List[int]: list of integers that represent the parameter in binary base
    """
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(to_int(data[i : min(len(data), i + chunk_size)], chunk_size, msb_first))
    return chunks


def split(data: int, chunk_size: int, chunk_count: int, msb_first: bool = False) -> List[int]:
    """splits an integer into ``chunk_count`` ``chunk_size``-bit integers

    Args:
        data (int): the integer to split
        chunk_size (int): bit width of the output chunks
        chunk_count (int): the number of output chunks
        msb_first (bool, optional): specifies whether the most significant chunk is returned on index 0 or -1. Defaults to False.

    Returns:
        List[int]: containing ``chunk_count`` ``chunk_size``-bit integers
    """
    chunks = []
    for i in range(chunk_count):
        chunks.append((data >> (i * chunk_size)) & (2**chunk_size - 1))
    return chunks.reverse() if msb_first else chunks


def concat_ints(values: List[int], chunk_size:int=8, msb_first: bool = False)->int:
    """concatenate a list of integers into one integer

    Args:
        values (List[int]): the integer chunks to concatenate
        chunk_size (List[int]): the bit width of the integer chunks
        msb_first (bool, optional): specifies whether the most significant stored on index 0 or -1. Defaults to False.

    Returns:
        int: the concatenated integer
    """    
    output = 0
    if msb_first:
        values = reversed(values)
    for i in range(len(values)):
        val = values[i] & (2**chunk_size - 1)
        output += val << (i * chunk_size)

    return output
