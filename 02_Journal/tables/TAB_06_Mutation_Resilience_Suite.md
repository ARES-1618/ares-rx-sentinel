# Table 6: Hardware Mutation Testing Suite & Assertion Coverage

**Table ID**: `TAB-06`  
**Target Paper Section**: Section VIII (Cyber-Physical Evaluation)  
**Caption**: *Summary of synthetic hardware mutation benchmarks (M1–M3) injected into synthesizable RTL to validate assertion coverage and eliminate false-negative verification.*

| Mutation ID | Target Submodule | Mutated RTL Logic / Injected Defect | Operational Security Risk | Detecting Assertion / Test Mechanism | Test Verdict |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **M1** | `ares_temporal_watchdog` | Glitch threshold reduced from $\Delta t < 8$ to $\Delta t < 4$ cycles | Sub-Nyquist runt glitches between 4–7 cycles would slip into decoder undetected | Trapped by AV01 assertion check (`assert tamper_alert == 1`) | **TRAPPED (PASS)** |
| **M2** | `ares_frame_validator` | Forced frame length acceptance counter threshold to bypass trailer check | Prematurely truncated or overflowing frames accepted into decoder | Trapped by AV07 & AV08 length assertions | **TRAPPED (PASS)** |
| **M3** | `ares_isolation_gate` | Forced combinational pass-through bypass (`safe_bus = raw_bus` even if faulted) | Malicious or corrupted payload passed to host MCU despite alert | Trapped by bus zeroization assertion (`assert safe_bus == 8'h00`) | **TRAPPED (PASS)** |
