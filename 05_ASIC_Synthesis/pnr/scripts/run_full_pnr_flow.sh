#!/bin/bash
# ==============================================================================
# Full ASIC Physical Implementation & Verification Flow (M5-F)
# Standard: Tiny Tapeout TT08 (SkyWater 130nm — sky130_fd_sc_hd)
# Designs: Baseline (tt_um_dusterthefirst_project) & Top (tt_um_ares_sentinel_project)
# Authority: Technical Architect / Research Direction (WO-2026-M5-F-001)
# ==============================================================================
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

echo "======================================================================"
echo " Starting M5-F Physical Implementation Flow (OpenROAD, Magic, Netgen) "
echo "======================================================================"

mkdir -p 05_ASIC_Synthesis/pnr/results/baseline
mkdir -p 05_ASIC_Synthesis/pnr/results/top

# --------------------------------------------------------------------
# 1. Baseline Design P&R
# --------------------------------------------------------------------
echo ""
echo ">>> [1/4] Running Baseline Place & Route in OpenROAD..."
openroad -exit 05_ASIC_Synthesis/pnr/scripts/pnr_baseline.tcl 2>&1 | tee 05_ASIC_Synthesis/pnr/results/baseline/pnr_baseline.log

echo ">>> [2/4] Running Baseline Magic PV (GDS Merge, DRC, SPICE Extraction)..."
export TOP_MODULE="tt_um_dusterthefirst_project"
export DEF_FILE="05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.def"
export OUT_DIR="05_ASIC_Synthesis/pnr/results/baseline"
magic -dnull -noconsole -rcfile 05_ASIC_Synthesis/pdk/sky130A.magicrc 05_ASIC_Synthesis/pnr/scripts/run_magic_pv.tcl 2>&1 | tee 05_ASIC_Synthesis/pnr/results/baseline/magic_pv.log

echo ">>> [3/4] Running Baseline Netgen LVS..."
bash 05_ASIC_Synthesis/pnr/scripts/run_netgen_lvs.sh \
    "tt_um_dusterthefirst_project" \
    "05_ASIC_Synthesis/pnr/results/baseline" \
    "05_ASIC_Synthesis/results/baseline_synth_netlist.v" 2>&1 | tee 05_ASIC_Synthesis/pnr/results/baseline/netgen_lvs.log

# --------------------------------------------------------------------
# 2. Integrated Top Design P&R
# --------------------------------------------------------------------
echo ""
echo ">>> [4/4] Running Top Integrated Place & Route in OpenROAD..."
openroad -exit 05_ASIC_Synthesis/pnr/scripts/pnr_top.tcl 2>&1 | tee 05_ASIC_Synthesis/pnr/results/top/pnr_top.log

echo ">>> Running Top Magic PV (GDS Merge, DRC, SPICE Extraction)..."
export TOP_MODULE="tt_um_ares_sentinel_project"
export DEF_FILE="05_ASIC_Synthesis/pnr/results/top/top_routed.def"
export OUT_DIR="05_ASIC_Synthesis/pnr/results/top"
magic -dnull -noconsole -rcfile 05_ASIC_Synthesis/pdk/sky130A.magicrc 05_ASIC_Synthesis/pnr/scripts/run_magic_pv.tcl 2>&1 | tee 05_ASIC_Synthesis/pnr/results/top/magic_pv.log

echo ">>> Running Top Netgen LVS..."
bash 05_ASIC_Synthesis/pnr/scripts/run_netgen_lvs.sh \
    "tt_um_ares_sentinel_project" \
    "05_ASIC_Synthesis/pnr/results/top" \
    "05_ASIC_Synthesis/results/top_synth_netlist.v" 2>&1 | tee 05_ASIC_Synthesis/pnr/results/top/netgen_lvs.log

echo ""
echo "======================================================================"
echo " M5-F Physical Implementation & Verification Completed Successfully! "
echo "======================================================================"
