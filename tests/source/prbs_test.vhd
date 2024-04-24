-- ============================================================
--   _____       ______  _____
--  |_   _|     |  ____|/ ____|
--    | |  _ __ | |__  | (___    Institute of Embedded Systems
--    | | | '_ \|  __|  \___ \   Zurich University of
--   _| |_| | | | |____ ____) |  Applied Sciences
--  |_____|_| |_|______|_____/   8401 Winterthur, Switzerland
-- ============================================================
--! @file prbs_test.vhd
--! @author scso (scso@zhaw.ch)
--! @copyright 2022 ZHAW Institute of Embedded Systems
--! @date 2022-10-14
--! @brief generates outgoing prbs and validates incomming prbs
--!
--! Generates a pseudo random bit sequence to send to another device or to loop back for single device testing
--! The incoming / returning prbs is oversampled for data clock recovery and rx signal debouncing
--! All tx signals are driven using the same prbs, but each rx signal is validated individually
--! Input validation in each signal is deactivated until G_ACTIVATION_EDGE_COUNT edges were observed on the input signal to remove initial sync problems from the 
--! 
--! 
--! 
-- ============================================================

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library work;
use work.type_pkg.all;
-------------------------------------------------------------------------------

entity prbs_test is
    generic (
        G_DATA_WIDTH                 : positive := 8;
        G_ACTIVATION_EDGE_COUNT      : positive := 10;
        G_BER_AVG_CYCLE_DURATION_LOG : positive := 20;
        G_BER_AVG_WINDOW_SIZE_LOG    : positive := 4;
        -- prbs gen / check
        G_POLY_LENGTH : positive := 7;
        G_POLY_TAP    : positive := 6;
        -- input oversampling / clk recovery
        G_SAMPLE_DATA_CLK_RATIO      : positive := 8;
        G_MAX_CORRECTION_CYCLE_COUNT : positive := 1;
        G_VALUE_MIN_SAMPLE_COUNT     : positive := 5;
        G_LOOK_AHEAD_SIZE            : positive := 4
    );
    port (
        clk_sample         : in std_logic           := '0';
        clk_data           : in std_logic           := '0';
        rst_n              : in std_logic           := '0';
        data_i             : in std_logic           := '0';
        data_o             : out std_logic          := '0';
        clk_data_o         : out std_logic          := '0';
        bit_error_result_o : out bit_error_result_t := C_PKG_BIT_ERROR_RESULT_INIT
    );

end entity prbs_test;

-------------------------------------------------------------------------------

architecture rtl of prbs_test is

    constant C_BER_AVG_CYCLE_DURATION : positive := 2 ** G_BER_AVG_CYCLE_DURATION_LOG - 1;
    -----------------------------------------------------------------------------
    -- Internal signal declarations
    -----------------------------------------------------------------------------
    signal prbs_data_out  : std_logic_vector(0 downto 0) := (others => '0');
    signal prbs_inj_error : std_logic_vector(0 downto 0) := (others => '0');
    signal prbs_error     : std_logic                    := '0';
    signal prbs_check_en  : std_logic                    := '0';
    signal flank_count    : integer                      := 0;
    signal err_count      : natural                      := 0;
    signal data_count     : natural                      := 0;

    signal rx_data_synced    : std_logic := '0';
    signal rx_data_edge      : std_logic := '0';
    signal rx_data_os_synced : std_logic := '0';
    signal rx_data_os_edge   : std_logic := '0';

    signal rx_clk_corrected : std_logic := '0';
    signal rx_clk_recovered : std_logic := '0';
    signal rx_data_os       : std_logic := '0';

    signal mov_avg_input_en  : std_logic := '0';
    signal mov_avg_output_en : std_logic := '0';
    signal mov_avg_output    : std_logic_vector(G_BER_AVG_CYCLE_DURATION_LOG - 1 downto 0);
    signal mov_avg_clear     : std_logic := '0';

    signal bit_error_result : bit_error_result_t := C_PKG_BIT_ERROR_RESULT_INIT;

    signal count : integer := 0;

begin -- architecture str

    clk_data_o         <= rx_clk_recovered;
    bit_error_result_o <= bit_error_result;

    prbs_gen_u : entity work.core_zsync_prbs
        generic map(
            CHK_MODE    => false,
            INV_PATTERN => false,
            POLY_LENGTH => G_POLY_LENGTH,
            POLY_TAP    => G_POLY_TAP,
            NBITS       => G_DATA_WIDTH
        )
        port map(
            RST         => not rst_n,
            CLK         => clk_data,
            DATA_IN     => prbs_inj_error,
            EN          => '1',
            DATA_OUT(0) => data_o
        );

    -- -------------------------------------------------------------------------------------
    -- Oversample
    -- -------------------------------------------------------------------------------------
    input_edge_detector : entity work.edge_detector
        generic map(
            G_WIDTH => 1,
            G_DELAY => 1
        )
        port map(
            clk              => clk_sample,
            rst_n            => rst_n,
            data_i(0)        => data_i,
            data_synced_o(0) => rx_data_synced,
            data_delayed_o   => open,
            rise_o           => open,
            fall_o           => open,
            edge_o(0)        => rx_data_edge
        );

    os_input_edge_detector : entity work.edge_detector
        generic map(
            G_WIDTH => 1,
            G_DELAY => 1
        )
        port map(
            clk              => rx_clk_recovered,
            rst_n            => rst_n,
            data_i(0)        => rx_data_os,
            data_synced_o(0) => rx_data_os_synced,
            data_delayed_o   => open,
            rise_o           => open,
            fall_o           => open,
            edge_o(0)        => rx_data_os_edge
        );

    rx_clk_recovery : entity work.data_clk_recovery
        generic map(
            G_SAMPLE_DATA_CLK_RATIO      => G_SAMPLE_DATA_CLK_RATIO,
            G_MAX_CORRECTION_CYCLE_COUNT => G_MAX_CORRECTION_CYCLE_COUNT,
            G_VALUE_MIN_SAMPLE_COUNT     => G_VALUE_MIN_SAMPLE_COUNT
        )
        port map(
            clk             => clk_sample,
            rst_n           => rst_n,
            data_i          => rx_data_synced,
            data_edge_i     => rx_data_edge,
            clk_o           => rx_clk_recovered,
            clk_corrected_o => rx_clk_corrected,
            data_o          => rx_data_os
        );
    -- -------------------------------------------------------------------------------------
    -- PRBS
    -- -------------------------------------------------------------------------------------
    prbs_check_u : entity work.core_zsync_prbs
        generic map(
            CHK_MODE    => true,
            INV_PATTERN => false,
            POLY_LENGTH => G_POLY_LENGTH,
            POLY_TAP    => G_POLY_TAP,
            NBITS       => 1
        )
        port map(
            RST         => not rst_n,
            CLK         => rx_clk_recovered,
            DATA_IN(0)  => rx_data_os,
            EN          => '1',
            DATA_OUT(0) => prbs_error
        );

    ber_moving_average : entity work.moving_average
        generic map(
            G_NBIT        => G_BER_AVG_CYCLE_DURATION_LOG,
            G_AVG_LEN_LOG => G_BER_AVG_WINDOW_SIZE_LOG
        )
        port map(
            clk          => rx_clk_recovered,
            rst_n        => rst_n,
            clear_i      => mov_avg_clear,
            data_en_i    => mov_avg_input_en,
            data_i       => std_logic_vector(to_unsigned(err_count, mov_avg_output'length)),
            data_valid_o => mov_avg_output_en,
            data_o       => mov_avg_output
        );

    prbs_check_prc : process (all)
    begin
        if not rst_n then
            flank_count      <= 0;
            prbs_check_en    <= '0';
            err_count        <= 0;
            count            <= 0;
            mov_avg_input_en <= '0';
            mov_avg_clear    <= '1';
            bit_error_result <= C_PKG_BIT_ERROR_RESULT_INIT;

        elsif rising_edge(rx_clk_recovered) then
            count            <= count;
            mov_avg_input_en <= '0';
            mov_avg_clear    <= '0';
            bit_error_result <= bit_error_result;

            prbs_check_en <= prbs_check_en;
            -- enable after first data has arrived
            if rx_data_os_edge = '1' and flank_count = G_ACTIVATION_EDGE_COUNT then
                prbs_check_en <= '1';
            elsif rx_data_os_edge = '1' and prbs_check_en = '0' then
                flank_count <= flank_count + 1;
            else
                flank_count <= flank_count;
            end if;

            if prbs_check_en = '1' then

                -- count errors
                if err_count < C_BER_AVG_CYCLE_DURATION and prbs_error = '1' then
                    err_count <= err_count + 1;
                end if;

                if count < C_BER_AVG_CYCLE_DURATION then
                    count <= count + 1;
                    if count >= C_BER_AVG_CYCLE_DURATION - 1 then
                        mov_avg_input_en <= '1';
                    end if;
                else
                    if err_count < bit_error_result.min then
                        bit_error_result.min <= err_count;
                    end if;
                    if err_count > bit_error_result.max then
                        bit_error_result.max <= err_count;
                    end if;

                    err_count <= 0;
                    count     <= 0;
                end if;
            end if;

            if mov_avg_output_en then
                bit_error_result.avg <= to_integer(unsigned(mov_avg_output));
            end if;

        end if;
    end process prbs_check_prc;

end architecture rtl;