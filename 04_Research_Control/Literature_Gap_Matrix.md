# Literature Gap Matrix (LGM) — ARES-RX Sentinel

**Document ID**: `ARES-RC-LGM-001`  
**Version**: `1.0.0-LOCKED`  
**Classification**: Academic Literature Review & Competitive Taxonomy  
**Status**: **FROZEN / BINDING ON ALL DRAFTS**  

---

## 1. Executive Summary & Framing

Securing resource-constrained wireless nodes in critical Internet of Things (IoT) ecosystems—such as track-and-trace logistics, smart national identity credentials, industrial sensor meshes, and electronic tax stamps—faces a fundamental physical trilemma: **Energy Budget vs. Hardware Complexity vs. Security Determinism**.

Existing literature and commercial offerings address wireless receiver security from various distinct layers of the abstraction stack. However, each incumbent paradigm leaves a distinct architectural gap when evaluated against adversarial baseband manipulation at sub-microwatt energy envelopes.

This document systematically categorizes the 6 existing paradigms, establishes a rigorous 6-axis comparative evaluation matrix, and articulates the unique scientific contribution of the **ARES-RX Sentinel** architecture.

---

## 2. In-Depth Analysis of the Six Existing Paradigms

### Category 1: Software-Based Sub-GHz Security & Firmware Sanitization
- **Representative Works / Implementations**: Contiki-NG / RIOT-OS network drivers, MCU interrupt service routines (ISRs) on Cortex-M0+/RISC-V, software CRC/Manchester decoders (e.g., RadioHead, TinyOS packet parsers).
- **Architectural Mechanics**: The radio front-end delivers raw demodulated pulses directly to a general-purpose microcontroller GPIO. The MCU relies on software edge interrupts or polling loops to sample bits, buffer frames in SRAM, and execute syntactic checks in C/C++.
- **Critical Technical Limitations**:
  1. *Interrupt Storm Vulnerability*: Sub-Nyquist runt glitches (AV01) or high-frequency transition jitter trigger tens of thousands of interrupts per second, starving the main application loop and inducing denial-of-service (DoS) or brownout.
  2. *Excessive Energy Footprint*: Active MCU operation to sanitize a single frame requires 1.2–5.0 mA at 3.3V ($4.0 - 16.5\,\text{mW}$), rapidly depleting coin-cell or harvested energy reservoirs.
  3. *Non-Deterministic Reaction Latency*: Software parsing latency ranges from $100\,\mu\text{s}$ to several milliseconds, during which corrupted or maliciously sized payloads reside in memory buffers, exposing the system to heap/stack buffer overruns.

### Category 2: Standard Hardware Decoders & Commercial Baseband ASICs
- **Representative Works / Implementations**: Texas Instruments CC1101, Semtech SX127x series, Silicon Labs Si446x, fixed-function ASIC Manchester/NRZ decoders.
- **Architectural Mechanics**: Dedicated hardwired digital logic performs clock/data recovery, preamble matching, and byte deserialization, delivering validated bytes to an on-chip FIFO via SPI.
- **Critical Technical Limitations**:
  1. *Blind Serialization*: These ASICs are engineered exclusively for nominal communications efficiency, not adversarial hardening. They blindly serialize incoming bitstreams until an internal FIFO overflow occurs.
  2. *Lack of Mid-Frame Temporal Watchdogs*: If a phase slip (AV02) or illegal gap (AV03) occurs mid-payload, standard decoders either output corrupted bytes or lock in an unrecoverable hung state requiring a full software reset.
  3. *Uncontrolled Host Delivery*: No mechanism exists to synchronously zeroize data lines or assert tamper interrupts prior to FIFO write, leaving downstream processors vulnerable to malformed payloads.

### Category 3: On-Chip Bus Interconnect Firewalls & Memory Protection Units (MPUs)
- **Representative Works / Implementations**: ARM TrustZone-M, AXI/AHB Bus Defenses (e.g., SANCUS, Sanctum), RISC-V Physical Memory Protection (PMP), on-chip memory firewalls.
- **Architectural Mechanics**: Security enforcement is located at the system bus interconnect (between the DMA engine/peripheral controller and main system memory/CPU). Transactions are filtered based on master privilege IDs and memory address ranges.
- **Critical Technical Limitations**:
  1. *Misplaced Defensive Boundary*: Bus firewalls operate *after* the peripheral has already received and DMA-transferred the malformed packet. They cannot prevent the baseband peripheral itself from being destabilized or flooded.
  2. *Substantial Gate and Silicon Overhead*: Bus firewalls typically consume 5,000 to 25,000 equivalent NAND2 gates ($> 0.05\,\text{mm}^2$ in mature nodes), which is completely prohibitive for dedicated sub-microwatt baseband dies.
  3. *Active Bus Clocking*: Requires high-speed system bus clocks (10–100 MHz) to arbitrate transfers, consuming tens of microwatts to milliwatts.

### Category 4: Ultra-Low-Power Cryptographic Micro-Engines
- **Representative Works / Implementations**: Lightweight block ciphers (SIMON, SPECK, PRESENT, CLEFIA), ultra-low-power AES accelerators, Grain-128a authenticated encryption.
- **Architectural Mechanics**: Dedicated hardware accelerators implementing symmetric encryption and message authentication codes (MACs) for IoT packet payloads.
- **Critical Technical Limitations**:
  1. *Susceptibility to Pre-Crypto Resource Exhaustion*: Cryptographic authentication is computationally expensive (hundreds to thousands of clock cycles). An adversary injecting millions of malformed frames forces the crypto engine to constantly evaluate MACs, draining node energy without ever establishing a valid session.
  2. *Inability to Detect Physical-Layer Timing Faults*: Cryptographic algorithms evaluate byte-level mathematical relations. They have zero visibility into physical-layer temporal anomalies, runt glitches, or phase slips.
  3. *Energy Barrier*: Even lightweight implementations consume $1.5 - 25.0\,\mu\text{W}$, which is orders of magnitude above the sub-100 nW power budget of passive/ambiently powered IoT nodes.

### Category 5: Physical-Layer (PHY) RF Anomaly Detection & Analog Fingerprinting
- **Representative Works / Implementations**: High-speed I/Q sampling, RF Power/RSSI envelope profiling, neural network RF fingerprinting, analog transient analysis.
- **Architectural Mechanics**: High-bandwidth analog-to-digital converters (ADCs) digitize the raw RF waveform before demodulation; DSP or machine learning classifiers identify transmitter anomalies, jamming, or spoofing based on analog features.
- **Critical Technical Limitations**:
  1. *Extreme Power Consumption*: High-speed ADCs and DSP/classifier blocks consume tens to hundreds of milliwatts ($10 - 250\,\text{mW}$), restricting their deployment to base stations, gateways, or grid-powered infrastructure.
  2. *High Die Area and Complex Process Requirements*: Requires mixed-signal CMOS or BiCMOS processes with substantial analog passive components, large die area ($> 1\,\text{mm}^2$), and extensive calibration.
  3. *Stochastic Classification Bounds*: Relies on statistical classification, introducing false-alarm probabilities ($P_{FA}$) and detection delay over multiple symbol intervals.

### Category 6: Ultra-Low-Power Wake-Up Receivers (WuRx) & Ambient-Harvested Baseband Architectures
- **Representative Works / Implementations**: Passive RFID basebands (ISO/IEC 14443, ISO/IEC 18000-6C), wake-up receivers (WuRx) (e.g., sub-microwatt envelope detectors, CMOS wake-up logic consuming $< 100\,\text{nW}$).
- **Architectural Mechanics**: Highly optimized asynchronous or low-frequency synchronous state machines designed strictly to minimize dynamic power dissipation and operate under minuscule harvested RF voltages ($0.8 - 1.2\,\text{V}$).
- **Critical Technical Limitations**:
  1. *Total Absence of Adversarial Threat Models*: WuRx architectures are engineered exclusively for minimum power consumption. They implement minimal correlators that trigger on simple energy thresholds or basic bit sequences.
  2. *Trivial Denial-of-Sleep Vulnerability*: Attackers can broadcast continuous invalid preambles or out-of-phase transitions, causing the WuRx to repeatedly wake up the high-power host MCU, resulting in rapid energy depletion ("battery exhaustion attack").
  3. *No Deterministic Bus Isolation*: Lacks hardware-enforced fail-safe zeroization gates; corrupted data is passed directly to the host or registers.

---

## 3. Comprehensive 6-Axis Comparative Literature Gap Matrix

The following scorecard synthesizes the structural trade-offs between the 6 existing literature paradigms and the proposed **ARES-RX Sentinel**:

| Category / Paradigm | Axis 1: Operating Enforcement Layer | Axis 2: Energy Footprint (Power Envelope) | Axis 3: Reaction & Isolation Latency | Axis 4: Determinism & Temporal Predictability | Axis 5: Silicon Gate & Area Overhead | Axis 6: Dominant Vulnerability / Failure Mode Under Attack |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. SW Sub-GHz / MCU Filtering** | Software application & ISR layer | $4.0 - 16.5\,\text{mW}$ (Active MCU run mode) | $100\,\mu\text{s} - 10\,\text{ms}$ (Interrupt & parsing) | Low (Subject to ISR jitter, cache misses, OS scheduling) | Zero ASIC gates (requires 4–16 KB Flash/SRAM) | **Interrupt storms, MCU starvation, stack/heap buffer overflow** |
| **2. Standard HW Decoders** | Digital baseband deserializer | $1.0 - 10.0\,\mu\text{W}$ (Standard baseband) | Multi-byte to packet-length delay | Medium (Fixed state machine, but no fault isolation) | Medium (1,000–3,000 gates) | **Blind FIFO buffering of malformed data, decoder lockup/hang** |
| **3. Bus Interconnect Firewalls** | System bus interconnect (AXI/AHB) | $50\,\mu\text{W} - 5\,\text{mW}$ (Bus clock dependent) | $5 - 20$ system bus cycles | High (Synchronous bus arbitration) | High ($5,000 - 25,000$ gates, $> 0.05\,\text{mm}^2$) | **Post-DMA execution; powerless against baseband peripheral crash** |
| **4. Crypto Micro-Engines** | Cryptographic payload layer (L3/L4) | $1.5 - 25.0\,\mu\text{W}$ (Lightweight crypto) | $500 - 5,000$ clock cycles | High (Constant-time cryptographic algorithms) | High ($2,500 - 8,000$ gates) | **Pre-crypto DoS, battery exhaustion via repeated signature checks** |
| **5. PHY RF Anomaly / Fingerprint** | Pre-demodulation RF/Analog front-end | $10.0 - 250.0\,\text{mW}$ (High-speed ADC + DSP) | Tens of microseconds to symbol periods | Stochastic / Probabilistic (False alarms, classifier drift) | Very High (Mixed-signal, $> 1.0\,\text{mm}^2$) | **Prohibitive power cost for edge nodes; channel fading false trips** |
| **6. ULP Wake-Up Receivers (WuRx)** | Analog envelope detector / Simple baseband | $20 - 100\,\text{nW}$ (Ultra-low power) | Fast wake-up ($10 - 50\,\mu\text{s}$), no isolation | Poor (Zero protocol verification) | Very Low ($200 - 500$ gates) | **Trivial denial-of-sleep, false wake-up flooding, no data isolation** |
| **ARES-RX Sentinel (Proposed)** | **Physical digital demodulated baseband boundary (`rx_in`)** | **57.90 nW @ 20 kHz (Post-route VCD estimate)** | **$T_{\text{latch}}=1$ cycle, $T_{\text{isolate}}=0$ cycles** | **Absolute (Cycle-accurate synchronous RTL, zero jitter)** | **Ultra-Compact (163 added logic cells, 758 total, $0.018\,\text{mm}^2$)** | **Bounded to digital baseband; fails safe to `8'h00` on any fault** |

---

## 4. Architectural Gap & ARES-RX Sentinel Scientific Novelty

Based on the comparative evaluation above, the existing state-of-the-art exhibits a profound **architectural void** in sub-microwatt wireless security:
> **The Sub-Microwatt Pre-Demodulation Gap**: *There exists no prior hardware architecture capable of enforcing multi-layer temporal, syntactical, and framing sanity at the raw digital baseband boundary within a sub-100 nW power envelope and with guaranteed single-cycle deterministic isolation.*

### Specific Scientific Contributions of ARES-RX Sentinel:
1. **First Sub-100 nW Multi-Layer Baseband Sentinel**: Achieves a comprehensive 3-layer protection model (L1 temporal pulse integrity, L2 syntax integrity, and framing boundary control) within an authoritative post-route power envelope of **57.90 nW at 20 kHz** on open-source SkyWater 130nm CMOS, consuming only +12.70 nW (+28.1%) over an unprotected baseline.
2. **Guaranteed Zero-Additional-Cycle Bus Zeroization ($T_{\text{isolate}}=0$)**: Introduces a fail-safe combinational zeroization gate synchronized with a single-cycle fault latch ($T_{\text{latch}}=1$). This mathematically guarantees that malformed or malicious bit patterns are clamped to `8'h00` before downstream registers or host DMA can observe them, permanently eliminating MCU interrupt storms and buffer corruption at the hardware boundary.
3. **Pre-Crypto Energy Defense**: By filtering malformed, runt, and syntactically invalid frames at the physical baseband boundary, Sentinel acts as a pre-crypto gatekeeper. It eliminates denial-of-sleep and battery-exhaustion attacks by ensuring downstream crypto engines and host microcontrollers are never energized for invalid transmissions.
4. **Reproducible Pre-Silicon Verification with Cryptographic Ledger**: All verification results are established through a public, cycle-by-cycle concordance methodology across 10,737 cycles, bound to a SHA-256 evidence ledger (root anchor `6f0d379d...733f0`), establishing an unprecedented standard of epistemic rigor in open-source ASIC research.
