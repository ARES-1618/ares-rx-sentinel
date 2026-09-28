#!/bin/bash
# ==============================================================================
# Netgen Layout vs. Schematic (LVS) Comparison Script
# Standard: Tiny Tapeout TT08 (SkyWater 130nm — sky130_fd_sc_hd)
# ==============================================================================
set -e

TOP_MODULE="$1"
OUT_DIR="$2"
NETLIST="$3"

if [ -z "$TOP_MODULE" ] || [ -z "$OUT_DIR" ] || [ -z "$NETLIST" ]; then
    echo "Usage: $0 <top_module> <output_dir> <netlist_verilog>"
    exit 1
fi

SETUP_TCL="05_ASIC_Synthesis/pdk/sky130A_setup.tcl"
EXTRACTED_SPICE="${OUT_DIR}/${TOP_MODULE}_extracted.spice"
REPORT="${OUT_DIR}/${TOP_MODULE}_lvs.rpt"

echo "=== Running Netgen LVS for ${TOP_MODULE} ==="
netgen -batch lvs \
    "${EXTRACTED_SPICE} ${TOP_MODULE}" \
    "${NETLIST} ${TOP_MODULE}" \
    "${SETUP_TCL}" \
    "${REPORT}"

echo "=== Netgen LVS finished. Summary: ==="
grep -E "(Netlists do not match|Netlists match uniquely|Circuits match uniquely|Property errors)" "${REPORT}" || true
echo "Full report: ${REPORT}"
