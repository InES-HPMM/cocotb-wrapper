import argparse
import os
import pathlib
import cocotb_wrapper.template


def main():
    parser = argparse.ArgumentParser(prog="cocotb_wrapper CLI", description="Offers commands to generate testbenches and other utilities for cocotb_wrapper usage")
    parser.add_argument("-g", "--gen-tb", type=str, action="store", metavar="<entity name>", help="generate a testbench for the specified entity at the currents directory")
    parser.add_argument("-i", "--init", action="store_true", help="generate pytest config files in local directory")
    args = parser.parse_args()
    if args.gen_tb:
        cocotb_wrapper.template.generate_test_bench(os.getcwd(), args.gen_tb)
    elif args.init:
        cocotb_wrapper.template.generate_pytest_config(os.getcwd())
    else:
        argparse.ArgumentParser.print_help(parser)
