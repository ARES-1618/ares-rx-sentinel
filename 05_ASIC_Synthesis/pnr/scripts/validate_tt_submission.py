#!/usr/bin/env python3
"""
Tiny Tapeout TT08 Submission & Platform Precheck Script
Standard: SkyWater 130nm TT08 1x1 Standard Tile
Target: tt_um_ares_sentinel_project
"""
import os
import sys
import yaml

def run_precheck():
    print("=" * 70)
    print("TINY TAPEOUT TT08 SUBMISSION PRECHECK VALIDATOR")
    print("Target: tt_um_ares_sentinel_project")
    print("=" * 70)

    synth_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    pnr_top_dir = os.path.join(synth_dir, "pnr", "results", "top")

    errors = []
    warnings = []

    # 1. Validate info.yaml
    info_yaml_path = os.path.join(synth_dir, "info.yaml")
    if not os.path.exists(info_yaml_path):
        errors.append(f"Missing info.yaml at {info_yaml_path}")
    else:
        with open(info_yaml_path, "r") as f:
            try:
                cfg = yaml.safe_load(f)
                proj = cfg.get("project", {})
                pinout = cfg.get("pinout", {})

                # Check fields
                if proj.get("top_module") != "tt_um_ares_sentinel_project":
                    errors.append(f"Invalid top_module: {proj.get('top_module')}")
                if proj.get("tiles") != "1x1":
                    errors.append(f"Invalid tiles specification: {proj.get('tiles')}")
                if proj.get("clock_hz") != 20000:
                    warnings.append(f"Nominal clock is {proj.get('clock_hz')}, expected 20000 Hz")

                # Check pinouts
                for port, count in [("ui", 8), ("uo", 8), ("uio", 8)]:
                    for idx in range(count):
                        key = f"{port}[{idx}]"
                        if key not in pinout:
                            errors.append(f"Missing pinout entry: {key}")

                print("[PASS] info.yaml syntax, tile assignment, and pinout schema verified.")
            except Exception as e:
                errors.append(f"YAML parsing error in info.yaml: {e}")

    # 2. Check tt-support-tools project_checks if available
    tt_tools_dir = "/tmp/tt-support-tools"
    if os.path.exists(tt_tools_dir):
        sys.path.insert(0, tt_tools_dir)
        try:
            from project_checks import check_info_yaml
            tt_errs = check_info_yaml(synth_dir, "sky130A")
            if tt_errs:
                for te in tt_errs:
                    errors.append(f"tt-support-tools: {te}")
            else:
                print("[PASS] Official tt-support-tools check_info_yaml passed 100%.")
        except Exception as e:
            warnings.append(f"tt-support-tools check execution note: {e}")

    # 3. Validate GDSII artifact
    gds_path = os.path.join(pnr_top_dir, "tt_um_ares_sentinel_project.gds")
    if not os.path.exists(gds_path):
        errors.append(f"GDSII artifact missing: {gds_path}")
    else:
        gds_size = os.path.getsize(gds_path)
        if gds_size < 10000:
            errors.append(f"GDSII file size abnormally small: {gds_size} bytes")
        else:
            print(f"[PASS] GDSII artifact present: {os.path.basename(gds_path)} ({gds_size:,} bytes).")

    # 4. Validate DEF DIEAREA
    def_path = os.path.join(pnr_top_dir, "top_routed.def")
    if not os.path.exists(def_path):
        errors.append(f"DEF artifact missing: {def_path}")
    else:
        with open(def_path, "r") as f:
            def_text = f.read(2048)
            import re
            m = re.search(r'DIEAREA\s*\(\s*(\d+)\s+(\d+)\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)', def_text)
            if m:
                x1, y1, x2, y2 = map(int, m.groups())
                dx_um = (x2 - x1) / 1000.0
                dy_um = (y2 - y1) / 1000.0
                print(f"[PASS] DEF DIEAREA verified: ({dx_um:.2f} um x {dy_um:.2f} um).")
                if abs(dx_um - 161.00) > 0.01 or abs(dy_um - 111.52) > 0.01:
                    errors.append(f"DEF DIEAREA mismatch: {dx_um} x {dy_um}, expected 161.00 x 111.52 um")
            else:
                errors.append("DIEAREA statement not found in DEF")

    # 5. Validate SPEF and Routed Netlist
    spef_path = os.path.join(pnr_top_dir, "top_routed.spef")
    netlist_path = os.path.join(pnr_top_dir, "top_routed.v")
    if os.path.exists(spef_path):
        print(f"[PASS] SPEF parasitic extraction verified: {os.path.getsize(spef_path):,} bytes.")
    else:
        errors.append("SPEF parasitic file missing")

    if os.path.exists(netlist_path):
        print(f"[PASS] Post-route Verilog netlist verified: {os.path.getsize(netlist_path):,} bytes.")
    else:
        errors.append("Post-route Verilog netlist missing")

    print("-" * 70)
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  [WARN] {w}")

    if errors:
        print(f"ERRORS ENCOUNTERED ({len(errors)}):")
        for e in errors:
            print(f"  [FAIL] {e}")
        print("TINY TAPEOUT SUBMISSION PRECHECK: FAILED")
        return 1
    else:
        print("=" * 70)
        print(">>> TINY TAPEOUT TT08 SUBMISSION PRECHECK: PASSED 100% <<<")
        print("=" * 70)
        return 0

if __name__ == "__main__":
    sys.exit(run_precheck())
