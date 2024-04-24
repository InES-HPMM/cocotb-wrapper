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
library work;
use work.const_pkg.all;


package type_pkg is

    type block_buff_cell_arr_t is array (natural range <>) of std_logic_vector(C_PKG_WIDTH_RAM_DATA-1 downto 0);

    
    type bit_error_result_t is record
        avg  : integer range 0 to 2**20;
        max : integer range 0 to 2**20;
        min : integer range 0 to 2**20;
    end record bit_error_result_t;
    
    constant C_PKG_BIT_ERROR_RESULT_INIT : bit_error_result_t := (
        avg  => 0,
        max  => 0,
        min => 2**20
    );

    type bit_error_results_t is array (integer range <>) of bit_error_result_t;
end package;
