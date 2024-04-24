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
        os.path.join(vhdl_source_root, f"shared/edge_detector.vhd"),
        os.path.join(vhdl_source_root, f"shared/moving_average.vhd"),
        os.path.join(vhdl_source_root, f"core_zsync_prbs.vhd"),
        os.path.join(vhdl_source_root, f"data_clk_recovery.vhd"),
        os.path.join(vhdl_source_root, f"prbs_check.vhd"),
        os.path.join(vhdl_source_root, f"prbs_test.vhd"),
        os.path.join(vhdl_source_root, f"{local_dir.name}.vhd"),

    ]}


@pytest.mark.parametrize("testcase", conftest.get_test_case_names(test_bench))
def test(module_run_args, testcase):
    run(**module_run_args, testcase=testcase, parameters={
        "G_DATA_WIDTH":1,
        "G_ACTIVATION_EDGE_COUNT=":0,
        "G_BER_AVG_CYCLE_DURATION_LOG":6,
        "G_BER_AVG_WINDOW_SIZE_LOG":2,
        "G_POLY_LENGTH":7,
        "G_POLY_TAP":6,
        "G_SAMPLE_DATA_CLK_RATIO":8,
        "G_MAX_CORRECTION_CYCLE_COUNT":1,
        "G_VALUE_MIN_SAMPLE_COUNT":5,
        "G_LOOK_AHEAD_SIZE":4,
        })
