onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate -divider Entity
add wave -noupdate /block_buffer/clk
add wave -noupdate /block_buffer/rst_n
add wave -noupdate /block_buffer/wr_en_i
add wave -noupdate /block_buffer/wr_data_i
add wave -noupdate /block_buffer/rd_data_o
add wave -noupdate /block_buffer/rd_valid_o
add wave -noupdate /block_buffer/empty_o
add wave -noupdate /block_buffer/full_o
add wave -noupdate /block_buffer/fill_count_o
add wave -noupdate -divider Internals
add wave -noupdate /block_buffer/blocks
add wave -noupdate /block_buffer/count_chamber
add wave -noupdate /block_buffer/next_count_chamber
add wave -noupdate /block_buffer/count_data
add wave -noupdate /block_buffer/next_count_data
add wave -noupdate /block_buffer/head
add wave -noupdate /block_buffer/tail
add wave -noupdate /block_buffer/fill_count
add wave -noupdate /block_buffer/BLOCK_REG_INIT
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
WaveRestoreZoom {0 ps} {493501 ps}
