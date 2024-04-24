

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.const_pkg.all;

entity test is
    generic (
        G_DATA_WIDTH : integer := 8
    );
    port (
        clk : in std_logic;
        clk_half_speed : in std_logic;
        rst_n  : in std_logic;
        serial_i : in std_logic := '0';
        serial_o : out std_logic := '0';
        data_i : in std_logic_vector(G_DATA_WIDTH-1 downto 0) := (others => '0');
        data_o : out std_logic_vector(G_DATA_WIDTH-1 downto 0) := (others => '0');
        count_i : in integer range C_PKG_MAX_COUNT-1 downto 0 := 0;
        count_o : out integer range C_PKG_MAX_COUNT-1 downto 0 := 0
    );
end entity test;

architecture test_arch of test is
    constant C_MAX_COUNT : integer := C_PKG_MAX_COUNT;
    signal serial_r : std_logic := '0';
    signal data_r : std_logic_vector(G_DATA_WIDTH-1 downto 0) := (others => '0');
    signal count_r : integer range C_MAX_COUNT-1 downto 0 := 0;

begin
    process(clk, rst_n)
    begin
        if (rst_n = '0') then
            serial_r <= '0';
            data_r <= (others => '0');
            count_r <= 0;
        elsif (rising_edge(clk)) then
            serial_r <= serial_i;
            data_r <= data_i;
            count_r <= count_i;
        end if;
    end process;

    serial_o <= serial_r;
    data_o <= data_r;
    count_o <= count_r;

end architecture test_arch;