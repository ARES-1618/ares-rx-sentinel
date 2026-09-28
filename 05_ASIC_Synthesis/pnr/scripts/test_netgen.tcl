# Read standard cell library verilog first
readnet verilog /home/ahmad/pdk/volare/sky130/versions/cd1748bb197f9b7af62a54507de6624e30363943/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v
# Read synthesized verilog
readnet verilog 05_ASIC_Synthesis/results/baseline_synth_netlist.v
# Read layout spice
readnet spice 05_ASIC_Synthesis/pnr/results/baseline/tt_um_dusterthefirst_project_extracted.spice

# Run LVS with setup.tcl
lvs "05_ASIC_Synthesis/pnr/results/baseline/tt_um_dusterthefirst_project_extracted.spice tt_um_dusterthefirst_project" "05_ASIC_Synthesis/results/baseline_synth_netlist.v tt_um_dusterthefirst_project" 05_ASIC_Synthesis/pdk/sky130A_setup.tcl 05_ASIC_Synthesis/pnr/results/baseline/test_lvs.rpt
exit 0
