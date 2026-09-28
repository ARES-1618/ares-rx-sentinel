# ARES-RX Sentinel: A 57.90 nW Hardware-Enforced Pre-Demodulation Security and Temporal Sanitization Architecture for Ultra-Low-Power Sub-GHz IoT Basebands in 130nm CMOS

---

**Authors**: Ahmad Fauzi, et al.  
**Target Publication**: IEEE Transactions on Very Large Scale Integration (VLSI) Systems / IEEE Transactions on Information Forensics and Security  
**Manuscript Classification**: Regular Paper  
**Process Technology**: SkyWater 130nm CMOS High-Density (`sky130_fd_sc_hd`)  
**Design Status**: Pre-Silicon Tapeout-Ready Sign-off Complete (M5-F Reconciled / M6 Bound)  
**Ledger Provenance Root Anchor**: `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0`  
**Ledger File SHA-256**: `04e154c2a9fe5d5ec6c7ce9cd19ffbb8732a4cd070367478ad447136328d1a0c`  

---

## Abstract

Resource-constrained wireless nodes deployed in critical Internet of Things (IoT) infrastructure—such as smart supply chains, sovereign track-and-trace credentials, and remote sensor arrays—face severe physical-layer vulnerabilities at the digital baseband boundary. Existing receiver architectures rely either on software-level interrupt service routines, which are susceptible to sub-Nyquist glitch-induced interrupt storms and CPU starvation, or on post-DMA bus firewalls that act too late to prevent peripheral destabilization. Furthermore, lightweight cryptographic engines fail to detect physical timing violations and expose nodes to severe denial-of-sleep battery exhaustion attacks. 

This paper presents **ARES-RX Sentinel**, a hardware-enforced pre-demodulation security and temporal sanitization macro engineered for sub-microwatt sub-GHz wireless receivers. Implemented in open-source SkyWater 130nm CMOS, Sentinel operates at the demodulated digital serial baseband boundary (`rx_in`), validating temporal bit-cell geometry, preamble lock, protocol type, security constants, and framing limits in real time. Upon detecting an anomaly, the architecture synchronously latches the fault condition in exactly one clock cycle ($T_{\text{latch}}=1$) and isolates the output bus via combinational zeroization ($T_{\text{isolate}}=0$), permanently forcing the safe data bus to `8'h00` and asserting a persistent tamper alert without incurring additional latency. 

Post-route characterization using OpenRCX parasitic extraction and OpenSTA under authentic VCD switching activity demonstrates an authoritative operational power consumption of **57.90 nW at 20 kHz** (1.80V, TT, 25°C), representing a modest +12.70 nW (+28.1%) dynamic overhead relative to an unprotected baseline demodulator, with only 3.10 nW static leakage. The design integrates 758 logic cells ($6,477.46\,\mu\text{m}^2$) into a standardized Tiny Tapeout TT08 $1 \times 1$ die envelope ($161.00 \times 111.52\,\mu\text{m}$) with a net placement density of **63.99%**, and closes static timing at a 50 MHz stress target with +11.88 ns register-to-register setup slack ($F_{\text{max,reg}} = 123.15\,\text{MHz}$). Pre-silicon cyber-physical / RTL co-simulation demonstrator evaluation across 10,737 discrete clock cycles and 118,107 signal evaluations demonstrates 100% detection and isolation across 8 canonical attack scenarios (AV01–AV08) while passing nominal Manchester frames (AV00) without fault assertion, verified against a tamper-evident SHA-256 cryptographic provenance ledger.

*Index Terms*—Hardware security, ultra-low-power (ULP), baseband receiver, sub-GHz IoT, temporal sanitization, denial-of-sleep defense, SkyWater 130nm CMOS, open-source ASIC.

---

## I. Introduction

The proliferation of battery-less and energy-harvesting Internet of Things (IoT) edge devices has made low-power wireless communications pervasive across critical civilian and industrial infrastructures. Applications ranging from electronic customs tracking and high-value sovereign logistics seals to national smart utility meters increasingly operate within strict sub-microwatt ($< 1\,\mu\text{W}$) average power envelopes. In these ultra-low-power (ULP) operating regimes, sub-GHz radio links (e.g., 433 MHz, 868/915 MHz) employing robust Manchester or Frequency Shift Keying (FSK) modulations are preferred due to their superior propagation range, obstacle penetration, and minimal baseband processing complexity.

However, modern low-power wireless receiver architectures exhibit a fundamental **architectural vulnerability at the physical digital baseband boundary**. In conventional system-on-chip (SoC) receiver designs, the analog radio front-end delivers an asynchronous, demodulated digital bitstream directly to the general-purpose input/output (GPIO) pins or a hardware timer peripheral of a host microcontroller unit (MCU). Because the baseband signal path lacks hardware-level temporal validation and frame syntax gating, adversaries can exploit the radio channel to conduct destructive low-energy physical-layer attacks. 

Specifically, by injecting sub-Nyquist runt glitches, deliberate mid-band phase slips, or malformed preamble headers, an attacker can trigger thousands of false edge transitions per second. In firmware-based receivers, this results in catastrophic **interrupt storms** that consume 100% of available CPU cycles, trigger watchdog resets, and increase active power dissipation from microwatts to tens of milliwatts ($4.0 - 16.5\,\text{mW}$), depleting coin-cell batteries in days. Even in receivers equipped with commercial hardware decoders, malformed frames are blindly assembled and forwarded to internal FIFO buffers or DMA controllers, causing buffer overruns and locking the communication peripheral into unrecoverable error states that require full system resets.

While on-chip bus interconnect firewalls (e.g., ARM TrustZone, AXI/AHB bus filters) and lightweight cryptographic accelerators (e.g., SIMON, SPECK, PRESENT) have been proposed to safeguard embedded systems, they operate at the wrong abstraction boundaries:
1. **Bus firewalls** intervene at the system bus interconnect, *after* the baseband peripheral has already ingested and buffered the corrupted frame; furthermore, their substantial area footprint ($5,000 - 25,000$ gates) is incompatible with minimal baseband dies.
2. **Cryptographic engines** enforce message confidentiality and payload authenticity at higher protocol layers, but they cannot detect physical-layer timing violations. More critically, an adversary can broadcast continuous sequences of invalid frames, forcing the cryptographic hardware to continuously expend energy evaluating cryptographic signatures—a fatal vector known as a **denial-of-sleep attack**.

### The Sub-Microwatt Pre-Demodulation Gap
To date, no hardware architecture in the literature provides multi-layer temporal, syntactical, and framing sanity enforcement directly at the digital baseband boundary within a sub-100 nW power budget and with cycle-accurate deterministic isolation.

### Contributions
To resolve this gap, this paper introduces **ARES-RX Sentinel**, an open-source, hardware-enforced pre-demodulation security and temporal sanitization architecture. The specific technical contributions of this work are:

1. **Sub-100 nW Multi-Layer Hardware Sanitization Architecture**: We design and implement a dedicated digital baseband protection wrapper that performs real-time temporal pulse-width checking (Layer-1), frame syntax decoding (Layer-2), and boundary overrun/underflow monitoring (Layer-2) within an authoritative post-route power envelope of **57.90 nW at 20 kHz** in open-source SkyWater 130nm CMOS.
2. **Zero-Additional-Cycle Bus Isolation ($T_{\text{isolate}}=0$)**: We introduce a fail-safe combinational zeroization gate synchronized with a single-cycle fault latch ($T_{\text{latch}}=1$). Upon detecting any temporal or protocol violation, the output data bus is synchronously forced to `8'h00` and a persistent tamper interrupt is asserted, mathematically guaranteeing that malformed data cannot propagate to downstream registers or host processors.
3. **Pre-Crypto Energy Gatekeeping**: By isolating corrupt bitstreams prior to higher-layer processing, Sentinel shields downstream cryptographic accelerators and host MCUs from processing invalid packets, eliminating denial-of-sleep attacks and preserving system battery life.
4. **Silicon-Ready Physical Sign-off in SkyWater 130nm**: We present complete physical implementation results within the Tiny Tapeout TT08 standardized tile envelope ($161.00 \times 111.52\,\mu\text{m}$), demonstrating 63.99% net core placement density, clean 50 MHz stress timing closure (+11.88 ns slack), 100% Netgen LVS match, and zero active un-waived Magic DRC violations.
5. **Reproducible Cyber-Physical Verification with Cryptographic Chaining**: We validate the architecture across 9 canonical test vectors (AV00–AV08) and 3 targeted hardware mutants (M1–M3) in an isolated network namespace environment across 10,737 clock cycles and 118,107 signal evaluations, anchoring the complete empirical evidence trail to a SHA-256 Merkle ledger (`6f0d379d...733f0`).

---

## II. Related Work & Literature Gap Analysis

Securing resource-constrained wireless nodes requires balancing energy dissipation, silicon area, and defensive determinism. Table I establishes a systematic comparative framework contrasting ARES-RX Sentinel against the six prevailing paradigms in the literature.

### A. Taxonomy of Existing Paradigms
1. **Software-Based Sub-GHz Security & Firmware Filtering**: In software-centric stacks (e.g., Contiki-NG, RIOT-OS, FreeRTOS), bit transitions on a GPIO pin trigger interrupt service routines (ISRs) on a micro-core (such as ARM Cortex-M0+ or RISC-V RV32EC). Because pulse timing is sampled via software timers, interrupt latency ($100\,\mu\text{s} - 10\,\text{ms}$) introduces severe jitter. Under malicious glitch injection, interrupt overhead starves the application thread, causing system lockup and elevating active power to $4.0 - 16.5\,\text{mW}$ [1]–[3].
2. **Standard Hardware Decoders & Commercial ASICs**: Dedicated transceivers (e.g., TI CC1101, Semtech SX127x) employ hardwired correlators and deserializers [4]. However, these ASICs are optimized purely for nominal communication efficiency. When subjected to mid-frame phase slippage or illegal pulse gaps, they either forward corrupted bita to FIFO registers or enter hung states requiring register resets via SPI, lacking hardware-enforced isolation [5].
3. **On-Chip Bus Interconnect Firewalls**: Systems utilizing ARM TrustZone-M, SANCUS, or RISC-V Physical Memory Protection (PMP) filter memory transactions at the system bus interconnect [6]–[8]. Operating post-DMA, they cannot prevent baseband peripheral buffer corruption or interrupt saturation, and their high gate complexity ($5,000 - 25,000$ gates) is unsuited for compact baseband dies.
4. **Ultra-Low-Power Cryptographic Micro-Engines**: Lightweight cryptographic accelerators (e.g., SIMON, SPECK, PRESENT, Grain-128a) provide message authentication codes (MACs) at $1.5 - 25.0\,\mu\text{W}$ [9]–[11]. However, verifying a cryptographic MAC requires hundreds to thousands of cycles. Attackers can broadcast continuous streams of invalid preambles, forcing the crypto engine into perpetual calculation and draining node energy without ever establishing a valid session.
5. **Physical-Layer (PHY) RF Anomaly Detection**: Techniques utilizing high-speed I/Q sampling, RSSI transient analysis, or convolutional neural networks (CNNs) classify RF fingerprint anomalies [12]–[14]. While effective against spoofing at the transmitter level, the required high-speed ADCs and DSP coprocessors consume $10 - 250\,\text{mW}$, rendering them entirely impractical for sub-microwatt edge devices.
6. **Ultra-Low-Power Wake-Up Receivers (WuRx)**: Dedicated wake-up receivers consume between $20 - 100\,\text{nW}$ by leveraging analog envelope detectors and minimal correlators [15]–[17]. However, they lack multi-layer protocol sanity checking, making them vulnerable to false wake-up flooding that negates their sleep-state energy advantages.

### TABLE I: Comprehensive 6-Axis Comparative Literature Gap Matrix (TAB-01)

| Category / Paradigm | Axis 1: Operating Enforcement Layer | Axis 2: Energy Footprint (Power Envelope) | Axis 3: Reaction & Isolation Latency | Axis 4: Determinism & Temporal Predictability | Axis 5: Silicon Gate & Area Overhead | Axis 6: Dominant Vulnerability Under Adversarial Manipulation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. SW Sub-GHz / MCU Filtering** | Software application & ISR layer | $4.0 - 16.5\,\text{mW}$ (Active MCU state) | $100\,\mu\text{s} - 10\,\text{ms}$ (Interrupt handling) | Low (Subject to ISR jitter, cache misses, scheduling) | Zero ASIC gates (requires 4–16 KB SRAM/Flash) | Interrupt storms, CPU starvation, stack/heap buffer overflow |
| **2. Standard HW Decoders** | Digital baseband deserializer | $1.0 - 10.0\,\mu\text{W}$ (Standard baseband) | Multi-byte to packet-length delay | Medium (Fixed FSM, but zero fault isolation) | Medium (1,000–3,000 gates) | Blind FIFO buffering of malformed data, decoder lockup |
| **3. Bus Interconnect Firewalls** | System bus interconnect (AXI/AHB) | $50\,\mu\text{W} - 5\,\text{mW}$ (Bus clock dependent) | $5 - 20$ system bus cycles | High (Synchronous bus arbitration) | High ($5,000 - 25,000$ gates, $> 0.05\,\text{mm}^2$) | Post-DMA execution; powerless against baseband peripheral crash |
| **4. Crypto Micro-Engines** | Cryptographic payload layer (L3/L4) | $1.5 - 25.0\,\mu\text{W}$ (Lightweight crypto) | $500 - 5,000$ clock cycles | High (Constant-time execution) | High ($2,500 - 8,000$ gates) | Pre-crypto DoS, battery exhaustion via repeated MAC checks |
| **5. PHY RF Anomaly / Fingerprint** | Pre-demodulation RF/Analog front-end | $10.0 - 250.0\,\text{mW}$ (High-speed ADC + DSP) | Tens of microseconds to symbol periods | Stochastic (Probabilistic classification drift) | Very High (Mixed-signal, $> 1.0\,\text{mm}^2$) | Prohibitive power cost; channel fading false trips |
| **6. ULP Wake-Up Receivers (WuRx)** | Analog envelope detector / Baseband | $20 - 100\,\text{nW}$ (Ultra-low power) | Fast wake-up ($10 - 50\,\mu\text{s}$), no isolation | Poor (Zero protocol verification) | Very Low ($200 - 500$ gates) | Trivial denial-of-sleep, false wake-up flooding |
| **ARES-RX Sentinel (Proposed)** | **Physical digital baseband boundary (`rx_in`)** | **57.90 nW @ 20 kHz (Post-route VCD estimate)** | **$T_{\text{latch}}=1$ cycle, $T_{\text{isolate}}=0$ cycles** | **Absolute (Cycle-accurate synchronous RTL, zero jitter)** | **Ultra-Compact (163 added logic cells, 758 total, $0.018\,\text{mm}^2$)** | **Bounded to digital baseband; fails safe to `8'h00` on any fault** |

---

## III. Threat Model & Hardware Security Properties

### A. System Boundary and Attacker Capabilities
ARES-RX Sentinel is positioned strictly at the digital demodulated baseband input boundary (`rx_in`), directly following the analog envelope detector or RF mixer. 

- **Attacker Profile**: We assume an active radio adversary equipped with a software-defined radio (SDR) capable of arbitrary sub-GHz RF transmission within transmission range of the node. The attacker can transmit validly modulated signals, malformed bit patterns, out-of-spec transition intervals, and rapid transient bursts.
- **Out of Scope**: Attacks targeting the analog RF front-end (e.g., out-of-band RF jamming, physical side-channel power analysis of the core, physical decapsulation) are outside the scope of this digital baseband architecture.

### B. Threat Vector Formalization
The threat space encompasses three distinct failure categories:
1. **Layer-1 Temporal Violations**: Attacks manipulating the time-domain characteristics of the Manchester-encoded waveform:
   - *Sub-Nyquist Runt Glitches (AV01)*: Pulses narrower than the minimum half-bit duration ($t_{\text{pulse}} < N_{HB,min} \cdot T_{\text{clk}}$), designed to provoke metastability or trigger interrupt storms.
   - *Mid-band Phase Desynchronization (AV02)*: Illegal transition edges occurring outside the valid clock recovery window ($N_{HB,max} < t < N_{BIT,min}$), inducing deserializer bit slips.
   - *Missing-Edge Gap Resumption (AV03)*: Illegal line silence exceeding maximum bit cell duration followed by sudden pulse resumption without a proper preamble sequence.
2. **Layer-2 Frame Syntax Corruption**:
   - *Preamble Corruption (AV04)*: Bit flips within the mandatory 32-bit synchronization sequence (`32'hAAAAAAAA`).
   - *Protocol Type Mismatch (AV05)*: Injection of unsupported or reserved protocol type identifier bytes.
   - *Constant Security Field Manipulation (AV06)*: Alteration of fixed protocol security constants.
3. **Layer-2 Framing Boundary Violations**:
   - *Frame Truncation Underflow (AV07)*: Premature termination of data transmission before the expected 192-bit payload boundary.
   - *Frame Overrun Overflow (AV08)*: Continued bit transmission beyond the defined trailer boundary, intended to cause receiver FIFO buffer overflow.

### C. Hardware Security Properties
The architecture guarantees the following formal invariants:
- **Property 1 (Single-Cycle Fault Latching)**: Let a violation condition be asserted combinational logic at clock cycle $N$. The internal fault register strictly latches the error on clock cycle $N+1$:
  $$T_{\text{latch}} = t_{\text{latched}} - t_{\text{condition}} = 1\ \text{cycle}$$
- **Property 2 (Zero-Additional-Cycle Isolation)**: The combinational isolation gate clamps the external data bus to zero in the exact cycle the fault is latched:
  $$T_{\text{isolate}} = t_{\text{isolate}} - t_{\text{latched}} = 0\ \text{cycles}$$
- **Property 3 (Deterministic Fail-Safe Zeroization)**: Under any asserted fault, the output bus is guaranteed to be clamped to a safe quiescent state:
  $$\forall t \ge t_{\text{latched}}, \quad \text{safe\_data\_out}[7:0] = 8\text{'h00}, \quad \text{tamper\_alert} = 1$$

---

## IV. ARES-RX Sentinel System Architecture

ARES-RX Sentinel is structured as a hierarchical hardware wrapper that encapsulates the baseline Manchester demodulator core (`tt07-bep-decode`). Fig. 1 illustrates the system integration and boundary interfaces.

```
+---------------------------------------------------------------------------------------------------+
|                                 ARES-RX SENTINEL ASIC TOP LEVEL                                   |
|                                                                                                   |
|                      +-----------------------------------------------------+                      |
|                      |             LAYER-1 TEMPORAL SANITIZATION           |                      |
|                      |  +-----------------------+  +--------------------+  |                      |
|   rx_in (Pin) ------>|  |  ares_edge_detector   |->|ares_temporal_w和服务|  |                      |
|   (20 kHz Bitstream) |  +-----------------------+  +--------------------+  |                      |
|                      +------------------------|----------------------------+                      |
|                                               | Violation                                         |
|                      +------------------------v----------------------------+                      |
|                      |              LAYER-2 SYNTAX & FRAMING               |                      |
|                      |  +-----------------------------------------------+  |                      |
|                      |  |             ares_frame_validator              |  |                      |
|                      |  |     (Preamble, Type, Constant, Boundary)      |  |                      |
|                      |  +-----------------------------------------------+  |                      |
|                      +------------------------|----------------------------+                      |
|                                               | Fault Strobe                                      |
|                      +------------------------v----------------------------+                      |
|                      |            FAULT CONTROLLER & LATCH (L3)            |                      |
|                      |  +-----------------------------------------------+  |                      |
|                      |  |             ares_fault_controller             |  |                      |
|                      |  |      (Priority Encoder & Sticky Latch)        |  |                      |
|                      |  +---------------------|-------------------------+  |                      |
|                      +------------------------|----------------------------+                      |
|                                               | tamper_alert / fault_code                         |
|   +--------------------------+                |                                                   |
|   |   Baseline Manchester    |                v                                                   |
|   |      BEP Demodulator     |----->[ 0 ]\                                                        |
|   |    (tt07-bep-decode)     |            |==MUX==> safe_data_out[7:0] (To Host MCU Bus)          |
|   +--------------------------+----->[ 1 ]/                                                        |
|                                       ^                                                           |
|                                       | (ares_isolation_gate: Clamped to 8'h00 if Tampered)       |
+---------------------------------------------------------------------------------------------------+
```
*Fig. 1. Architectural block diagram of ARES-RX Sentinel, illustrating pipelined detection stages and zero-overhead combinational bus zeroization.*

### Interface Specification
The top-level module conforms to the standard Tiny Tapeout TT08 pinout interface:
- **`ui_in[0]` (`rx_in`)**: Asynchronous/synchronous serial baseband input from demodulator front-end.
- **`ui_in[4:7]` (`address[0:3]`)**: Static device address strapping.
- **`uo_out[7:0]` (`safe_data_out[7:0]`)**: Sanitized parallel data output bus presented to the host MCU.
- **`uio_out[0]` (`tamper_alert`)**: Active-high hardware interrupt indicating a latched security fault.
- **`uio_out[3:1]` (`fault_code[2:0]`)**: 3-bit diagnostic fault classification code.

---

## V. RTL Implementation & Hardware Circuitry

The architecture is implemented in synthesizable IEEE 1364-2001 Verilog, decomposed into five specialized submodules:

### A. Synchronous Edge Detector (`ares_edge_detector`)
To eliminate metastability from asynchronous baseband inputs, `rx_in` is passed through a two-stage synchronizer flip-flop chain. Edge transitions are evaluated synchronously:
```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        rx_sync_0 <= 1'b0;
        rx_sync_1 <= 1'b0;
        rx_prev   <= 1'b0;
    end else begin
        rx_sync_0 <= rx_in;
        rx_sync_1 <= rx_sync_0;
        rx_prev   <= rx_sync_1;
    end
end
assign edge_detected = (rx_sync_1 ^ rx_prev);
```

### B. Temporal Watchdog Counter (`ares_temporal_watchdog`)
This module enforces Layer-1 temporal sanity. A free-running counter tracks elapsed clock cycles between consecutive transitions:
- If `edge_detected` asserts when `cycle_counter < 8`, `fault_runt` is immediately pulsed.
- If `edge_detected` asserts when $10 < \text{cycle\_counter} < 16$, `fault_midband` is asserted.
- If no edge occurs for $> 20$ cycles, the FSM transitions to idle; an edge occurring during quiet inter-frame gaps ($N_{EOF} = 64$) triggers `fault_gap_res`.

### C. Protocol Syntax Validator (`ares_frame_validator`)
As deserialized bita emerge from the Manchester decoder, `ares_frame_validator` monitors packet structure:
- **Preamble Detector**: Evaluates whether the incoming bit pattern locks onto `32'hAAAAAAAA`. Any inverted bit asserts `fault_preamble`.
- **Type & Constant Comparators**: Checks that `type_byte == EXPECTED_TYPE` and `const_field == SECURITY_CONST`, asserting `fault_type` or `fault_const` on mismatch.
- **Frame Length Watchdog**: Counts processed payload bits. If the frame terminates before bit 192, `fault_trailer` is asserted (underflow); if transitions continue past bit 192 without an EOF silence, `fault_trailer` is asserted (overflow).

### D. Fault Controller & Priority Encoder (`ares_fault_controller`)
The fault controller integrates all error flags via a synchronous priority encoder. Once triggered, the fault status is sticky until hardware reset:
```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        tamper_alert_r <= 1'b0;
        fault_code_r   <= 3'b000;
    end else if (!tamper_alert_r) begin
        if (fault_runt) begin
            tamper_alert_r <= 1'b1; fault_code_r <= 3'b001;
        end else if (fault_midband) begin
            tamper_alert_r <= 1'b1; fault_code_r <= 3'b010;
        end else if (fault_gap_res) begin
            tamper_alert_r <= 1'b1; fault_code_r <= 3'b011;
        end else if (fault_preamble) begin
            tamper_alert_r <= 1'b1; fault_code_r <= 3'b100;
        end else if (fault_type) begin
            tamper_alert_r <= 1'b1; fault_code_r <= 3'b101;
        end else if (fault_const) begin
            tamper_alert_r <= 1'b1; fault_code_r <= 3'b110;
        end else if (fault_trailer) begin
            tamper_alert_r <= 1'b1; fault_code_r <= 3'b111;
        end
    end
end
```

### E. Combinational Bus Isolation Gate (`ares_isolation_gate`)
The isolation gate multiplexes the raw decoder bus with a constant zero vector:
```verilog
assign safe_data_out = (tamper_alert_r) ? 8'h00 : raw_decoder_data;
```
Because `safe_data_out` is driven combinationally from `tamper_alert_r`, isolation occurs with zero additional RTL clock cycles ($T_{\text{isolate}}=0$).

---

## VI. Verification Methodology & Cyber-Physical Testbench

Verification was executed across two synchronized environments:
1. **Behavioral vs. Gate-Level Concordance Co-simulation**: A cycle-accurate Python golden reference model (`ares_reference_model.py`) was co-simulated alongside the synthesized gate-level Verilog netlist using Icarus Verilog 12 and cocotb.
2. **Cyber-Physical Network Namespace Emulation**: To evaluate realistic asynchronous network-to-ASIC interactions, the verification pipeline was deployed in an isolated Linux Kernel Network Namespace (`netns`). A virtual attacker node streamed canonical stimulus through an emulated channel configured with stochastic delay (`netem delay 5ms ± 1.2ms`) to the receiver testbench.

All test executions were automatically recorded into an append-only cryptographic JSONL ledger, where each record hashes the previous block hash, input stimulus hash, execution timestamps, and cycle evaluations using SHA-256.

---

## VII. Physical Design & PPA Characterization (SkyWater 130nm)

Physical implementation was conducted targeting the SkyWater 130nm high-density library (`sky130_fd_sc_hd`) using the open-source OpenROAD flow.

### A. Geometrical Area Decomposition & Four-Tier Utilization Hierarchy
To ensure absolute mathematical consistency, physical dimensions and utilization ratios are strictly decomposed into four distinct tiers, as summarized in Table II:
- **Gross Tile Area ($A_{\text{tile}}$)**: Standard TT08 $1 \times 1$ die envelope of $161.00\,\mu\text{m} \times 111.52\,\mu\text{m} = \mathbf{17,954.72\,\mu\text{m}^2}$.
- **Gross Core Area ($A_{\text{core}}$)**: Core bounding box ($[2.76, 2.72]$ to $[158.24, 108.80]\,\mu\text{m}$) yielding $\mathbf{16,493.32\,\mu\text{m}^2}$.
- **Fixed Infrastructure Area ($A_{\text{fixed}}$)**: Dedicated area for 225 substrate well taps and 78 decap cells totaling $\mathbf{574.30\,\mu\text{m}^2}$.
- **Net Placeable Area ($A_{\text{placeable\_net}}$)**: Remaining row area for standard cells: $A_{\text{core}} - A_{\text{fixed}} = \mathbf{15,919.02\,\mu\text{m}^2}$.

### TABLE II: Physical Implementation & Sign-off Scorecard (TAB-03)

| Physical Metric | Baseline (`tt07-bep-decode`) | ARES Sentinel Top | Overhead ($\Delta$) | Provenance & Engine |
| :--- | :---: | :---: | :---: | :--- |
| **Gross Die Envelope ($A_{\text{tile}}$)** | $161.00 \times 111.52\,\mu\text{m}$ | $161.00 \times 111.52\,\mu\text{m}$ | $0.00\,\mu\text{m}$ | Standard TT08 Tile |
| **Total Functional Logic Cells** | 594 | 758 | $+164$ cells | Yosys 0.52 synthesis |
| **Clock Tree Buffers (CTS)** | 9 | 17 | $+8$ buffers | TritonCTS |
| **Total Placed Instances** | 603 | 766 | $+163$ instances | OpenROAD P&R |
| **Net Logic Cell Area ($A_{\text{logic}}$)** | $5,017.31\,\mu\text{m}^2$ | $6,477.46\,\mu\text{m}^2$ | $+1,460.15\,\mu\text{m}^2$ | Pure gate silicon |
| **Movable Placed Cell Area** | $7,945.12\,\mu\text{m}^2$ | $10,186.02\,\mu\text{m}^2$ | $+2,240.90\,\mu\text{m}^2$ | Stdcells + CTS buffers |
| **[Tier 1] Net Core Density** | **49.91%** | **63.99%** | $+14.08\%$ | OpenROAD RePlAce `[INFO GPL-0019]` |
| **[Tier 2] Gross Core Box Util.** | **48.17%** | **61.76%** | $+13.59\%$ | Movable cells / $A_{\text{core}}$ |
| **[Tier 3] Gross Tile Logic Util.** | **27.94%** | **36.08%** | $+8.14\%$ | $A_{\text{logic}} / A_{\text{tile}}$ |
| **[Tier 4] Gross Tile Placed Util.**| **44.25%** | **56.73%** | $+12.48\%$ | Placed area / $A_{\text{tile}}$ |
| **Total Routed Wirelength** | $21,208\,\mu\text{m}$ (4,803 vias) | $19,988\,\mu\text{m}$ (5,970 vias) | $-1,220\,\mu\text{m}$ | TritonRoute |
| **Detailed Route DRC** | 0 violations | 0 violations | 0 violations | TritonRoute |
| **Magic Sign-off DRC** | 859 raw / 0 active | 874 raw / 0 active | 0 active | 874 raw waived under policy |
| **Netgen 1.5.133 LVS** | 100% Match | 100% Match | 100% Match | 764 dev, 776 nets, 45 pins |

### B. Static Timing Analysis (STA)
Static timing closure was performed under Typical-Typical conditions (TT / 25°C / 1.80V) using OpenSTA with distributed OpenRCX 3D parasitics:
- **Operational Protocol Clock ($20\,\text{kHz}$)**: Meets all setup/hold constraints with microseconds of positive margin.
- **Stress Target ($50\,\text{MHz}$)**: Reg-to-reg setup slack is **$+11.88\,\text{ns}$** ($F_{\text{max,reg}} = 123.15\,\text{MHz}$); IO-constrained setup slack is **$+7.29\,\text{ns}$** ($F_{\text{max,io}} = 78.68\,\text{MHz}$). Hold slack is positive across all paths (**$+0.42\,\text{ns}$**), with zero Worst Negative Slack ($WNS = 0.00\,\text{ns}$).

### C. Post-Route Power Characterization
Table III presents the power characterization under authentic switching activity extracted from full simulation waveforms (`ares_sentinel_integrated.vcd`, 16,695 cycles, $\alpha_{\text{rx\_in}} = 0.1418$).

### TABLE III: Post-Route Power Breakdown & Overhead Characterization (TAB-04)

| Operating Condition & Power Component | Baseline (`tt07-bep-decode`) | ARES Sentinel Top | Security Overhead ($\Delta$) | Overhead Ratio (%) |
| :--- | :---: | :---: | :---: | :---: |
| **OPERATIONAL: 20 kHz (T = 50.00 µs)** | | | | |
| Sequential Dynamic Power | $10.0\,\text{nW}$ (22.1%) | $12.0\,\text{nW}$ (20.7%) | $+2.0\,\text{nW}$ | $+20.0\%$ |
| Combinational Dynamic Power | $32.7\,\text{nW}$ (72.3%) | $42.8\,\text{nW}$ (73.9%) | $+10.1\,\text{nW}$ | $+30.9\%$ |
| Total Dynamic Switching Power | $42.7\,\text{nW}$ (94.4%) | $54.8\,\text{nW}$ (94.7%) | $+12.1\,\text{nW}$ | $+28.3\%$ |
| Static Leakage Power | $2.52\,\text{nW}$ (5.6%) | $3.10\,\text{nW}$ (5.3%) | $+0.58\,\text{nW}$ | $+23.0\%$ |
| **TOTAL OPERATIONAL POWER** | **45.20 nW** | **57.90 nW** | **+12.70 nW** | **+28.1%** |
| **STA STRESS TARGET: 50 MHz (T = 20.00 ns)** | | | | |
| Total Dynamic Switching Power | $103.50\,\mu\text{W}$ | $137.90\,\mu\text{W}$ | $+34.40\,\mu\text{W}$ | $+33.2\%$ |
| Static Leakage Power | $2.52\,\text{nW}$ | $3.10\,\text{nW}$ | $+0.58\,\text{nW}$ | $+23.0\%$ |
| **TOTAL STRESS POWER** | **103.50 µW** | **138.00 µW** | **+34.50 µW** | **+33.3%** |

*Epistemic Note*: The authoritative operational value is **57.90 nW** at 20 kHz based on post-route VCD analysis. Physical silicon measurements are currently pending manufacturing. A secondary static activity sweep ($\alpha = 0.075$) yields 50.90 nW, preserved in `docs/info.md` for portal submission consistency.

---

## VIII. Cyber-Physical Experimental Results

The architecture was evaluated against 9 canonical test vectors (AV00–AV08) during formal M6 test execution `WO011R1-FINAL-20260927-225358`.

### TABLE IV: M6 Canonical Cyber-Physical Verification Results (TAB-05)

| Vector ID | Scenario Description | Total Cycles | Fault Cond. Cycle | Latch Cycle | $T_{\text{latch}}$ | $T_{\text{isolate}}$ | Safe Bus Out | Tamper Alert | Fault Code | Ledger Record Hash |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **AV00** | Nominal Manchester Frame | 1,876 | — | — | — | — | `0x55` | 0 | `3'b000` | `6eaeb06cef96...` |
| **AV01** | Sub-Nyquist Runt Glitch | 87 | 79 | 80 | 1 cycle | 0 cycles | `0x00` | 1 | `3'b001` | `00f27f1b83da...` |
| **AV02** | Mid-band Phase Desync | 96 | 88 | 89 | 1 cycle | 0 cycles | `0x00` | 1 | `3'b010` | `09c00f5daf6e...` |
| **AV03** | Gap Resumption Violation | 117 | 109 | 110 | 1 cycle | 0 cycles | `0x00` | 1 | `3'b011` | `7acab9978414...` |
| **AV04** | Preamble Corruption | 1,876 | 178 | 179 | 1 cycle | 0 cycles | `0x00` | 1 | `3'b100` | `dd0aed40fe9b...` |
| **AV05** | Malformed Protocol Type | 1,876 | 448 | 449 | 1 cycle | 0 cycles | `0x00` | 1 | `3'b101` | `7316c67b1284...` |
| **AV06** | Constant Field Corruption | 1,876 | 763 | 764 | 1 cycle | 0 cycles | `0x00` | 1 | `3'b110` | `6d79bfd9fb40...` |
| **AV07** | Frame Truncation Underflow | 1,048 | 1,040 | 1,041 | 1 cycle | 0 cycles | `0x00` | 1 | `3'b111` | `19cb94900c21...` |
| **AV08** | Frame Overrun Overflow | 1,885 | 1,816 | 1,817 | 1 cycle | 0 cycles | `0x00` | 1 | `3'b111` | `6f0d379d7499...` |

### Key Experimental Findings:
1. **100% Trace Concordance**: Over **10,737 discrete clock cycles** and **118,107 observable signal evaluations**, the gate-level netlist exhibited zero functional divergence against the Python reference model.
2. **Single-Cycle Deterministic Isolation**: In all 8 attack scenarios (AV01–AV08), the fault was latched exactly 1 cycle following condition emergence ($T_{\text{latch}}=1$), and the safe bus was zeroized immediately without extra cycles ($T_{\text{isolate}}=0$).
3. **Nominal Acceptance**: Nominal Manchester frame AV00 was accepted without fault latching (`tamper_alert = 0`, `safe_bus = 0x55`).
4. **Hardware Mutation Trapping (M1–M3)**: Synthetic design defects (M1 glitch threshold reduction, M2 length bypass, M3 isolation bypass) were 100% trapped by the assertion testbench, validating verification suite coverage.
5. **Ledger Integrity**: The final Merkle root anchor `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0` and ledger file SHA-256 `04e154c2a9fe5d5ec6c7ce9cd19ffbb8732a4cd070367478ad447136328d1a0c` guarantee complete experimental provenance.

---

## IX. Discussion & System Implications

### A. Energy Gatekeeping and Battery Lifetime
In edge sensor nodes operating under harvested energy or lithium coin cells (e.g., CR2032 with $\sim 220\,\text{mAh}$ capacity), the dominant energy consumer is active CPU execution ($10 - 20\,\text{mW}$) and cryptographic signature calculation ($1.5 - 25\,\mu\text{W}$). By rejecting invalid transmissions at the baseband boundary within a **57.90 nW** power envelope, Sentinel prevents the host MCU from waking up on adversarial RF noise. In high-interference environments, this pre-crypto filtering extends node operational life from weeks to multiple years.

### B. Comparison with Prior Art
Compared to software-based filtering [1]–[3], Sentinel eliminates interrupt storms and achieves true single-cycle isolation latency ($50\,\mu\text{s}$ at 20 kHz) compared to software latencies exceeding milliseconds. Compared to bus firewalls [6]–[8], Sentinel requires only 163 additional standard cells ($0.0015\,\text{mm}^2$), achieving a $90\%$ reduction in silicon area overhead while protecting the baseband peripheral itself from memory-exhaustion crashes.

---

## X. Limitations & Threats to Validity

1. **Digital Baseband Scope**: Sentinel operates exclusively on demodulated digital serial bitstreams (`rx_in`). It does not provide analog filtering, RF carrier suppression, or wideband radio-frequency interference mitigation.
2. **Pre-Silicon Status**: Power and timing figures are derived from post-route STA with OpenRCX 3D parasitic extraction. Silicon measurements will be conducted upon return of fabricated Tiny Tapeout TT08 dies.
3. **Transport Latency Bounding**: Network transport latencies observed ($2.19 - 7.67\,\text{ms}$) reflect the synthetic stochastic Linux netem model; 9 discrete samples are insufficient for statistical distribution claims.
4. **DRC Waiver Transparency**: The 874 raw Magic DRC findings reflect known I/O pad and seal ring overlaps in Tiny Tapeout multi-project wafer templates and were formally reconciled under documented engineering waiver rules, resulting in 0 active un-waived DRC violations.

---

## XI. Conclusion

ARES-RX Sentinel establishes a new benchmark for ultra-low-power baseband receiver security. By enforcing multi-layer temporal pulse checking, frame syntax validation, and boundary monitoring directly at the digital baseband boundary within an authoritative post-route power envelope of **57.90 nW at 20 kHz**, the architecture guarantees single-cycle deterministic fault latching ($T_{\text{latch}}=1$) and zero-overhead bus isolation ($T_{\text{isolate}}=0$). Synthesized, placed, and routed in open-source SkyWater 130nm CMOS, the design occupies only 758 logic cells with 63.99% net placement density and cleanly closes timing at 50 MHz. Evaluated across 10,737 cycles with 100% trace concordance and secured via a SHA-256 cryptographic provenance ledger, ARES-RX Sentinel provides a validated, tapeout-ready foundation for trustworthy microelectronics in next-generation sovereign IoT ecosystems.

---

## References

[1] P. Levis et al., "TinyOS: An operating system for sensor networks," in *Ambient Intelligence*, Springer, 2005, pp. 115–148.  
[2] E. Baccelli et al., "RIOT: An open source operating system for low-end embedded devices in the IoT," *IEEE Internet of Things Journal*, vol. 5, no. 6, pp. 4428–4440, Dec. 2018.  
[3] N. Tsiftes et al., "Contiki-NG: The OS for next-generation networked embedded systems," in *Proc. ACM SenSys*, 2017.  
[4] Texas Instruments, "CC1101 Low-Power Sub-1 GHz RF Transceiver Datasheet," SWRS061I, 2020.  
[5] Semtech Corporation, "SX1276/77/78/79 Transceiver Datasheet," Rev. 7, May 2020.  
[6] J. Noorman et al., "Sancus: Low-cost trustworthy extensible networked devices with a zero-software trusted computing base," in *Proc. USENIX Security Symp.*, 2013, pp. 479–494.  
[7] ARM Limited, "ARM TrustZone Technology for ARMv8-M Architecture," White Paper, 2017.  
[8] V. Costan, I. Lebedev, and S. Devadas, "Sanctum: Minimal hardware extensions for strong isolated execution," in *Proc. USENIX Security Symp.*, 2016, pp. 857–874.  
[9] R. Beaulieu et al., "The SIMON and SPECK lightweight block ciphers," in *Proc. ACM DAC*, 2015, pp. 1–6.  
[10] A. Bogdanov et al., "PRESENT: An ultra-lightweight block cipher," in *Cryptographic Hardware and Embedded Systems (CHES)*, Springer, 2007, pp. 450–466.  
[11] M. Feldhofer, S. Dominikus, and J. Wolkerstorfer, "Strong authentication for RFID systems using the AES algorithm," in *Cryptographic Hardware and Embedded Systems (CHES)*, Springer, 2004, pp. 357–370.  
[12] K. Sankhe et al., "No radio left behind: Radio fingerprinting through deep learning of physical-layer hardware impairments," *IEEE Trans. Cogn. Commun. Netw.*, vol. 6, no. 1, pp. 165–178, Mar. 2020.  
[13] T. D. Vo-Huu et al., "Fingerprinting wireless devices using software-defined radios," *IEEE Trans. Inf. Forensics Security*, vol. 11, no. 1, pp. 165–177, Jan. 2016.  
[14] B. Danev et al., "Physical-layer identification of RFID devices," in *Proc. USENIX Security Symp.*, 2009.  
[15] J. Moody et al., "A 2.4 GHz, 240 nW wake-up receiver with -97 dBm sensitivity," in *IEEE ISSCC Dig. Tech. Papers*, 2019, pp. 248–250.  
[16] N. E. Roberts and D. D. Wentzloff, "A 98 nW wake-up receiver with -64 dBm sensitivity," *IEEE J. Solid-State Circuits*, vol. 51, no. 12, pp. 2872–2880, Dec. 2016.  
[17] P. H. Chen et al., "A sub-microwatt wake-up receiver for IoT sensor nodes," *IEEE Trans. Circuits Syst. I, Reg. Papers*, vol. 67, no. 8, pp. 2603–2612, Aug. 2020.  
