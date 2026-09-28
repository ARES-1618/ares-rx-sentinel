#!/usr/bin/env python3
import re
from collections import Counter

def analyze_verilog_instances(v_file):
    counts = Counter()
    with open(v_file, 'r') as f:
        for line in f:
            m = re.search(r'^\s*(sky130_fd_sc_hd__\w+)\s+(\S+)', line)
            if m:
                master = m.group(1)
                counts[master] += 1
    return counts

base_v = "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.v"
c_v = analyze_verilog_instances(base_v)

ignore_cells = {'sky130_fd_sc_hd__fill_1', 'sky130_fd_sc_hd__fill_2', 'sky130_fd_sc_hd__fill_4', 'sky130_fd_sc_hd__fill_8',
                'sky130_fd_sc_hd__tapvpwrvgnd_1', 'sky130_fd_sc_hd__decap_3'}

total_v = sum(c_v.values())
logic_v = sum(cnt for m, cnt in c_v.items() if m not in ignore_cells)
conb_v = c_v.get('sky130_fd_sc_hd__conb_1', 0)
cts_v = sum(cnt for m, cnt in c_v.items() if 'clkbuf' in m or 'clkinv' in m)

print("=" * 80)
print(" BASELINE POST-ROUTE INSTANCE AUDIT")
print("=" * 80)
for m, cnt in sorted(c_v.items()):
    print(f"  {m:<40} : {cnt}")
print("=" * 80)
print(f"Total Physical Instances: {total_v}")
print(f"Total Logic/Functional (including CTS): {logic_v}")
print(f"Tie-off cells (conb_1): {conb_v}")
print(f"Net Logic without tie-off (stdcells + CTS): {logic_v - conb_v}")
