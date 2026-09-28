# Figure 1: ARES-RX Sentinel System Architecture & Boundary Pipeline

**Figure ID**: `FIG-01`  
**Target Paper Section**: Section IV (ARES-RX Sentinel System Architecture)  
**Caption**: *System boundary block diagram of ARES-RX Sentinel positioned between the physical digital baseband input (`rx_in`) and the downstream host microcontroller interface (`safe_data_out[7:0]`, `tamper_alert`).*

```mermaid
flowchart LR
    subgraph RF_FrontEnd ["Physical Analog & RF Domain"]
        Antenna["Sub-GHz Antenna\n(433 / 868 / 915 MHz)"] --> Demod["Envelope Detector / Mixer\n& Hard-Limiter Slicer"]
    end

    Demod -->|"rx_in (Digital Serial Baseband @ 20 kHz)"| SentinelBoundary

    subgraph SentinelBoundary ["ARES-RX Sentinel ASIC Wrapper (SkyWater 130nm TT08)"]
        subgraph L1_L2_Pipeline ["Pipelined Sanitization & Validation Engine"]
            EdgeDet["Synchronous Edge Detector\n(2-Stage Metastability Filter)"]
            TemporalWatchdog["L1 Temporal Watchdog\n(N_HB in [8,10], N_BIT in [16,20], N_EOF=64)"]
            SyntaxValidator["L2 Frame Syntax Validator\n(Preamble, Protocol Type, Security Constant)"]
            BoundaryWatchdog["L2 Framing Boundary Guard\n(Underflow / Overrun Tracker)"]
            EdgeDet --> TemporalWatchdog
            EdgeDet --> SyntaxValidator
            SyntaxValidator --> BoundaryWatchdog
        end

        subgraph L3_Enforcement ["Deterministic Enforcement & Arbitration"]
            FaultArbiter["Fault Priority Encoder & Sticky Latch\n(Single-Cycle Latch: T_latch = 1)"]
            TemporalWatchdog -->|"fault_runt / fault_midband / fault_gap"| FaultArbiter
            SyntaxValidator -->|"fault_preamble / fault_type / fault_const"| FaultArbiter
            BoundaryWatchdog -->|"fault_trailer"| FaultArbiter

            IsolationGate["Fail-Safe Combinational Isolation Gate\n(Zero-Cycle Propagation: T_isolate = 0)"]
            FaultArbiter -->|"tamper_alert / zeroize_en"| IsolationGate
        end

        BaselineCore["Baseline Manchester Demodulator\n(tt07-bep-decode Core)"]
        Demod -.->|"rx_in"| BaselineCore
        BaselineCore -->|"raw_data[7:0]"| IsolationGate
    end

    IsolationGate -->|"safe_data_out[7:0] (0x00 if Tampered)"| HostMCU["Downstream Host Microcontroller / SoC Bus"]
    FaultArbiter -->|"tamper_alert (Active High Interrupt)"| HostMCU
```
