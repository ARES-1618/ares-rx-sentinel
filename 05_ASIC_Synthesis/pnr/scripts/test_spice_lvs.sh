#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

echo "=== Running Netgen LVS SPICE-to-SPICE ==="
netgen -batch lvs \
    "05_ASIC_Synthesis/pnr/results/top/top_gates_clean.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pnr/results/top/top_routed.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pdk/sky130A_setup.tcl" \
    "05_ASIC_Synthesis/pnr/results/top/lvs_spice_comp.rpt"

echo "=== Netgen LVS Result ==="
grep -E "(Netlists do not match|Netlists match uniquely|Circuits match uniquely|Property errors)" 05_ASIC_Synthesis/pnr/results/top/lvs_spice_comp.rpt || true
tail -n 40 05_ASIC_Synthesis/pnr/results/top/lvs_spice_comp.rpt
