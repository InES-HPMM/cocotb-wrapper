-- ------------------------------------------------------------------
-- --  _____       ______  _____                                   --
-- -- |_   _|     |  ____|/ ____|                                  --
-- --   | |  _ __ | |__  | (___    Institute of Embedded Systems   --
-- --   | | | '_ \|  __|  \___ \   Zurich University of            --
-- --  _| |_| | | | |____ ____) |  Applied Sciences                --
-- -- |_____|_| |_|______|_____/   8401 Winterthur, Switzerland    --
-- ------------------------------------------------------------------
--! @file block_buffer.vhd
--! @author scso <scso@zhaw.ch>
--! @copyright 2022 ZHAW Institute of Embedded Systems
--! @date 2022-03-30
--! @brief block cycle buffer that stores arrays of vectors as blocks to buffer and serialize the vectors into a RAM feed
--!
--! 
---------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
library work;
use work.const_pkg.all;
use work.type_pkg.all;
entity block_buffer is
    generic (
        G_BLOCK_DEPTH : integer;
        G_BLOCK_WIDTH : integer;
        G_BLOCK_COUNT : integer
    );
    port (
        clk   : in std_logic;
        rst_n : in std_logic;

        -- Write port
        wr_en_i   : in std_logic;
        wr_data_i : in block_buff_cell_arr_t(G_BLOCK_DEPTH - 1 downto 0);

        -- Read port
        rd_data_o  : out std_logic_vector(G_BLOCK_WIDTH - 1 downto 0);
        rd_valid_o : out std_logic;

        -- Flags
        empty_o : out std_logic;
        full_o  : out std_logic;

        -- The number of elements in the FIFO
        fill_count_o : out integer range 0 to G_BLOCK_COUNT
    );
end block_buffer;

architecture rtl of block_buffer is
    type block_reg_t is record
        full : std_logic;
        data : block_buff_cell_arr_t(G_BLOCK_DEPTH - 1 downto 0);
    end record block_reg_t;

    constant BLOCK_REG_INIT : block_reg_t := (
        full => '0',
        data => (others => (others => '0'))
    );

    type block_arr_t is array (0 to G_BLOCK_COUNT - 1) of block_reg_t;
    signal blocks : block_arr_t := (others => BLOCK_REG_INIT);

    signal count_chamber, next_count_chamber : integer range 0 to 2;
    signal count_data, next_count_data       : integer range 0 to G_BLOCK_DEPTH - 1;
    signal head                              : integer range 0 to G_BLOCK_COUNT - 1;
    signal tail                              : integer range 0 to G_BLOCK_COUNT - 1;

    signal fill_count : integer range 0 to G_BLOCK_DEPTH;
    signal rd_valid   : std_logic;
begin
    empty_o      <= not blocks(tail).full;
    full_o       <= blocks(head).full;
    rd_data_o    <= blocks(tail).data(count_data);
    fill_count_o <= (G_BLOCK_COUNT - (tail - head)) when tail > head
        else head - tail when tail < head
        else G_BLOCK_COUNT when blocks(head).full
        else 0;
    rd_valid_o <= blocks(tail).full;

    -- Update the head pointer in write
    PROC_HEAD : process (all)
    begin
        if not rst_n then
            count_chamber <= 0;
            count_data    <= 0;
            head          <= 0;
            tail          <= 0;
            blocks        <= (others => BLOCK_REG_INIT);
        elsif rising_edge(clk) then

            if blocks(tail).data(count_data) = (x"01" & C_PKG_TERMINATOR) then
                blocks(tail).full <= '0';
                blocks(tail).data <= (others => (others => '0'));
                tail              <= (tail + 1) mod G_BLOCK_COUNT;
                count_data        <= 0;
            elsif blocks(tail).full then
                count_data <= count_data + 1;
            end if;

            if wr_en_i = '1' and blocks(head).full = '0' then
                blocks(head).data <= wr_data_i;
                blocks(head).full <= '1';
                head              <= (head + 1) mod G_BLOCK_COUNT;
            end if;
        end if;
    end process;

end architecture;