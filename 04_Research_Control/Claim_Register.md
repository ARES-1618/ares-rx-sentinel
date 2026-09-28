# Claim Register — ARES-RX Sentinel

**Document ID**: `ARES-RC-CR-001`  
**Version**: `1.0.0-LOCKED`  
**Status**: **FROZEN / BINDING ON ALL DRAFTS**  

---

## 1. Structure of the Claim Register

This register divides all possible technical statements regarding **ARES-RX Sentinel** into two disjoint sets:
- **Part A: Permitted & Grounded Claims** (empirically supported, bounded, and verified).
- **Part B: Forbidden Claims Register** (overclaims, out-of-boundary assertions, or ungrounded generalizations).
- **Part C: Epistemic Qualifying Rules** (mandatory phrasing constraints).

---

## 2. Part A: Permitted & Grounded Claims

### A.1 Architecture & Physical Boundary
1. **Digital Baseband Isolation**: ARES-RX Sentinel is a hardware-enforced pre-demodulation security and temporal sanitization filter placed between a raw digital demodulator input (`rx_in`) and downstream digital processing logic.
2. **Deterministic Response Timing**: The detection-to-latching latency is exactly 1 system clock cycle ($T_{\text{latch}}=1$). The isolation, zeroization, and alert assertion occur with zero additional RTL clock cycles ($T_{\text{isolate}}=0, T_{\text{safe}}=0$).
3. **Fail-Safe Bus Zeroization**: Upon detection of any temporal, syntactical, or boundary violation, the 8-bit output bus (`safe_data_out`) is synchronously clamped to `8'h00`, and `tamper_alert` is driven high until hardware reset.
4. **Minimal Gate Footprint**: Sentinel logic requires only 163 standard cells ($1,460.15\,\mu\text{m}^2$ net logic area), bringing the total integrated macro to 758 logic cells ($6,477.46\,\mu\text{m}^2$).

### A.2 Silicon Implementation & Physical Sign-Off (SkyWater 130nm)
1. **Target Envelope**: Implemented within the Tiny Tapeout TT08 $1 \times 1$ standard tile ($161.00\,\mu\text{m} \times 111.52\,\mu\text{m} = 17,954.72\,\mu\text{m}^2$).
2. **Placement Density**: Net placement density (RePlAce) is 63.99%; gross core utilization is 61.76%; gross tile logic utilization is 36.08%; gross tile placed utilization is 56.73%.
3. **Clock Tree & Static Timing**: The design easily closes timing at 50 MHz stress clock with positive setup slack (+11.88 ns reg-to-reg, +7.29 ns IO-constrained) and positive hold slack (+0.42 ns), yielding $F_{\text{max,reg}} = 123.15\,\text{MHz}$ and $F_{\text{max,io}} = 78.68\,\text{MHz}$.
4. **Physical Verification**: 100% Netgen LVS clean (764 devices, 776 nets, 45 pins). 0 active un-waived Magic DRC violations under documented internal project engineering waiver policy (874 raw pad/halo DRCs waived).

### A.3 Power Characterization
1. **Operational Power**: Post-route VCD-workload-derived power estimate is **57.90 nW at 20 kHz** ($\alpha = 0.1418$, TT/25°C/1.80V), consisting of 12.0 nW sequential, 42.8 nW combinational, and 3.10 nW static leakage.
2. **Security Overhead**: Introduces +12.70 nW (+28.1%) total power overhead and +0.58 nW static leakage overhead compared to the unprotected baseline (45.20 nW).
3. **Stress Condition**: At 50 MHz STA stress target, total power is 138.00 µW (vs 103.50 µW baseline).

### A.4 Verification & Resilience
1. **Canonical Test Suite**: Demonstrates 100% detection and isolation across 8 canonical attack scenarios (AV01–AV08) while passing nominal Manchester frames (AV00) without fault assertion.
2. **Cycle Concordance**: Validated across 10,737 discrete clock cycles and 118,107 observable signal evaluations with 100% trace concordance between high-level behavioral model and gate-level RTL.
3. **Mutation Resilience**: Traps 100% of synthetic hardware mutations (M1 glitch threshold, M2 frame boundary, M3 gate bypass).
4. **Cryptographic Provenance**: Anchored to a verifiable SHA-256 evidence ledger (final root anchor `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0`, ledger file hash `04e154c2a9fe5d5ec6c7ce9cd19ffbb8732a4cd070367478ad447136328d1a0c`).

---

## 3. Part B: Forbidden Claims Register

The following statements are strictly prohibited across all manuscripts, proposals, and summaries:

| Category | Strictly Forbidden Claim | Reason for Prohibition | Mandatory Remediation / Bounded Alternative |
| :--- | :--- | :--- | :--- |
| **Power** | "Silicon operational power confirmed" / "Measured silicon power" | Physical silicon has not yet been fabricated; empirical measurement on silicon is not available. | "Authoritative post-route VCD-workload-derived power estimate: 57.90 nW at 20 kHz." |
| **Power** | "Zero power overhead" / "Negligible energy" | The design has a quantified +28.1% (+12.70 nW) power overhead. | Explicitly report +12.70 nW (+28.1%) dynamic overhead and +0.58 nW leakage overhead. |
| **Fabrication** | "Silicon-proven" / "Fabricated ASIC validated" | Design is at post-route tapeout-ready sign-off status, not fabricated silicon. | "Pre-silicon tapeout-ready layout fully qualified through post-route physical sign-off." |
| **RF / Analog** | "Secures wireless radio frequency transmission" / "Anti-jamming hardware" | Sentinel does not possess an antenna, RF mixer, or analog filter; it operates on digital demodulated bitstreams. | "Secures digital baseband bitstream boundaries following RF demodulation." |
| **RF / Analog** | "Filters electromagnetic interference (EMI)" | EMI filtering occurs in the analog/RF domain; Sentinel is purely a digital synchronous logic block. | "Filters digital temporal glitches and invalid bit-cell transitions at the baseband level." |
| **Security Scope** | "Protects against all wireless cyber attacks" / "100% secure IoT device" | Overclaim. Sentinel addresses specific physical/link baseband manipulation vectors (AV01–AV08). | "Detects and isolates 8 canonical baseband attack vectors within 1 clock cycle." |
| **Software Scope**| "Guarantees host operating system memory safety" / "Eliminates all malware" | Sentinel isolates the baseband I/O bus; it does not audit host OS memory or application software. | "Prevents host MCU buffer overruns and interrupt storms caused by raw malformed baseband frames." |
| **Cryptography** | "Hardware cryptographic authentication" / "Encrypted data filter" | Sentinel provides protocol-level syntax and temporal sanitization, not cryptographic decryption or signature verification. | "Enforces hardware protocol syntax, temporal sanity, and boundary integrity checks." |
| **Certification** | "PERURI-certified microchip" / "National security standard silicon" | The project is an independent R&D technical proposal submitted for PERURI evaluation. | "Proposed sovereign microelectronics architecture tailored for high-assurance IoT ecosystems." |
| **Network** | "Statistically proven 5 ms transport latency" | The 9-sample network namespace testbench is insufficient for statistical distribution claims. | "Observed under a synthetic stochastic network emulation model (5 ms ± 1.2 ms delay)." |
| **Testbed Nomenclature** | "Hardware-in-the-loop (HIL)" / "Physical RF packet emulator" (for M6-B) | No physical RX hardware or physical RF transceiver exists in the current loop; M6 is purely an RTL co-simulation testbed. HIL is strictly reserved for future M6-C physical testbeds. | "Pre-silicon cyber-physical / RTL co-simulation demonstrator" |
| **Timing** | "Instantaneous isolation" / "Zero-time response" | Physical digital logic requires synchronous clock transitions; latching requires 1 cycle. | "Status kesalahan dikunci dalam 1 siklus logika; isolasi tidak menambah siklus tambahan." |

---

## 4. Part C: Epistemic Qualifying Rules

1. **Rule of Power Attribution**: Every mention of 57.90 nW must state that it is a *post-route VCD-workload-derived power estimate* at the 20 kHz operating point.
2. **Rule of Baseline Separation**: When comparing against baseline, the baseline must be identified as the unprotected demodulator (`tt07-bep-decode`, 45.20 nW, 594 stdcells).
3. **Rule of Timing Latency**: Latency must always be broken down into:
   - Detection/latching latency: $T_{\text{latch}} = 1\ \text{cycle}$ ($50\,\mu\text{s}$ at 20 kHz; $20\,\text{ns}$ at 50 MHz).
   - Isolation propagation: $T_{\text{isolate}} = 0\ \text{additional cycles}$ (combinational gating).
   - Safe bus stabilization: $T_{\text{safe}} = 0\ \text{additional cycles}$ (immediate zeroization).
4. **Rule of Nominal Acceptance**: AV00 must be described as: "Transmisi nominal AV00 diterima tanpa fault pada pengujian kanonik" / "Nominal baseline AV00 accepted without fault during canonical evaluation."
5. **Rule of Physical DRC**: Magic DRC must always be reported as: "0 active un-waived violations under documented internal project engineering waiver policy (874 raw pad/halo DRCs formally waived)."
