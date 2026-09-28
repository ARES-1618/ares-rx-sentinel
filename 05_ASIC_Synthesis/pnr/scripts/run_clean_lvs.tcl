set pdk_spice "/home/ahmad/pdk/volare/sky130/versions/cd1748bb197f9b7af62a54507de6624e30363943/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice"

readnet spice $pdk_spice
readnet spice 05_ASIC_Synthesis/pnr/results/top/top_gates_clean.spice 1
readnet spice 05_ASIC_Synthesis/pnr/results/top/top_routed.spice 2

lvs "05_ASIC_Synthesis/pnr/results/top/top_gates_clean.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pnr/results/top/top_routed.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pdk/sky130A_setup.tcl" \
    "05_ASIC_Synthesis/pnr/results/top/lvs_clean_hier.rpt"
