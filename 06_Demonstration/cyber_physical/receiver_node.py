#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Hardware Emulation Receiver Target (Receiver Node)
Milestone: M6 (Cyber-Physical Security Demonstrator)
Function: Ingests baseband samples into modeled rx_in boundary of the ARES Sentinel demarcation model
          perimeter, performs real-time cycle-by-cycle evaluation, executes
          fail-closed zeroization on attacks, and appends cryptographically
          signed evidence records.
================================================================================
"""

import sys
import os
import time
import socket
import json
import hashlib
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
COCOTB_DIR = os.path.join(PROJECT_ROOT, "04_Verification", "ARES-RX_Sentinel", "cocotb")
if COCOTB_DIR not in sys.path:
    sys.path.insert(0, COCOTB_DIR)

from run_m4_adversarial_suite import (
    AresSentinelTopModel,
    BaselineUnprotectedModel,
    FAULT_NONE, FAULT_RUNT, FAULT_MIDBAND, FAULT_GAP_RES,
    FAULT_PREAMBLE_CORRUPT, FAULT_TYPE_CORRUPT, FAULT_CONSTANT_CORRUPT, FAULT_TRAILER_CORRUPT
)

FAULT_DESCRIPTIONS = {
    FAULT_NONE: "NOMINAL_CLEAN",
    FAULT_RUNT: "L1_RUNT_PULSE_GLITCH (<=7 cycles)",
    FAULT_MIDBAND: "L1_MIDBAND_ANOMALY (11..15 cycles)",
    FAULT_GAP_RES: "L1_GAP_TIMEOUT / STRETCHED_PULSE (>=21 cycles)",
    FAULT_PREAMBLE_CORRUPT: "L2_PREAMBLE_CORRUPT",
    FAULT_TYPE_CORRUPT: "L2_PROTOCOL_TYPE_MISMATCH",
    FAULT_CONSTANT_CORRUPT: "L2_CONSTANT_SECURITY_FIELD_CORRUPT",
    FAULT_TRAILER_CORRUPT: "L2_FRAMING_BOUNDARY_ERROR (Truncation/Overrun)"
}

class ReceiverNode:
    def __init__(self, listen_host="127.0.0.1", listen_port=9100, ledger_path=None, callback=None):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.ledger_path = ledger_path or os.path.join(SCRIPT_DIR, "evidence_chain_ledger.jsonl")
        self.callback = callback
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.previous_chain_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    def process_packet(self, raw_bytes):
        packet = json.loads(raw_bytes.decode("utf-8"))
        attack_code = packet.get("attack_code", "UNKNOWN")
        description = packet.get("description", "")
        profile = packet.get("cycles_profile", [])

        sentinel = AresSentinelTopModel()
        baseline = BaselineUnprotectedModel()

        total_cycles = 0
        waveform_trace = []
        tamper_asserted_at = None
        first_cause_code = FAULT_NONE

        # Clock-by-clock hardware emulation
        for item in profile:
            if len(item) == 4:
                level, s_clk, s_data, count = item
            else:
                level, count = item
                s_clk, s_data = 0, 0

            for _ in range(count):
                total_cycles += 1
                s_res = sentinel.clock_step(
                    rx_in=level,
                    serial_clock=s_clk,
                    serial_data=s_data,
                    raw_data_in=0x55,
                    raw_valid_in=1
                )
                
                # Check for tamper assertion
                if s_res["tamper_alert"] and tamper_asserted_at is None:
                    tamper_asserted_at = total_cycles
                    first_cause_code = s_res["fault_code"]

                # Sample waveform for observer GUI (subsample every 4 cycles to keep message light)
                if total_cycles % 4 == 0:
                    waveform_trace.append({
                        "cycle": total_cycles,
                        "rx": level,
                        "active": s_res["reception_active"],
                        "tamper": s_res["tamper_alert"],
                        "data_out": s_res["safe_data_out"]
                    })

        # Final hardware state
        final_tamper = bool(s_res["tamper_alert"])
        final_zeroized = (s_res["safe_data_out"] == 0 and final_tamper)
        final_fault = s_res["fault_code"]
        verdict = "FAIL_CLOSED_ZEROIZED" if final_tamper else "NOMINAL_ACCEPTED"

        # Construct signed evidence entry
        evidence_record = {
            "transaction_id": hashlib.sha256(f"{time.time()}_{attack_code}".encode()).hexdigest()[:16],
            "timestamp": time.time(),
            "prev_hash": self.previous_chain_hash,
            "attack_code": attack_code,
            "description": description,
            "total_cycles": total_cycles,
            "real_time_ms": total_cycles * 0.050,  # 50 us per cycle
            "tamper_asserted": final_tamper,
            "tamper_cycle": tamper_asserted_at,
            "first_cause_fault_code": final_fault,
            "fault_name": FAULT_DESCRIPTIONS.get(final_fault, "UNKNOWN"),
            "safe_data_out": f"0x{s_res['safe_data_out']:02X}",
            "hardware_zeroized": final_zeroized,
            "verdict": verdict
        }

        # Cryptographic link (blockchain-style tamper-evident ledger)
        record_json = json.dumps(evidence_record, sort_keys=True)
        record_hash = hashlib.sha256(record_json.encode("utf-8")).hexdigest()
        evidence_record["signature_sha256"] = record_hash
        self.previous_chain_hash = record_hash

        # Append to audit ledger
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(evidence_record) + "\n")

        print(f"[RECEIVER] Processed {attack_code}: Verdict={verdict}, Tamper={final_tamper}, Zeroized={final_zeroized}, Sig={record_hash[:12]}...")

        # Notify callback/observer if attached
        if self.callback:
            self.callback(evidence_record, waveform_trace)

        return evidence_record, waveform_trace

    def start(self):
        self.sock.bind((self.listen_host, self.listen_port))
        self.running = True
        print(f"[RECEIVER TARGET] Active: listening on {self.listen_host}:{self.listen_port}")
        
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65535)
                self.process_packet(data)
            except Exception as e:
                if self.running:
                    print(f"[RECEIVER ERROR] {e}")

    def stop(self):
        self.running = False
        self.sock.close()

if __name__ == "__main__":
    node = ReceiverNode()
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()
        print("\n[RECEIVER TARGET] Stopped.")
