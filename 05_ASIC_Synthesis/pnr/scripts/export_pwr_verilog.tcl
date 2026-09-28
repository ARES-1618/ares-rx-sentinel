read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__nom.tlef"
read_lef "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd.lef"
read_def "05_ASIC_Synthesis/pnr/results/top/top_routed.def"
write_verilog -include_pwr_gnd "05_ASIC_Synthesis/pnr/results/top/top_routed_pwr.v"
exit
