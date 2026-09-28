#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Bounded Differential Simulation Correlation Engine
Work Order: WO-2026-M6-ARCH-010: Network-to-rx_in Causal Closure & Differential Hardening
Authority: Technical Architect / Research Direction

Purpose:
  Performs exhaustive, cycle-by-cycle bounded differential simulation correlation
  between the Python behavioral reference model and the actual frozen M4
  synthesizable Verilog RTL (ares_sentinel_top.v + submodules compiled via Icarus Verilog).

  On EVERY clock cycle n across all 9 canonical vectors (AV00-AV08), verifies exact
  equality of the full 11-signal observable state vector:
    O(n) = (
      rx_in,
      serial_clock,
      serial_data,
      reception_active,
      frame_complete,
      temporal_fault,
      frame_fault,
      tamper_alert,
      latched_fault_code,
      safe_data_out,
      safe_valid_out
    )
================================================================================
"""

import sys
import os
import json
import subprocess
import hashlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

# Single canonical vector loader
CYBER_DIR = os.path.join(PROJECT_ROOT, "06_Demonstration", "cyber_physical")
if CYBER_DIR not in sys.path:
    sys.path.insert(0, CYBER_DIR)
from canonical_vector_loader import get_all_canonical_vectors, get_canonical_vector

FAULT_NAMES = {
    0: "FAULT_NONE",
    1: "FAULT_RUNT",
    2: "FAULT_MIDBAND",
    3: "FAULT_GAP_RES",
    4: "FAULT_PREAMBLE_CORRUPT",
    5: "FAULT_TYPE_CORRUPT",
    6: "FAULT_CONSTANT_CORRUPT",
    7: "FAULT_TRAILER_CORRUPT"
}

FAULT_CODES_BIN = {
    0: "3'b000",
    1: "3'b001",
    2: "3'b010",
    3: "3'b011",
    4: "3'b100",
    5: "3'b101",
    6: "3'b110",
    7: "3'b111"
}

RTL_SRC_DIR = os.path.join(PROJECT_ROOT, "05_ASIC_Synthesis", "tt08_submission_repo", "src")
HARNESS_V = os.path.join(SCRIPT_DIR, "tb_m6_canonical_harness.v")
SIM_VVP = os.path.join(SCRIPT_DIR, "m6_canonical_sim.vvp")

# -----------------------------------------------------------------------------
# Cycle-Accurate Python Behavioral Reference Model (11 Observable Signals)
# -----------------------------------------------------------------------------
class CycleAccurateTimingSentinelModel:
    def __init__(self):
        self.state = 0
        self.interval_counter = 0
        self.reception_active = 0
        self.temporal_fault = 0
        self.fault_code = 0

    def clock_step(self, pos_edge: bool, neg_edge: bool):
        edge_detected = pos_edge or neg_edge
        old_counter = self.interval_counter
        is_runt = (old_counter < 8) and (old_counter > 0)
        is_half = (8 <= old_counter <= 10)
        is_mid = (10 < old_counter < 16)
        is_full = (16 <= old_counter <= 20)
        is_valid = is_half or is_full

        self.temporal_fault = 0

        # Synchronous counter update
        if edge_detected:
            self.interval_counter = 1
        elif self.interval_counter < 255:
            self.interval_counter += 1

        # State transition evaluating registered old_counter
        if self.state == 0:  # STATE_IDLE
            self.reception_active = 0
            if edge_detected:
                self.state = 1  # STATE_ARMED
        elif self.state == 1:  # STATE_ARMED
            self.reception_active = 0
            if edge_detected:
                if is_valid:
                    self.reception_active = 1
                    self.state = 2  # STATE_ACTIVE
                elif is_runt or is_mid:
                    self.state = 1
            elif old_counter >= 21:
                self.state = 0
        elif self.state == 2:  # STATE_ACTIVE
            self.reception_active = 1
            if edge_detected:
                if is_valid:
                    self.state = 2
                elif is_runt:
                    self.temporal_fault = 1
                    self.fault_code = 1
                    self.reception_active = 0
                    self.state = 0
                elif is_mid:
                    self.temporal_fault = 1
                    self.fault_code = 2
                    self.reception_active = 0
                    self.state = 0
            elif old_counter >= 21:
                self.state = 3  # STATE_LONG_GAP_PENDING
        elif self.state == 3:  # STATE_LONG_GAP_PENDING
            self.reception_active = 1
            if edge_detected:
                self.temporal_fault = 1
                self.fault_code = 3
                self.reception_active = 0
                self.state = 0
            elif old_counter >= 64:
                self.reception_active = 0
                self.state = 0


class CycleAccurateFrameFsmModel:
    KNOWN_TYPE = 0xD391
    KNOWN_CONST = 0x0DFFFFFE

    def __init__(self):
        self.state = 0
        self.bit_counter = 0
        self.frame_started = 0
        self.frame_complete = 0
        self.frame_fault = 0
        self.frame_fault_code = 0
        self.prev_reception_active = 0

    def _check_bit(self, bit_idx: int, serial_data: int):
        if bit_idx <= 31:
            exp = 1 if (bit_idx % 2 == 0) else 0
            return (serial_data != exp), 4  # FAULT_PREAMBLE_CORRUPT
        elif 32 <= bit_idx <= 47:
            exp = (self.KNOWN_TYPE >> (47 - bit_idx)) & 1
            return (serial_data != exp), 5  # FAULT_TYPE_CORRUPT
        elif 48 <= bit_idx <= 63:
            exp = (self.KNOWN_TYPE >> (63 - bit_idx)) & 1
            return (serial_data != exp), 5  # FAULT_TYPE_CORRUPT
        elif 64 <= bit_idx <= 95:
            exp = (self.KNOWN_CONST >> (95 - bit_idx)) & 1
            return (serial_data != exp), 6  # FAULT_CONSTANT_CORRUPT
        return False, 0

    def clock_step(self, serial_clock: int, serial_data: int, reception_active: int):
        self.frame_fault = 0
        old_prev_rec = self.prev_reception_active
        self.prev_reception_active = reception_active

        if self.state == 0:  # STATE_IDLE
            if reception_active and serial_clock:
                self.frame_started = 1
                err, code = self._check_bit(0, serial_data)
                if err:
                    self.frame_fault = 1
                    self.frame_fault_code = code
                    self.state = 3  # STATE_FAULT
                else:
                    self.bit_counter = 1
                    self.state = 1  # STATE_RECEIVING
        elif self.state == 1:  # STATE_RECEIVING
            if old_prev_rec and (not reception_active) and self.frame_started and (not self.frame_complete):
                self.frame_fault = 1
                self.frame_fault_code = 7  # FAULT_TRAILER_CORRUPT (Truncation)
                self.state = 3
            elif serial_clock:
                err, code = self._check_bit(self.bit_counter, serial_data)
                if err:
                    self.frame_fault = 1
                    self.frame_fault_code = code
                    self.state = 3
                else:
                    if self.bit_counter == 191:
                        self.bit_counter = 192
                        self.frame_complete = 1
                        self.state = 2  # STATE_COMPLETE
                    else:
                        self.bit_counter += 1
        elif self.state == 2:  # STATE_COMPLETE
            if reception_active and serial_clock:
                self.frame_fault = 1
                self.frame_fault_code = 7  # FAULT_TRAILER_CORRUPT (Overrun)
                self.state = 3
            elif not reception_active:
                self.state = 0  # STATE_IDLE
                self.frame_complete = 0
                self.frame_started = 0
                self.bit_counter = 0


class CycleAccurateSentinelTopModel:
    def __init__(self):
        self.l1 = CycleAccurateTimingSentinelModel()
        self.l2 = CycleAccurateFrameFsmModel()
        self.prev_rx = 0
        self.fault_latched = 0
        self.latched_code = 0
        self.pending_latch = 0
        self.pending_code = 0

    def clock_step(self, rx_in: int, serial_clock: int, serial_data: int, raw_data_in: int = 0x55, raw_valid_in: int = 1):
        pos_edge = (rx_in == 1 and self.prev_rx == 0)
        neg_edge = (rx_in == 0 and self.prev_rx == 1)
        self.prev_rx = rx_in

        # Registered latch update from previous cycle's set_fault
        if self.pending_latch and not self.fault_latched:
            self.fault_latched = 1
            self.latched_code = self.pending_code

        old_rec_active = self.l1.reception_active
        self.l1.clock_step(pos_edge, neg_edge)
        self.l2.clock_step(serial_clock, serial_data, old_rec_active)

        temporal_fault = self.l1.temporal_fault
        frame_fault = self.l2.frame_fault
        reception_active = self.l1.reception_active
        frame_complete = self.l2.frame_complete

        # Combinational arbiter
        set_fault = temporal_fault or frame_fault
        code = self.l1.fault_code if temporal_fault else self.l2.frame_fault_code
        if set_fault:
            self.pending_latch = 1
            if self.pending_code == 0:
                self.pending_code = code

        # Downstream isolation gate (instantaneous once latched)
        safe_data_out = 0x00 if self.fault_latched else raw_data_in
        safe_valid_out = 0 if self.fault_latched else raw_valid_in

        # Return the exact 11-signal observable tuple O(n)
        return (
            rx_in,
            serial_clock,
            serial_data,
            reception_active,
            frame_complete,
            temporal_fault,
            frame_fault,
            self.fault_latched,
            self.latched_code,
            safe_data_out,
            safe_valid_out
        )


def compile_rtl(custom_rtl_files=None, output_vvp=None):
    out = output_vvp or SIM_VVP
    if custom_rtl_files:
        rtl_files = custom_rtl_files
    else:
        rtl_files = [
            HARNESS_V,
            os.path.join(RTL_SRC_DIR, "ares_sentinel_top.v"),
            os.path.join(RTL_SRC_DIR, "ares_timing_sentinel.v"),
            os.path.join(RTL_SRC_DIR, "ares_frame_fsm.v"),
            os.path.join(RTL_SRC_DIR, "ares_fault_arbiter.v"),
            os.path.join(RTL_SRC_DIR, "ares_fault_latch.v"),
            os.path.join(RTL_SRC_DIR, "ares_isolation_gate.v"),
            os.path.join(RTL_SRC_DIR, "ares_isolation_l3.v"),
        ]
    cmd = ["iverilog", "-g2005", "-o", out] + rtl_files
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"RTL compilation failed:\n{res.stderr}")
    return out


def run_rtl_vector(cycles_profile, vvp_file=None, work_dir=None):
    wd = work_dir or SCRIPT_DIR
    vvp = vvp_file or SIM_VVP
    stim_path = os.path.join(wd, "stimulus_in.txt")
    out_path = os.path.join(wd, "sim_out.json")
    trace_path = os.path.join(wd, "sim_trace.tsv")

    if os.path.exists(out_path):
        os.remove(out_path)
    if os.path.exists(trace_path):
        os.remove(trace_path)

    trace_lines = []
    with open(stim_path, "w", encoding="utf-8") as f:
        for r_in, s_clk, s_data, count in cycles_profile:
            line = f"{r_in} {s_clk} {s_data}\n"
            for _ in range(count):
                f.write(line)
                trace_lines.append(line)

    rtl_trace_hash = hashlib.sha256("".join(trace_lines).encode('utf-8')).hexdigest()

    res = subprocess.run(["vvp", vvp], cwd=wd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Simulation failed:\n{res.stderr}")

    with open(out_path, "r", encoding="utf-8") as f:
        sim_data = json.load(f)

    # Read cycle-by-cycle observable trace
    rtl_observable_trace = []
    with open(trace_path, "r", encoding="utf-8") as f:
        lines = [line.strip().split("\t") for line in f if line.strip()]
        for row in lines[1:]:  # skip header
            # row: [cycle, rx_in, serial_clock, serial_data, reception_active, frame_complete,
            #       temporal_fault, frame_fault, tamper_alert, latched_fault_code, safe_data_out, safe_valid_out]
            obs = tuple(int(x) for x in row[1:])
            rtl_observable_trace.append(obs)

    if os.path.exists(stim_path):
        os.remove(stim_path)
    if os.path.exists(out_path):
        os.remove(out_path)
    if os.path.exists(trace_path):
        os.remove(trace_path)

    sim_data["baseband_input_trace_hash"] = compute_baseband_input_trace_hash(cycles_profile)
    sim_data["rx_in_trace_hash"] = compute_rx_in_trace_hash(cycles_profile)
    sim_data["rtl_trace_hash"] = compute_observable_trace_hash(rtl_observable_trace)
    sim_data["rtl_observable_trace_hash"] = sim_data["rtl_trace_hash"]
    sim_data["observable_trace"] = rtl_observable_trace

    f_cond = sim_data.get("fault_condition_cycle", -1)
    f_latch = sim_data.get("fault_latched_cycle", -1)
    iso_eff = sim_data.get("isolation_effective_cycle", -1)
    safe_out = sim_data.get("safe_output_cycle", -1)
    t_latch = (f_latch - f_cond) if (sim_data.get("tamper_alert") and f_cond > 0 and f_latch > 0) else -1
    t_isolate = (iso_eff - f_latch) if (sim_data.get("tamper_alert") and f_latch > 0 and iso_eff > 0) else -1
    t_safe = (safe_out - f_latch) if (sim_data.get("tamper_alert") and f_latch > 0 and safe_out > 0) else -1
    sim_data["latch_latency_cycles"] = t_latch
    sim_data["isolation_latency_cycles"] = t_isolate
    sim_data["safe_output_latency_cycles"] = t_safe
    return sim_data


def compute_rx_in_trace_hash(cycles_profile):
    """
    Computes H_rxin: the SHA-256 hash of the serialized discrete baseband rx_in[n] stream.
    Used as an auxiliary diagnostic hash.
    """
    rx_in_sequence = "".join(str(r_in) * count for r_in, _, _, count in cycles_profile)
    return hashlib.sha256(rx_in_sequence.encode('utf-8')).hexdigest()


def compute_baseband_input_trace_hash(cycles_profile):
    """
    Computes H_baseband: the SHA-256 hash of the complete physical digital baseband
    input vector S[n] = (rx_in[n], serial_clock[n], serial_data[n]) across all clock cycles.
    Uniquely distinguishes all 9 canonical vectors entering the Sentinel hardware.
    """
    lines = []
    for r_in, s_clk, s_data, count in cycles_profile:
        chunk = f"{r_in} {s_clk} {s_data}\n" * count
        lines.append(chunk)
    return hashlib.sha256("".join(lines).encode('utf-8')).hexdigest()


def compute_observable_trace_hash(observable_trace):
    """
    Computes H_rtl: the SHA-256 hash of the complete 11-signal observable state vector O(n)
    sampled cycle-by-cycle across the entire simulation duration.
    """
    lines = [",".join(str(x) for x in obs) + "\n" for obs in observable_trace]
    return hashlib.sha256("".join(lines).encode('utf-8')).hexdigest()


def run_python_model(cycles_profile):
    sentinel = CycleAccurateSentinelTopModel()
    cyc = 0
    tamper_cycle = None
    latched_code = 0
    tamper_alert_latched = 0
    f_cond_cyc = None
    f_latch_cyc = None
    iso_eff_cyc = None
    safe_out_cyc = None
    observable_trace = []

    for rx_val, s_clk, s_data, count in cycles_profile:
        for _ in range(count):
            cyc += 1
            obs = sentinel.clock_step(
                rx_in=rx_val,
                serial_clock=s_clk,
                serial_data=s_data,
                raw_data_in=0x55,
                raw_valid_in=1
            )
            observable_trace.append(obs)

            t_fault, f_fault, tamper_alert = obs[5], obs[6], obs[7]
            if (t_fault or f_fault) and f_cond_cyc is None:
                f_cond_cyc = cyc

            if tamper_alert and not tamper_alert_latched:
                tamper_alert_latched = 1
                tamper_cycle = cyc
                f_latch_cyc = cyc
                latched_code = obs[8]
                if obs[9] == 0:
                    iso_eff_cyc = cyc
                    safe_out_cyc = cyc

    final_safe_bus = 0x00 if tamper_alert_latched else 0x55
    iso_lat = 1 if tamper_alert_latched else None
    t_latch = (f_latch_cyc - f_cond_cyc) if (tamper_alert_latched and f_cond_cyc is not None and f_latch_cyc is not None) else -1
    t_isolate = (iso_eff_cyc - f_latch_cyc) if (tamper_alert_latched and f_latch_cyc is not None and iso_eff_cyc is not None) else -1
    t_safe = (safe_out_cyc - f_latch_cyc) if (tamper_alert_latched and f_latch_cyc is not None and safe_out_cyc is not None) else -1

    return {
        "total_cycles": cyc,
        "tamper_alert": tamper_alert_latched,
        "detection_cycle": tamper_cycle if tamper_cycle is not None else -1,
        "fault_code": latched_code,
        "isolation_latency": iso_lat if iso_lat is not None else -1,
        "fault_condition_cycle": f_cond_cyc if f_cond_cyc is not None else -1,
        "fault_latched_cycle": f_latch_cyc if f_latch_cyc is not None else -1,
        "isolation_effective_cycle": iso_eff_cyc if iso_eff_cyc is not None else -1,
        "safe_output_cycle": safe_out_cyc if safe_out_cyc is not None else -1,
        "latch_latency_cycles": t_latch,
        "isolation_latency_cycles": t_isolate,
        "safe_output_latency_cycles": t_safe,
        "safe_data_out": final_safe_bus,
        "baseband_input_trace_hash": compute_baseband_input_trace_hash(cycles_profile),
        "rx_in_trace_hash": compute_rx_in_trace_hash(cycles_profile),
        "rtl_observable_trace_hash": compute_observable_trace_hash(observable_trace),
        "observable_trace": observable_trace
    }


def run_correlation_suite():
    compile_rtl()
    vectors = get_all_canonical_vectors()

    print("=" * 140)
    print(" ARES-RX SENTINEL: BOUNDED DIFFERENTIAL SIMULATION CORRELATION ENGINE (WO-2026-M6-ARCH-010)")
    print(" Standard: Full Cycle-by-Cycle Observable Trace Equality Across All 11 Hardware Signals O(n)")
    print("=" * 140)
    print(f"{'Vector':<6} | {'Category':<22} | {'Fault Name':<22} | {'Cycles':<6} | {'Detect Cyc (Py/RTL)':<20} | {'Iso':<5} | {'Bus':<6} | Observable Trace")
    print("-" * 140)

    all_concordant = True
    correlation_records = []

    for v in vectors:
        vid = v["id"]
        profile = v["cycles_profile"]

        py_res = run_python_model(profile)
        rtl_res = run_rtl_vector(profile)

        # 1. Summary checks
        match_tamper  = (py_res["tamper_alert"] == rtl_res["tamper_alert"])
        match_code    = (py_res["fault_code"] == rtl_res["fault_code"])
        match_detect  = (py_res["detection_cycle"] == rtl_res["detection_cycle"])
        match_isolate = (py_res["isolation_latency"] == rtl_res["isolation_latency"])
        match_bus     = (py_res["safe_data_out"] == rtl_res["safe_data_out"])

        # 2. Exhaustive Cycle-by-Cycle Trace Comparison across all 11 signals:
        py_trace = py_res["observable_trace"]
        rtl_trace = rtl_res["observable_trace"]
        trace_len_match = (len(py_trace) == len(rtl_trace))

        trace_mismatches = []
        if trace_len_match:
            for c_idx, (p_obs, r_obs) in enumerate(zip(py_trace, rtl_trace)):
                if p_obs != r_obs:
                    trace_mismatches.append((c_idx + 1, p_obs, r_obs))
        else:
            trace_mismatches.append((-1, f"len={len(py_trace)}", f"len={len(rtl_trace)}"))

        trace_perfect = (len(trace_mismatches) == 0) and trace_len_match
        is_equiv = match_tamper and match_code and match_detect and match_isolate and match_bus and trace_perfect

        if not is_equiv:
            all_concordant = False

        det_str = f"{py_res['detection_cycle']} / {rtl_res['detection_cycle']}" if py_res['tamper_alert'] else "N/A / N/A"
        iso_str = f"{rtl_res['isolation_latency']}c" if rtl_res['tamper_alert'] else "N/A"
        bus_str = f"0x{rtl_res['safe_data_out']:02X}"
        trace_str = f"100% MATCH ({len(py_trace)}/{len(py_trace)} cyc, 11 sigs)" if trace_perfect else f"MISMATCH ({len(trace_mismatches)} cyc)"

        print(f"{vid:<6} | {v['category']:<22} | {FAULT_NAMES[rtl_res['fault_code']]:<22} | {len(py_trace):<6} | {det_str:<20} | {iso_str:<5} | {bus_str:<6} | {trace_str}")

        correlation_records.append({
            "vector_id": vid,
            "vector_name": v["name"],
            "stimulus_hash": v["vector_stimulus_sha256"],
            "rtl_trace_hash": rtl_res["rtl_trace_hash"],
            "fault_code_bin": FAULT_CODES_BIN[rtl_res["fault_code"]],
            "fault_name": FAULT_NAMES[rtl_res["fault_code"]],
            "tamper_alert": rtl_res["tamper_alert"],
            "detection_cycle": rtl_res["detection_cycle"] if rtl_res["tamper_alert"] else None,
            "isolation_latency_cycles": rtl_res["isolation_latency"] if rtl_res["tamper_alert"] else None,
            "safe_data_out": f"0x{rtl_res['safe_data_out']:02X}",
            "total_cycles": len(py_trace),
            "signals_evaluated_per_cycle": 11,
            "cycles_matching": len(py_trace) - len(trace_mismatches),
            "cycle_trace_perfect": trace_perfect,
            "differential_correlation_status": "EXACT_OBSERVABLE_TRACE_MATCH" if trace_perfect else "TRACE_DISCORDANCE"
        })

    print("=" * 140)
    if all_concordant:
        print("[AUDIT PROOF] BOUNDED DIFFERENTIAL SIMULATION CORRELATION CONFIRMED ACROSS ALL 9 CANONICAL VECTORS:")
        print("              Python Reference Model === Frozen M4 Synthesizable Verilog RTL Simulation.")
        print("              Exhaustive 11-Signal Observable State Vector O(n) matches on 100% of discrete clock cycles.")
    else:
        print("[AUDIT FAIL] Observable trace discrepancy detected!")
    print("=" * 140)

    proof_path = os.path.join(SCRIPT_DIR, "m6_model_rtl_correlation_proof.json")
    with open(proof_path, "w", encoding="utf-8") as f:
        json.dump({
            "work_order": "WO-2026-M6-ARCH-011R1",
            "differential_correlation": all_concordant,
            "total_vectors_tested": len(vectors),
            "evaluation_standard": "Full 11-Signal Observable State Vector O(n) Cycle-by-Cycle Comparison",
            "records": correlation_records
        }, f, indent=2)

    return correlation_records


if __name__ == "__main__":
    records = run_correlation_suite()
