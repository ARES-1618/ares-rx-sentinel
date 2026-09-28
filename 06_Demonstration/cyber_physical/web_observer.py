#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Live Web Observer & Telemetry Server
Milestone: M6 (Cyber-Physical Security Demonstrator)
Function: Provides HTTP server and live REST endpoints for the real-time
          oscilloscope dashboard and cryptographic evidence chain display.
================================================================================
"""

import sys
import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
from attacker_daemon import AttackerDaemon
from receiver_node import ReceiverNode
from virtual_channel import VirtualChannel

LATEST_EVENT = {
    "status": "INITIALIZING",
    "verdict": "READY",
    "attack_code": "AV00_NOMINAL",
    "description": "System Ready — Waiting for transmission or attack injection.",
    "tamper_asserted": False,
    "hardware_zeroized": False,
    "safe_data_out": "0x00",
    "signature_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "waveform": []
}

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            html_path = os.path.join(SCRIPT_DIR, "dashboard.html")
            if os.path.exists(html_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        elif parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(LATEST_EVENT).encode("utf-8"))
        elif parsed.path == "/api/ledger":
            ledger_path = os.path.join(SCRIPT_DIR, "evidence_chain_ledger.jsonl")
            records = []
            if os.path.exists(ledger_path):
                with open(ledger_path, "r") as f:
                    for line in f:
                        if line.strip():
                            records.append(json.loads(line.strip()))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(records[-30:]).encode("utf-8"))  # Return last 30
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/inject":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                attack_code = data.get("attack", "AV00_NOMINAL")
                attacker = AttackerDaemon(target_host="127.0.0.1", target_port=9099)
                attacker.inject_attack(attack_code)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "SUCCESS", "injected": attack_code}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ERROR", "message": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence routine HTTP access logs
        return

def on_hardware_telemetry(record, waveform):
    global LATEST_EVENT
    LATEST_EVENT = dict(record)
    LATEST_EVENT["waveform"] = waveform

def start_observer_services(http_port=8080):
    # Step 1: Start Virtual Channel
    vchannel = VirtualChannel(listen_port=9099, target_port=9100)
    vchan_thread = threading.Thread(target=vchannel.start, daemon=True)
    vchan_thread.start()

    # Step 2: Start Receiver Target Node
    receiver = ReceiverNode(listen_port=9100, callback=on_hardware_telemetry)
    rx_thread = threading.Thread(target=receiver.start, daemon=True)
    rx_thread.start()

    # Step 3: Start HTTP Server
    server = HTTPServer(("0.0.0.0", http_port), DashboardHandler)
    print(f"\n================================================================================")
    print(f" ARES-RX SENTINEL CYBER-PHYSICAL DEMONSTRATOR ACTIVE")
    print(f" Web Observer Dashboard available at: http://localhost:{http_port}")
    print(f"================================================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping demonstrator services...")
        receiver.stop()
        vchannel.stop()
        server.server_close()

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start_observer_services(http_port=port)
