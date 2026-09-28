#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
export PDK_ROOT="/home/ahmad/pdk/volare/sky130/versions/cd1748bb197f9b7af62a54507de6624e30363943"

echo "=== Testing Magic LEF/DEF Gate Extraction ==="
magic -dnull -noconsole -rcfile 05_ASIC_Synthesis/pdk/sky130A.magicrc << 'EOF'
lef read 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd.lef
def read 05_ASIC_Synthesis/pnr/results/top/top_routed.def
load tt_um_ares_sentinel_project
select top cell
extract do local
extract no capacitance
extract no coupling
extract no resistance
extract all
ext2spice lvs
ext2spice -o 05_ASIC_Synthesis/pnr/results/top/top_gates_extracted.spice
exit 0
EOF

echo "=== Extracted Gate SPICE Head ==="
head -n 40 05_ASIC_Synthesis/pnr/results/top/top_gates_extracted.spice
