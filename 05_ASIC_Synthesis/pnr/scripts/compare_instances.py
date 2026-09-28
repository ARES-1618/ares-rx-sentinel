#!/usr/bin/env python3
import re
from collections import Counter

def analyze_spice_instances(spice_file):
    counts = Counter()
    with open(spice_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('X'):
                parts = line.split()
                master = parts[-1]
                counts[master] += 1
    return counts

def analyze_verilog_instances(v_file):
    counts = Counter()
    with open(v_file, 'r') as f:
        for line in f:
            m = re.search(r'^\s*(sky130_fd_sc_hd__\w+)\s+(\S+)', line)
            if m:
                master = m.group(1)
                counts[master] += 1
    return counts

top_spice = "05_ASIC_Synthesis/pnr/results/top/top_gates_clean.spice"
top_v = "05_ASIC_Synthesis/pnr/results/top/top_routed.v"

c_spice = analyze_spice_instances(top_spice)
c_v = analyze_verilog_instances(top_v)

print("=" * 80)
print(f"{'Cell Master':<40} {'Extracted SPICE':<18} {'Routed Verilog':<18} {'Match?'}")
print("=" * 80)

all_masters = sorted(set(list(c_spice.keys()) + list(c_v.keys())))
total_sp = 0
total_v = 0
logic_sp = 0
logic_v = 0

ignore_cells = {'sky130_fd_sc_hd__fill_1', 'sky130_fd_sc_hd__fill_2', 'sky130_fd_sc_hd__fill_4', 'sky130_fd_sc_hd__fill_8',
                'sky130_fd_sc_hd__tapvpwrvgnd_1', 'sky130_fd_sc_hd__decap_3'}

for m in all_masters:
    s_cnt = c_spice.get(m, 0)
    v_cnt = c_v.get(m, 0)
    total_sp += s_cnt
    total_v += v_cnt
    is_logic = m not in ignore_cells
    if is_logic:
        logic_sp += s_cnt
        logic_v += v_cnt
    match_str = "EXACT MATCH" if s_cnt == v_cnt else "MISMATCH"
    print(f"{m:<40} {s_cnt:<18} {v_cnt:<18} {match_str}")

print("=" * 80)
print(f"Total Physical Instances:       SPICE = {total_sp:<8} Verilog = {total_v:<8} {'MATCH' if total_sp == total_v else 'DIFF'}")
print(f"Total Functional/Logic Cells:   SPICE = {logic_sp:<8} Verilog = {logic_v:<8} {'EXACT 1-TO-1 MATCH' if logic_sp == logic_v else 'DIFF'}")
print("=" * 80)
