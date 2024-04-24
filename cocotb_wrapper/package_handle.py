

from typing import Any
from cocotb.handle import SimHandle


class PackageHandle:
    _name:str
    _sim_handle: SimHandle

    def __init__(self, name:str, sim_handle:SimHandle) -> None:
        self._name = name
        self._sim_handle = sim_handle

    def __getattr__(self, __name: str) -> Any:
        if hasattr(self._sim_handle, __name):
            return getattr(self._sim_handle, __name).value
        raise ValueError(f"constant {__name} could not be found in the loaded vhdl package {self._name}")
    
    def __hassattr__(self, __name: str) -> bool:
        return hasattr(self._sim_handle, __name)