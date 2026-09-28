#!/bin/bash
set -e
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

echo "=== Running Authoritative Netgen LVS ==="
netgen -batch lvs \
    "05_ASIC_Synthesis/pnr/results/top/top_extracted_clean.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pnr/results/top/top_routed_pwr.spice tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pdk/sky130A_setup.tcl" \
    "05_ASIC_Synthesis/results/lvs_authoritative.rpt"

echo "=== LVS Result Summary ==="
grep -E "(Netlists do not match|Netlists match uniquely|Circuits match uniquely|Property errors)" 05_ASIC_Synthesis/results/lvs_authoritative.rpt || true
tail -n 35 05_ASIC_Synthesis/results/lvs_authoritative.rpt
