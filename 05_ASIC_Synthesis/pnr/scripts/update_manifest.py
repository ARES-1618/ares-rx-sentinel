#!/usr/bin/env python3
import hashlib
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

files_to_hash = [
    # M4 Frozen RTL
    "03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_arbiter.v",
    "03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_latch.v",
    "03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_frame_fsm.v",
    "03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_gate.v",
    "03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_l3.v",
    "03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_sentinel_top.v",
    "03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_timing_sentinel.v",
    # M5-F Post-Route Physical Deliverables
    "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.def",
    "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.spef",
    "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.v",
    "05_ASIC_Synthesis/pnr/results/baseline/tt_um_dusterthefirst_project.gds",
    "05_ASIC_Synthesis/pnr/results/top/top_routed.def",
    "05_ASIC_Synthesis/pnr/results/top/top_routed.spef",
    "05_ASIC_Synthesis/pnr/results/top/top_routed.v",
    "05_ASIC_Synthesis/pnr/results/top/tt_um_ares_sentinel_project.gds",
    # M5-F Sign-off Reports and Dossiers
    "05_ASIC_Synthesis/results/post_route_ppa_benchmarking_report.md",
    "05_ASIC_Synthesis/results/drc_reconciliation.md",
    "05_ASIC_Synthesis/results/drc_waiver_basis.md",
    "05_ASIC_Synthesis/results/sta_reconciliation.md",
    "05_ASIC_Synthesis/results/power_reconciliation.md",
    "05_ASIC_Synthesis/results/sta_power_scenario_b_vcd.txt",
    "05_ASIC_Synthesis/results/lvs_authoritative.rpt",
    "05_ASIC_Synthesis/info.yaml",
]

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

manifest_lines = []
print("=" * 80)
print(" PHYSICAL IMPLEMENTATION DELIVERABLES SHA-256 SEAL")
print("=" * 80)

for rel_path in files_to_hash:
    full_path = os.path.join(repo_root, rel_path)
    if os.path.exists(full_path):
        digest = sha256_file(full_path)
        norm_path = rel_path.replace("\\", "/")
        print(f"{digest}  {norm_path}")
        manifest_lines.append(f"{digest}  {norm_path}\n")
    else:
        print(f"[MISSING] {rel_path}")

manifest_path = os.path.join(repo_root, "05_ASIC_Synthesis", "02_Physical_Implementation_Manifest.sha256")
with open(manifest_path, "w") as f:
    f.writelines(manifest_lines)

print(f"\nSuccessfully sealed {len(manifest_lines)} artifacts into:")
print(f"  {manifest_path}")
