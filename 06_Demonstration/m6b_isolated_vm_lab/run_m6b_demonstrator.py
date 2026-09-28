#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Milestone M6-B Demonstrator Test Runner & Audit Verifier
Module: run_m6b_demonstrator.py
Authority: Technical Architect / Research Direction

Purpose:
  Executes end-to-end evaluation across canonical vectors AV00..AV08 against
  the ARES demarcation boundary in local UDP loopback mode, logs transitions
  to the tamper-evident SHA-256 hash-chain ledger, and mathematically verifies
  unbroken cryptographic linkage.

  Note: For full Linux Kernel Network Namespace isolation (ns_attacker <-> ns_receiver
  via veth + bridge + netem), execute `run_netns_test.sh`.
================================================================================
"""

import sys
import os
import time
import json
import hashlib
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
from attacker_vm_node import AttackerNode
from receiver_vm_node import ReceiverNode

def run_evaluation():
    ledger_path = os.path.join(SCRIPT_DIR, "m6b_test_ledger.jsonl")
    if os.path.exists(ledger_path):
        os.remove(ledger_path)

    test_port = 9188
    receiver = ReceiverNode(host="127.0.0.1", port=test_port, ledger_path=ledger_path)
    
    stop_event = threading.Event()
    def receiver_loop():
        receiver.sock.settimeout(0.5)
        while not stop_event.is_set():
            try:
                data, addr = receiver.sock.recvfrom(65535)
                receiver.process_packet(data, addr)
            except Exception:
                pass
        receiver.sock.close()

    t = threading.Thread(target=receiver_loop, daemon=True)
    t.start()
    time.sleep(0.1)

    attacker = AttackerNode(target_host="127.0.0.1", target_port=test_port)

    vectors = ["AV00", "AV01", "AV02", "AV03", "AV04", "AV05", "AV06", "AV07", "AV08"]
    print("=" * 125)
    print(" ARES-RX SENTINEL: MILESTONE M6-B DEMONSTRATOR EVALUATION MATRIX (CANONICAL VECTORS AV00-AV08)")
    print("=" * 125)
    print(f"{'Vector':<6} | {'Category':<24} | {'Stimulus Hash':<18} | {'Fault Name':<22} | {'Detect':<8} | {'Isolate':<8} | {'Bus':<6} | Status")
    print("-" * 125)

    for code in vectors:
        attacker.send_vector(code)
        time.sleep(0.05)

    stop_event.set()
    t.join(timeout=1.0)

    # Read back and audit ledger entries
    records = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    # Verify cryptographic hash chain
    chain_valid = True
    prev = "0000000000000000000000000000000000000000000000000000000000000000"
    for r in records:
        if r["previous_hash"] != prev:
            chain_valid = False
            break
        body = json.dumps(r["payload"], sort_keys=True, separators=(',', ':'))
        computed = hashlib.sha256((prev + body).encode('utf-8')).hexdigest()
        if computed != r["record_hash"]:
            chain_valid = False
            break
        prev = r["record_hash"]

    for r in records:
        p = r["payload"]
        hw = p["hardware_evaluation"]
        iso = p["isolation_response"]
        stim_disp = p["stimulus_hash"][:8] + "..." + p["stimulus_hash"][-6:]
        det_disp = str(hw["detection_cycle"]) if hw["detection_cycle"] is not None else "N/A"
        iso_disp = f"{iso['isolation_latency_cycles']} cyc" if hw["tamper_alert"] else "N/A"
        print(f"{p['vector_id']:<6} | {p['category']:<24} | {stim_disp:<18} | {hw['fault_name']:<22} | {det_disp:<8} | {iso_disp:<8} | {iso['safe_bus_output']:<6} | {hw['status']}")

    print("=" * 125)
    print(f"[AUDIT] Tamper-Evident SHA-256 Hash Chain: {'UNBROKEN / VALID' if chain_valid else 'CORRUPTED'}")
    print(f"        Total Sealed Events: {len(records)}")
    print(f"        Final Cryptographic Anchor: {records[-1]['record_hash']}")
    print("=" * 125)

    # Contract Assertions
    assert len(records) == 9, f"Expected 9 records, got {len(records)}"
    assert chain_valid, "Cryptographic hash chain failed verification!"
    assert records[0]["payload"]["hardware_evaluation"]["tamper_alert"] == 0, "AV00 nominal false alarm!"
    assert records[0]["payload"]["isolation_response"]["safe_bus_output"] == "0x55", "AV00 bus corrupted!"

    for r in records[1:]:
        p = r["payload"]
        assert p["hardware_evaluation"]["tamper_alert"] == 1, f"Vector {p['vector_id']} failed to tamper!"
        assert p["isolation_response"]["safe_bus_output"] == "0x00", f"Vector {p['vector_id']} failed to zeroize!"
        assert p["isolation_response"]["isolation_latency_cycles"] == 1, f"Vector {p['vector_id']} isolation latency violated!"

    print("[SUCCESS] 100% mitigation verified across canonical AV00-AV08 demonstrator vectors.")
    print("          Safe-output isolation propagates within one system cycle after fault assertion.")

if __name__ == "__main__":
    run_evaluation()
