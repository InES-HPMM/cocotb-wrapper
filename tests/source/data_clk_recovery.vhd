-- ============================================================
--   _____       ______  _____
--  |_   _|     |  ____|/ ____|
--    | |  _ __ | |__  | (___    Institute of Embedded Systems
--    | | | '_ \|  __|  \___ \   Zurich University of
--   _| |_| | | | |____ ____) |  Applied Sciences
--  |_____|_| |_|______|_____/   8401 Winterthur, Switzerland
-- ============================================================
--! @file rx_clk_recovery.vhd
--! @author scso (scso@zhaw.ch)
--! @copyright 2022 ZHAW Institute of Embedded Systems
--! @date 2022-10-14
--! @brief oversamples an input signal for data and clock recovery
--!
--! Recovers the clock from an input signal
--! Evaluates the oversampled input bits to determine most likely data bit.
--!     This causes an input delay of up to one data cycle 
--! Performs clock correction wihin a certain threshold to account for instability and clock drift
-- ============================================================
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
-------------------------------------------------------------------------------
entity data_clk_recovery is
    generic (
        G_SAMPLE_DATA_CLK_RATIO      : positive := 8; -- ratio of sample clk period to expected data clock period
        G_MAX_CORRECTION_CYCLE_COUNT : positive := 1; -- max amount of sample clk cycles that can be shaved of a data clk period in a single instance to correct for clock missmatch / drift
        G_VALUE_MIN_SAMPLE_COUNT     : positive := 5; -- the number of sampled 1s that need to be observed to output 1 for the next data clk period
        G_LOOK_AHEAD_SIZE            : positive := 4  -- the size of the lookahead buffer that is used to prevent sample bit errors from triggering a clock correction
    );
    port (
        clk         : in std_logic;
        rst_n       : in std_logic;
        data_i      : in std_logic := '0';
        data_edge_i : in std_logic := '0';
        -- data_expected_i : in std_logic  := '0';
        clk_o           : out std_logic := '0';
        clk_corrected_o : out std_logic := '0';
        data_o          : out std_logic := '0'
    );
end entity data_clk_recovery;
-------------------------------------------------------------------------------
architecture rtl of data_clk_recovery is

    -----------------------------------------------------------------------------
    -- Internal signal declarations
    -----------------------------------------------------------------------------
    signal clk_corrected          : boolean                                          := false;
    signal clk_count              : integer range 0 to 2 * G_SAMPLE_DATA_CLK_RATIO   := 0;
    signal ones                   : integer range 0 to 2 * G_SAMPLE_DATA_CLK_RATIO   := 0;
    signal zeros                  : integer range 0 to 2 * G_SAMPLE_DATA_CLK_RATIO   := 0;
    signal sample_count           : integer range 0 to 2 * G_SAMPLE_DATA_CLK_RATIO   := 0;
    signal data                   : std_logic                                        := '0';
    signal data_synced            : std_logic                                        := '0';
    signal clk_data_rec           : std_logic                                        := '0';
    signal new_bit                : boolean                                          := false;
    signal sample_shift_reg       : std_logic_vector(G_LOOK_AHEAD_SIZE - 1 downto 0) := (others => '0');
    signal sample_edge_shift_reg  : std_logic_vector(G_LOOK_AHEAD_SIZE - 1 downto 0) := (others => '0');
    signal look_ahead_delay_count : integer range 0 to G_LOOK_AHEAD_SIZE             := G_LOOK_AHEAD_SIZE;
begin -- architecture str
    clk_o           <= clk_data_rec;
    data_o          <= data_synced;
    clk_corrected_o <= '1' when clk_corrected else '0';
    clk_recover : process (all)
        variable v_reset_data_count : boolean := false;
        variable v_rising_edge      : boolean := false;
    begin
        if not rst_n then
            clk_count              <= 0;
            clk_data_rec           <= '1';
            clk_corrected          <= false;
            data                   <= '0';
            data_synced            <= '0';
            ones                   <= 0;
            zeros                  <= 0;
            new_bit                <= false;
            sample_shift_reg       <= (others => '0');
            sample_edge_shift_reg  <= (others => '0');
            look_ahead_delay_count <= G_LOOK_AHEAD_SIZE;
            elsif rising_edge(clk) then
            data                  <= data;
            new_bit               <= new_bit;
            sample_shift_reg      <= data_i & sample_shift_reg(G_LOOK_AHEAD_SIZE - 1 downto 1);
            sample_edge_shift_reg <= data_edge_i & sample_edge_shift_reg(G_LOOK_AHEAD_SIZE - 1 downto 1);
            v_reset_data_count := false;

            if look_ahead_delay_count > 0 then
                look_ahead_delay_count <= look_ahead_delay_count - 1;
                sample_count           <= 0;
                zeros                  <= 0;
                ones                   <= 0;
            else
                ones         <= ones + to_integer(unsigned'('0' & sample_shift_reg(0)));
                zeros        <= zeros + to_integer(unsigned'('0' & not sample_shift_reg(0)));
                sample_count <= sample_count + 1;
            end if;

            if sample_edge_shift_reg(0) = '1' or sample_count >= G_SAMPLE_DATA_CLK_RATIO - 1 then
                if ones >= G_VALUE_MIN_SAMPLE_COUNT and ((or sample_shift_reg = '0') or sample_count >= G_SAMPLE_DATA_CLK_RATIO - 1) then
                    data    <= '1';
                    new_bit <= true;
                    v_reset_data_count := true;
                elsif zeros >= G_VALUE_MIN_SAMPLE_COUNT and ((and sample_shift_reg = '1') or sample_count >= G_SAMPLE_DATA_CLK_RATIO - 1) then
                    data    <= '0';
                    new_bit <= true;
                    v_reset_data_count := true;
                end if;

                if v_reset_data_count then
                    sample_count <= 0;
                    -- set zeros and ones to 1 or 0 depending on whether the current sample is high
                    zeros        <= to_integer(unsigned'('0' & not sample_shift_reg(0)));
                    ones         <= to_integer(unsigned'('0' & sample_shift_reg(0)));
                    -- if sample_shift_reg(0) = '1' then
                    --     zeros <= 0;
                    --     ones  <= 1;
                    -- else
                    --     zeros <= 1;
                    --     ones  <= 0;
                    -- end if;
                end if;
            end if;

            data_synced   <= data_synced;
            clk_corrected <= false;
            clk_count     <= clk_count + 1;
            clk_data_rec  <= clk_data_rec;
            if clk_count >= G_SAMPLE_DATA_CLK_RATIO/2 - 1 then
                -- always drive clk low after 4 cycles to ensure stable half periods
                clk_data_rec <= '0';
            end if;

            v_rising_edge := false;
            v_rising_edge := v_rising_edge or (sample_count > G_SAMPLE_DATA_CLK_RATIO/2 and new_bit and clk_count >= G_SAMPLE_DATA_CLK_RATIO - 1 - G_MAX_CORRECTION_CYCLE_COUNT);
            v_rising_edge := v_rising_edge or (sample_count < G_SAMPLE_DATA_CLK_RATIO/2 and new_bit and clk_count >= G_SAMPLE_DATA_CLK_RATIO - 1 + G_MAX_CORRECTION_CYCLE_COUNT);
            v_rising_edge := v_rising_edge or (sample_count = G_SAMPLE_DATA_CLK_RATIO/2 and clk_count >= G_SAMPLE_DATA_CLK_RATIO - 1);

            if v_rising_edge then
                new_bit       <= false;
                data_synced   <= data;
                clk_count     <= 0;
                clk_data_rec  <= '1';
                clk_corrected <= clk_count /= G_SAMPLE_DATA_CLK_RATIO - 1;
            end if;
        end if;
    end process clk_recover;
end architecture rtl;