# Test script for OpenROAD floorplan initialization
set ::env(STRESS_50MHZ) 1

puts "=== 1/6 Reading LEF files ==="
read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__nom.tlef"
read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd.lef"

puts "=== 2/6 Reading Liberty file ==="
read_liberty "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib"

puts "=== 3/6 Reading Netlist ==="
read_verilog "05_ASIC_Synthesis/results/baseline_synth_netlist.v"

puts "=== 4/6 Linking Design ==="
link_design "tt_um_dusterthefirst_project"

puts "=== 5/6 Reading Timing Constraints ==="
read_sdc "05_ASIC_Synthesis/constraints/ares_sentinel_sky130.sdc"

puts "=== 6/6 Initializing Floorplan from Template DEF ==="
read_def -floorplan_initialize "05_ASIC_Synthesis/pdk/tt_block_1x1_pg.def"

puts "=== Floorplan Summary ==="
report_checks
puts "=== COMPLETED INITIALIZATION TEST SUCCESSFULLY ==="
exit 0
