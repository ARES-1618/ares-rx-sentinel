set pdk_spice "/home/ahmad/pdk/volare/sky130/versions/cd1748bb197f9b7af62a54507de6624e30363943/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice"
puts "=== Step 1: Reading PDK SPICE ==="
set source_lib [readnet spice $pdk_spice]
puts "=== Step 2: Reading Verilog ==="
readnet verilog 05_ASIC_Synthesis/pnr/results/top/top_routed.v $source_lib
puts "=== Step 3: Reading Layout SPICE ==="
set layout [readnet spice 05_ASIC_Synthesis/pnr/results/top/top_extracted_clean.spice]
puts "=== Step 4: Running LVS ==="
lvs "$layout tt_um_ares_sentinel_project" "$source_lib tt_um_ares_sentinel_project" 05_ASIC_Synthesis/pdk/sky130A_setup.tcl 05_ASIC_Synthesis/pnr/results/top/lvs_test1.rpt
puts "=== Done ==="
exit
