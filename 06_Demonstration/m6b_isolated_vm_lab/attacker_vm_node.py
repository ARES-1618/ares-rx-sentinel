#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Milestone M6-B Attacker Namespace Node
Module: attacker_vm_node.py
Target IP: 192.168.100.20:9100 (Linux Network Namespace Security Lab: ns_receiver)
Work Order: WO-2026-M6-ARCH-011: Final Causal Evidence Run & Timing Reconciliation
Authority: Technical Architect / Research Direction

Purpose:
  Simulates a compromised/adversarial Sub-GHz RF transmitter inside an isolated
  network domain (ns_attacker). Emits canonical attack vectors AV00..AV08 sourced
  strictly from the authoritative single canonical vector manifest.
================================================================================
"""

import sys
import os
import time
import socket
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CYBER_DIR = os.path.join(PROJECT_ROOT, "06_Demonstration", "cyber_physical")
if CYBER_DIR not in sys.path:
    sys.path.insert(0, CYBER_DIR)

from canonical_vector_loader import get_canonical_vector

class AttackerNode:
    def __init__(self, target_host="192.168.100.20", target_port=9100, run_id=None):
        self.target_host = target_host
        self.target_port = target_port
        self.run_id = run_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def generate_scenario(self, attack_code):
        vec = get_canonical_vector(attack_code)
        return {
            "run_id": self.run_id,
            "attack_code": vec["id"],
            "vector_name": vec["name"],
            "category": vec["category"],
            "description": vec["description"],
            "cycles_profile": vec["cycles_profile"],
            "stimulus_sha256": vec["vector_stimulus_sha256"]
        }

    def send_vector(self, attack_code):
        scenario = self.generate_scenario(attack_code)
        # Capture high-resolution timestamp immediately prior to transmission
        scenario["tx_timestamp"] = time.time()
        payload = json.dumps(scenario, separators=(',', ':')).encode("utf-8")
        self.sock.sendto(payload, (self.target_host, self.target_port))
        print(f"[Attacker Node] Emitted vector {attack_code} -> {self.target_host}:{self.target_port} ({len(payload)} bytes)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARES-RX M6-B Attacker Namespace Node")
    parser.add_argument("--target", default="192.168.100.20", help="Target receiver IP")
    parser.add_argument("--port", type=int, default=9100, help="Target receiver port")
    parser.add_argument("--vector", default="AV00", help="Vector code (AV00..AV08)")
    parser.add_argument("--run-id", default=None, help="Authoritative Run ID")
    args = parser.parse_args()

    node = AttackerNode(args.target, args.port, run_id=args.run_id)
    node.send_vector(args.vector)
