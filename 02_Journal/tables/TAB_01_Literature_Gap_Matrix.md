# Table 1: Comprehensive 6-Axis Comparative Literature Gap Matrix

**Table ID**: `TAB-01`  
**Target Paper Section**: Section II (Related Work & Literature Gap Analysis)  
**Caption**: *Comprehensive multi-dimensional comparison between existing IoT receiver security paradigms and the proposed ARES-RX Sentinel architecture across six standardized analytical axes.*

| Category / Paradigm | Axis 1: Operating Enforcement Layer | Axis 2: Energy Footprint (Power Envelope) | Axis 3: Reaction & Isolation Latency | Axis 4: Determinism & Temporal Predictability | Axis 5: Silicon Gate & Area Overhead | Axis 6: Dominant Vulnerability Under Adversarial Manipulation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. SW Sub-GHz / MCU Filtering** | Software application & ISR layer | $4.0 - 16.5\,\text{mW}$ (Active MCU state) | $100\,\mu\text{s} - 10\,\text{ms}$ (Interrupt handling) | Low (Subject to ISR jitter, cache misses, scheduling) | Zero ASIC gates (requires 4–16 KB SRAM/Flash) | Interrupt storms, CPU starvation, stack/heap buffer overflow |
| **2. Standard HW Decoders** | Digital baseband deserializer | $1.0 - 10.0\,\mu\text{W}$ (Standard baseband) | Multi-byte to packet-length delay | Medium (Fixed FSM, but zero fault isolation) | Medium (1,000–3,000 gates) | Blind FIFO buffering of malformed data, decoder lockup |
| **3. Bus Interconnect Firewalls** | System bus interconnect (AXI/AHB) | $50\,\mu\text{W} - 5\,\text{mW}$ (Bus clock dependent) | $5 - 20$ system bus cycles | High (Synchronous bus arbitration) | High ($5,000 - 25,000$ gates, $> 0.05\,\text{mm}^2$) | Post-DMA execution; powerless against baseband peripheral crash |
| **4. Crypto Micro-Engines** | Cryptographic payload layer (L3/L4) | $1.5 - 25.0\,\mu\text{W}$ (Lightweight crypto) | $500 - 5,000$ clock cycles | High (Constant-time execution) | High ($2,500 - 8,000$ gates) | Pre-crypto DoS, battery exhaustion via repeated MAC checks |
| **5. PHY RF Anomaly / Fingerprint** | Pre-demodulation RF/Analog front-end | $10.0 - 250.0\,\text{mW}$ (High-speed ADC + DSP) | Tens of microseconds to symbol periods | Stochastic (Probabilistic classification drift) | Very High (Mixed-signal, $> 1.0\,\text{mm}^2$) | Prohibitive power cost; channel fading false trips |
| **6. ULP Wake-Up Receivers (WuRx)** | Analog envelope detector / Baseband | $20 - 100\,\text{nW}$ (Ultra-low power) | Fast wake-up ($10 - 50\,\mu\text{s}$), no isolation | Poor (Zero protocol verification) | Very Low ($200 - 500$ gates) | Trivial denial-of-sleep, false wake-up flooding |
| **ARES-RX Sentinel (Proposed)** | **Physical digital baseband boundary (`rx_in`)** | **57.90 nW @ 20 kHz (Post-route VCD estimate)** | **$T_{\text{latch}}=1$ cycle, $T_{\text{isolate}}=0$ cycles** | **Absolute (Cycle-accurate synchronous RTL, zero jitter)** | **Ultra-Compact (163 added logic cells, 758 total, $0.018\,\text{mm}^2$)** | **Bounded to digital baseband; fails safe to `8'h00` on any fault** |
