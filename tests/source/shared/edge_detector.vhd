-- ------------------------------------------------------------------
-- --  _____       ______  _____                                   --
-- -- |_   _|     |  ____|/ ____|                                  --
-- --   | |  _ __ | |__  | (___    Institute of Embedded Systems   --
-- --   | | | '_ \|  __|  \___ \   Zurich University of            --
-- --  _| |_| | | | |____ ____) |  Applied Sciences                --
-- -- |_____|_| |_|______|_____/   8401 Winterthur, Switzerland    --
-- ------------------------------------------------------------------
--! @file edge_detector.vhd
--! @author scso <scso@zhaw.ch>
--! @copyright 2022 ZHAW Institute of Embedded Systems
--! @date 2022-03-30
--! @brief variable bit length edge detector
--!
--! 
---------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
-------------------------------------------------------------------------------

entity edge_detector is
    generic (
        G_WIDTH : positive := 1;
        G_DELAY : positive := 1
    );
    port (
        clk            : in std_logic;
        rst_n          : in std_logic;
        data_i         : in std_logic_vector(G_WIDTH - 1 downto 0);
        data_synced_o  : out std_logic_vector(G_WIDTH - 1 downto 0);
        data_delayed_o : out std_logic_vector(G_WIDTH - 1 downto 0);
        rise_o         : out std_logic_vector(G_WIDTH - 1 downto 0);
        fall_o         : out std_logic_vector(G_WIDTH - 1 downto 0);
        edge_o         : out std_logic_vector(G_WIDTH - 1 downto 0)
    );

end entity edge_detector;

-------------------------------------------------------------------------------

architecture rtl of edge_detector is

    -----------------------------------------------------------------------------
    -- Internal signal declarations
    -----------------------------------------------------------------------------
    type delay_queue_t is array(G_DELAY downto 0) of std_logic_vector(G_WIDTH - 1 downto 0);
    signal delay_queue : delay_queue_t                          := (others => (others => '0'));
    signal rise        : std_logic_vector(G_WIDTH - 1 downto 0) := (others => '0');
    signal fall        : std_logic_vector(G_WIDTH - 1 downto 0) := (others => '0');

begin -- architecture str

    proc : process (clk, rst_n) is
    begin 
        if rst_n = '0' then -- asynchronous reset (active low)
            delay_queue <= (others => (others => '0'));
        elsif rising_edge(clk) then -- rising clock edge
            delay_queue(0)                <= data_i;
            delay_queue(G_DELAY downto 1) <= delay_queue(G_DELAY - 1 downto 0);
        end if;
    end process proc;

    rise           <= not delay_queue(G_DELAY) and delay_queue(G_DELAY - 1);
    fall           <= delay_queue(G_DELAY) and not delay_queue(G_DELAY - 1);
    data_synced_o  <= delay_queue(0);
    data_delayed_o <= delay_queue(G_DELAY);
    rise_o         <= rise;
    fall_o         <= fall;
    edge_o         <= rise or fall;

end architecture rtl;