# Test script for OpenROAD PDN generation without manual global_connect call
set ::env(STRESS_50MHZ) 1

read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__nom.tlef"
read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd.lef"
read_liberty "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib"
read_verilog "05_ASIC_Synthesis/results/baseline_synth_netlist.v"
link_design "tt_um_dusterthefirst_project"
read_sdc "05_ASIC_Synthesis/constraints/ares_sentinel_sky130.sdc"
read_def -floorplan_initialize "05_ASIC_Synthesis/pdk/tt_block_1x1_pg.def"

puts "=== Setting Global Connections ==="
add_global_connection -net {VPWR} -inst_pattern {.*} -pin_pattern {^VPWR$} -power
add_global_connection -net {VGND} -inst_pattern {.*} -pin_pattern {^VGND$} -ground
add_global_connection -net {VPWR} -inst_pattern {.*} -pin_pattern {^VPB$}
add_global_connection -net {VGND} -inst_pattern {.*} -pin_pattern {^VNB$}

puts "=== Defining PDN Grid ==="
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

puts "=== Running pdngen ==="
pdngen

puts "=== PDN Generated Successfully! ==="
exit 0
