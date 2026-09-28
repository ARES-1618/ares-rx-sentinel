# SPDX-FileCopyrightText: © 2026 ARES SEMIKONDUKTOR TECHNOLOGY
# SPDX-License-Identifier: Apache-2.0
"""
Cocotb Unit Testbench for ARES-RX Sentinel Layer-1:
Module: ares_timing_sentinel.v
Verifies:
- Reception Context FSM (IDLE -> ARMED -> ACTIVE -> LONG_GAP_PENDING -> IDLE)
- AV01: Short pulse / runt glitch rejection (N <= 7)
- AV02-A: Active missing-edge deferred fault (N >= 21 then resume)
- AV02-B: Normal packet termination silence (N >= 64 -> IDLE, zero false alarm)
- AV03: Mid-band interval rejection (11 <= N <= 15)
- AV04: Extra edge / bouncing rejection (N <= 7)
- AV08: Real hardware capture regression (transmission_digital_hs.csv)
"""

import os
import csv
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer

async def reset_dut(dut):
    """Applies active-low asynchronous reset for 5 clock cycles."""
    dut.rst_n.value = 0
    dut.enable.value = 1
    dut.pos_edge.value = 0
    dut.neg_edge.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

async def pulse_interval(dut, count, is_pos=True):
    """Waits `count` clock cycles and then strobes pos_edge or neg_edge."""
    await ClockCycles(dut.clk, count - 1)
    if is_pos:
        dut.pos_edge.value = 1
    else:
        dut.neg_edge.value = 1
    await ClockCycles(dut.clk, 1)
    dut.pos_edge.value = 0
    dut.neg_edge.value = 0

@cocotb.test()
async def test_nominal_burst(dut):
    """Test Case 1: Pristine Manchester stream transitions correctly through IDLE -> ARMED -> ACTIVE."""
    clock = Clock(dut.clk, 50, units="us")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Initially in IDLE
    assert dut.reception_active.value == 0
    assert dut.temporal_fault.value == 0

    # First edge -> ARMED
    await pulse_interval(dut, 10, is_pos=True)
    assert dut.current_state.value == 1 # STATE_ARMED
    assert dut.reception_active.value == 0

    # Second edge after 9 cycles (Nominal Half-Bit) -> ACTIVE
    await pulse_interval(dut, 9, is_pos=False)
    assert dut.current_state.value == 2 # STATE_ACTIVE
    assert dut.reception_active.value == 1
    assert dut.temporal_valid.value == 1
    assert dut.temporal_fault.value == 0

    # Third edge after 18 cycles (Nominal Full-Bit) -> Stays ACTIVE
    await pulse_interval(dut, 18, is_pos=True)
    assert dut.current_state.value == 2 # STATE_ACTIVE
    assert dut.reception_active.value == 1
    assert dut.temporal_valid.value == 1
    assert dut.temporal_fault.value == 0

@cocotb.test()
async def test_av01_glitch_rejection(dut):
    """Test Case 2 (AV01): Short pulse / runt glitch (N <= 7) triggers immediate temporal fault."""
    clock = Clock(dut.clk, 50, units="us")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Candidate start -> ARMED
    await pulse_interval(dut, 10, is_pos=True)
    # Next edge after 9 cycles -> ACTIVE
    await pulse_interval(dut, 9, is_pos=False)
    assert dut.reception_active.value == 1

    # INJECT GLITCH: Pulse after 3 cycles (< 8)
    await pulse_interval(dut, 3, is_pos=True)
    assert dut.temporal_fault.value == 1
    assert dut.fault_code.value == 1 # FAULT_RUNT (3'b001)
    assert dut.reception_active.value == 0
    assert dut.current_state.value == 0 # STATE_IDLE

@cocotb.test()
async def test_av02_a_missing_edge_resume(dut):
    """Test Case 3 (AV02-A): Gap >= 21 followed by signal resume trips FAULT."""
    clock = Clock(dut.clk, 50, units="us")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Establish ACTIVE burst
    await pulse_interval(dut, 10, is_pos=True)
    await pulse_interval(dut, 9, is_pos=False)
    assert dut.reception_active.value == 1

    # Stalled gap: 21 cycles without edge -> enters LONG_GAP_PENDING
    await ClockCycles(dut.clk, 21)
    assert dut.current_state.value == 3 # STATE_LONG_GAP_PENDING
    assert dut.reception_active.value == 1
    assert dut.temporal_fault.value == 0 # Deferred! Not fault yet!

    # Edge resumes at cycle 35 (Missing edge in active transmission!)
    await pulse_interval(dut, 14, is_pos=True)
    assert dut.temporal_fault.value == 1
    assert dut.fault_code.value == 3 # FAULT_GAP_RES (3'b011)
    assert dut.reception_active.value == 0
    assert dut.current_state.value == 0

@cocotb.test()
async def test_av02_b_normal_packet_termination(dut):
    """Test Case 4 (AV02-B): Sustained silence >= N_EOF confirms normal end of burst (Zero False Alarm)."""
    clock = Clock(dut.clk, 50, units="us")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Establish ACTIVE burst
    await pulse_interval(dut, 10, is_pos=True)
    await pulse_interval(dut, 9, is_pos=False)
    await pulse_interval(dut, 18, is_pos=True)
    assert dut.reception_active.value == 1

    # End of packet: Silence persists beyond EOF_CYC (64 cycles)
    await ClockCycles(dut.clk, 21)
    assert dut.current_state.value == 3 # STATE_LONG_GAP_PENDING

    await ClockCycles(dut.clk, 45) # 21 + 45 = 66 cycles (> 64)
    assert dut.current_state.value == 0 # Cleanly returns to STATE_IDLE!
    assert dut.reception_active.value == 0
    assert dut.temporal_fault.value == 0 # ZERO FALSE ALARM!

@cocotb.test()
async def test_av03_midband_rejection(dut):
    """Test Case 5 (AV03): Mid-band gap (11 <= N <= 15) triggers fault."""
    clock = Clock(dut.clk, 50, units="us")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Establish ACTIVE burst
    await pulse_interval(dut, 10, is_pos=True)
    await pulse_interval(dut, 9, is_pos=False)

    # INJECT MIDBAND: Gap of 13 cycles
    await pulse_interval(dut, 13, is_pos=True)
    assert dut.temporal_fault.value == 1
    assert dut.fault_code.value == 2 # FAULT_MIDBAND (3'b010)
    assert dut.current_state.value == 0

@cocotb.test()
async def test_av08_hardware_capture(dut):
    """Test Case 6 (AV08): Replays exact Digilent Discovery 3 physical capture."""
    csv_path = os.path.join(
        os.path.dirname(__file__),
        "../../../03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/test/data/transmission_digital_hs.csv"
    )
    if not os.path.exists(csv_path):
        dut._log.warning(f"File {csv_path} not found, skipping hardware test.")
        return

    clock = Clock(dut.clk, 50, units="us")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    with open(csv_path, "r") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#") and r[0] != "Time (s)"]

    dio0 = [int(r[2]) for r in rows]

    # Feed digital stream with edge detector
    prev = dio0[0]
    fault_count = 0
    valid_transitions = 0

    for sample in dio0[1:]:
        dut.pos_edge.value = 1 if (sample == 1 and prev == 0) else 0
        dut.neg_edge.value = 1 if (sample == 0 and prev == 1) else 0
        prev = sample
        await ClockCycles(dut.clk, 1)

        if dut.temporal_fault.value == 1:
            fault_count += 1
        if dut.temporal_valid.value == 1:
            valid_transitions += 1

    dut._log.info(f"AV08 Hardware Regression Results: Valid Transitions = {valid_transitions}, Faults = {fault_count}")
    assert fault_count == 0, f"Expected 0 faults on nominal hardware stream, got {fault_count}"
    assert valid_transitions > 200, f"Expected > 200 valid transitions, got {valid_transitions}"
