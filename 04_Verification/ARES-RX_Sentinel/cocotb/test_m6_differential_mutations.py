#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Differential Verification Hardening: Behavioral Mutation Test
Work Order: WO-2026-M6-ARCH-010: Differential Test Hardening
Authority: Technical Architect / Research Direction

Purpose:
  Proves that the bounded differential simulation correlation framework is
  strictly sensitive to behavioral RTL divergence.

Methodology:
  1. Compiles and executes Golden RTL against Python reference model:
     -> MUST PASS (100% observable trace match across all 9 canonical vectors).
  2. Creates temporary mutated RTL copies in an isolated temporary directory
     strictly outside the frozen source tree:
     - Mutation M1: Timing Threshold Mutation (HB_MIN changed from 8 to 4)
     - Mutation M2: Security Constant Mutation (KNOWN_CONSTANT altered)
     - Mutation M3: Fail-Open Isolation Bypass (safe_data_out unclamped)
  3. Executes correlation against each mutant:
     -> MUST FAIL (cleanly trapping behavioral deviation).
  4. Automatically purges all temporary mutation artifacts upon completion.
================================================================================
"""

import sys
import os
import shutil
import json
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

# Single canonical vector loader
CYBER_DIR = os.path.join(PROJECT_ROOT, "06_Demonstration", "cyber_physical")
if CYBER_DIR not in sys.path:
    sys.path.insert(0, CYBER_DIR)
from canonical_vector_loader import get_all_canonical_vectors, get_canonical_vector

from run_m6_model_rtl_correlation import (
    run_python_model,
    run_rtl_vector,
    compile_rtl,
    RTL_SRC_DIR,
    HARNESS_V,
    FAULT_NAMES
)

TEMP_MUTATION_DIR = os.path.join(SCRIPT_DIR, "temp_mutation")

def setup_mutation_dir():
    if os.path.exists(TEMP_MUTATION_DIR):
        shutil.rmtree(TEMP_MUTATION_DIR)
    os.makedirs(TEMP_MUTATION_DIR)

    # Copy frozen files into temporary sandbox
    src_files = [
        "ares_sentinel_top.v",
        "ares_timing_sentinel.v",
        "ares_frame_fsm.v",
        "ares_fault_arbiter.v",
        "ares_fault_latch.v",
        "ares_isolation_gate.v",
        "ares_isolation_l3.v",
    ]
    for sf in src_files:
        shutil.copy2(os.path.join(RTL_SRC_DIR, sf), os.path.join(TEMP_MUTATION_DIR, sf))
    shutil.copy2(HARNESS_V, os.path.join(TEMP_MUTATION_DIR, "tb_m6_canonical_harness.v"))

def clean_mutation_dir():
    if os.path.exists(TEMP_MUTATION_DIR):
        shutil.rmtree(TEMP_MUTATION_DIR)

def evaluate_rtl_set(vvp_path, vectors):
    failures = []
    for v in vectors:
        py_res = run_python_model(v["cycles_profile"])
        rtl_res = run_rtl_vector(v["cycles_profile"], vvp_file=vvp_path, work_dir=TEMP_MUTATION_DIR)

        py_trace = py_res["observable_trace"]
        rtl_trace = rtl_res["observable_trace"]

        mismatches = []
        if len(py_trace) != len(rtl_trace):
            mismatches.append(f"Length mismatch: Py={len(py_trace)} vs RTL={len(rtl_trace)}")
        else:
            for idx, (p_obs, r_obs) in enumerate(zip(py_trace, rtl_trace)):
                if p_obs != r_obs:
                    mismatches.append((idx + 1, p_obs, r_obs))
                    if len(mismatches) > 3:
                        break

        if mismatches:
            failures.append({
                "vector_id": v["id"],
                "vector_name": v["name"],
                "mismatch_count": len(mismatches),
                "first_mismatch": mismatches[0]
            })
    return failures

def run_differential_mutation_audit():
    print("=" * 130)
    print(" ARES-RX SENTINEL: BEHAVIORAL MUTATION SENSITIVITY AUDIT (WO-2026-M6-ARCH-010)")
    print(" Proving that Bounded Differential Simulation Correlation strictly traps RTL behavioral mutations")
    print("=" * 130)

    vectors = get_all_canonical_vectors()
    audit_results = {}

    # 1. Baseline Golden RTL
    print("[1/4] Evaluating Golden RTL baseline...")
    golden_vvp = compile_rtl()
    golden_failures = []
    for v in vectors:
        py_res = run_python_model(v["cycles_profile"])
        rtl_res = run_rtl_vector(v["cycles_profile"])
        if py_res["observable_trace"] != rtl_res["observable_trace"]:
            golden_failures.append(v["id"])

    assert len(golden_failures) == 0, f"Golden RTL unexpectedly failed on: {golden_failures}"
    print("      -> Golden RTL: 100% MATCH across all 9 canonical vectors (PASS)")
    audit_results["golden_rtl"] = {"status": "PASS", "concordance": "100%"}

    # 2. Mutation M1: Physical Timing Threshold Mutation (HB_MIN changed from 8 to 4)
    print("\n[2/4] Testing Mutation M1: Timing Threshold Mutation (HB_MIN: 8 -> 4 in ares_timing_sentinel.v)...")
    setup_mutation_dir()
    timing_file = os.path.join(TEMP_MUTATION_DIR, "ares_timing_sentinel.v")
    with open(timing_file, "r") as f:
        content = f.read()
    mutated_content = content.replace("parameter integer HB_MIN      = 8,", "parameter integer HB_MIN      = 4,")
    with open(timing_file, "w") as f:
        f.write(mutated_content)

    m1_vvp = os.path.join(TEMP_MUTATION_DIR, "sim_m1.vvp")
    mutated_files = [
        os.path.join(TEMP_MUTATION_DIR, "tb_m6_canonical_harness.v"),
        os.path.join(TEMP_MUTATION_DIR, "ares_sentinel_top.v"),
        timing_file,
        os.path.join(TEMP_MUTATION_DIR, "ares_frame_fsm.v"),
        os.path.join(TEMP_MUTATION_DIR, "ares_fault_arbiter.v"),
        os.path.join(TEMP_MUTATION_DIR, "ares_fault_latch.v"),
        os.path.join(TEMP_MUTATION_DIR, "ares_isolation_gate.v"),
        os.path.join(TEMP_MUTATION_DIR, "ares_isolation_l3.v"),
    ]
    compile_rtl(custom_rtl_files=mutated_files, output_vvp=m1_vvp)
    m1_failures = evaluate_rtl_set(m1_vvp, vectors)
    clean_mutation_dir()

    print(f"      -> Trapped Deviations in {len(m1_failures)} vectors: {[f['vector_id'] for f in m1_failures]}")
    assert len(m1_failures) > 0, "Mutation M1 was not trapped by correlation suite!"
    print("      -> Mutation M1 Verification: MUST FAIL requirement CONFIRMED.")
    audit_results["mutation_m1_timing_threshold"] = {
        "description": "HB_MIN modified from 8 to 4",
        "expected": "FAIL",
        "actual": "FAIL",
        "trapped_vectors": [f["vector_id"] for f in m1_failures]
    }

    # 3. Mutation M2: Security Constant Mutation (KNOWN_CONSTANT altered)
    print("\n[3/4] Testing Mutation M2: Security Constant Mutation (KNOWN_CONSTANT altered in ares_frame_fsm.v)...")
    setup_mutation_dir()
    frame_file = os.path.join(TEMP_MUTATION_DIR, "ares_frame_fsm.v")
    with open(frame_file, "r") as f:
        content = f.read()
    mutated_content = content.replace("32'h0DFFFFFE", "32'h0DFFFFFF")
    with open(frame_file, "w") as f:
        f.write(mutated_content)

    m2_vvp = os.path.join(TEMP_MUTATION_DIR, "sim_m2.vvp")
    mutated_files[3] = frame_file
    mutated_files[2] = os.path.join(TEMP_MUTATION_DIR, "ares_timing_sentinel.v")
    compile_rtl(custom_rtl_files=mutated_files, output_vvp=m2_vvp)
    m2_failures = evaluate_rtl_set(m2_vvp, vectors)
    clean_mutation_dir()

    print(f"      -> Trapped Deviations in {len(m2_failures)} vectors: {[f['vector_id'] for f in m2_failures]}")
    assert len(m2_failures) > 0, "Mutation M2 was not trapped by correlation suite!"
    print("      -> Mutation M2 Verification: MUST FAIL requirement CONFIRMED.")
    audit_results["mutation_m2_security_constant"] = {
        "description": "KNOWN_CONSTANT modified from 32'h0DFFFFFE to 32'h0DFFFFFF",
        "expected": "FAIL",
        "actual": "FAIL",
        "trapped_vectors": [f["vector_id"] for f in m2_failures]
    }

    # 4. Mutation M3: Fail-Open Isolation Gate Bypass
    print("\n[4/4] Testing Mutation M3: Fail-Open Isolation Gate Bypass (unclamping safe_data_out)...")
    setup_mutation_dir()
    gate_file = os.path.join(TEMP_MUTATION_DIR, "ares_isolation_gate.v")
    with open(gate_file, "r") as f:
        content = f.read()
    mutated_content = content.replace(
        "assign out_data     = fault_latched ? {DATA_WIDTH{1'b0}} : in_data;",
        "assign out_data     = in_data;"
    )
    with open(gate_file, "w") as f:
        f.write(mutated_content)

    m3_vvp = os.path.join(TEMP_MUTATION_DIR, "sim_m3.vvp")
    mutated_files[6] = gate_file
    mutated_files[3] = os.path.join(TEMP_MUTATION_DIR, "ares_frame_fsm.v")
    compile_rtl(custom_rtl_files=mutated_files, output_vvp=m3_vvp)
    m3_failures = evaluate_rtl_set(m3_vvp, vectors)
    clean_mutation_dir()

    print(f"      -> Trapped Deviations in {len(m3_failures)} vectors: {[f['vector_id'] for f in m3_failures]}")
    assert len(m3_failures) == 8, f"Expected 8 attack vector failures on fail-open gate, got {len(m3_failures)}"
    print("      -> Mutation M3 Verification: MUST FAIL requirement CONFIRMED.")
    audit_results["mutation_m3_isolation_bypass"] = {
        "description": "Fail-open bypass: safe_data_out clamped to raw_data_in",
        "expected": "FAIL",
        "actual": "FAIL",
        "trapped_vectors": [f["vector_id"] for f in m3_failures]
    }

    # Save proof JSON
    proof_path = os.path.join(SCRIPT_DIR, "m6_mutation_test_proof.json")
    with open(proof_path, "w", encoding="utf-8") as f:
        json.dump({
            "work_order": "WO-2026-M6-ARCH-010",
            "audit": "Behavioral Mutation Sensitivity Proof",
            "results": audit_results,
            "conclusion": "Differential correlation test is empirically proven sensitive to timing, frame syntax, and isolation gate mutations."
        }, f, indent=2)

    print("\n" + "=" * 130)
    print("[AUDIT RESULT] DIFFERENTIAL VERIFICATION HARDENING PROVEN:")
    print("               1. Golden RTL vs. Python Model  ==> PASS (100% Concordance)")
    print("               2. Mutated RTLs vs. Python Model ==> ALL DETECTED & FAILED AS REQUIRED")
    print(f"[PROOF LOG] Written to: {proof_path}")
    print("=" * 130)

if __name__ == "__main__":
    run_differential_mutation_audit()
