#!/usr/bin/env python3
import re
import sys

def parse_log(log_path, design_name):
    print(f"==================================================")
    print(f"PARSING LOG: {design_name} ({log_path})")
    print(f"==================================================")
    with open(log_path) as f:
        content = f.read()

    # Placement metrics
    m_inst_area = re.search(r'\[INFO GPL-0018\] PlaceInstsArea:\s*(\d+)', content)
    m_util = re.search(r'\[INFO GPL-0019\] Util\(%\):\s*([\d\.]+)', content)
    m_std_area = re.search(r'\[INFO GPL-0020\] StdInstsArea:\s*(\d+)', content)
    m_bin_area = re.search(r'\[INFO GPL-0027\] TotalBinArea:\s*(\d+)', content)

    if m_inst_area:
        inst_area_um2 = int(m_inst_area.group(1)) / 1e6
        bin_area_um2 = int(m_bin_area.group(1)) / 1e6 if m_bin_area else 0
        util_pct = float(m_util.group(1)) if m_util else 0
        print(f"PlaceInstsArea: {inst_area_um2:.2f} um^2")
        print(f"TotalBinArea (Core Placement Site): {bin_area_um2:.2f} um^2")
        print(f"RePlAce Reported Core Utilization: {util_pct:.2f}%")
        print(f"Calculated Ratio (PlaceInstsArea / TotalBinArea): {(inst_area_um2 / bin_area_um2)*100:.2f}%")

    # FastRoute Congestion / Global Route metrics
    print("\n--- Global Route Congestion & Routing Resource Analysis ---")
    lines = content.splitlines()
    gr_lines = []
    capture = False
    for line in lines:
        if "global_route" in line or "Start global routing" in line or "Routing resources analysis" in line:
            capture = True
        if capture:
            if any(k in line for k in ["Routing resources analysis", "Final congestion report", "overflow", "Capacity", "Demand", "Utilization", "Layer", "GRT-"]):
                gr_lines.append(line.strip())
            if "detailed_route" in line or "Detailed Routing" in line:
                break

    for l in gr_lines[:40]:
        print(" ", l)

if __name__ == "__main__":
    parse_log("05_ASIC_Synthesis/pnr/results/baseline/pnr_baseline.log", "Baseline (tt07-bep-decode)")
    print("\n")
    parse_log("05_ASIC_Synthesis/pnr/results/top/pnr_top.log", "Sentinel Integrated Top")
