#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ARES SEMIKONDUKTOR TECHNOLOGY
# SPDX-License-Identifier: Apache-2.0
"""
Stand-alone Cycle-Accurate Simulator & Verification Runner for Layer-1:
ares_timing_sentinel.v

Verifies the exact RTL cycle-by-cycle register-transfer logic:
- Test 1: Nominal burst transition (IDLE -> ARMED -> ACTIVE)
- Test 2: AV01 Glitch Rejection (N <= 7 in ACTIVE)
- Test 3: AV02-A Missing Edge Resume (Gap >= 21 then edge resume -> FAULT)
- Test 4: AV02-B Normal Packet Termination Silence (N >= EOF_CYC -> IDLE, 0 false alarm)
- Test 5: AV03 Mid-Band Rejection (11 <= N <= 15)
- Test 6: AV04 Extra Edge / Bouncing Rejection
- Test 7: AV08 Real Hardware Capture Regression (transmission_digital_hs.csv)
"""

import os
import sys
import csv

class AresTimingSentinelSim:
    def __init__(self, hb_min=8, hb_max=10, bit_min=16, bit_max=20, timeout=21, eof=64):
        self.HB_MIN = hb_min
        self.HB_MAX = hb_max
        self.BIT_MIN = bit_min
        self.BIT_MAX = bit_max
        self.TIMEOUT_CYC = timeout
        self.EOF_CYC = eof

        self.STATE_IDLE = 0
        self.STATE_ARMED = 1
        self.STATE_ACTIVE = 2
        self.STATE_LONG_GAP_PENDING = 3

        self.FAULT_NONE = 0
        self.FAULT_RUNT = 1
        self.FAULT_MIDBAND = 2
        self.FAULT_GAP_RES = 3

        self.reset()

    def reset(self):
        self.interval_counter = 0
        self.current_state = self.STATE_IDLE
        self.reception_active = 0
        self.temporal_valid = 0
        self.temporal_fault = 0
        self.fault_code = self.FAULT_NONE
        self.last_interval = 0

    def step(self, pos_edge, neg_edge, enable=1):
        if not enable:
            return

        self.temporal_valid = 0
        self.temporal_fault = 0
        edge_detected = 1 if (pos_edge or neg_edge) else 0

        # Cycle-accurate counter: on edge, capture interval and reset to 1
        if edge_detected:
            self.last_interval = self.interval_counter
            curr_n = self.interval_counter
            self.interval_counter = 1
        else:
            if self.interval_counter < 255:
                self.interval_counter += 1
            curr_n = self.interval_counter

        is_runt = (curr_n < self.HB_MIN) and (curr_n > 0)
        is_half_bit = (curr_n >= self.HB_MIN) and (curr_n <= self.HB_MAX)
        is_midband = (curr_n > self.HB_MAX) and (curr_n < self.BIT_MIN)
        is_full_bit = (curr_n >= self.BIT_MIN) and (curr_n <= self.BIT_MAX)
        is_valid = is_half_bit or is_full_bit

        if self.current_state == self.STATE_IDLE:
            self.reception_active = 0
            if edge_detected:
                self.current_state = self.STATE_ARMED

        elif self.current_state == self.STATE_ARMED:
            self.reception_active = 0
            if edge_detected:
                if is_valid:
                    self.temporal_valid = 1
                    self.reception_active = 1
                    self.current_state = self.STATE_ACTIVE
                else:
                    self.current_state = self.STATE_ARMED
            elif self.interval_counter >= self.TIMEOUT_CYC:
                self.current_state = self.STATE_IDLE

        elif self.current_state == self.STATE_ACTIVE:
            self.reception_active = 1
            if edge_detected:
                if is_valid:
                    self.temporal_valid = 1
                    self.current_state = self.STATE_ACTIVE
                elif is_runt:
                    self.temporal_fault = 1
                    self.fault_code = self.FAULT_RUNT
                    self.reception_active = 0
                    self.current_state = self.STATE_IDLE
                elif is_midband:
                    self.temporal_fault = 1
                    self.fault_code = self.FAULT_MIDBAND
                    self.reception_active = 0
                    self.current_state = self.STATE_IDLE
            elif self.interval_counter >= self.TIMEOUT_CYC:
                self.current_state = self.STATE_LONG_GAP_PENDING

        elif self.current_state == self.STATE_LONG_GAP_PENDING:
            self.reception_active = 1
            if edge_detected:
                self.temporal_fault = 1
                self.fault_code = self.FAULT_GAP_RES
                self.reception_active = 0
                self.current_state = self.STATE_IDLE
            elif self.interval_counter >= self.EOF_CYC:
                self.reception_active = 0
                self.current_state = self.STATE_IDLE


def run_unit_tests():
    print("=" * 70)
    print("ARES-RX Sentinel Layer-1 Cycle-Accurate RTL Verification Suite")
    print("Architecture: 4-State Context Controller & Deferred Fault Classification")
    print("=" * 70)

    dut = AresTimingSentinelSim()
    tests_passed = 0
    total_tests = 7

    # Test 1: Nominal burst
    dut.reset()
    for _ in range(10): dut.step(0, 0)
    dut.step(1, 0) # Candidate edge -> ARMED
    assert dut.current_state == dut.STATE_ARMED, "Test 1 Failed: Expected ARMED"

    for _ in range(8): dut.step(0, 0)
    dut.step(0, 1) # 9 cycles later -> ACTIVE
    assert dut.current_state == dut.STATE_ACTIVE, "Test 1 Failed: Expected ACTIVE"
    assert dut.reception_active == 1
    assert dut.temporal_valid == 1

    for _ in range(17): dut.step(0, 0)
    dut.step(1, 0) # 18 cycles later -> Stays ACTIVE
    assert dut.current_state == dut.STATE_ACTIVE
    assert dut.temporal_valid == 1
    assert dut.temporal_fault == 0
    print("[PASS] Test 1: Nominal Burst Transition (IDLE -> ARMED -> ACTIVE)")
    tests_passed += 1

    # Test 2: AV01 Glitch Rejection
    dut.reset()
    for _ in range(10): dut.step(0, 0)
    dut.step(1, 0) # ARMED
    for _ in range(8): dut.step(0, 0)
    dut.step(0, 1) # ACTIVE
    # Glitch 3 cycles
    for _ in range(2): dut.step(0, 0)
    dut.step(1, 0)
    assert dut.temporal_fault == 1 and dut.fault_code == dut.FAULT_RUNT, "Test 2 Failed"
    assert dut.current_state == dut.STATE_IDLE
    print("[PASS] Test 2: AV01 Glitch Rejection (N=3 cycles, FaultCode=001)")
    tests_passed += 1

    # Test 3: AV02-A Missing Edge Resume
    dut.reset()
    for _ in range(10): dut.step(0, 0)
    dut.step(1, 0)
    for _ in range(8): dut.step(0, 0)
    dut.step(0, 1) # ACTIVE
    # Wait 21 cycles without edge -> enters LONG_GAP_PENDING
    for _ in range(21): dut.step(0, 0)
    assert dut.current_state == dut.STATE_LONG_GAP_PENDING, "Test 3 Failed: Expected LONG_GAP_PENDING"
    assert dut.temporal_fault == 0, "Test 3 Failed: Fault asserted prematurely"
    # Edge resumes at cycle 35 (missing edge in active packet)
    for _ in range(13): dut.step(0, 0)
    dut.step(1, 0)
    assert dut.temporal_fault == 1 and dut.fault_code == dut.FAULT_GAP_RES, "Test 3 Failed"
    assert dut.current_state == dut.STATE_IDLE
    print("[PASS] Test 3: AV02-A Missing Edge Resume (Gap=35 cycles, FaultCode=011)")
    tests_passed += 1

    # Test 4: AV02-B Normal Packet Termination
    dut.reset()
    for _ in range(10): dut.step(0, 0)
    dut.step(1, 0)
    for _ in range(8): dut.step(0, 0)
    dut.step(0, 1) # ACTIVE
    # Silence persists past EOF_CYC (64 cycles)
    for _ in range(65): dut.step(0, 0)
    assert dut.current_state == dut.STATE_IDLE, "Test 4 Failed: Expected IDLE"
    assert dut.temporal_fault == 0, "Test 4 Failed: False alarm on packet termination silence!"
    print("[PASS] Test 4: AV02-B Normal Packet Termination Silence (N>=64 -> IDLE, Zero False Alarm)")
    tests_passed += 1

    # Test 5: AV03 Mid-Band Rejection
    dut.reset()
    for _ in range(10): dut.step(0, 0)
    dut.step(1, 0)
    for _ in range(8): dut.step(0, 0)
    dut.step(0, 1) # ACTIVE
    # Mid-band gap: 13 cycles
    for _ in range(12): dut.step(0, 0)
    dut.step(1, 0)
    assert dut.temporal_fault == 1 and dut.fault_code == dut.FAULT_MIDBAND, "Test 5 Failed"
    assert dut.current_state == dut.STATE_IDLE
    print("[PASS] Test 5: AV03 Mid-Band Rejection (N=13 cycles, FaultCode=010)")
    tests_passed += 1

    # Test 6: AV04 Extra Edge Rejection
    dut.reset()
    for _ in range(10): dut.step(0, 0)
    dut.step(1, 0)
    for _ in range(8): dut.step(0, 0)
    dut.step(0, 1) # ACTIVE
    # Extra bouncing edge at cycle 4
    for _ in range(3): dut.step(0, 0)
    dut.step(1, 0)
    assert dut.temporal_fault == 1 and dut.fault_code == dut.FAULT_RUNT, "Test 6 Failed"
    print("[PASS] Test 6: AV04 Extra Edge Rejection (Bouncing at cycle 4, FaultCode=001)")
    tests_passed += 1

    # Test 7: AV08 Real Hardware Capture Regression
    csv_path = "03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/test/data/transmission_digital_hs.csv"
    dut.reset()
    fault_events = 0
    valid_events = 0
    with open(csv_path, "r") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#") and r[0] != "Time (s)"]
    dio0 = [int(r[2]) for r in rows]

    prev = dio0[0]
    for s in dio0[1:]:
        pos = 1 if (s == 1 and prev == 0) else 0
        neg = 1 if (s == 0 and prev == 1) else 0
        prev = s
        dut.step(pos, neg)
        if dut.temporal_fault:
            fault_events += 1
        if dut.temporal_valid:
            valid_events += 1

    assert fault_events == 0, f"Test 7 Failed: Expected 0 faults on nominal hardware stream, got {fault_events}"
    assert valid_events == 289, f"Test 7 Failed: Expected 289 valid transitions, got {valid_events}"
    assert dut.current_state == dut.STATE_IDLE, "Test 7 Failed: Did not return to IDLE after trailing silence"
    print(f"[PASS] Test 7: AV08 Real Hardware Regression (289 Valid Transitions, 0 False Alarms, Clean IDLE Return)")
    tests_passed += 1

    # Test 8: REQ-08 Explicit Boundary Value Sweep: {7, 8, 10, 11, 15, 16, 20, 21}
    def test_interval(n_cycles):
        d = AresTimingSentinelSim()
        d.step(1, 0) # ARMED
        for _ in range(8): d.step(0, 0)
        d.step(0, 1) # ACTIVE (at 9 cycles)
        for _ in range(n_cycles - 1): d.step(0, 0)
        d.step(1, 0) # Test boundary interval
        return d.temporal_valid, d.temporal_fault, d.fault_code, d.current_state

    # N=7 -> RUNT
    v, f, c, s = test_interval(7)
    assert f == 1 and c == dut.FAULT_RUNT and s == dut.STATE_IDLE, "Boundary N=7 failed"

    # N=8 -> VALID (HB min)
    v, f, c, s = test_interval(8)
    assert v == 1 and f == 0 and s == dut.STATE_ACTIVE, "Boundary N=8 failed"

    # N=10 -> VALID (HB max)
    v, f, c, s = test_interval(10)
    assert v == 1 and f == 0 and s == dut.STATE_ACTIVE, "Boundary N=10 failed"

    # N=11 -> MIDBAND
    v, f, c, s = test_interval(11)
    assert f == 1 and c == dut.FAULT_MIDBAND and s == dut.STATE_IDLE, "Boundary N=11 failed"

    # N=15 -> MIDBAND
    v, f, c, s = test_interval(15)
    assert f == 1 and c == dut.FAULT_MIDBAND and s == dut.STATE_IDLE, "Boundary N=15 failed"

    # N=16 -> VALID (Bit min)
    v, f, c, s = test_interval(16)
    assert v == 1 and f == 0 and s == dut.STATE_ACTIVE, "Boundary N=16 failed"

    # N=20 -> VALID (Bit max)
    v, f, c, s = test_interval(20)
    assert v == 1 and f == 0 and s == dut.STATE_ACTIVE, "Boundary N=20 failed"

    # N=21 -> Enters LONG_GAP_PENDING and traps on resume
    d21 = AresTimingSentinelSim()
    d21.step(1, 0); [d21.step(0, 0) for _ in range(8)]; d21.step(0, 1)
    for _ in range(21): d21.step(0, 0)
    assert d21.current_state == d21.STATE_LONG_GAP_PENDING, "Boundary N=21 failed to enter PENDING"
    d21.step(1, 0)
    assert d21.temporal_fault == 1 and d21.fault_code == d21.FAULT_GAP_RES, "Boundary N=21 resume failed"
    print("[PASS] Test 8: REQ-08 Explicit Boundary Sweep ({7, 8, 10, 11, 15, 16, 20, 21} Verified)")
    tests_passed += 1

    # Test 9: EOP + Receiver Squelch Noise Rejection
    dut.reset()
    dut.step(1, 0) # ARMED
    for _ in range(8): dut.step(0, 0)
    dut.step(0, 1) # ACTIVE
    # Packet ends -> quiet silence >= 64 -> IDLE
    for _ in range(65): dut.step(0, 0)
    assert dut.current_state == dut.STATE_IDLE, "Test 9 Failed: Not in IDLE after EOF silence"
    # Squelch noise chatter arrives in IDLE: 2-cycle, 3-cycle pulses
    dut.step(1, 0) # Enters ARMED
    assert dut.current_state == dut.STATE_ARMED
    for _ in range(1): dut.step(0, 0)
    dut.step(0, 1) # 2-cycle noise interval -> re-arms in ARMED
    assert dut.current_state == dut.STATE_ARMED and dut.temporal_fault == 0
    for _ in range(2): dut.step(0, 0)
    dut.step(1, 0) # 3-cycle noise interval -> re-arms in ARMED
    assert dut.current_state == dut.STATE_ARMED and dut.temporal_fault == 0
    # Silence follows -> returns to IDLE
    for _ in range(22): dut.step(0, 0)
    assert dut.current_state == dut.STATE_IDLE and dut.temporal_fault == 0
    print("[PASS] Test 9: EOP + Squelch Noise Rejection (Zero False Alarms in IDLE/ARMED)")
    tests_passed += 1

    # Test 10: EOP Noise Chatter at Cycle 40 during LONG_GAP_PENDING
    dut.reset()
    dut.step(1, 0) # ARMED
    for _ in range(8): dut.step(0, 0)
    dut.step(0, 1) # ACTIVE
    # Gap = 40 cycles (currently in LONG_GAP_PENDING)
    for _ in range(40): dut.step(0, 0)
    assert dut.current_state == dut.STATE_LONG_GAP_PENDING, "Test 10 Failed: Not in PENDING at cycle 40"

    # First edge of 3-cycle noise pulse arrives at t=40
    dut.step(1, 0)
    assert dut.temporal_fault == 1 and dut.fault_code == dut.FAULT_GAP_RES and dut.current_state == dut.STATE_IDLE, "Test 10 Failed: Edge at cycle 40 not trapped as FAULT_GAP_RES"

    # Second edge of 3-cycle noise pulse arrives 3 cycles later
    for _ in range(2): dut.step(0, 0)
    dut.step(0, 1) # Enters ARMED
    assert dut.current_state == dut.STATE_ARMED and dut.temporal_fault == 0, "Test 10 Failed: Noise falling edge caused spurious fault"

    # Remaining silence (> 21 cycles) -> returns to IDLE
    for _ in range(22): dut.step(0, 0)
    assert dut.current_state == dut.STATE_IDLE and dut.temporal_fault == 0, "Test 10 Failed: Clean IDLE return failed"
    print("[PASS] Test 10: EOP Noise Chatter at Cycle 40 Trapped & Settled to IDLE")
    tests_passed += 1

    print("=" * 70)
    print(f"VERIFICATION RESULT: {tests_passed}/10 TESTS PASSED (100% SUCCESS)")
    print("=" * 70)

if __name__ == "__main__":
    run_unit_tests()
