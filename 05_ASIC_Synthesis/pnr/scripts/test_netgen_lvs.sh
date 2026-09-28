#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

PDK_ROOT="/home/ahmad/pdk/volare/sky130/versions/cd1748bb197f9b7af62a54507de6624e30363943/sky130A"
STD_SPICE="$PDK_ROOT/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice"
STD_CDL="$PDK_ROOT/libs.ref/sky130_fd_sc_hd/cdl/sky130_fd_sc_hd.cdl"

echo "=== Exporting clean routed verilog with pwr gnd and without fillers ==="
openroad -exit -no_init -no_splash << 'EOF'
read_lef 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__nom.tlef
read_lef 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd.lef
read_def 05_ASIC_Synthesis/pnr/results/top/top_routed.def
write_verilog -include_pwr_gnd -remove_cells {sky130_fd_sc_hd__fill_1 sky130_fd_sc_hd__fill_2 sky130_fd_sc_hd__fill_4 sky130_fd_sc_hd__fill_8 sky130_fd_sc_hd__tapvpwrvgnd_1 sky130_fd_sc_hd__decap_3} 05_ASIC_Synthesis/pnr/results/top/top_lvs_netlist.v
write_verilog -remove_cells {sky130_fd_sc_hd__fill_1 sky130_fd_sc_hd__fill_2 sky130_fd_sc_hd__fill_4 sky130_fd_sc_hd__fill_8 sky130_fd_sc_hd__tapvpwrvgnd_1 sky130_fd_sc_hd__decap_3} 05_ASIC_Synthesis/pnr/results/top/top_lvs_nopwr.v
EOF

echo "=== Checking netlist instance count ==="
grep -E '^\s*sky130_fd_sc_hd__' 05_ASIC_Synthesis/pnr/results/top/top_lvs_netlist.v | wc -l
