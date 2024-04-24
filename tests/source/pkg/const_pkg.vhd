-- ------------------------------------------------------------------
-- --  _____       ______  _____                                   --
-- -- |_   _|     |  ____|/ ____|                                  --
-- --   | |  _ __ | |__  | (___    Institute of Embedded Systems   --
-- --   | | | '_ \|  __|  \___ \   Zurich University of            --
-- --  _| |_| | | | |____ ____) |  Applied Sciences                --
-- -- |_____|_| |_|______|_____/   8401 Winterthur, Switzerland    --
-- ------------------------------------------------------------------
--! @file shared_pkg.vhd
--! @author scso <scso@zhaw.ch>
--! @copyright 2022 ZHAW Institute of Embedded Systems
--! @date 2022-03-30
--! @brief holds general config constants and shared types for the ccu_prototype project
--!
--! 
---------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


package const_pkg is

    constant C_PKG_TERMINATOR : std_logic_vector(7 downto 0) := x"9c";
    constant C_PKG_WIDTH_RAM_DATA : positive := 16;
    constant C_PKG_MAX_COUNT : integer := 100;
end package;
