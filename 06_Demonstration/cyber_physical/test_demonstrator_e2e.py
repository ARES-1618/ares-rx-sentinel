#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — End-to-End Cyber-Physical Demonstrator Test & Verification
Milestone: M6 (Cyber-Physical Security Demonstrator)
Function: Boots the Attacker Daemon, Virtual Channel, and Hardware Target Node,
          executes the full AV00..AV08 adversarial battery over live UDP sockets,
          verifies cycle-by-cycle perimeter zeroization, and audits the
          cryptographic hash chain ledger.
================================================================================
"""

import sys
import os
import time
import json
import socket
import threading
import hashlib

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
from attacker_daemon import AttackerDaemon
from virtual_channel import VirtualChannel
from receiver_node import ReceiverNode

TEST_LEDGER_PATH = os.path.join(SCRIPT_DIR, "test_evidence_chain_ledger.jsonl")

def run_e2e_demonstration():
    print("=" * 80)
    print(" ARES-RX SENTINEL CYBER-PHYSICAL DEMONSTRATOR -- E2E VERIFICATION BATTERY")
    print("=" * 80)

    # Clean existing test ledger if present
    if os.path.exists(TEST_LEDGER_PATH):
        os.remove(TEST_LEDGER_PATH)

    received_events = []
    event_lock = threading.Lock()

    def on_telemetry(record, waveform):
        with event_lock:
            received_events.append(record)

    # 1. Start Virtual Channel on test ports (19099 -> 19100)
    vchan = VirtualChannel(listen_port=19099, target_port=19100, simulated_delay_ms=1.0, jitter_ms=0.2)
    vchan_thread = threading.Thread(target=vchan.start, daemon=True)
    vchan_thread.start()

    # 2. Start Hardware Receiver Target on test port 19100
    receiver = ReceiverNode(listen_port=19100, ledger_path=TEST_LEDGER_PATH, callback=on_telemetry)
    rx_thread = threading.Thread(target=receiver.start, daemon=True)
    rx_thread.start()

    time.sleep(0.1)  # Allow sockets to bind

    # 3. Instantiate Attacker targeting virtual channel port 19099
    attacker = AttackerDaemon(target_host="127.0.0.1", target_port=19099)

    scenarios = [
        ("AV00_NOMINAL",          False, "NOMINAL_ACCEPTED",     "Nominal Authenticated Frame"),
        ("AV01_RUNT_GLITCH",       True,  "FAIL_CLOSED_ZEROIZED", "L1 Sub-Nyquist Glitch (<=7c)"),
        ("AV02_STRETCHED_PULSE",   True,  "FAIL_CLOSED_ZEROIZED", "L1 Gap Timeout (>=21c)"),
        ("AV03_MIDBAND",           True,  "FAIL_CLOSED_ZEROIZED", "L1 Midband Jitter (11..15c)"),
        ("AV04_PREAMBLE_TAMPER",   True,  "FAIL_CLOSED_ZEROIZED", "L2 Preamble Bit Corruption"),
        ("AV05_TYPE_MUTATION",     True,  "FAIL_CLOSED_ZEROIZED", "L2 Protocol Type Mismatch"),
        ("AV06_CONSTANT_CORRUPT",  True,  "FAIL_CLOSED_ZEROIZED", "L2 Security Field Corrupt"),
        ("AV07_TRUNCATION",        True,  "FAIL_CLOSED_ZEROIZED", "L2 Framing Truncation (<192b)"),
        ("AV08_OVERRUN",           True,  "FAIL_CLOSED_ZEROIZED", "L2 Buffer Overrun (>192b)")
    ]

    results_table = []
    all_passed = True

    print("\n[STEP 1] Executing Real-Time Cyber-Physical Transmission Battery...")
    print("-" * 80)

    for code, expect_tamper, expect_verdict, desc in scenarios:
        initial_count = len(received_events)
        attacker.inject_attack(code)

        # Wait for propagation across virtual channel and hardware processing
        timeout = 2.0
        start_wait = time.time()
        while len(received_events) == initial_count and (time.time() - start_wait) < timeout:
            time.sleep(0.01)

        if len(received_events) == initial_count:
            print(f"[FAIL] Timeout waiting for event {code}")
            all_passed = False
            continue

        latest = received_events[-1]
        
        # Verify hardware assertions
        is_tamper_ok = (latest["tamper_asserted"] == expect_tamper)
        is_verdict_ok = (latest["verdict"] == expect_verdict)
        
        if expect_tamper:
            is_zeroized_ok = latest["hardware_zeroized"] and (latest["safe_data_out"] == "0x00")
        else:
            is_zeroized_ok = (not latest["hardware_zeroized"]) and (not latest["tamper_asserted"])

        test_ok = is_tamper_ok and is_verdict_ok and is_zeroized_ok
        if not test_ok:
            all_passed = False

        results_table.append({
            "code": code,
            "desc": desc,
            "cycles": latest["total_cycles"],
            "tamper": latest["tamper_asserted"],
            "tamper_cycle": latest["tamper_cycle"],
            "data_out": latest["safe_data_out"],
            "verdict": latest["verdict"],
            "signature": latest["signature_sha256"][:12] + "...",
            "pass": test_ok
        })

    # Stop background daemon threads
    receiver.stop()
    vchan.stop()

    # 4. Display Results Table
    print("\n" + "=" * 80)
    print(" HARDWARE DEMONSTRATOR EXECUTION AUDIT SUMMARY")
    print("=" * 80)
    print(f"{'Vector':<18} | {'Cycles':<6} | {'Tamper':<6} | {'Cycle#':<6} | {'Bus Out':<7} | {'Verdict':<20} | {'Status'}")
    print("-" * 80)

    for r in results_table:
        status_str = "PASS [OK]" if r["pass"] else "FAIL [X]"
        tamper_str = "YES" if r["tamper"] else "NO"
        cycle_str = str(r["tamper_cycle"]) if r["tamper_cycle"] is not None else "--"
        print(f"{r['code']:<18} | {r['cycles']:<6} | {tamper_str:<6} | {cycle_str:<6} | {r['data_out']:<7} | {r['verdict']:<20} | {status_str}")

    # 5. Cryptographic Evidence Chain Verification
    print("\n" + "=" * 80)
    print(" CRYPTOGRAPHIC EVIDENCE CHAIN AUDIT (SHA-256 BLOCKCHAIN)")
    print("=" * 80)

    with open(TEST_LEDGER_PATH, "r") as f:
        ledger_lines = [json.loads(line.strip()) for line in f if line.strip()]

    print(f"Total Block Records in Ledger: {len(ledger_lines)}")
    expected_prev = "0000000000000000000000000000000000000000000000000000000000000000"
    chain_valid = True

    for idx, entry in enumerate(ledger_lines):
        prev = entry["prev_hash"]
        sig = entry["signature_sha256"]

        # Recalculate hash over entry without signature
        entry_copy = dict(entry)
        del entry_copy["signature_sha256"]
        recomputed_hash = hashlib.sha256(json.dumps(entry_copy, sort_keys=True).encode("utf-8")).hexdigest()

        hash_matches = (recomputed_hash == sig)
        prev_matches = (prev == expected_prev)

        if not (hash_matches and prev_matches):
            chain_valid = False
            print(f" [CORRUPT] Block {idx} ({entry['attack_code']}): hash_matches={hash_matches}, prev_matches={prev_matches}")
        else:
            print(f" [VALID] Block #{idx:02d}: Tx={entry['transaction_id']} | Prev={prev[:10]}... | Sig={sig[:10]}... | {entry['attack_code']}")

        expected_prev = sig

    print("-" * 80)
    if chain_valid:
        print(" [RESULT] Cryptographic Ledger Integrity: 100% UNBROKEN & MATHEMATICALLY VERIFIED.")
    else:
        print(" [RESULT] Cryptographic Ledger Integrity: BROKEN HASH CHAIN!")
        all_passed = False

    print("=" * 80)
    if all_passed and chain_valid:
        print(" >>> MILESTONE M6 CYBER-PHYSICAL DEMONSTRATOR: FULL PASS & CLOSURE <<<")
        print("=" * 80)
        return 0
    else:
        print(" >>> MILESTONE M6 DEMONSTRATOR: VERIFICATION FAILED <<<")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(run_e2e_demonstration())
