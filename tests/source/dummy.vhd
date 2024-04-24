-- ============================================================
--   _____       ______  _____
--  |_   _|     |  ____|/ ____|
--    | |  _ __ | |__  | (___    Institute of Embedded Systems
--    | | | '_ \|  __|  \___ \   Zurich University of
--   _| |_| | | | |____ ____) |  Applied Sciences
--  |_____|_| |_|______|_____/   8401 Winterthur, Switzerland
-- ============================================================
--! @file test_bench_delay_test.vhd
--! @author scso (scso@zhaw.ch)
--! @copyright 2023 ZHAW Institute of Embedded Systems
--! @date 2023-02-16
--! @brief dummy entity used to test functionality of the custom cocotb testbench 
-- ============================================================
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
-------------------------------------------------------------------------------
entity dummy is
    port (
        clk   : in std_logic;
        rst_n : in std_logic
    );
end entity dummy;
-------------------------------------------------------------------------------
architecture rtl of dummy is
    signal any_edge_count : integer := 0;
    signal rising_edge_count : integer := 0;
    signal falling_edge_count : integer := 0;
begin

    edge_proc : process (clk, rst_n)
    begin
        if rst_n = '0' then
            any_edge_count <= 0;
            rising_edge_count <= 0;
            falling_edge_count <= 0;
        elsif rising_edge(clk) then
            any_edge_count <= any_edge_count + 1;
            rising_edge_count <= rising_edge_count + 1;
        elsif falling_edge(clk) then
            any_edge_count <= any_edge_count + 1;
            falling_edge_count <= falling_edge_count + 1;
        end if;
    end process edge_proc;
end architecture rtl;