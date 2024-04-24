-- ============================================================
--   _____       ______  _____
--  |_   _|     |  ____|/ ____|
--    | |  _ __ | |__  | (___    Institute of Embedded Systems
--    | | | '_ \|  __|  \___ \   Zurich University of
--   _| |_| | | | |____ ____) |  Applied Sciences
--  |_____|_| |_|______|_____/   8401 Winterthur, Switzerland
-- ============================================================
--! @file moving_average.vhd
--! @author Surf-VHDL https://surf-vhdl.com/how-to-implement-moving-average-in-vhdl/#:~:text=VHDL%20code%20for%20moving%20average&text=This%20VHDL%20implementation%20of%20moving,perform%20the%20output%20right%20shift.
--! @date 2018-10-13
--! @brief calculates a moving aberage over 2**G_AVG_LEN_LOG values
-- ============================================================

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity moving_average is
    generic (
        G_NBIT        : integer := 8;
        G_AVG_LEN_LOG : integer := 2
    );
    port (
        clk        : in std_logic :='0';
        rst_n       : in std_logic :='0';
        clear_i : in std_logic :='0';
        -- input
        data_en_i : in std_logic :='0';
        data_i     : in std_logic_vector(G_NBIT - 1 downto 0):= (others => '0');
        -- output
        data_valid_o : out std_logic :='0';
        data_o       : out std_logic_vector(G_NBIT - 1 downto 0):= (others => '0')
    );
end moving_average;

architecture rtl of moving_average is

    type t_moving_average is array (0 to 2 ** G_AVG_LEN_LOG - 1) of unsigned(G_NBIT - 1 downto 0);

    signal p_moving_average : t_moving_average := (others => (others => '0'));
    signal r_acc            : unsigned(G_NBIT + G_AVG_LEN_LOG - 1 downto 0) := (others => '0'); -- average accumulator
    signal r_data_valid     : std_logic := '0';

begin

    p_average : process (all)
    begin
        if (rst_n = '0') then
            r_acc            <= (others => '0');
            p_moving_average <= (others => (others => '0'));
            r_data_valid     <= '0';
            data_valid_o     <= '0';
            data_o           <= (others => '0');
        elsif (rising_edge(clk)) then
            r_data_valid <= data_en_i;
            data_valid_o <= r_data_valid;
            if (clear_i = '1') then
                r_acc            <= (others => '0');
                p_moving_average <= (others => (others => '0'));
            elsif (data_en_i = '1') then
                p_moving_average <= unsigned(data_i) & p_moving_average(0 to p_moving_average'length - 2);
                r_acc            <= r_acc + unsigned(data_i) - p_moving_average(p_moving_average'length - 1);
            end if;
            data_o <= std_logic_vector(r_acc(G_NBIT + G_AVG_LEN_LOG - 1 downto G_AVG_LEN_LOG)); -- divide by 2^G_AVG_LEN_LOG

        end if;
    end process p_average;

end rtl;