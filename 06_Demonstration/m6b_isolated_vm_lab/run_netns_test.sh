#!/usr/bin/env bash
# ==============================================================================
# Script: run_netns_test.sh
# Purpose: Authoritative Single-Run Execution of ARES M6-B Demonstrator
# Work Order: WO-2026-M6-ARCH-011R1: Evidence Identity & Timing Qualification Patch
# Authority: Technical Architect / Research Direction
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RUN_TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
RUN_ID="WO011R1-FINAL-${RUN_TIMESTAMP}"
RUN_START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "=================================================================================="
echo " ARES-RX SENTINEL: AUTHORITATIVE FINAL CAUSAL EVIDENCE RUN (WO-2026-M6-ARCH-011R1)"
echo " RUN_ID: ${RUN_ID} | START: ${RUN_START}"
echo "=================================================================================="

echo "[1/7] Verifying / Initializing Linux Network Namespaces & Physical Bridge..."
if ! ip netns list | grep -q "ns_receiver"; then
    echo "[*] Initializing isolated namespace topology..."
    bash ./setup_isolated_namespace.sh
fi

echo "[2/7] Capturing and Verifying Kernel Traffic Control (tc netem) Telemetry..."
QDISC_CONF=$(ip netns exec ns_attacker tc qdisc show dev veth_atk)
echo "[+] Active qdisc configuration: ${QDISC_CONF}"
echo "${QDISC_CONF}" > /tmp/netem_qdisc_config.txt

echo "[3/7] Initializing Single Authoritative Forensic Ledger..."
LEDGER_FILE="${SCRIPT_DIR}/m6_unified_evidence_ledger.jsonl"
rm -f "${LEDGER_FILE}"

echo "[4/7] Launching In-Line Causal Receiver Node in ns_receiver..."
ip netns exec ns_receiver python3 -u receiver_vm_node.py \
    --host 0.0.0.0 \
    --port 9100 \
    --count 9 \
    --run-id "${RUN_ID}" \
    --reset-ledger \
    --ledger "${LEDGER_FILE}" > /tmp/receiver_netns.log 2>&1 &
RX_PID=$!
echo "[+] Receiver PID: ${RX_PID}"
sleep 1

echo "[*] Network Namespace Verification for Receiver Process:"
ls -l "/proc/${RX_PID}/ns/net"
ip netns identify "${RX_PID}"

echo "[5/7] Emitting Canonical Vectors AV00-AV08 across isolated physical bridge..."
for v in AV00 AV01 AV02 AV03 AV04 AV05 AV06 AV07 AV08; do
    ip netns exec ns_attacker python3 attacker_vm_node.py \
        --target 192.168.100.20 \
        --port 9100 \
        --vector "$v" \
        --run-id "${RUN_ID}"
    sleep 0.15
done

sleep 1
echo "[6/7] Terminating Receiver Node..."
kill "${RX_PID}" 2>/dev/null || true
wait "${RX_PID}" 2>/dev/null || true
RUN_END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "=== RECEIVER EVALUATION LOG (FROM INSIDE ns_receiver) ==="
cat /tmp/receiver_netns.log

echo "[7/7] Auditing Single Authoritative Forensic Ledger & Generating Anchor..."
python3 -c "
import json, sys, hashlib, os

ledger_path = '${LEDGER_FILE}'
with open(ledger_path, 'r', encoding='utf-8') as f:
    lines = [json.loads(line) for line in f if line.strip()]

assert len(lines) == 9, f'Expected 9 records, found {len(lines)}'

print(f'Total Sealed Ledger Records: {len(lines)}')
print(f'Authoritative RUN_ID: {lines[0][\"payload\"][\"run_id\"]}')
print(f'Run Start: ${RUN_START} | Run End: ${RUN_END}')
print(f'Genesis Hash: {lines[0][\"prev_record_hash\"]}')
assert lines[0]['prev_record_hash'] == '0000000000000000000000000000000000000000000000000000000000000000'

prev = lines[0]['prev_record_hash']
for idx, entry in enumerate(lines):
    # Verify prev link
    assert entry['prev_record_hash'] == prev, f'Chain broken at index {idx}'
    # Verify hash integrity
    serialized = json.dumps(entry['payload'], sort_keys=True, separators=(',', ':'))
    computed = hashlib.sha256((prev + serialized).encode('utf-8')).hexdigest()
    assert computed == entry['record_hash'], f'Record hash corruption at index {idx}'
    prev = entry['record_hash']

    # Invariants audit
    p = entry['payload']
    assert p['decoded_stimulus_hash'] == p['canonical_stimulus_hash'], f'Invariant C mismatch on {p[\"vector_id\"]}'
    assert len(p['baseband_input_trace_hash']) == 64, f'Invariant D missing baseband hash on {p[\"vector_id\"]}'
    assert len(p['rtl_trace_hash']) == 64, f'Invariant E missing rtl hash on {p[\"vector_id\"]}'
    assert p['run_id'] == '${RUN_ID}', f'Run ID mismatch on {p[\"vector_id\"]}'
    dt = p['network_trace']['packet_transport_delta_ms']
    print(f'  [{p[\"vector_id\"]}] Delay: {dt:.3f} ms | C_cond: {p[\"latency_semantics\"][\"fault_condition_cycle\"]} | C_latch: {p[\"latency_semantics\"][\"fault_latched_cycle\"]} | Bus: {p[\"isolation_response\"][\"safe_bus_output\"]} | H_bb: {p[\"baseband_input_trace_hash\"][:12]}... | Hash: {entry[\"record_hash\"][:16]}...')

final_anchor = lines[-1]['record_hash']
print('=' * 82)
print(f'AUTHORITATIVE FINAL LEDGER ANCHOR: {final_anchor}')
print('=' * 82)

# Copy authoritative ledger to cyber_physical directory for unified single-source evidence
cyber_ledger = os.path.abspath(os.path.join('${SCRIPT_DIR}', '..', 'cyber_physical', 'm6_unified_evidence_ledger.jsonl'))
with open(cyber_ledger, 'w', encoding='utf-8') as f:
    for entry in lines:
        f.write(json.dumps(entry) + '\n')
print(f'[+] Synchronized authoritative ledger to: {cyber_ledger}')

# Write Run Manifest
manifest = {
    'run_id': '${RUN_ID}',
    'run_start': '${RUN_START}',
    'run_end': '${RUN_END}',
    'qdisc_config': '${QDISC_CONF}',
    'final_anchor': final_anchor,
    'record_count': len(lines),
    'records': [
        {
            'index': idx,
            'vector_id': l['payload']['vector_id'],
            'category': l['payload']['category'],
            'canonical_stimulus_hash': l['payload']['canonical_stimulus_hash'],
            'packet_payload_hash': l['payload']['packet_payload_hash'],
            'baseband_input_trace_hash': l['payload']['baseband_input_trace_hash'],
            'rx_in_trace_hash': l['payload']['rx_in_trace_hash'],
            'rtl_trace_hash': l['payload']['rtl_trace_hash'],
            'packet_tx_iso': l['payload']['network_trace']['packet_tx_iso'],
            'packet_rx_iso': l['payload']['network_trace']['packet_rx_iso'],
            'transport_delta_ms': l['payload']['network_trace']['packet_transport_delta_ms'],
            'timing_qualification': l['payload']['transport_telemetry']['timing_qualification'],
            'fault_condition_cycle': l['payload']['latency_semantics']['fault_condition_cycle'],
            'fault_latched_cycle': l['payload']['latency_semantics']['fault_latched_cycle'],
            'isolation_effective_cycle': l['payload']['latency_semantics']['isolation_effective_cycle'],
            'safe_output_cycle': l['payload']['latency_semantics']['safe_output_cycle'],
            'latch_latency_cycles': l['payload']['latency_semantics']['latch_latency_cycles'],
            'isolation_latency_cycles': l['payload']['latency_semantics']['isolation_latency_cycles'],
            'safe_output_latency_cycles': l['payload']['latency_semantics']['safe_output_latency_cycles'],
            'safe_bus_output': l['payload']['isolation_response']['safe_bus_output'],
            'record_hash': l['record_hash'],
            'prev_record_hash': l['prev_record_hash']
        }
        for idx, l in enumerate(lines)
    ]
}
with open(os.path.join('${SCRIPT_DIR}', 'm6_final_run_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)
print('[+] Authoritative Run Manifest written to: m6_final_run_manifest.json')
"
echo "=== AUTHORITATIVE DEMONSTRATOR RUN COMPLETE ==="
