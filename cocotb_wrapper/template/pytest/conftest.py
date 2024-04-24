import os
import pytest
import logging
import re
import cocotb.decorators


def pytest_addoption(parser):
    parser.addoption("--kw", action="store", default=None)
    parser.addoption("--gui", action="store_true", default=False)
    parser.addoption("--tb-log-level", action="store", default="WARNING")
    parser.addoption("--force-compile", action="store_true", default=False)
    parser.addoption("--ignore-skip", action="store_true", default=False)


def pytest_collection_modifyitems(session, config, items):
    selected = []
    deselected = []
    if session.config.getoption("--kw"):
        for item in items:
            if len(selected) == 0 and re.search(f"\\W{session.config.getoption('--kw')}\\W", item.name):
                selected.append(item)
            else:
                deselected.append(item)
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


def pytest_collection_finish(session):
    if session.config.getoption("--gui") and len(session.items) > 1:
        for item in session.items:
            logging.warning(item.name)
        pytest.exit(f"GUI can only be used if no more than 1 test are collected (collected_test_count: {len(session.items)}). Reduce number of collected tests using the option -k <test_name> for substring search, or --kw <test_name> for whole word  match.")


@pytest.fixture(scope="session")
def simulator():
    return "questa"


@pytest.fixture(scope="session")
def toplevel_lang():
    return "vhdl"


@pytest.fixture(scope="session")
def seed():
    return 123456789


@pytest.fixture(scope="session")
def vhdl_compile_args():
    return ["-2008", "+acc"]


@pytest.fixture(scope="session")
def sim_args():
    return ["-t", "1ps", "-64"]


@pytest.fixture(scope="session")
def force_compile(request):
    return request.config.getoption("--force-compile")


@pytest.fixture(scope="session")
def vhdl_source_root():
    if os.environ.get("SOURCE_DIR") == None:
        pytest.exit("Environment variable SOURCE_DIR not set. Please set SOURCE_DIR to the root directory of the vhdl source code.")
    return os.environ.get("SOURCE_DIR")


@pytest.fixture(scope="session")
def sim_lib_root():
    sim_lib_paths = ["/opt/altera/20.1/quartus/eda/sim_lib", "/mnt/d/altera/quartus/20.1/quartus/eda/sim_lib"]
    for sim_lib_path in sim_lib_paths:
        if os.path.exists(sim_lib_path):
            return sim_lib_path
    pytest.exit(f"Non of the configured sim_lib_path options exist on your system. Find your .../quartus/eda/sim_lib absolute path and add it to the sim_lib_paths list in conftest.py:sim_lib_root(). The following sim_lib_paths have been checked: {sim_lib_paths}")


@pytest.fixture(scope="session")
def session_run_args(request, simulator, toplevel_lang, seed, vhdl_compile_args, sim_args, force_compile):
    if request.session.config.getoption("--log-cli-level") != None:
        loglevel = request.session.config.getoption("--log-cli-level")
    else:
        loglevel = "WARNING"

    gui = request.session.config.getoption("--gui")

    return {
        "simulator": simulator,
        "toplevel_lang": toplevel_lang,
        "seed": seed,
        "vhdl_compile_args": vhdl_compile_args,
        "sim_args": sim_args,
        "force_compile": force_compile,
        "gui": gui,
        "sim_script": "setupgui.do" if gui else None,
        "extra_env": {"TB_LOG_LEVEL": loglevel},
    }


@pytest.fixture(scope="module")
def verilog_sources(vhdl_source_root):
    return []


@pytest.fixture(scope="module")
def module_run_args(session_run_args, vhdl_sources, verilog_sources, toplevel, cocotb_module, test_bench_dir):
    if isinstance(vhdl_sources, dict):
        for key, source_list in vhdl_sources.items():
            session_run_args["extra_env"][f"VHDL_SOURCES_{key}"] = " ".join(source_list)  #
    else:
        session_run_args["extra_env"][f"VHDL_SOURCES"] = " ".join(vhdl_sources)  #
    session_run_args["vhdl_sources"] = vhdl_sources
    session_run_args["verilog_sources"] = verilog_sources
    session_run_args["toplevel"] = toplevel  # vhdl top level entity
    session_run_args["module"] = cocotb_module  # python cocotb test bench module
    session_run_args["sim_build"] = os.path.join(test_bench_dir, "sim_build")

    if session_run_args["gui"]:
        sim_build_dir = os.path.join(test_bench_dir, "sim_build")
        do_script_dir = os.path.join(test_bench_dir, "do")
        wave = os.path.join(do_script_dir, "wave.do")
        run = os.path.join(do_script_dir, "setupgui.do")
        wave_link = os.path.join(sim_build_dir, "wave.do")
        run_link = os.path.join(sim_build_dir, "setupgui.do")

        if not os.path.exists(sim_build_dir):
            os.mkdir(sim_build_dir)
        if not os.path.exists(wave_link):
            os.symlink(wave, wave_link)
        if not os.path.exists(run_link):
            os.symlink(run, run_link)

    return session_run_args


def get_test_case_names(test_bench):
    test_cases = []
    for name in dir(test_bench):
        test_case = getattr(test_bench, name)
        if isinstance(test_case, cocotb.decorators.test):
            marks = []
            if test_case.skip:
                marks.append(pytest.mark.skipif(condition="not config.getoption('--ignore-skip')", reason="Marked as skipped in test bench"))
            test_cases.append(pytest.param(name, marks=marks, id=".".join(test_bench.__name__.split(".")[:-1]) + "." + name))
    return test_cases
