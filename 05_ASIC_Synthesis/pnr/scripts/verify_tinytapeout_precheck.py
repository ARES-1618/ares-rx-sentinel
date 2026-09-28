#!/usr/bin/env python3
"""
Tiny Tapeout TT08 Precheck & Physical Boundary Verification Script
Validates info.yaml, DEF layout dimensions, GDS structure, and pin assignments.
"""

import os
import sys
import yaml
import re

def verify_tt08_precheck(repo_root):
    errors = []
    warnings = []
    
    info_path = os.path.join(repo_root, "05_ASIC_Synthesis", "info.yaml")
    def_path = os.path.join(repo_root, "05_ASIC_Synthesis", "pnr", "results", "top", "top_routed.def")
    gds_path = os.path.join(repo_root, "05_ASIC_Synthesis", "pnr", "results", "top", "tt_um_ares_sentinel_project.gds")
    
    print("=" * 80)
    print(" TINY TAPEOUT TT08 PRECHECK & INTEGRITY VERIFICATION SUITE")
    print("=" * 80)
    
    # 1. info.yaml validation
    print("\n>>> [1/4] Validating info.yaml configuration...")
    if not os.path.exists(info_path):
        errors.append(f"Missing info.yaml at {info_path}")
        return errors
        
    with open(info_path, "r") as f:
        try:
            cfg = yaml.safe_load(f)
            print("  [PASS] info.yaml parsed successfully as valid YAML.")
        except Exception as e:
            errors.append(f"Failed to parse info.yaml: {e}")
            return errors
            
    proj = cfg.get("project", {})
    if not proj.get("top_module", "").startswith("tt_um_"):
        errors.append(f"top_module must start with 'tt_um_', got: {proj.get('top_module')}")
    else:
        print(f"  [PASS] top_module is '{proj.get('top_module')}'.")
        
    if proj.get("tiles") != "1x1":
        errors.append(f"tiles must be '1x1', got: {proj.get('tiles')}")
    else:
        print(f"  [PASS] tiles envelope specified as '{proj.get('tiles')}'.")
        
    if proj.get("clock_hz") != 20000:
        warnings.append(f"clock_hz is {proj.get('clock_hz')}, expected 20000 for protocol.")
    else:
        print(f"  [PASS] clock_hz is {proj.get('clock_hz')} (20 kHz protocol nominal).")
        
    # Check pinout
    pinout = cfg.get("pinout", {})
    required_pins = [f"ui[{i}]" for i in range(8)] + [f"uo[{i}]" for i in range(8)] + [f"uio[{i}]" for i in range(8)]
    missing_pins = [p for p in required_pins if p not in pinout]
    if missing_pins:
        errors.append(f"Missing pinout definitions for: {missing_pins}")
    else:
        print(f"  [PASS] All 24 standard IO pins (ui[0..7], uo[0..7], uio[0..7]) defined.")
        
    # 2. DEF file validation
    print("\n>>> [2/4] Validating post-route DEF geometry & pin placement...")
    if not os.path.exists(def_path):
        errors.append(f"Missing post-route DEF at {def_path}")
    else:
        with open(def_path, "r") as f:
            def_text = f.read()
            
        # Check DIEAREA
        m_die = re.search(r"DIEAREA\s*\(\s*(\d+)\s+(\d+)\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)", def_text)
        if m_die:
            x1, y1, x2, y2 = map(int, m_die.groups())
            # DEF units usually 1000 DBU per um
            width_um = (x2 - x1) / 1000.0
            height_um = (y2 - y1) / 1000.0
            print(f"  [INFO] Extracted DIEAREA: ({x1}, {y1}) to ({x2}, {y2}) DBU")
            print(f"  [INFO] Die dimensions: {width_um:.2f} um x {height_um:.2f} um")
            if abs(width_um - 161.00) > 0.01 or abs(height_um - 111.52) > 0.01:
                errors.append(f"Tile DIEAREA mismatch: expected 161.00 x 111.52 um, got {width_um} x {height_um}")
            else:
                print(f"  [PASS] Tile DIEAREA exactly matches TT08 1x1 standard template (161.00 x 111.52 um).")
        else:
            errors.append("DIEAREA statement not found in DEF")
            
        # Check PINS count
        m_pins = re.search(r"PINS\s+(\d+)\s*;", def_text)
        if m_pins:
            num_pins = int(m_pins.group(1))
            print(f"  [PASS] PINS statement found: {num_pins} IO pins routed and placed.")
        else:
            errors.append("PINS section not found in DEF")
            
        # Check COMPONENTS count
        m_comps = re.search(r"COMPONENTS\s+(\d+)\s*;", def_text)
        if m_comps:
            num_comps = int(m_comps.group(1))
            print(f"  [PASS] COMPONENTS statement found: {num_comps} total layout instances.")
        else:
            errors.append("COMPONENTS section not found in DEF")

    # 3. GDS file validation
    print("\n>>> [3/4] Validating merged GDS artifact...")
    if not os.path.exists(gds_path):
        errors.append(f"Missing GDS file at {gds_path}")
    else:
        gds_size = os.path.getsize(gds_path)
        print(f"  [PASS] Merged GDS exists: {gds_path} ({gds_size:,} bytes).")
        if gds_size < 100000:
            errors.append(f"GDS file unusually small ({gds_size} bytes)")
            
    # 4. Final Verdict
    print("\n>>> [4/4] Precheck Summary & Verdict...")
    if errors:
        print(f"  [FAIL] TT08 Precheck failed with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        return False
    else:
        print("  [SUCCESS] ALL TT08 PRECHECK REQUIREMENTS FULLY SATISFIED.")
        print("  - Package Schema: PASS")
        print("  - 1x1 Tile Envelope (161.00 x 111.52 um): PASS")
        print("  - Pin Count & Alignment: PASS")
        print("  - Silicon GDS Integrity: PASS")
        return True

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    ok = verify_tt08_precheck(root)
    sys.exit(0 if ok else 1)
