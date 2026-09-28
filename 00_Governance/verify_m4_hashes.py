#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Milestone M4 Cryptographic Hash Concordance Verifier
Authority: Technical Architect / Research Direction (WO-2026-FINAL-AUDIT-007)
Purpose: Formally audits the 7 frozen M4 RTL modules on disk by independently
         verifying that the Authoritative Manifest, the Core Development Source,
         and the TT08 Submission Source are 100% bit-for-bit concordant.
================================================================================
"""

import os
import sys
import hashlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "00_Governance", "M4_Cryptographic_Manifest.sha256")

CORE_DIR = os.path.join(PROJECT_ROOT, "03_Core_Projects", "ARES-RX_Sentinel", "ares_sentinel")
SUBMISSION_DIR = os.path.join(PROJECT_ROOT, "05_ASIC_Synthesis", "tt08_submission_repo", "src")

def compute_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def verify_m4_independent_concordance():
    if not os.path.exists(MANIFEST_PATH):
        print(f"[ERROR] Manifest not found: {MANIFEST_PATH}")
        return 1

    expected = {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    h = parts[0].lower()
                    fname = parts[1].lstrip("*")
                    expected[fname] = h

    print("=" * 135)
    print(" ARES-RX SENTINEL: M4 INDEPENDENT 3-WAY CRYPTOGRAPHIC CONCORDANCE AUDIT (WO-2026-FINAL-AUDIT-007)")
    print("=" * 135)
    print(f"{'Module Filename':<24} | {'Expected Manifest':<26} | {'Core Project Hash':<26} | {'Submission Repo Hash':<26} | Concordance")
    print("-" * 135)

    all_matched = True
    for mod, exp_hash in expected.items():
        core_path = os.path.join(CORE_DIR, mod)
        subm_path = os.path.join(SUBMISSION_DIR, mod)

        core_hash = compute_sha256(core_path)
        subm_hash = compute_sha256(subm_path)

        match_core = (core_hash == exp_hash)
        match_subm = (subm_hash == exp_hash)
        is_three_way_match = match_core and match_subm

        if not is_three_way_match:
            all_matched = False

        if is_three_way_match:
            status = "MATCH [3-WAY FROZEN]"
        elif not match_core:
            status = "MISMATCH [CORE DIVERGED]"
        elif not match_subm:
            status = "MISMATCH [SUBMISSION DIVERGED]"
        else:
            status = "MISMATCH [CORRUPT]"

        exp_disp = f"{exp_hash[:12]}...{exp_hash[-6:]}" if exp_hash else "NONE"
        core_disp = f"{core_hash[:12]}...{core_hash[-6:]}" if core_hash else "MISSING"
        subm_disp = f"{subm_hash[:12]}...{subm_hash[-6:]}" if subm_hash else "MISSING"

        print(f"{mod:<24} | {exp_disp:<26} | {core_disp:<26} | {subm_disp:<26} | {status}")

    print("=" * 135)
    if all_matched and len(expected) == 7:
        print(" [AUDIT RESULT] 100% BIT-FOR-BIT 3-WAY MATCH: Manifest == Core Source == Submission Source (7/7 modules).")
        print(" [AUDIT RESULT] M4 RTL source is strictly hash-concordant across all repositories.")
        print("=" * 135)
        return 0
    else:
        print(" [AUDIT RESULT] VIOLATION: M4 independent multi-source concordance mismatch detected!")
        print("=" * 135)
        return 1

if __name__ == "__main__":
    sys.exit(verify_m4_independent_concordance())
