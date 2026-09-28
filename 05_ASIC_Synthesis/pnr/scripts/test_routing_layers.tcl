# Test script to verify set_routing_layers syntax and effect
read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__nom.tlef"
read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd.lef"
read_liberty "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib"
read_verilog "05_ASIC_Synthesis/results/baseline_synth_netlist.v"
link_design "tt_um_dusterthefirst_project"
read_def -floorplan_initialize "05_ASIC_Synthesis/pdk/tt_block_1x1_pg.def"

puts "Testing set_routing_layers:"
catch {set_routing_layers -signal met1-met4 -clock met1-met4} res1
puts "Result 1: $res1"

catch {set_routing_layers -signal "met1-met4" -clock "met1-met4"} res2
puts "Result 2: $res2"

catch {set_routing_layers -signal {met1 met4} -clock {met1 met4}} res3
puts "Result 3: $res3"

puts "Testing global routing commands:"
puts [info commands *route*]
exit 0
