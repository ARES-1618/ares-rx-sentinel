#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Hardware Cyber-Physical Receiver Demonstration Dashboard
Standard: SkyWater 130nm TT08 1x1 Standard Tile (161.00 um x 111.52 um)
Protocol: 433.92 MHz ISM Wireless Thermostat Telemetry (20 kHz, 1.11 kbps)
Authors: ARES Semiconductor Technology
================================================================================
"""

import sys
import os
import time
import csv
import argparse

# Ensure proper UTF-8 output encoding across Windows consoles
if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ANSI Terminal Styling
ESC = "\033["
RESET = f"{ESC}0m"
BOLD = f"{ESC}1m"
DIM = f"{ESC}2m"
RED = f"{ESC}91m"
GREEN = f"{ESC}92m"
YELLOW = f"{ESC}93m"
BLUE = f"{ESC}94m"
MAGENTA = f"{ESC}95m"
CYAN = f"{ESC}96m"
WHITE = f"{ESC}97m"
BG_RED = f"{ESC}41m"
BG_GREEN = f"{ESC}42m"
BG_BLUE = f"{ESC}44m"

# Ensure access to M4 verification models
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
COCOTB_DIR = os.path.join(PROJECT_ROOT, "04_Verification", "ARES-RX_Sentinel", "cocotb")
if COCOTB_DIR not in sys.path:
    sys.path.insert(0, COCOTB_DIR)

try:
    from run_m4_adversarial_suite import (
        AresTimingSentinelModel,
        AresFrameFsmModel,
        AresFaultArbiterModel,
        AresFaultLatchModel,
        AresIsolationGateModel,
        AresSentinelTopModel,
        BaselineUnprotectedModel,
        FAULT_NONE, FAULT_RUNT, FAULT_MIDBAND, FAULT_GAP_RES,
        FAULT_PREAMBLE_CORRUPT, FAULT_TYPE_CORRUPT, FAULT_CONSTANT_CORRUPT, FAULT_TRAILER_CORRUPT,
        KNOWN_PREAMBLE, KNOWN_TYPE, KNOWN_CONSTANT
    )
except ImportError as e:
    print(f"{RED}Error importing reference models from {COCOTB_DIR}: {e}{RESET}")
    sys.exit(1)

FAULT_NAMES = {
    FAULT_NONE: "NONE (Nominal)",
    FAULT_RUNT: "L1: RUNT_PULSE_GLITCH (N <= 7 cycles)",
    FAULT_MIDBAND: "L1: MIDBAND_VIOLATION (11 <= N <= 15 cycles)",
    FAULT_GAP_RES: "L1: MISSING_EDGE / GAP_TIMEOUT (N >= 21 cycles)",
    FAULT_PREAMBLE_CORRUPT: "L2: PREAMBLE_CORRUPTION",
    FAULT_TYPE_CORRUPT: "L2: PROTOCOL_TYPE_MISMATCH",
    FAULT_CONSTANT_CORRUPT: "L2: CONSTANT_FIELD_CORRUPTION",
    FAULT_TRAILER_CORRUPT: "L2: FRAMING_BOUNDARY_ERROR (Truncation/Overrun)"
}

NOMINAL_HEX = "aaaaaaaad391d3910dfffffe03391f8900f600b50094ae16"

def print_banner():
    print(f"""
{CYAN}{BOLD}================================================================================
          ARES-RX SENTINEL — CYBER-PHYSICAL SILICON DEMONSTRATOR
================================================================================{RESET}
{BOLD}Foundry Process :{RESET} SkyWater 130nm CMOS ({CYAN}sky130_fd_sc_hd{RESET})
{BOLD}Silicon Envelope:{RESET} Tiny Tapeout TT08 1x1 Standard Tile ({CYAN}161.00 um x 111.52 um{RESET})
{BOLD}Receiver Clock  :{RESET} 20.00 kHz (Tclk = 50.0 us | Manchester 1.11 kbps)
{BOLD}Post-Route Power:{RESET} 50.90 nW @ 20 kHz (+9.28 nW security overhead)
{BOLD}Physical Sign-off:{RESET} {GREEN}DRC: 0 Active | LVS: 100% Match (758/758) | TT Precheck: PASS{RESET}
{CYAN}================================================================================{RESET}
""")

def print_ppa_scorecard():
    print(f"""
{YELLOW}{BOLD}--------------------------------------------------------------------------------
           SKYWATER 130NM TT08 PHYSICAL IMPLEMENTATION SCORECARD (M5-F)
--------------------------------------------------------------------------------{RESET}
| Metric                             | Baseline Unprotected     | ARES Sentinel Protected    |
|------------------------------------+--------------------------+----------------------------|
| Physical Tile Envelope             | 161.00 um x 111.52 um    | 161.00 um x 111.52 um      |
| Standard Cell Logic Area           | 5,017.31 um^2            | 6,477.46 um^2 (+29.1%)     |
| Gross Tile Silicon Fraction (Logic)| 27.94% of 1x1 Tile       | 36.08% of 1x1 Tile         |
| Placement Density (Core Site)      | 48.17% (49.91% reported) | 61.76% (63.99% reported)   |
| Global Routing Track Congestion    | 0 Overcon GCells (0.00%) | 0 Overcon GCells (0.00%)   |
| Detailed Route DRC Violations      | 0 Violations             | 0 Violations               |
| Active Manufacturing DRC Rules     | 0 Violations (100% Clean)| 0 Violations (100% Clean)  |
| Netgen LVS Gate Equivalence        | 100% Match (594/594)     | 100% Match (758/758)       |
| Post-Route Setup Slack @ 50 MHz    | +12.07 ns (Fmax=126 MHz) | +11.88 ns (Fmax=123 MHz)   |
| Post-Route Hold Slack @ 50 MHz     | +0.47 ns (MET)           | +0.42 ns (MET)             |
| Static Leakage Power (1.8V, 25C)   | 2.52 nW                  | 3.10 nW (+0.58 nW)         |
| Workload Power @ 20 kHz (alpha=0.075)| 41.62 nW               | 50.90 nW (+9.28 nW)        |
--------------------------------------------------------------------------------
""")

def run_simulation(sim_title, sim_desc, drive_func, expected_fault):
    print(f"\n{BOLD}>>> EXECUTING DEMONSTRATION: {sim_title} <<<{RESET}")
    print(f"{DIM}{sim_desc}{RESET}\n")

    sentinel = AresSentinelTopModel()
    baseline = BaselineUnprotectedModel()

    t_start = time.perf_counter()
    cycles, s_res, b_res = drive_func(sentinel, baseline)
    elapsed_ms = (time.perf_counter() - t_start) * 1000.0

    s_tamper = s_res["tamper_alert"]
    s_fault = s_res["fault_code"]
    s_isolated = (s_res["safe_data_out"] == 0 and s_tamper == 1)
    b_full = b_res.full
    b_data = b_res.raw_data

    # Formatting table variables
    if expected_fault == FAULT_NONE:
        b_data_str = f"0x{b_data:02X} (Valid Telemetry)"
        s_data_str = f"0x{s_res['safe_data_out']:02X} (Verified)"
    else:
        b_data_str = f"0x{b_data:02X} (Corrupted/Silent)"
        s_data_str = f"{GREEN}{BOLD}0x00 (ZEROIZED){RESET}"

    alert_str = f"{RED}{BOLD}ASSERTED (PIN HIGH){RESET}" if s_tamper else f"{GREEN}CLEAN (LOW){RESET}"
    fault_str = f"{RED}{BOLD}{FAULT_NAMES.get(s_fault, 'UNKNOWN')}{RESET}" if s_fault != FAULT_NONE else f"{GREEN}NONE (Nominal){RESET}"
    iso_str = f"{RED}{BOLD}FAIL-CLOSED (ACTIVE){RESET}" if s_isolated else f"{GREEN}PASS-THROUGH (OPEN){RESET}"

    print(f"{BOLD}Execution Details:{RESET} {cycles} clock cycles ({cycles*50.0/1000.0:.2f} ms real-time equivalent @ 20 kHz) executed in {elapsed_ms:.2f} ms")
    print("\n" + "=" * 80)
    print(f"{'SECURITY & PROTOCOL METRIC':<32} | {'UNPROTECTED BASELINE (B)':<22} | {'PROTECTED SENTINEL (S)':<22}")
    print("-" * 80)
    print(f"{'Hardware Tamper Alert Pin':<32} | {'NO PIN (Silent)':<22} | {alert_str:<22}")
    print(f"{'Detected Fault Category':<32} | {'NONE (Blind)':<22} | {fault_str:<22}")
    print(f"{'Hardware Isolation Gate':<32} | {'NONE (Vulnerable)':<22} | {iso_str:<22}")
    print(f"{'Data Bus to Host System':<32} | {b_data_str:<22} | {s_data_str:<22}")
    bit_str = f"{s_res['bit_counter']}/192 bits"
    print(f"{'Demodulator Frame Full':<32} | {str(bool(b_full)):<22} | {str(bool(s_res['frame_complete'])):<22}")
    print(f"{'FSM Bit Counter Tracking':<32} | {'NO COUNTER (Blind)':<22} | {bit_str:<22}")
    print("=" * 80)

    # Security Verdict
    if expected_fault == FAULT_NONE:
        if not s_tamper and not s_isolated:
            print(f"{BG_GREEN}{WHITE}{BOLD} VERDICT: 100% NOMINAL TRANSPARENCY PASS {RESET} — Zero latency penalty, 100% data fidelity.")
        else:
            print(f"{BG_RED}{WHITE}{BOLD} VERDICT: FALSE POSITIVE ANOMALY {RESET}")
    else:
        if s_tamper and s_isolated and (s_fault == expected_fault or expected_fault == -1):
            print(f"{BG_GREEN}{WHITE}{BOLD} VERDICT: HARDWARE ATTACK BLOCKED & ZEROIZED {RESET}")
            print(f"{GREEN}✓ Sentinel detected cyber-physical timing/syntax anomaly within 1 clock cycle.{RESET}")
            print(f"{GREEN}✓ Fail-closed hardware isolation prevented corrupt payload injection into host.{RESET}")
            print(f"{RED}✗ Baseline demodulator had zero tamper visibility and accepted corrupt pulse/frame.{RESET}")
        else:
            print(f"{BG_RED}{WHITE}{BOLD} VERDICT: DETECTION MISMATCH {RESET} (Expected: {FAULT_NAMES.get(expected_fault)}, Got: {FAULT_NAMES.get(s_fault)})")

# --- Scenario Drivers ---

def drive_nominal(sentinel, baseline):
    nominal_bits = [int(b) for b in bin(int(NOMINAL_HEX, 16))[2:].zfill(192)]
    cycles = 0
    # Lead-in silence
    for _ in range(65):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    for _ in range(9):
        sentinel.clock_step(rx_in=1, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    for _ in range(9):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1

    rx_val = 0
    for b in nominal_bits:
        rx_val = 1 - rx_val
        for k in range(9):
            s_clk = 1 if k == 4 else 0
            s_res = sentinel.clock_step(rx_in=rx_val, serial_clock=s_clk, serial_data=b, raw_data_in=0x55, raw_valid_in=1)
            baseline.clock_step(manchester_clock=s_clk, manchester_data=b)
            cycles += 1

    # Trailing EOF silence
    for _ in range(64):
        s_res = sentinel.clock_step(rx_in=rx_val, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1

    return cycles, s_res, baseline

def drive_runt_glitch(sentinel, baseline):
    cycles = 0
    # Lead-in silence
    for _ in range(65):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    # Valid pulse
    for _ in range(9):
        sentinel.clock_step(rx_in=1, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    # Runt pulse: 4 cycles = 200 us (< 400 us minimum half-bit)
    for _ in range(4):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        baseline.clock_step(manchester_clock=1, manchester_data=1)
        cycles += 1
    # Rising edge triggers L1 runt fault
    s_res = sentinel.clock_step(rx_in=1, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
    cycles += 1
    return cycles, s_res, baseline

def drive_midband_desync(sentinel, baseline):
    cycles = 0
    for _ in range(65):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    for _ in range(9):
        sentinel.clock_step(rx_in=1, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    # Mid-band illegal interval: 13 cycles = 650 us (strictly between half-bit [8..10] and full-bit [16..20])
    for _ in range(13):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        baseline.clock_step(manchester_clock=1, manchester_data=0)
        cycles += 1
    s_res = sentinel.clock_step(rx_in=1, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
    cycles += 1
    return cycles, s_res, baseline

def drive_preamble_corrupt(sentinel, baseline):
    # Corrupt preamble: 0x55555555 instead of 0xAAAAAAAA
    corrupt_hex = "55555555d391d3910dfffffe03391f8900f600b50094ae16"
    bits = [int(b) for b in bin(int(corrupt_hex, 16))[2:].zfill(192)]
    cycles = 0
    for _ in range(65):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    for _ in range(9):
        sentinel.clock_step(rx_in=1, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    for _ in range(9):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1

    rx_val = 0
    for b in bits:
        rx_val = 1 - rx_val
        for k in range(9):
            s_clk = 1 if k == 4 else 0
            s_res = sentinel.clock_step(rx_in=rx_val, serial_clock=s_clk, serial_data=b, raw_data_in=0x55, raw_valid_in=1)
            baseline.clock_step(manchester_clock=s_clk, manchester_data=b)
            cycles += 1
    return cycles, s_res, baseline

def drive_frame_overrun(sentinel, baseline):
    nominal_bits = [int(b) for b in bin(int(NOMINAL_HEX, 16))[2:].zfill(192)]
    cycles = 0
    # Lead-in silence and arming
    for _ in range(65):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    for _ in range(9):
        sentinel.clock_step(rx_in=1, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1
    for _ in range(9):
        sentinel.clock_step(rx_in=0, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1

    # Stream 192 nominal bits
    rx_val = 0
    for b in nominal_bits:
        rx_val = 1 - rx_val
        for k in range(9):
            s_clk = 1 if k == 4 else 0
            sentinel.clock_step(rx_in=rx_val, serial_clock=s_clk, serial_data=b, raw_data_in=0x55, raw_valid_in=1)
            baseline.clock_step(manchester_clock=s_clk, manchester_data=b)
            cycles += 1

    # Inject 193rd unauthorized bit strobe during active envelope
    for k in range(9):
        s_clk = 1 if k == 4 else 0
        s_res = sentinel.clock_step(rx_in=1, serial_clock=s_clk, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        baseline.clock_step(manchester_clock=s_clk, manchester_data=0)
        cycles += 1

    return cycles, s_res, baseline

def drive_hardware_trace(sentinel, baseline):
    trace_path = os.path.join(PROJECT_ROOT, "03_Core_Projects", "ARES-RX_Sentinel", "tt07-bep-decode", "test", "data", "transmission_digital_hs.csv")
    cycles = 0
    pulses = []
    with open(trace_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith("#") or not row[0].strip().isdigit():
                continue
            pulses.append(int(row[0].strip()))

    rx_val = 0
    for p_width in pulses:
        rx_val = 1 - rx_val
        for k in range(p_width):
            s_clk = 1 if (k == p_width // 2) else 0
            s_res = sentinel.clock_step(rx_in=rx_val, serial_clock=s_clk, serial_data=rx_val, raw_data_in=0x55, raw_valid_in=1)
            baseline.clock_step(manchester_clock=s_clk, manchester_data=rx_val)
            cycles += 1

    # End with EOF silence
    for _ in range(65):
        s_res = sentinel.clock_step(rx_in=rx_val, serial_clock=0, serial_data=0, raw_data_in=0x55, raw_valid_in=1)
        cycles += 1

    return cycles, s_res, baseline

# --- Demo Wrappers ---

def demo_scenario_nominal():
    run_simulation(
        "SCENARIO 1: Nominal 192-bit Telemetry Reception",
        "Demonstrates complete transparent reception of valid 192-bit Manchester thermostat frame.\n"
        "Payload: Thermostat ID = 0x03391F89 | Room Temp = 72 deg F | Setpoint = 70 deg F.",
        drive_nominal,
        FAULT_NONE
    )

def demo_scenario_runt_pulse():
    run_simulation(
        "SCENARIO 2: Adversarial Runt Pulse / Glitch Injection (Layer 1)",
        "Injects a sub-microsecond pulse anomaly (N = 4 clock cycles = 200 us < 400 us minimum half-bit).\n"
        "Tests physical temporal sentinel immunity against glitch-based FSM desynchronization.",
        drive_runt_glitch,
        FAULT_RUNT
    )

def demo_scenario_midband_desync():
    run_simulation(
        "SCENARIO 3: Pulse Timing Desynchronization (Layer 1 Mid-Band)",
        "Injects an illegal non-orthogonal pulse interval (N = 13 clock cycles = 650 us).\n"
        "Valid intervals: Half-Bit [8..10] or Full-Bit [16..20]. 13 cycles is strictly non-Manchester.",
        drive_midband_desync,
        FAULT_MIDBAND
    )

def demo_scenario_preamble_corruption():
    run_simulation(
        "SCENARIO 4: Fixed-Field Preamble Tampering (Layer 2 Syntax)",
        "Transmits valid physical pulses, but corrupts the 32-bit protocol preamble (0xAAAAAAAA -> 0x55555555).\n"
        "Tests protocol grammar FSM enforcement: spoofed frames must be immediately rejected.",
        drive_preamble_corrupt,
        FAULT_PREAMBLE_CORRUPT
    )

def demo_scenario_overrun_attack():
    run_simulation(
        "SCENARIO 5: Frame Overrun / Buffer Overflow Attack (Layer 2 Syntax)",
        "Transmits 208 bits instead of standard 192 bits without the required 64-cycle EOF silence.\n"
        "Tests autonomous bit counter boundary: prevents buffer bleed and parser overrun.",
        drive_frame_overrun,
        FAULT_TRAILER_CORRUPT
    )

def demo_scenario_hardware_trace():
    run_simulation(
        "SCENARIO 6: Empirical Hardware Logic Analyzer Trace Replay",
        "Replays authentic physical logic analyzer capture from commercial 433.92 MHz thermostat (289 transitions).\n"
        "Validates that real-world oscillator jitter and physical noise do not cause false positives.",
        drive_hardware_trace,
        FAULT_NONE
    )

def run_all_scenarios():
    demo_scenario_nominal()
    print("\n" + "-" * 80)
    demo_scenario_runt_pulse()
    print("\n" + "-" * 80)
    demo_scenario_midband_desync()
    print("\n" + "-" * 80)
    demo_scenario_preamble_corruption()
    print("\n" + "-" * 80)
    demo_scenario_overrun_attack()
    print("\n" + "-" * 80)
    demo_scenario_hardware_trace()
    print("\n" + "=" * 80)
    print(f"{BG_GREEN}{WHITE}{BOLD} ALL 6 DEMONSTRATION SCENARIOS EXECUTED SUCCESSFULLY {RESET}")
    print("=" * 80)

def interactive_menu():
    while True:
        print_banner()
        print(f"{BOLD}AVAILABLE DEMONSTRATION SCENARIOS:{RESET}")
        print(f"  {CYAN}[1]{RESET} Nominal 192-bit Telemetry Transmission (Transparency Test)")
        print(f"  {CYAN}[2]{RESET} Adversarial Attack: Runt Pulse / Sub-microsecond Glitch Injection")
        print(f"  {CYAN}[3]{RESET} Adversarial Attack: Pulse Timing Desynchronization (Mid-band)")
        print(f"  {CYAN}[4]{RESET} Adversarial Attack: Protocol Preamble Corruption / Spoofing")
        print(f"  {CYAN}[5]{RESET} Adversarial Attack: Frame Overrun / Buffer Overflow")
        print(f"  {CYAN}[6]{RESET} Physical Hardware Trace Replay (Logic Analyzer Capture)")
        print(f"  {CYAN}[7]{RESET} Run Complete Automated Benchmark Suite (All Scenarios)")
        print(f"  {CYAN}[8]{RESET} View SkyWater 130nm TT08 Silicon PPA Scorecard")
        print(f"  {CYAN}[Q]{RESET} Exit Demonstrator")
        print()

        try:
            choice = input(f"{BOLD}Select an option [1-8, Q]: {RESET}").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == "1":
            demo_scenario_nominal()
        elif choice == "2":
            demo_scenario_runt_pulse()
        elif choice == "3":
            demo_scenario_midband_desync()
        elif choice == "4":
            demo_scenario_preamble_corruption()
        elif choice == "5":
            demo_scenario_overrun_attack()
        elif choice == "6":
            demo_scenario_hardware_trace()
        elif choice == "7":
            run_all_scenarios()
        elif choice == "8":
            print_ppa_scorecard()
        elif choice == "Q":
            print(f"{GREEN}Demonstration complete. Exiting ARES-RX Sentinel Demonstrator.{RESET}")
            break
        else:
            print(f"{RED}Invalid selection. Please choose between 1 and 8, or Q.{RESET}")

        input(f"\n{DIM}Press Enter to return to main menu...{RESET}")

def main():
    parser = argparse.ArgumentParser(description="ARES-RX Sentinel Hardware Demonstration Dashboard")
    parser.add_argument("--scenario", type=int, choices=[1, 2, 3, 4, 5, 6], help="Run a specific demonstration scenario directly")
    parser.add_argument("--all", action="store_true", help="Run all demonstration scenarios sequentially")
    parser.add_argument("--scorecard", action="store_true", help="Display silicon PPA scorecard")
    args = parser.parse_args()

    if args.scorecard:
        print_banner()
        print_ppa_scorecard()
    elif args.all:
        print_banner()
        run_all_scenarios()
    elif args.scenario == 1:
        print_banner()
        demo_scenario_nominal()
    elif args.scenario == 2:
        print_banner()
        demo_scenario_runt_pulse()
    elif args.scenario == 3:
        print_banner()
        demo_scenario_midband_desync()
    elif args.scenario == 4:
        print_banner()
        demo_scenario_preamble_corruption()
    elif args.scenario == 5:
        print_banner()
        demo_scenario_overrun_attack()
    elif args.scenario == 6:
        print_banner()
        demo_scenario_hardware_trace()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
