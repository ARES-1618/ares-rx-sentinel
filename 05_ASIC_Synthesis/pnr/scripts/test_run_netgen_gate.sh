#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

echo "=== Running Netgen LVS (Clean Gate-Level) ==="
netgen -batch lvs \
    "05_ASIC_Synthesis/pnr/results/top/top_gates_clean.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pnr/results/top/top_routed.v tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pdk/sky130A_setup.tcl" \
    "05_ASIC_Synthesis/pnr/results/top/lvs_clean_gate.rpt"

echo "=== Netgen LVS Summary ==="
grep -E "(Netlists do not match|Netlists match uniquely|Circuits match uniquely|Property errors)" 05_ASIC_Synthesis/pnr/results/top/lvs_clean_gate.rpt || true
tail -n 30 05_ASIC_Synthesis/pnr/results/top/lvs_clean_gate.rpt
