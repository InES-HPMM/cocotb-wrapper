onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate -divider Entity
add wave -noupdate /prbs_test/clk_sample
add wave -noupdate /prbs_test/clk_data
add wave -noupdate /prbs_test/rst_n
add wave -noupdate /prbs_test/data_i
add wave -noupdate /prbs_test/data_o
add wave -noupdate -radix unsigned -childformat {{/prbs_test/bit_error_result_o.avg -radix unsigned} {/prbs_test/bit_error_result_o.max -radix unsigned} {/prbs_test/bit_error_result_o.min -radix unsigned}} -expand -subitemconfig {/prbs_test/bit_error_result_o.avg {-radix unsigned} /prbs_test/bit_error_result_o.max {-radix unsigned} /prbs_test/bit_error_result_o.min {-radix unsigned}} /prbs_test/bit_error_result_o
add wave -noupdate -divider Internals
add wave -noupdate /prbs_test/prbs_data_out
add wave -noupdate /prbs_test/prbs_inj_error
add wave -noupdate -expand -group prbs_check /prbs_test/data_i
add wave -noupdate -expand -group prbs_check /prbs_test/clk_data_o
add wave -noupdate -expand -group prbs_check -radix unsigned /prbs_test/bit_error_result_o
add wave -noupdate -expand -group prbs_check /prbs_test/prbs_error
add wave -noupdate -expand -group prbs_check /prbs_test/prbs_check_en
add wave -noupdate -expand -group prbs_check -radix unsigned /prbs_test/flank_count
add wave -noupdate -expand -group prbs_check -radix unsigned /prbs_test/err_count
add wave -noupdate -expand -group prbs_check -radix unsigned /prbs_test/data_count
add wave -noupdate -expand -group prbs_check /prbs_test/rx_data_synced
add wave -noupdate -expand -group prbs_check /prbs_test/rx_data_edge
add wave -noupdate -expand -group prbs_check /prbs_test/rx_data_os_synced
add wave -noupdate -expand -group prbs_check /prbs_test/rx_data_os_edge
add wave -noupdate -expand -group prbs_check /prbs_test/rx_clk_corrected
add wave -noupdate -expand -group prbs_check /prbs_test/rx_clk_recovered
add wave -noupdate -expand -group prbs_check /prbs_test/rx_data_os
add wave -noupdate -expand -group prbs_check -radix unsigned -childformat {{/prbs_test/bit_error_result.avg -radix unsigned} {/prbs_test/bit_error_result.max -radix unsigned} {/prbs_test/bit_error_result.min -radix unsigned}} -expand -subitemconfig {/prbs_test/bit_error_result.avg {-height 17 -radix unsigned} /prbs_test/bit_error_result.max {-height 17 -radix unsigned} /prbs_test/bit_error_result.min {-height 17 -radix unsigned}} /prbs_test/bit_error_result
add wave -noupdate -expand -group prbs_check /prbs_test/mov_avg_input_en
add wave -noupdate -expand -group prbs_check /prbs_test/mov_avg_output_en
add wave -noupdate -expand -group prbs_check -radix unsigned /prbs_test/mov_avg_output
add wave -noupdate -expand -group prbs_check -radix unsigned /prbs_test/count
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/G_SAMPLE_DATA_CLK_RATIO
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/G_MAX_CORRECTION_CYCLE_COUNT
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/G_VALUE_MIN_SAMPLE_COUNT
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/clk
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/rst_n
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/data_i
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/data_edge_i
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/clk_o
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/clk_corrected_o
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/data_o
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/clk_corrected
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/clk_count
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/data
add wave -noupdate -group data_clk_recovery /prbs_test/rx_clk_recovery/clk_data_rec
add wave -noupdate -expand -group moving_average /prbs_test/ber_moving_average/data_en_i
add wave -noupdate -expand -group moving_average -radix unsigned /prbs_test/ber_moving_average/data_i
add wave -noupdate -expand -group moving_average /prbs_test/ber_moving_average/data_valid_o
add wave -noupdate -expand -group moving_average -radix unsigned /prbs_test/ber_moving_average/data_o
add wave -noupdate -expand -group moving_average -radix unsigned /prbs_test/ber_moving_average/p_moving_average
add wave -noupdate -expand -group moving_average -radix unsigned /prbs_test/ber_moving_average/r_acc
add wave -noupdate -expand -group moving_average /prbs_test/ber_moving_average/r_data_valid
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/RST
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/CLK
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/DATA_IN
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/EN
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/DATA_OUT
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/prbs
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/data_in_i
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/prbs_xor_a
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/prbs_xor_b
add wave -noupdate -group core_zsync_prbs /prbs_test/prbs_check_u/prbs_msb
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/RST
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/CLK
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/DATA_IN
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/EN
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/DATA_OUT
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/prbs
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/data_in_i
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/prbs_xor_a
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/prbs_xor_b
add wave -noupdate -group prbs_gen /prbs_test/prbs_gen_u/prbs_msb
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {298593000 ps} 0}
quietly wave cursor active 1
configure wave -namecolwidth 193
configure wave -valuecolwidth 84
configure wave -justifyvalue left
configure wave -signalnamewidth 1
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ns
update
WaveRestoreZoom {329601 ns} {332729 ns}
