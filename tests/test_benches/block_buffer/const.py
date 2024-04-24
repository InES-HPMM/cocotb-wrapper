from typing import Any, Dict, List, Union
from cocotb.handle import HierarchyObject
import cocotb_wrapper as ctw


class Constants(ctw.Constants):
    sequence_terminator: int

    def __init__(self, dut: HierarchyObject, flat: bool = False, pkg_name_regex: Union[str, List[str]] = None, pkg_names: List[str] = None):
        super().__init__(dut, flat, pkg_name_regex, pkg_names)
        self.sequence_terminator = 0x019C
