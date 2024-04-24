import os
import pytest
import pathlib
from cocotb_test.simulator import run
import conftest
from . import test_bench

local_dir = pathlib.Path(__file__).parent.resolve()


@pytest.fixture(scope="module")
def test_bench_dir():
    return local_dir


@pytest.fixture(scope="module")
def cocotb_module():
    return test_bench.__name__


@pytest.fixture(scope="module")
def toplevel():
    return local_dir.name


@pytest.fixture(scope="module")
def vhdl_sources(vhdl_source_root):
    return {local_dir.name: [
        os.path.join(vhdl_source_root, f"pkg/const_pkg.vhd"),
        os.path.join(vhdl_source_root, f"pkg/type_pkg.vhd"),
        os.path.join(vhdl_source_root, f"shared/{local_dir.name}.vhd"),

    ]}


@pytest.mark.parametrize("testcase", conftest.get_test_case_names(test_bench))
def test(module_run_args, testcase):
    run(**module_run_args, testcase=testcase, parameters={
        "G_BLOCK_DEPTH":12,
        "G_BLOCK_WIDTH":16,
        "G_BLOCK_COUNT":5
        })
