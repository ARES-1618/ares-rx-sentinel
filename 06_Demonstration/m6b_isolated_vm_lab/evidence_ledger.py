#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Tamper-Evident SHA-256 Forensic Audit Ledger
Module: evidence_ledger.py
Milestone: M6-B (Isolated Cyber-Physical Demonstrator Lab)
Standard: FIPS 180-4 SHA-256 Hash Chain
Authority: Technical Architect / Research Direction

Purpose:
  Provides an immutable, tamper-evident forensic event ledger where each
  recorded security event cryptographically seals its payload and references
  the SHA-256 digest of the previous record.
================================================================================
"""

import os
import json
import time
import hashlib

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class TamperEvidentLedger:
    def __init__(self, ledger_path="m6b_evidence_ledger.jsonl"):
        self.ledger_path = ledger_path
        self.last_hash = GENESIS_HASH
        self.entry_count = 0
        self._initialize_or_verify()

    def _initialize_or_verify(self):
        """Verify unbroken chain if ledger file exists on disk."""
        if not os.path.exists(self.ledger_path):
            return

        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                expected_prev = record.get("prev_hash")
                if expected_prev != self.last_hash:
                    raise ValueError(
                        f"Tamper detected in ledger at line {line_idx}! "
                        f"Expected prev_hash: {self.last_hash}, found: {expected_prev}"
                    )
                # Compute record digest excluding 'record_hash'
                record_content = {k: v for k, v in record.items() if k != "record_hash"}
                computed_hash = hashlib.sha256(
                    json.dumps(record_content, sort_keys=True).encode("utf-8")
                ).hexdigest()

                if computed_hash != record.get("record_hash"):
                    raise ValueError(
                        f"Cryptographic corruption at line {line_idx}! "
                        f"Recorded hash: {record.get('record_hash')}, computed: {computed_hash}"
                    )

                self.last_hash = computed_hash
                self.entry_count += 1

    def append_event(self, event_type, attack_vector, status, hardware_metrics, run_id=None):
        """Append a new tamper-evident record with unbroken hash link."""
        record_content = {
            "index": self.entry_count,
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_id or "RUN-M6B-LOCAL",
            "event_type": event_type,
            "attack_vector": attack_vector,
            "status": status,
            "hardware_metrics": hardware_metrics,
            "prev_hash": self.last_hash
        }

        record_hash = hashlib.sha256(
            json.dumps(record_content, sort_keys=True).encode("utf-8")
        ).hexdigest()

        record_entry = dict(record_content)
        record_entry["record_hash"] = record_hash

        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record_entry) + "\n")

        self.last_hash = record_hash
        self.entry_count += 1
        return record_entry

    def verify_integrity(self):
        """Full audit check confirming mathematical unbrokenness of the chain."""
        if not os.path.exists(self.ledger_path):
            return True, 0, GENESIS_HASH

        current_prev = GENESIS_HASH
        count = 0
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if r["prev_hash"] != current_prev:
                    return False, idx, f"Broken link at {idx}"
                content = {k: v for k, v in r.items() if k != "record_hash"}
                c_hash = hashlib.sha256(json.dumps(content, sort_keys=True).encode("utf-8")).hexdigest()
                if c_hash != r["record_hash"]:
                    return False, idx, f"Hash mismatch at {idx}"
                current_prev = c_hash
                count += 1
        return True, count, current_prev
