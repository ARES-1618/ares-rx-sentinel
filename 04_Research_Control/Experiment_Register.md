# Experiment Register (ER) — ARES-RX Sentinel

**Document ID**: `ARES-RC-ER-001`  
**Version**: `1.0.0-LOCKED`  
**Classification**: Test Protocol, Canonical Vectors & Experimental Manifest Ledger  
**Status**: **FROZEN / BINDING ON ALL DRAFTS**  

---

## 1. Experimental Methodology Overview

Verification and cyber-physical validation of ARES-RX Sentinel were conducted across three complementary layers:
1. **Behavioral vs. Gate-Level Concordance Layer**: Cycle-accurate co-simulation comparing a reference golden behavioral model (`ares_reference_model.py`) with the gate-level synthesized netlist across 10,737 discrete clock cycles and 118,107 individual signal evaluations.
2. **Canonical Vector Suite (AV00–AV08)**: 9 standardized physical and protocol-level scenarios covering nominal reception, temporal phase/edge violations, syntax corruption, and framing overrun/underflow.
3. **Cyber-Physical Network Namespace Emulation**: Execution in an isolated Linux network namespace (`netns`) under stochastic packet delay (`netem delay 5ms ± 1.2ms`), bound to a cryptographic SHA-256 provenance ledger.

---

## 2. Canonical Vector Manifest (AV00 – AV08)

All canonical vectors are defined in `06_Demonstration/cyber_physical/AV_Canonical_Vector_Manifest.yaml` and recorded in `06_Demonstration/m6b_isolated_vm_lab/m6_final_run_manifest.json`.

| Vector ID | Vector Name | Threat Classification | Total Cycles | Fault Cond. Cycle | Latched Cycle | $T_{\text{latch}}$ (cycles) | $T_{\text{isolate}}$ (cycles) | Safe Bus Out | Tamper Alert | Fault Code | Record Hash (SHA-256) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **AV00** | Nominal Authenticated Frame | Nominal Baseline | 1,876 | — | — | — | — | `0x55` | 0 | `3'b000` (NONE) | `6eaeb06cef96...591a` |
| **AV01** | Sub-Nyquist Runt Glitch | Layer-1 Temporal Integrity | 87 | 79 | 80 | 1 | 0 | `0x00` | 1 | `3'b001` (RUNT) | `00f27f1b83da...a66b` |
| **AV02** | Mid-band Phase Desynchronization | Layer-1 Temporal Integrity | 96 | 88 | 89 | 1 | 0 | `0x00` | 1 | `3'b010` (MIDBAND) | `09c00f5daf6e...170c` |
| **AV03** | Missing-Edge Gap Resumption | Layer-1 Temporal Integrity | 117 | 109 | 110 | 1 | 0 | `0x00` | 1 | `3'b011` (GAP_RES) | `7acab9978414...8f28` |
| **AV04** | Preamble Header Corruption | Layer-2 Frame Syntax Integrity | 1,876 | 178 | 179 | 1 | 0 | `0x00` | 1 | `3'b100` (PREAMBLE) | `dd0aed40fe9b...11e9` |
| **AV05** | Malformed Protocol Type Identifier | Layer-2 Frame Syntax Integrity | 1,876 | 448 | 449 | 1 | 0 | `0x00` | 1 | `3'b101` (TYPE) | `7316c67b1284...7ed2` |
| **AV06** | Security Field Constant Corruption | Layer-2 Frame Syntax Integrity | 1,876 | 763 | 764 | 1 | 0 | `0x00` | 1 | `3'b110` (CONSTANT) | `6d79bfd9fb40...9185` |
| **AV07** | Frame Truncation Underflow | Layer-2 Framing Boundary | 1,048 | 1,040 | 1,041 | 1 | 0 | `0x00` | 1 | `3'b111` (TRAILER) | `19cb94900c21...10ea` |
| **AV08** | Frame Overrun Overflow | Layer-2 Framing Boundary | 1,885 | 1,816 | 1,817 | 1 | 0 | `0x00` | 1 | `3'b111` (TRAILER) | `6f0d379d7499...33f0` |

### Detailed Vector Technical Mechanics:
- **AV00 (Nominal Baseline)**: Standard 192-bit Manchester frame with 32-bit preamble (`32'hAAAAAAAA`), valid protocol identifier, correct constant field, and nominal payload `0x55`. Accepted without fault latching; `tamper_alert = 0`, `safe_bus = 0x55`.
- **AV01 (Sub-Nyquist Runt Glitch)**: High-to-low transition pulse width $< N_{HB,min}$ (under 8 clock cycles). Trapped by temporal glitch counter; latching at cycle 80.
- **AV02 (Mid-band Phase Desynchronization)**: Half-bit transition arriving out-of-phase ($8 < \Delta t < 16$ cycles). Trapped by phase tracking window logic; latching at cycle 89.
- **AV03 (Missing-Edge Gap Resumption)**: Transition silent beyond maximum bit cell window ($> 20$ clock cycles) followed by sudden bit resumption. Trapped by gap watchdog; latching at cycle 110.
- **AV04 (Preamble Header Corruption)**: Preamble sequence bit inverted (`32'hAAAA_AAEA`). Trapped upon preamble lock phase; latching at cycle 179.
- **AV05 (Malformed Protocol Type Identifier)**: Unsupported protocol identifier byte injected into header. Trapped by header syntax decoder; latching at cycle 449.
- **AV06 (Security Field Constant Corruption)**: Required security constant byte altered from expected protocol value. Trapped by constant field comparator; latching at cycle 764.
- **AV07 (Frame Truncation Underflow)**: Frame terminated prematurely before expected 192-bit boundary followed by idle line. Trapped by frame length counter; latching at cycle 1041.
- **AV08 (Frame Overrun Overflow)**: Continuous stream of transitions extending past trailer boundary ($> 192$ bits). Trapped by trailer boundary detector; latching at cycle 1817.

---

## 3. Hardware Mutation Resilience Suite (M1 – M3)

To ensure the verification environment was not subject to false positive detection or superficial assertions, three targeted hardware mutations were injected into the synthesizable RTL:

| Mutation ID | Target Submodule | Mutated RTL Logic / Defect Injected | Operational Impact if Undetected | Detection Mechanism | Test Verdict |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **M1** | `ares_temporal_watchdog` | Modified glitch threshold window from $\Delta t < 8$ to $\Delta t < 4$. | Narrow glitches between 4–7 cycles would slip into decoder undetected. | Trapped by AV01 testbench assertion. | **TRAPPED (PASS)** |
| **M2** | `ares_frame_validator` | Forced frame length acceptance counter threshold to bypass trailer check. | Overrun and truncation attacks would not assert trailer fault. | Trapped by AV07 & AV08 assertions. | **TRAPPED (PASS)** |
| **M3** | `ares_isolation_gate` | Forced combinational pass-through bypass (`safe_bus = raw_bus` even if faulted). | Malicious payload delivered to host despite tamper alert. | Trapped by bus zeroization assertion. | **TRAPPED (PASS)** |

---

## 4. Cyber-Physical Testbench Execution Parameters

- **Execution Run ID**: `WO011R1-FINAL-20260927-225358`
- **Simulation Time Span**: 2026-09-27T22:53:58Z to 2026-09-27T22:54:05Z (7 seconds wall-clock runtime)
- **Host Platform**: Isolated Linux Kernel Namespace (`netns`)
- **Stochastic Channel Delay**: `tc qdisc add dev veth0 root netem delay 5ms 1.2ms seed 6904303736131909358`
- **Network Sample Observations**: 9 packets transmitted (one per canonical vector)
  - AV00 transport delta: $7.67\,\text{ms}$
  - AV01 transport delta: $2.19\,\text{ms}$
  - AV02 transport delta: $3.34\,\text{ms}$
  - AV03 transport delta: $5.49\,\text{ms}$
  - AV04 transport delta: $6.69\,\text{ms}$
  - AV05 transport delta: $6.71\,\text{ms}$
  - AV06 transport delta: $6.56\,\text{ms}$
  - AV07 transport delta: $6.16\,\text{ms}$
  - AV08 transport delta: $6.47\,\text{ms}$
  - *Epistemic Note*: The observed network latency range ($2.19 - 7.67\,\text{ms}$) reflects the configured synthetic stochastic transport model; 9 discrete samples are insufficient for statistical distribution claims.
- **Cryptographic Provenance**:
  - Final Block Hash / Root Anchor: `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0`
  - Unified Ledger File SHA-256: `04e154c2a9fe5d5ec6c7ce9cd19ffbb8732a4cd070367478ad447136328d1a0c`
