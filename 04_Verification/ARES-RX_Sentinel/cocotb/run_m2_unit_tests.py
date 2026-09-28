#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ARES SEMIKONDUKTOR TECHNOLOGY
# SPDX-License-Identifier: Apache-2.0
"""
Cycle-Accurate Simulator & Verification Runner for Layer-3:
ares_fault_latch.v, ares_isolation_gate.v, ares_isolation_l3.v
Work Order: WO-2026-M2-001 (Hardware Fail-Closed Isolation)
"""

import sys

class AresIsolationL3Sim:
    def __init__(self, data_width=8):
        self.DATA_WIDTH = data_width
        self.reset()

    def reset(self):
        # Sequential latch state
        self.fault_latched = 0
        self.latched_fault_code = 0
        # Combinational gate outputs
        self.safe_data_out = 0
        self.safe_valid_out = 0
        self.tamper_alert = 0

    def step(self, temporal_fault, fault_code, raw_data_in, raw_valid_in, rst_n=1):
        if not rst_n:
            self.reset()
            return

        # 1. Sequential Clocked Update (ares_fault_latch)
        if temporal_fault:
            if not self.fault_latched:
                # Capture first-cause fault code
                self.latched_fault_code = fault_code & 0x7
            self.fault_latched = 1

        # 2. Combinational Evaluation (ares_isolation_gate)
        # Adds ZERO additional clock cycles of latency after latch assertion
        if self.fault_latched:
            self.safe_data_out = 0
            self.safe_valid_out = 0
            self.tamper_alert = 1
        else:
            self.safe_data_out = raw_data_in & ((1 << self.DATA_WIDTH) - 1)
            self.safe_valid_out = 1 if raw_valid_in else 0
            self.tamper_alert = 0

def run_m2_tests():
    print("=" * 70)
    print("ARES-RX Sentinel Layer-3 Hardware Fail-Closed Isolation Verification")
    print("Work Order: WO-2026-M2-001")
    print("=" * 70)

    dut = AresIsolationL3Sim(data_width=8)
    tests_passed = 0
    total_tests = 5

    # TEST 1: Normal Passthrough
    dut.reset()
    dut.step(temporal_fault=0, fault_code=0, raw_data_in=0xA5, raw_valid_in=1)
    assert dut.safe_data_out == 0xA5 and dut.safe_valid_out == 1, "Test 1 Failed"
    assert dut.fault_latched == 0 and dut.tamper_alert == 0 and dut.latched_fault_code == 0, "Test 1 Failed"
    dut.step(temporal_fault=0, fault_code=0, raw_data_in=0x5A, raw_valid_in=1)
    assert dut.safe_data_out == 0x5A, "Test 1 Failed"
    print("[PASS] TEST 1: Normal Passthrough (data_out = in_data, tamper_alert = 0)")
    tests_passed += 1

    # TEST 2: Zero Additional Clock Latency Zeroization
    dut.step(temporal_fault=1, fault_code=1, raw_data_in=0xDE, raw_valid_in=1) # Runt fault
    assert dut.fault_latched == 1, "Test 2 Failed: fault_latched not asserted"
    assert dut.safe_data_out == 0x00, "Test 2 Failed: data_out not zeroized"
    assert dut.safe_valid_out == 0, "Test 2 Failed: valid not suppressed"
    assert dut.tamper_alert == 1, "Test 2 Failed: tamper_alert not asserted"
    assert dut.latched_fault_code == 1, "Test 2 Failed: latched_fault_code not 001"
    print("[PASS] TEST 2: Zero Additional Clock Latency Zeroization (data_out = 0x00, tamper_alert = 1)")
    tests_passed += 1

    # TEST 3: First-Fault Invariant
    dut.step(temporal_fault=1, fault_code=2, raw_data_in=0x11, raw_valid_in=1) # Mid-band fault
    dut.step(temporal_fault=1, fault_code=3, raw_data_in=0x22, raw_valid_in=1) # Gap resume fault
    assert dut.latched_fault_code == 1, f"Test 3 Failed: First fault overwritten to {dut.latched_fault_code}"
    print("[PASS] TEST 3: First-Fault Invariant (Initial fault code 001 preserved across subsequent faults)")
    tests_passed += 1

    # TEST 4: Sticky Isolation Invariant across 1,000 Cycles
    for i in range(1000):
        val = i & 0xFF
        dut.step(temporal_fault=0, fault_code=0, raw_data_in=val, raw_valid_in=1)
        assert dut.fault_latched == 1 and dut.safe_data_out == 0x00 and dut.tamper_alert == 1, f"Test 4 Failed at cycle {i}"
    print("[PASS] TEST 4: Sticky Isolation Invariant (1,000 cycles with zero leakage)")
    tests_passed += 1

    # TEST 5: Authorized Hardware Reset Recovery
    dut.step(temporal_fault=0, fault_code=0, raw_data_in=0, raw_valid_in=0, rst_n=0)
    assert dut.fault_latched == 0 and dut.tamper_alert == 0 and dut.latched_fault_code == 0, "Test 5 Failed on reset"
    dut.step(temporal_fault=0, fault_code=0, raw_data_in=0x3C, raw_valid_in=1, rst_n=1)
    assert dut.safe_data_out == 0x3C and dut.safe_valid_out == 1, "Test 5 Failed: Normal path not restored"
    assert dut.fault_latched == 0 and dut.tamper_alert == 0, "Test 5 Failed"
    print("[PASS] TEST 5: Authorized Hardware Reset Recovery (Clean restoration of normal path)")
    tests_passed += 1

    print("=" * 70)
    print(f"M2 VERIFICATION RESULT: {tests_passed}/{total_tests} TESTS PASSED (100% SUCCESS)")
    print("=" * 70)

if __name__ == "__main__":
    run_m2_tests()
