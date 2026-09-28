# Table 2: ARES Threat Model & Canonical Vector Mapping

**Table ID**: `TAB-02`  
**Target Paper Section**: Section III (Threat Model & Hardware Security Properties)  
**Caption**: *Mapping of the 9 canonical test vectors to physical fault mechanics, protocol vulnerabilities, internal detection submodules, and latched fault codes.*

| Vector ID | Vector Name | Threat Classification | Physical Stimulus Mechanism | Detecting Submodule | Expected Fault Code | Latched State | Safe Bus Output |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **AV00** | Nominal Authenticated Frame | Nominal Baseline | 192-bit Manchester frame conforming to timing and syntax | All submodules nominal | `3'b000` (FAULT_NONE) | Normal | `0x55` |
| **AV01** | Sub-Nyquist Runt Glitch | Layer-1 Temporal Integrity | Pulse width $< N_{HB,min}$ (under 8 clock cycles) | `ares_temporal_watchdog` | `3'b001` (FAULT_RUNT) | Fault Locked | `0x00` |
| **AV02** | Mid-band Phase Desync | Layer-1 Temporal Integrity | Edge transition arriving at $8 < \Delta t < 16$ clock cycles | `ares_temporal_watchdog` | `3'b010` (FAULT_MIDBAND) | Fault Locked | `0x00` |
| **AV03** | Gap Resumption Violation | Layer-1 Temporal Integrity | Sudden edge resumption after silent interval ($> 20$ cycles) | `ares_temporal_watchdog` | `3'b011` (FAULT_GAP_RES) | Fault Locked | `0x00` |
| **AV04** | Preamble Header Corruption | Layer-2 Frame Syntax Integrity | Inverted bit in 32-bit preamble sequence (`32'hAAAA_AAEA`) | `ares_frame_validator` | `3'b100` (FAULT_PREAMBLE) | Fault Locked | `0x00` |
| **AV05** | Malformed Protocol Type | Layer-2 Frame Syntax Integrity | Reserved or unsupported protocol identifier byte injected | `ares_frame_validator` | `3'b101` (FAULT_TYPE) | Fault Locked | `0x00` |
| **AV06** | Constant Field Corruption | Layer-2 Frame Syntax Integrity | Protocol security constant field altered from expected byte | `ares_frame_validator` | `3'b110` (FAULT_CONSTANT) | Fault Locked | `0x00` |
| **AV07** | Frame Truncation Underflow | Layer-2 Framing Boundary | Frame terminated before 192-bit boundary followed by idle line | `ares_frame_validator` | `3'b111` (FAULT_TRAILER) | Fault Locked | `0x00` |
| **AV08** | Frame Overrun Overflow | Layer-2 Framing Boundary | Continued bitstream transmission beyond 192-bit boundary | `ares_frame_validator` | `3'b111` (FAULT_TRAILER) | Fault Locked | `0x00` |
