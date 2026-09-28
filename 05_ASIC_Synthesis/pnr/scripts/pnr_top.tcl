# ==============================================================================
# OpenROAD Place & Route Flow — Integrated Top (tt_um_ares_sentinel_project)
# Standard: Tiny Tapeout TT08 (SkyWater 130nm — sky130_fd_sc_hd)
# Tile Size: 1x1 (161.00 um x 111.52 um)
# Authority: Technical Architect / Research Direction (WO-2026-M5-F-001)
# ==============================================================================

set ::env(STRESS_50MHZ) 1

puts "=== Step 1/10: Reading PDK LEF Files ==="
read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__nom.tlef"
read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd.lef"

puts "=== Step 2/10: Reading Liberty Timing Library ==="
read_liberty "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib"

puts "=== Step 3/10: Reading Synthesized Gate-Level Netlist ==="
read_verilog "05_ASIC_Synthesis/results/top_synth_netlist.v"

puts "=== Step 4/10: Linking Design & Loading SDC Constraints ==="
link_design "tt_um_ares_sentinel_project"
read_sdc "05_ASIC_Synthesis/constraints/ares_sentinel_sky130.sdc"

puts "=== Step 5/10: Floorplan & Pin Initialization from TT08 Template ==="
read_def -floorplan_initialize "05_ASIC_Synthesis/pdk/tt_block_1x1_pg.def"

puts "=== Step 6/10: Power Distribution Network (PDN) Synthesis ==="
add_global_connection -net {VPWR} -inst_pattern {.*} -pin_pattern {^VPWR$} -power
add_global_connection -net {VGND} -inst_pattern {.*} -pin_pattern {^VGND$} -ground
add_global_connection -net {VPWR} -inst_pattern {.*} -pin_pattern {^VPB$}
add_global_connection -net {VGND} -inst_pattern {.*} -pin_pattern {^VNB$}

set_voltage_domain -name CORE -power VPWR -ground VGND

define_pdn_grid \
    -name stdcell_grid \
    -starts_with POWER \
    -voltage_domain CORE \
    -pins met4

add_pdn_stripe \
    -grid stdcell_grid \
    -layer met4 \
    -width 1.6 \
    -pitch 38.87 \
    -offset 16.32 \
    -starts_with POWER

add_pdn_stripe \
    -grid stdcell_grid \
    -layer met1 \
    -width 0.48 \
    -followpins \
    -starts_with POWER

add_pdn_connect \
    -grid stdcell_grid \
    -layers "met1 met4"

pdngen

puts "=== Step 7/10: Tapcell Insertion & Placement ==="
tapcell -tapcell_master sky130_fd_sc_hd__tapvpwrvgnd_1 -endcap_master sky130_fd_sc_hd__decap_3 -distance 14

global_placement -timing_driven -density 0.68 -pad_left 2 -pad_right 2
detailed_placement
check_placement -verbose

puts "=== Step 8/10: Clock Tree Synthesis (CTS) ==="
clock_tree_synthesis \
    -root_buf sky130_fd_sc_hd__clkbuf_16 \
    -buf_list {sky130_fd_sc_hd__clkbuf_16 sky130_fd_sc_hd__clkbuf_8 sky130_fd_sc_hd__clkbuf_4 sky130_fd_sc_hd__clkbuf_2}

set_propagated_clock [all_clocks]
detailed_placement
check_placement

puts "=== Step 9/10: Filler Insertion & Routing ==="
filler_placement {sky130_fd_sc_hd__fill_8 sky130_fd_sc_hd__fill_4 sky130_fd_sc_hd__fill_2 sky130_fd_sc_hd__fill_1}
check_placement

set_global_routing_layer_adjustment met5 1.0
set_routing_layers -signal met1-met4 -clock met1-met4
global_route -allow_congestion
detailed_route -bottom_routing_layer met1 -top_routing_layer met5 -verbose 1

puts "=== Step 10/10: Parasitics Extraction, Timing & Physical Export ==="
write_def "05_ASIC_Synthesis/pnr/results/top/top_routed.def"

define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file "05_ASIC_Synthesis/pdk/rules.openrcx.sky130A.nom.spef_extractor" -lef_res
write_spef "05_ASIC_Synthesis/pnr/results/top/top_routed.spef"

puts "=== Post-Route STA Reports ==="
report_checks -path_delay min_max -fields {slew cap input nets fanout} -format full_clock_expanded
report_power
report_wns
report_tns

puts "=== TOP INTEGRATED PNR FLOW COMPLETED SUCCESSFULLY ==="
exit 0
