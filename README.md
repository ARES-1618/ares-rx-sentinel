# ARES-RX Sentinel — Tiny Tapeout TT08 Hardware Security Boundary

[![Tiny Tapeout](https://img.shields.io/badge/Tiny%20Tapeout-TT08-blue)](https://tinytapeout.com)
[![PDK](https://img.shields.io/badge/PDK-SkyWater%20130nm-green)](https://github.com/google/skywater-pdk)
[![Internal CI](https://img.shields.io/badge/Internal%20CI-Passing%20(Runs%2036320019363%2C%2036320019357)-brightgreen)](#8-continuous-integration-provenance)
[![Tile](https://img.shields.io/badge/Tile-1%C3%971%20(161.00%20%C2%B5m%20%C3%97%20111.52%20%C2%B5m)-orange)](#4-post-route-silicon-benchmark--power-reconciliation)
[![Power](https://img.shields.io/badge/Power%20(Est.)-57.90%20nW%20%40%2020%20kHz-blueviolet)](#4-post-route-silicon-benchmark--power-reconciliation)
[![Fabrication Status](https://img.shields.io/badge/Silicon%20Fabrication-PENDING-yellow)](#9-epistemic-boundary)

---

## 1. Title and System Identification

* **Project Title:** ARES-RX Sentinel: Hardware Receiver Security Guard
* **Submission Target:** Tiny Tapeout TT08 Shuttle (SkyWater 130nm `sky130_fd_sc_hd` standard cell library)
* **Top Module:** `tt_um_ares_sentinel_project`
* **Silicon Commit:** `a748738cf665e63bc9c215748ee5bead18422665` (Tree: `4bd810d39c4968e376843287a277080976e337bc`)
* **Primary Provenance:** Work Order `WO-2026-M5F-AUDIT-002` / Dossier `WO-2026-M6-QC-012`

---

## 2. Description and Security Rationale

The **ARES-RX Sentinel** is a synthesizable Verilog hardware security perimeter designed to protect 433 MHz Sub-GHz RF receivers (such as remote keyless entry, critical infrastructure telemetry, and secure industrial transceivers) against physical-layer baseband glitches, clock desynchronization, and malformed frame injection attacks. Conventional receiver architectures rely on microcontrollers or firmware running software protocol parsers; when subjected to adversarial baseband glitching or corrupted preambles, these software parsers suffer from catastrophic failure modes including interrupt storms, buffer overflows, and state machine lockups. ARES-RX Sentinel intercepts raw demodulated digital baseband signals directly at the digital CMOS boundary before they can reach the host application processor. By enforcing a dual-condition hardware verification formulation ($V_{\text{trusted}} = V_{\text{physical}} \land V_{\text{protocol}}$) in deterministic silicon logic, Sentinel guarantees that any physical timing anomaly or protocol syntax violation triggers a fail-closed hardware isolation gate within 1 clock cycle ($50.0\,\mu\text{s}$ at 20 kHz nominal clock, with an estimated $\approx 1.2\,\text{ns}$ physical combinational path), zeroizing the output bus and asserting a non-maskable sticky tamper alert to safeguard downstream systems.

---

## 3. Architecture Overview

ARES-RX Sentinel implements a **3-layer defence-in-depth** hardware pipeline between the external digital baseband demodulator and the downstream host microcontroller interface:

```text
                                  ARES-RX SENTINEL
                     Demodulated Digital Baseband Security Guard
                     
     +-----------------------------------------------------------------------+
     | ui_in[0] (rx_in)                                                      |
     | [Digital Baseband Input from Sub-GHz RF Demodulator - Digital CMOS]   |
     +------------------------------------+----------------------------------+
                                          |
                                          v
     +=======================================================================+
     | LAYER 1: TEMPORAL SENTINEL (ares_timing_sentinel.v)                   |
     |  - Pulse duration & interval counter (20 kHz sampling clock)          |
     |  - Runt Glitch Detection: Pulse width N <= 7 clock cycles             |
     |  - Mid-Band Desync Detection: 11 <= N <= 15 clock cycles              |
     |  - Missing-Edge Detection: Inter-edge interval N >= 21 clock cycles   |
     +------------------------------------+----------------------------------+
                                          | Valid Transitions
                                          v
     +=======================================================================+
     | LAYER 2: FRAME SYNTAX MONITOR FSM (ares_frame_fsm.v)                  |
     |  - Preamble Sync Lock: Strict 32-bit alternating pattern (0xAAAAAAAA) |
     |  - Protocol Type Identifier: Enforces mandatory Type ID (0xD391)      |
     |  - Constant Header Verification: Validates fixed field (0x0DFFFFFE)   |
     |  - Frame Length & Boundary Guard: Exactly 192 bits (bounds check)     |
     |  - Truncation (<192 bits) & Overrun (>192 bits) Trap States          |
     +------------------------------------+----------------------------------+
                                          |
                        +-----------------+-----------------+
                        | Temporal Fault                    | Syntactic Fault
                        v                                   v
     +=======================================================================+
     | LAYER 3: FAIL-CLOSED ISOLATION SUBSYSTEM                              |
     |  [Priority Fault Arbiter & Sticky Hardware Latch]                     |
     |  (ares_fault_arbiter.v, ares_fault_latch.v, ares_isolation_gate.v)    |
     |                                                                       |
     |  +-----------------------------------------------------------------+  |
     |  | Deterministic 1-Cycle Fault Latch (T_latch = 1 cycle / 50.0 us) |  |
     |  | Combinational Zeroization (T_isolate ~ 1.2 ns gate delay model) |  |
     |  +-----------------------------------------------------------------+  |
     +--------------------+-----------------------------+--------------------+
                          |                             |
                          | Clean Frame                 | Latched Fault
                          v                             v
           +------------------------------+   +------------------------------+
           | Parallel Safe Bus: uo_out[7:0]|   | Tamper Flag:  uio_out[6]     |
           | [Verified Payload to MCU]    |   | [Non-Maskable Hardware Alert]|
           | (On Fault: Bus = 8'h00)      |   | (Asserted = 1 until rst_n)   |
           +------------------------------+   +------------------------------+
```

### Layer-by-Layer Functional Description

* **Layer 1: Temporal Sentinel (`ares_timing_sentinel.v`):**  
  Layer 1 continuously monitors the raw digital baseband stream on `ui_in[0]`, measuring every pulse duration and inter-edge interval using a calibrated counter clocked at 20 kHz. It traps physical anomalies including high-frequency runt glitches ($N \le 7$ cycles), mid-band desynchronization pulses ($11 \le N \le 15$ cycles), and missing-edge transmission dropouts ($N \ge 21$ cycles). By discarding timing deviations before baseband decoding occurs, Layer 1 shields downstream logic from clock recovery corruption and physical injection attacks.

* **Layer 2: Frame Syntax Monitor FSM (`ares_frame_fsm.v`):**  
  Layer 2 enforces strict protocol grammar on the Manchester-decoded bitstream through a deterministic state machine. It validates the mandatory 32-bit preamble sequence (`0xAAAAAAAA`), extracts frame synchronization, validates the 16-bit protocol Type Identifier (`0xD391`), checks the 32-bit constant header field (`0x0DFFFFFE`), and guards exact 192-bit frame length boundaries. Any syntactic error, header corruption, premature truncation underflow ($<192$ bits), or payload overrun overflow ($>192$ bits) triggers an immediate transition into a non-recoverable error trap state.

* **Layer 3: Fail-Closed Isolation Subsystem (`ares_fault_arbiter.v`, `ares_fault_latch.v`, `ares_isolation_gate.v`, `ares_isolation_l3.v`):**  
  Layer 3 arbitrates concurrent fault signals, latches detected violations into sticky hardware registers, and manages output bus quarantine. When any Layer 1 or Layer 2 fault is detected, the subsystem latches the fault within exactly 1 clock cycle ($50.0\,\mu\text{s}$) and combinational gates immediately clamp the 8-bit parallel output bus (`uo_out[7:0]`) to `0x00`. Concurrently, it asserts the dedicated active-high `tamper_alert` pin (`uio_out[6]`), which remains persistently locked until an explicit external hardware reset (`rst_n`) is applied.

---

## 4. Post-Route Silicon Benchmark & Power Reconciliation

All physical layout metrics and power estimates are derived from sign-off post-route OpenLane and OpenSTA implementations targeting the SkyWater 130nm process node.

### 4.1 Post-Route Benchmark Summary Table

| Metric / Parameter | Value | Source & Verification Scope |
|:---|:---|:---|
| **Authoritative Power Estimate (Primary)** | **57.90 nW** @ 20 kHz ($1.8\,\text{V}$) | **Authoritative post-route VCD-workload-derived power estimate: 57.90 nW at the 20 kHz operating point. This is not a fabricated-silicon power measurement.** |
| **Secondary Static Power Sweep** | **50.90 nW** @ 20 kHz ($1.8\,\text{V}$) | **Secondary static activity sweep estimate (Scenario A, $\alpha=0.075$). Preserved in sealed `docs/info.md` for Tiny Tapeout portal display.** |
| **Die Gross Tile Dimensions** | $161.00\,\mu\text{m} \times 111.52\,\mu\text{m}$ ($1\times 1$ Tile) | Standard Tiny Tapeout TT08 shuttle slot ($A_{\text{tile}} = 17,954.72\,\mu\text{m}^2$) |
| **Standard Cell Logic Area ($A_{\text{logic}}$)** | $6,477.46\,\mu\text{m}^2$ ($36.08\%$ gross tile) | OpenLane post-route sign-off summary |
| **Total Placed Movable Area** | $10,186.02\,\mu\text{m}^2$ ($56.73\%$ gross tile) | `PlaceInstsArea` (including macro margins) |
| **Standard Logic Cell Count** | 758 logic cells (741 movable + 17 CTS buffers) | Netgen 1.5.133 reports 764 devices including tapcells |
| **Core Whitespace & Filler Cells** | 1,547 filler cells ($34.76\%$ whitespace) | Fillers inserted for DRC antenna & density rules |
| **Operating Frequency ($F_{\text{nom}}$ / $F_{\max}$)** | $20\,\text{kHz}$ nominal / $\approx 123.7\,\text{MHz}$ max | OpenSTA sign-off static timing analysis |
| **Setup Slack (@ 50 MHz Stress Clock)** | **$+11.88\,\text{ns}$** (WNS = $0.00\,\text{ns}$) | OpenSTA timing report (Stress test 2,500× above nominal) |
| **Hold Slack (@ 50 MHz Stress Clock)** | **$+0.42\,\text{ns}$** (MET) | OpenSTA min-delay timing report |
| **Routing Geometry** | Wirelength: $19,988\,\mu\text{m}$, Vias: 5,970 | Detailed routing sign-off metrics |
| **Design Rule Check (DRC)** | **0 active violations** | 874 raw / 874 waived / 0 un-waived under project engineering waiver policy |
| **Layout vs. Schematic (LVS)** | **100% Structural Instance Match** | Netgen 1.5.133: 764/764 devices, 776/776 nets, 45/45 pins (`Circuits match uniquely`) |
| **Sealed Physical Commit** | `a748738cf665e63bc9c215748ee5bead18422665` | Manifest: `00_Governance/M5_Physical_Manifest.sha256` |

### 4.2 Power Methodology Reconciliation Note

To maintain absolute epistemic integrity across all documentation layers, the discrepancy between the power figure reported in `docs/info.md` and this technical README is reconciled as follows:

* **Authoritative Operating Point (Scenario B — 57.90 nW):**  
  Documented in `05_ASIC_Synthesis/results/power_reconciliation.md` (`ARES-ASIC-M5F-PWR-001`, Work Order `WO-2026-M5F-AUDIT-002`). This figure is derived by applying authentic post-route VCD switching activity traces (`ares_sentinel_integrated.vcd`, 16,695 cycles) through OpenSTA. The empirical toggle rate on `rx_in` is $\alpha = 0.1418$ transitions/cycle ($\alpha_{\text{prob}} = 0.0709$, duty cycle = 0.50).
  * Sequential Dynamic Power: $12.0\,\text{nW}$ ($20.7\%$)
  * Combinational Dynamic Power: $42.8\,\text{nW}$ ($73.9\%$)
  * Dynamic Switching Total: $54.8\,\text{nW}$ ($94.7\%$)
  * Static Leakage Power: $3.10\,\text{nW}$ ($5.3\%$)
  * **Total Simulated Model Power (Scenario B):** **$57.90\,\text{nW}$** ($+12.70\,\text{nW}$ / $+28.1\%$ security overhead compared to unprotected baseline receiver of $45.20\,\text{nW}$).
  * Stress Operating Point (at 50 MHz): $138.00\,\mu\text{W}$.

* **Preserved Portal Display Estimate (Scenario A — 50.90 nW):**  
  The sealed file `docs/info.md` records **$50.90\,\text{nW}$** at 20 kHz. This represents an earlier static activity sweep estimate assuming an unweighted arbitrary toggle factor $\alpha = 0.075$. Because `docs/info.md` is cryptographically sealed under `M5_Physical_Manifest.sha256` (hash `0888d516933a06a5db558d7597fd8339dda1cc495ceacff425d1aec93b213085`) for the Tiny Tapeout automated catalog ingestion portal, it remains untouched as a secondary benchmark.

* **Mandatory Epistemic Classification:**  
  Both figures are pre-silicon post-route simulation models. Neither figure is a fabricated-silicon measurement. Fabricated silicon power measurements are strictly **NOT AVAILABLE** because physical chip fabrication is currently **PENDING**.

---

## 5. Pin and Signal Mapping

The complete pinout mapping is established directly from `05_ASIC_Synthesis/tt08_submission_repo/info.yaml`:

### 5.1 Dedicated Inputs (`ui_in[7:0]`)

| Pin Index | Signal Name | Type | Description |
|:---:|:---|:---:|:---|
| `ui_in[0]` | `rx_in` | Input | Digital demodulated baseband input from Sub-GHz RF receiver front-end (**strictly a digital CMOS GPIO input**, not an analog antenna port). |
| `ui_in[1]` | *Reserved* | Input | Unused in design (tied low internally). |
| `ui_in[2]` | `halt` | Input | Active-high system halt / enable gating control. When low, output bus is masked. |
| `ui_in[3]` | *Reserved* | Input | Unused in design (tied low internally). |
| `ui_in[4]` | `address[0]` | Input | Target receiver destination address bit 0. |
| `ui_in[5]` | `address[1]` | Input | Target receiver destination address bit 1. |
| `ui_in[6]` | `address[2]` | Input | Target receiver destination address bit 2. |
| `ui_in[7]` | `address[3]` | Input | Target receiver destination address bit 3. |

### 5.2 Dedicated Outputs (`uo_out[7:0]`)

| Pin Index | Signal Name | Type | Description |
|:---:|:---|:---:|:---|
| `uo_out[0]` | `data_out[0]` | Output | Parallel verified payload data bus bit 0. Clamped to `0` when `tamper_alert` is active. |
| `uo_out[1]` | `data_out[1]` | Output | Parallel verified payload data bus bit 1. Clamped to `0` when `tamper_alert` is active. |
| `uo_out[2]` | `data_out[2]` | Output | Parallel verified payload data bus bit 2. Clamped to `0` when `tamper_alert` is active. |
| `uo_out[3]` | `data_out[3]` | Output | Parallel verified payload data bus bit 3. Clamped to `0` when `tamper_alert` is active. |
| `uo_out[4]` | `data_out[4]` | Output | Parallel verified payload data bus bit 4. Clamped to `0` when `tamper_alert` is active. |
| `uo_out[5]` | `data_out[5]` | Output | Parallel verified payload data bus bit 5. Clamped to `0` when `tamper_alert` is active. |
| `uo_out[6]` | `data_out[6]` | Output | Parallel verified payload data bus bit 6. Clamped to `0` when `tamper_alert` is active. |
| `uo_out[7]` | `data_out[7]` | Output | Parallel verified payload data bus bit 7. Clamped to `0` when `tamper_alert` is active. |

### 5.3 Dedicated Bidirectional Pins (`uio_out[7:0]`, `uio_oe[7:0] = 8'b11111111`)

All 8 bidirectional I/O pins are configured as active dedicated outputs (`uio_oe = 0xFF`):

| Pin Index | Signal Name | Output Function |
|:---:|:---|:---|
| `uio[0]` | `baseline_full` | Receiver buffer status flag (FIFO full indicator from baseband deserializer). |
| `uio[1]` | `manchester_clock` | Recovered Manchester synchronization clock output. |
| `uio[2]` | `manchester_data` | Recovered serial baseband Manchester data bitstream. |
| `uio[3]` | `transmission_begin` | Pulse indicator marking start of valid preamble detection. |
| `uio[4]` | `base_neg_edge` | Diagnostic falling edge pulse strobe from baseband edge detector. |
| `uio[5]` | `base_pos_edge` | Diagnostic rising edge pulse strobe from baseband edge detector. |
| `uio[6]` | `tamper_alert` | **Non-maskable sticky tamper alert flag.** Asserted high (`1`) upon any Layer 1/2 violation; locked until hardware reset (`rst_n`). |
| `uio[7]` | `reception_active` | Frame reception in progress indicator. |

---

## 6. How-to-Test Instructions

The verification testbench in `test/` uses **Cocotb** and **Icarus Verilog** to run automated cycle-accurate simulations of the design wrapper.

### 6.1 Prerequisites and Setup

Ensure Python 3, `iverilog`, and `cocotb` are installed:

```bash
pip install cocotb pytest
```

Navigate to the test suite directory:

```bash
cd test
```

### 6.2 Test 1: Nominal Frame Transmission Test

* **Test Objective:** Verify that a legitimate Manchester-encoded frame with a valid 32-bit preamble (`0xAAAAAAAA`) completes without false alarms (`tamper_alert == 0`).
* **Execution Command:**
  ```bash
  make clean && make SIM=icarus
  ```
* **Execution Details (`test_nominal_transmission` in `test.py`):**
  1. Configures nominal clock frequency: $20\,\text{kHz}$ ($\text{period} = 50,000\,\text{ns}$).
  2. Asserts reset (`rst_n = 0`) for 10 cycles, then releases reset.
  3. Transmits lead-in arming sequence followed by 32 Manchester bits representing `0xAA` octets (9 cycles high, 9 cycles low per half-bit).
  4. Verifies observable signals:
     * `tamper_alert == 0` (no false positive)
     * Parallel output bus available to host MCU.
* **Expected Output:**
  ```text
  test_nominal_transmission passed: tamper_alert = 0
  ```

### 6.3 Test 2: Adversarial Glitch Injection Test

* **Test Objective:** Verify that an injected runt pulse (< 8 clock cycles) is trapped by Layer 1, causing deterministic fail-closed output zeroization and sticky tamper alert latching.
* **Execution Command:**
  ```bash
  make clean && make SIM=icarus
  ```
* **Execution Details (`test_runt_glitch_rejection` in `test.py`):**
  1. Sets up and arms the DUT.
  2. Injects a 4-clock-cycle runt glitch on `ui_in[0]` (violating the minimum valid Manchester half-bit width of $\ge 8$ cycles).
  3. Waits 3 clock cycles for edge detector, timing classifier, and fault latching pipeline propagation.
  4. Asserts:
     * `tamper_alert == 1` (sticky hardware latch active)
     * `uo_out[7:0] == 0x00` (parallel data bus zeroized)
* **Expected Output:**
  ```text
  test_runt_glitch_rejection passed: tamper_alert = 1, uo_out = 0x00
  ** TESTS=2 PASS=2 FAIL=0 SKIP=0 **
  ```

### 6.4 Gate-Level Simulation (Post-Route)

To run the post-route gate-level simulation against the synthesized netlist:

```bash
make GATES=yes
```

---

## 7. M6 Cyber-Physical Evidence Summary

ARES-RX Sentinel has completed comprehensive pre-silicon cyber-physical / RTL co-simulation demonstrator verification documented in dossier `WO-2026-M6-QC-012` and sealed in the immutable M6 Evidence Package.

* **Final Execution Run ID:** `WO011R1-FINAL-20260927-225358`
* **Test Platform:** Isolated Linux network namespace (`netem`) pre-silicon baseband stream generator linked to cycle-accurate RTL co-simulation.
* **Trace Concordance:** **100.0%** concordance across 10,737 discrete clock cycles and 118,107 individual signal evaluations.
* **Synchronous Latching Latency ($T_{\text{latch}}$):** Exactly 1 clock cycle ($50.0\,\mu\text{s}$) at the synchronous RTL abstraction.
* **Combinational Isolation Latency ($T_{\text{isolate}}$):** $\approx 1.2\,\text{ns}$ gate delay model (OpenSTA post-route static timing).
* **Final Ledger Anchor Hash:**
  ```text
  6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0
  ```
  *(Sealed in `06_Demonstration/m6b_isolated_vm_lab/m6_unified_evidence_ledger.jsonl`).*
* **Full Demonstration Dossier:** Refer to [`06_Demonstration/PERURI_CYBER_PHYSICAL_DEMO_DOSSIER.md`](../../06_Demonstration/PERURI_CYBER_PHYSICAL_DEMO_DOSSIER.md).

### 7.1 Canonical Attack Vector Summary (AV00–AV08)

| Vector ID | Attack Class / Stimulus Category | Injected Anomaly Parameter | Simulated Cycles | Trigger Cycle ($C_{\text{fault}}$) | Latch Cycle ($C_{\text{latch}}$) | Tamper Alert | Data Bus (`uo_out`) | Security Verdict |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **AV00** | Nominal Transmission | Clean 433 MHz packet | 1,876 | N/A | N/A | `0` | `0x55` | `ACCEPTED_NOMINAL` |
| **AV01** | Runt Glitch Attack | Pulse width $N \le 7$ cycles | 87 | 79 | 80 | `1` | `0x00` | `MITIGATED_TRAPPED` |
| **AV02** | Mid-Band Clock Desync | Pulse width $11 \le N \le 15$ | 96 | 88 | 89 | `1` | `0x00` | `MITIGATED_TRAPPED` |
| **AV03** | Missing-Edge Inter-Frame Gap | Interval $N \ge 21$ cycles | 117 | 109 | 110 | `1` | `0x00` | `MITIGATED_TRAPPED` |
| **AV04** | Preamble Sync Corruption | Preamble $\neq \text{0xAAAAAAAA}$ | 1,876 | 178 | 179 | `1` | `0x00` | `MITIGATED_TRAPPED` |
| **AV05** | Malformed Protocol Type ID | Type ID $\neq \text{0xD391}$ | 1,876 | 448 | 449 | `1` | `0x00` | `MITIGATED_TRAPPED` |
| **AV06** | Constant Header Corruption | Header $\neq \text{0x0DFFFFFE}$ | 1,876 | 763 | 764 | `1` | `0x00` | `MITIGATED_TRAPPED` |
| **AV07** | Frame Truncation Underflow | Frame length $< 192$ bits | 1,048 | 1040 | 1041 | `1` | `0x00` | `MITIGATED_TRAPPED` |
| **AV08** | Frame Overrun Overflow | Frame length $> 192$ bits | 1,885 | 1816 | 1817 | `1` | `0x00` | `MITIGATED_TRAPPED` |

---

## 8. Continuous Integration Provenance

Automated verification of the submission repository is tracked via GitHub Actions workflows:

* **GDS Synthesis & Precheck Workflow (`.github/workflows/gds.yaml`):**
  * **Remote CI Run ID:** `36320019363`
  * **Status:** PASS (precheck, documentation syntax, GDS/DEF deliverable checks completed)
* **Functional & Glitch Test Workflow (`.github/workflows/test.yaml`):**
  * **Remote CI Run ID:** `36320019357`
  * **Status:** PASS (Cocotb simulation, nominal transmission, and runt glitch tests verified clean)

> **Important Provenance Qualification:**  
> GitHub Actions Runs `36320019363` and `36320019357` document **internal project remote CI provenance**. They confirm that the design repository passes automated simulation, linting, and packaging workflows on remote runners. They **DO NOT** constitute official Tiny Tapeout portal catalog acceptance, nor do they represent SkyWater foundry tapeout sign-off or silicon manufacturing approval.

---

## 9. Epistemic Boundary

To guarantee scientific rigor, audit transparency, and prevent misinterpretation, the following epistemic boundaries are established for all claims regarding ARES-RX Sentinel:

1. **TT08 Silicon Fabrication Status: PENDING**  
   The physical layout (GDSII, DEF, SPEF) and synthesizable Verilog source files are frozen, validated, and sealed. However, physical wafer manufacturing by SkyWater Technology under the Tiny Tapeout TT08 shuttle is **PENDING**. No physical silicon chips currently exist.

2. **Silicon Power Measurement: NOT AVAILABLE**  
   No fabricated silicon chips have been packaged or bench-tested. Any laboratory measurement of physical chip power is strictly **NOT AVAILABLE**.

3. **Nature of Power Figures ($57.90\,\text{nW}$ vs $50.90\,\text{nW}$):**  
   The primary power metric of **$57.90\,\text{nW}$** at 20 kHz is an **authoritative post-route VCD-workload-derived power estimate** generated by OpenSTA using switching activity from simulated authentic frame workloads (`ares_sentinel_integrated.vcd`). This is not a fabricated-silicon power measurement. The secondary figure of **$50.90\,\text{nW}$** is a static activity sweep estimate ($\alpha = 0.075$) preserved in the sealed `docs/info.md` file for Tiny Tapeout portal compliance.

4. **Scope of M6 Cyber-Physical Evidence:**  
   The M6 evidence package confirms 100.0% concordance across 9 canonical attack vectors within an isolated Linux network namespace emulating baseband packet transport. This represents **bounded empirical verification** of digital RTL and gate-level logic behavior. It does not model analog RF propagation, antenna impedance mismatch, environmental thermal noise, or long-term semiconductor aging.

5. **Internal CI vs External Acceptance:**  
   Gate B CI pass status (Runs `36320019363` and `36320019357`) demonstrates internal automated build and test health. It does not constitute Tiny Tapeout portal shuttle acceptance or foundry sign-off.

6. **Epistemic Invariance Axiom:**  
   ```text
   M6 Evidence Sealed ≠ Tiny Tapeout Portal Accepted ≠ Silicon Validated
   ```
