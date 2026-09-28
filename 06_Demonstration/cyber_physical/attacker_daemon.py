#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Cyber-Physical Attack Injector Daemon (Attacker Node)
Milestone: M6 (Cyber-Physical Security Demonstrator)
Protocol: 433.92 MHz Manchester Telemetry (Nominal Fclk = 20 kHz, Tclk = 50 us)
Target: tt_um_ares_sentinel_project
================================================================================
"""

import sys
import os
import time
import socket
import json
import argparse

NOMINAL_PREAMBLE = 0xAAAAAAAA
NOMINAL_TYPE_1   = 0xD391
NOMINAL_TYPE_2   = 0xD391
NOMINAL_CONSTANT = 0x0DFFFFFE
NOMINAL_PAYLOAD  = "03391f8900f600b50094ae16"  # 96-bit payload (ID + Temp + Tail)

def build_stream_segments(bits, rx_toggle=True):
    """
    Encode binary bits into clock-cycle segments matching the demodulator strobe.
    Each bit: 9 cycles total, with s_clk pulsed for 1 cycle at cycle 4.
    """
    segments = []
    rx_val = 0
    for b in bits:
        if rx_toggle:
            rx_val = 1 - rx_val
        # 4 cycles pre-strobe
        segments.append((rx_val, 0, b, 4))
        # 1 cycle sample strobe
        segments.append((rx_val, 1, b, 1))
        # 4 cycles post-strobe
        segments.append((rx_val, 0, b, 4))
    return segments

class AttackerDaemon:
    def __init__(self, target_host="127.0.0.1", target_port=9099):
        self.target_host = target_host
        self.target_port = target_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def generate_scenario(self, attack_code):
        nominal_hex = f"{NOMINAL_PREAMBLE:08x}{NOMINAL_TYPE_1:04x}{NOMINAL_TYPE_2:04x}{NOMINAL_CONSTANT:08x}{NOMINAL_PAYLOAD}"
        nominal_int = int(nominal_hex, 16)
        nominal_bits = [int(b) for b in bin(nominal_int)[2:].zfill(192)]

        attack_meta = {
            "timestamp": time.time(),
            "attack_code": attack_code,
            "description": "",
            "cycles_profile": []
        }

        # ---------------------------------------------------------------------
        # AV00: Nominal Authenticated Transmission (192 bits, 20 kHz)
        # ---------------------------------------------------------------------
        if attack_code == "AV00_NOMINAL":
            attack_meta["description"] = "Nominal Authenticated Frame (192 bits, 20 kHz)"
            profile = [(0, 0, 0, 65), (1, 0, 0, 9), (0, 0, 0, 9)]
            profile.extend(build_stream_segments(nominal_bits))
            profile.append((0, 0, 0, 65))
            attack_meta["cycles_profile"] = profile

        # ---------------------------------------------------------------------
        # AV01: L1 Sub-Nyquist Runt Pulse Glitch (<= 7 cycles)
        # ---------------------------------------------------------------------
        elif attack_code == "AV01_RUNT_GLITCH":
            attack_meta["description"] = "L1 Attack: Sub-Nyquist Runt Pulse Glitch (4 cycles pulse width)"
            profile = [
                (0, 0, 0, 65),
                (1, 0, 0, 9),
                (0, 0, 0, 4),  # Runt glitch: 4 cycles (violates N_HB >= 8)
                (1, 0, 0, 9)
            ]
            attack_meta["cycles_profile"] = profile

        # ---------------------------------------------------------------------
        # AV02: L1 Stretched Pulse / Missing Edge Gap Timeout (>= 21 cycles)
        # ---------------------------------------------------------------------
        elif attack_code == "AV02_STRETCHED_PULSE":
            attack_meta["description"] = "L1 Attack: Stretched Pulse / Gap Timeout (25 cycles pulse width)"
            profile = [
                (0, 0, 0, 65),
                (1, 0, 0, 9),
                (0, 0, 0, 9),
                (0, 0, 0, 25), # Stretched gap: 25 cycles (violates N_BIT <= 20)
                (1, 0, 0, 9)   # Illegal resumption
            ]
            attack_meta["cycles_profile"] = profile

        # ---------------------------------------------------------------------
        # AV03: L1 Midband Timing Anomaly (11 <= N <= 15 cycles)
        # ---------------------------------------------------------------------
        elif attack_code == "AV03_MIDBAND":
            attack_meta["description"] = "L1 Attack: Midband Timing Anomaly (13 cycles pulse width)"
            profile = [
                (0, 0, 0, 65),
                (1, 0, 0, 9),
                (0, 0, 0, 13), # Forbidden midband deadband: 13 cycles
                (1, 0, 0, 9)
            ]
            attack_meta["cycles_profile"] = profile

        # ---------------------------------------------------------------------
        # AV04: L2 Preamble Bit-Flip Corruption
        # ---------------------------------------------------------------------
        elif attack_code == "AV04_PREAMBLE_TAMPER":
            attack_meta["description"] = "L2 Attack: Preamble Bit-Flip Corruption (Bit 10 mutated)"
            tampered_bits = list(nominal_bits)
            tampered_bits[10] = 1 - tampered_bits[10]
            profile = [(0, 0, 0, 65), (1, 0, 0, 9), (0, 0, 0, 9)]
            profile.extend(build_stream_segments(tampered_bits))
            profile.append((0, 0, 0, 65))
            attack_meta["cycles_profile"] = profile

        # ---------------------------------------------------------------------
        # AV05: L2 Protocol Type Field Mismatch
        # ---------------------------------------------------------------------
        elif attack_code == "AV05_TYPE_MUTATION":
            attack_meta["description"] = "L2 Attack: Protocol Type Field Mismatch (Bit 40 mutated to 0xCAFE)"
            tampered_bits = list(nominal_bits)
            tampered_bits[40] = 1 - tampered_bits[40]
            profile = [(0, 0, 0, 65), (1, 0, 0, 9), (0, 0, 0, 9)]
            profile.extend(build_stream_segments(tampered_bits))
            profile.append((0, 0, 0, 65))
            attack_meta["cycles_profile"] = profile

        # ---------------------------------------------------------------------
        # AV06: L2 Constant Security Field Corruption
        # ---------------------------------------------------------------------
        elif attack_code == "AV06_CONSTANT_CORRUPT":
            attack_meta["description"] = "L2 Attack: Constant Security Field Mutation (Bit 75 mutated)"
            tampered_bits = list(nominal_bits)
            tampered_bits[75] = 1 - tampered_bits[75]
            profile = [(0, 0, 0, 65), (1, 0, 0, 9), (0, 0, 0, 9)]
            profile.extend(build_stream_segments(tampered_bits))
            profile.append((0, 0, 0, 65))
            attack_meta["cycles_profile"] = profile

        # ---------------------------------------------------------------------
        # AV07: L2 Framing Premature Truncation (< 192 bits)
        # ---------------------------------------------------------------------
        elif attack_code == "AV07_TRUNCATION":
            attack_meta["description"] = "L2 Attack: Premature Transmission Truncation (Abort at bit 100)"
            profile = [(0, 0, 0, 65), (1, 0, 0, 9), (0, 0, 0, 9)]
            profile.extend(build_stream_segments(nominal_bits[:100]))
            profile.append((0, 0, 0, 65)) # Quiet line induces reception_active fall before 192b
            attack_meta["cycles_profile"] = profile

        # ---------------------------------------------------------------------
        # AV08: L2 Overrun Framing Flooding (> 192 bits)
        # ---------------------------------------------------------------------
        elif attack_code == "AV08_OVERRUN":
            attack_meta["description"] = "L2 Attack: Overrun Buffer Flooding (193rd sample strobe injected)"
            profile = [(0, 0, 0, 65), (1, 0, 0, 9), (0, 0, 0, 9)]
            profile.extend(build_stream_segments(nominal_bits))
            # Inject 193rd sample strobe while reception_active is still asserted
            profile.append((1, 0, 0, 4))
            profile.append((1, 1, 0, 1))
            profile.append((1, 0, 0, 4))
            profile.append((0, 0, 0, 65))
            attack_meta["cycles_profile"] = profile

        else:
            raise ValueError(f"Unknown attack code: {attack_code}")

        return attack_meta

    def inject_attack(self, attack_code):
        packet_data = self.generate_scenario(attack_code)
        payload = json.dumps(packet_data).encode("utf-8")
        self.sock.sendto(payload, (self.target_host, self.target_port))
        print(f"[ATTACKER] Injected: {attack_code} -> {packet_data['description']} ({len(payload)} bytes sent)")
        return packet_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARES-RX Sentinel Attack Injector Daemon")
    parser.add_argument("--attack", default="AV00_NOMINAL", help="Attack vector code (AV00_NOMINAL .. AV08_OVERRUN)")
    parser.add_argument("--host", default="127.0.0.1", help="Target receiver host")
    parser.add_argument("--port", type=int, default=9099, help="Target receiver port")
    args = parser.parse_args()

    daemon = AttackerDaemon(target_host=args.host, target_port=args.port)
    daemon.inject_attack(args.attack)
