import os
from typing import Any, Dict, List, Union
from cocotb.handle import SimHandle, SimLog
import cocotb
import re
from cocotb_wrapper.package_handle import PackageHandle


class Constants:
    _pkg: dict = {}
    _pkg_names: List[str] = []
    _dut: SimHandle = None
    _flat: bool
    _log: SimLog

    def __init__(self, dut: SimHandle, flat: bool = False, pkg_name_regex: Union[str, List[str]] = None, pkg_names: List[str] = None) -> None:
        """init constants wrapper and load packages from dut

        Args:
            dut (SimHandle): SimHandle of the device under test
            flat (bool, optional): defines wether the package members are all accessible directly on the config object or whether they are added as sub attributes of their package name. Defaults to False.
            pkg_name_regex (Union[str,List[str]], optional): regex patterns used to match package paths. Default pattern: f"^.*pkg\\/.*\\.vhd$".
            pkg_names (List[str], optional): specific packages to include. Specify only package name without path or file ext. Defaults to None.
        """
        self._log = SimLog(type(self).__name__)
        self.dut = dut
        self._flat = flat
        if pkg_name_regex == None:
            pkg_name_regex = [f"^.*pkg\\/.*\\.vhd$"]
        elif isinstance(pkg_name_regex, str):
            pkg_name_regex = [pkg_name_regex]
        if pkg_names == None:
            self._pkg_names = []
        else:
            self._pkg_names = pkg_names

        # auto load packages from the makefile vhdl_source definition by extracting <package-name> from any path that matches ".*pkg\/<package-name>.vhd"
        source_env_var_list = {key: val for key, val in os.environ.items() if "VHDL_SOURCES" in key}
        for key, val in source_env_var_list.items():
            if isinstance(val, str):
                patterns = []
                for regex in pkg_name_regex:
                    patterns.append(re.compile(regex))

                for path in val.split(" "):
                    for regex in pkg_name_regex:
                        pattern = re.compile(regex)
                        if pattern.match(path):
                            self._pkg_names.append(os.path.splitext(os.path.basename(path))[0])

                self._pkg_names = list(set(self._pkg_names))

        for name in self._pkg_names:
            try:
                if self._flat:
                    self._pkg[name] = SimHandle(cocotb.simulator.get_root_handle(name))
                else:
                    self.__setattr__(name, PackageHandle(name, SimHandle(cocotb.simulator.get_root_handle(name))))
                self._log.debug(f"Successfully loaded vhdl package {name}")
            except Exception as ex:
                self._log.warning(f"Unable to load vhdl package {name}")

    # by overwriting the __getattr__ method, any attribute gets that can't be resolved on the config object, will be searched in the loaded packages
    def __getattr__(self, __name: str) -> Any:
        # search dut sim handle for attribute (e.g. generics)
        if self.dut != None and hasattr(self.dut, __name):
            return getattr(self.dut, __name).value

        if self._flat:
            for pkg in self._pkg.values():
                if hasattr(pkg, __name):
                    return getattr(pkg, __name).value
            raise ValueError(f"Constant {__name} could not be found in dut or any of the loaded vhdl packages {list(self._pkg_names)}")
        else:
            raise ValueError(f"Constant {__name} could not be found in dut. Packages are loaded hierarchically. Please check the following attributes {list(self._pkg_names)}")
