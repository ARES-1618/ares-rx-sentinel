#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

cat << 'EOF' > 05_ASIC_Synthesis/pnr/scripts/run_clean_lvs.tcl
set pdk_spice "/home/ahmad/pdk/volare/sky130/versions/cd1748bb197f9b7af62a54507de6624e30363943/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice"

readnet spice $pdk_spice
readnet spice 05_ASIC_Synthesis/pnr/results/top/top_gates_clean.spice 1
readnet spice 05_ASIC_Synthesis/pnr/results/top/top_routed.spice 2

lvs "05_ASIC_Synthesis/pnr/results/top/top_gates_clean.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pnr/results/top/top_routed.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pdk/sky130A_setup.tcl" \
    "05_ASIC_Synthesis/pnr/results/top/lvs_clean_hier.rpt"
EOF

netgen -batch source 05_ASIC_Synthesis/pnr/scripts/run_clean_lvs.tcl
grep -E "(Netlists do not match|Netlists match uniquely|Circuits match uniquely|Property errors)" 05_ASIC_Synthesis/pnr/results/top/lvs_clean_hier.rpt || true
tail -n 30 05_ASIC_Synthesis/pnr/results/top/lvs_clean_hier.rpt
