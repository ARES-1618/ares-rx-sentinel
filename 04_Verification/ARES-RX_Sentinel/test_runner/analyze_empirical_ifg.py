#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ARES SEMIKONDUKTOR TECHNOLOGY
# SPDX-License-Identifier: Apache-2.0
"""
Empirical Inter-Frame Gap (IFG) and Nominal Timing Analysis
Dataset: 25 Nominal Hardware Captures from Digilent Discovery 3 Logic Analyzer
Target: ARES-RX Sentinel Layer-1 Verification (WO-M1-QA-002)
"""

import os
import glob
import csv
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/test/data"))

def parse_csv(filepath):
    """Parses a Digilent Waveforms CSV and extracts the DIO 0 bitstream."""
    dio0 = []
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith("#") or row[0].startswith("Time"):
                continue
            try:
                dio0.append(int(row[2]))
            except (ValueError, IndexError):
                continue
    return dio0

def extract_intervals(dio0):
    """
    Extracts sample-count intervals between consecutive transitions (edges).
    Also records edge polarity (rising vs falling) and absolute sample index.
    """
    intervals = []
    prev_val = dio0[0]
    count = 1
    edge_indices = []

    for idx in range(1, len(dio0)):
        curr_val = dio0[idx]
        if curr_val != prev_val:
            intervals.append(count)
            edge_indices.append((idx, curr_val)) # curr_val is the new level
            count = 1
            prev_val = curr_val
        else:
            count += 1
    # Last trailing silence
    intervals.append(count)
    return intervals, edge_indices

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


def main():
    nominal_files = []
    # 1. Main single transmission
    p_main = os.path.join(BASE_DIR, "transmission_digital_hs.csv")
    if os.path.exists(p_main):
        nominal_files.append(("Single", "transmission_digital_hs.csv", p_main))

    # 2. hs_long (4 files)
    for f in sorted(glob.glob(os.path.join(BASE_DIR, "hs_long", "*.csv"))):
        nominal_files.append(("hs_long", os.path.basename(f), f))

    # 3. hs_repeating (10 files)
    for f in sorted(glob.glob(os.path.join(BASE_DIR, "hs_repeating", "*.csv"))):
        nominal_files.append(("hs_repeating", os.path.basename(f), f))

    # 4. hs_super_long (10 files)
    for f in sorted(glob.glob(os.path.join(BASE_DIR, "hs_super_long", "*.csv"))):
        nominal_files.append(("hs_super_long", os.path.basename(f), f))

    print(f"Total Nominal Hardware Captures Found: {len(nominal_files)}")
    print("=" * 80)

    all_inframe_intervals = []
    all_ifg_intervals = []
    all_settling_intervals = []
    dataset_metrics = []

    total_samples = 0
    total_edges = 0
    total_valids = 0
    total_faults = 0

    dut = AresTimingSentinelSim(eof=64)

    for category, name, path in nominal_files:
        dio0 = parse_csv(path)
        samples_count = len(dio0)
        total_samples += samples_count

        intervals, edge_indices = extract_intervals(dio0)
        edge_count = len(edge_indices)
        total_edges += edge_count

        # Run Sentinel simulation over this capture
        dut.reset()
        file_valids = 0
        file_faults = 0
        prev = dio0[0]
        for s in dio0[1:]:
            pos = 1 if (s == 1 and prev == 0) else 0
            neg = 1 if (s == 0 and prev == 1) else 0
            prev = s
            dut.step(pos, neg)
            if dut.temporal_fault:
                file_faults += 1
            if dut.temporal_valid:
                file_valids += 1

        total_valids += file_valids
        total_faults += file_faults

        # Identify in-frame intervals vs inter-frame gaps
        # Gaps between bursts: intervals >= 21
        # Intervals in [8, 10] or [16, 20] are valid in-frame Manchester
        in_frame = [x for x in intervals[1:-1] if (8 <= x <= 10) or (16 <= x <= 20)]
        gaps = [x for x in intervals[1:-1] if x >= 21]
        settling = [x for x in intervals[1:-1] if x not in in_frame and x not in gaps]

        all_inframe_intervals.extend(in_frame)
        all_ifg_intervals.extend(gaps)
        all_settling_intervals.extend(settling)

        dataset_metrics.append({
            "category": category,
            "name": name,
            "samples": samples_count,
            "edges": edge_count,
            "in_frame": len(in_frame),
            "gaps": len(gaps),
            "gap_min": min(gaps) if gaps else None,
            "gap_max": max(gaps) if gaps else None,
            "file_valids": file_valids,
            "file_faults": file_faults,
            "final_state": dut.current_state
        })

        print(f"[{category:<14}] {name:<28} | Samples: {samples_count:5d} | Edges: {edge_count:4d} | Valids: {file_valids:4d} | Faults: {file_faults} | Gaps: {len(gaps)}")

    print("=" * 80)
    print("AGGREGATE EMPIRICAL ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Total Datasets Evaluated:      {len(nominal_files)}")
    print(f"Total Physical Samples:         {total_samples:,}")
    print(f"Total Physical Transitions:     {total_edges:,}")
    print(f"Total Valid Transitions:        {total_valids:,}")
    print(f"Total Temporal False Alarms:    {total_faults}")
    print(f"False Alarm Rate (FAR):         {total_faults / total_valids if total_valids else 0.0:.6f}")

    if all_ifg_intervals:
        g_min = min(all_ifg_intervals)
        g_max = max(all_ifg_intervals)
        g_median = np.median(all_ifg_intervals)
        g_mean = np.mean(all_ifg_intervals)
        g_std = np.std(all_ifg_intervals)
        p1 = np.percentile(all_ifg_intervals, 1)
        p5 = np.percentile(all_ifg_intervals, 5)
        print("\n--- Inter-Frame Gap (G_IFG) Statistics ---")
        print(f"Total Inter-Burst Gaps Detected: {len(all_ifg_intervals)}")
        print(f"G_IFG Min:     {g_min} samples ({g_min * 50} us)")
        print(f"G_IFG 1st Pct: {p1:.1f} samples ({p1 * 50:.1f} us)")
        print(f"G_IFG 5th Pct: {p5:.1f} samples ({p5 * 50:.1f} us)")
        print(f"G_IFG Median:  {g_median:.1f} samples ({g_median * 50:.1f} us)")
        print(f"G_IFG Mean:    {g_mean:.1f} samples ({g_mean * 50:.1f} us)")
        print(f"G_IFG StdDev:  {g_std:.1f} samples ({g_std * 50:.1f} us)")
        print(f"G_IFG Max:     {g_max} samples ({g_max * 50} us)")

    if all_inframe_intervals:
        in_min = min(all_inframe_intervals)
        in_max = max(all_inframe_intervals)
        print("\n--- In-Frame Interval Statistics ---")
        print(f"Total In-Frame Manchester Edges: {len(all_inframe_intervals)}")
        print(f"In-Frame Min: {in_min} samples ({in_min * 50} us)")
        print(f"In-Frame Max: {in_max} samples ({in_max * 50} us)")

    print("\n--- Boundary & Inactivity Condition Assessment ---")
    print(f"N_TIMEOUT (Active Gap Threshold): {dut.TIMEOUT_CYC} samples ({dut.TIMEOUT_CYC * 50} us)")
    print(f"N_EOF (Provisional End-of-Burst): {dut.EOF_CYC} samples ({dut.EOF_CYC * 50} us)")
    if all_ifg_intervals:
        print(f"Empirical Minimum IFG (G_IFG,min): {g_min} samples ({g_min * 50} us)")
        condition_holds = (dut.TIMEOUT_CYC < dut.EOF_CYC < g_min)
        print(f"Condition: N_TIMEOUT ({dut.TIMEOUT_CYC}) < N_EOF ({dut.EOF_CYC}) < G_IFG,min ({g_min})")
        print(f"STATUS: {'SATISFIED (MATHEMATICALLY DEFENDABLE)' if condition_holds else 'VIOLATED'}")

    return dataset_metrics, all_ifg_intervals

if __name__ == "__main__":
    main()
