#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Virtual Physical Channel & Transport Bridge
Milestone: M6 (Cyber-Physical Security Demonstrator)
Function: Emulates the physical channel / VLAN network transport between
          the Attacker Node and the Receiver Target, supporting physical
          latency, jitter modeling, and line observation.
================================================================================
"""

import socket
import json
import time
import random
import threading

class VirtualChannel:
    def __init__(self, listen_host="127.0.0.1", listen_port=9099,
                 target_host="127.0.0.1", target_port=9100,
                 simulated_delay_ms=2.0, jitter_ms=0.5):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.simulated_delay_ms = simulated_delay_ms
        self.jitter_ms = jitter_ms
        self.running = False
        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.sock_in.bind((self.listen_host, self.listen_port))
        self.running = True
        print(f"[VIRTUAL CHANNEL] Active: listening on {self.listen_host}:{self.listen_port} -> forwarding to {self.target_host}:{self.target_port}")
        
        while self.running:
            try:
                data, addr = self.sock_in.recvfrom(65535)
                # Simulate physical channel propagation delay & jitter
                delay = max(0.0001, (self.simulated_delay_ms + random.uniform(-self.jitter_ms, self.jitter_ms)) / 1000.0)
                time.sleep(delay)
                
                # Forward to receiver
                self.sock_out.sendto(data, (self.target_host, self.target_port))
            except Exception as e:
                if self.running:
                    print(f"[VIRTUAL CHANNEL ERROR] {e}")

    def stop(self):
        self.running = False
        self.sock_in.close()
        self.sock_out.close()

if __name__ == "__main__":
    channel = VirtualChannel()
    try:
        channel.start()
    except KeyboardInterrupt:
        channel.stop()
        print("\n[VIRTUAL CHANNEL] Stopped.")
