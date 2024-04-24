import os
import pathlib
import shutil
import site
import sys


def generate_test_bench(target_dir: str, entity_name: str):
    template_dir = os.path.join(sys.modules["cocotb_wrapper"].__path__[0], "template", "test_bench")
    test_bench_dir = pathlib.Path(os.path.join(target_dir, entity_name))
    test_bench_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_dir, test_bench_dir, dirs_exist_ok=True)
    open(os.path.join(test_bench_dir, "__init__.py"), "w")


def generate_pytest_config(target_dir: str):
    template_dir = os.path.join(sys.modules["cocotb_wrapper"].__path__[0], "template", "pytest")
    shutil.copytree(template_dir, target_dir, dirs_exist_ok=True)
