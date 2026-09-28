# Table 5: M6 Canonical Cyber-Physical Verification Results

**Table ID**: `TAB-05`  
**Target Paper Section**: Section VIII (Cyber-Physical Evaluation)  
**Caption**: *Execution scorecard across the 9 canonical verification vectors, documenting fault latching cycles, zero-overhead bus isolation, safe output values, and cryptographic ledger record hashes.*

| Vector ID | Scenario Description | Threat Category | Total Cycles | Fault Cond. Cycle | Latch Cycle | $T_{\text{latch}}$ (cycles) | $T_{\text{isolate}}$ (cycles) | Safe Bus Out | Tamper Alert | Fault Code | SHA-256 Ledger Record Hash |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **AV00** | Nominal Authenticated Frame | Nominal Baseline | 1,876 | — | — | — | — | `0x55` | 0 | `3'b000` | `6eaeb06cef96...591a` |
| **AV01** | Sub-Nyquist Runt Glitch | L1 Temporal Integrity | 87 | 79 | 80 | 1 | 0 | `0x00` | 1 | `3'b001` | `00f27f1b83da...a66b` |
| **AV02** | Mid-band Phase Desync | L1 Temporal Integrity | 96 | 88 | 89 | 1 | 0 | `0x00` | 1 | `3'b010` | `09c00f5daf6e...170c` |
| **AV03** | Gap Resumption Violation | L1 Temporal Integrity | 117 | 109 | 110 | 1 | 0 | `0x00` | 1 | `3'b011` | `7acab9978414...8f28` |
| **AV04** | Preamble Corruption | L2 Frame Syntax | 1,876 | 178 | 179 | 1 | 0 | `0x00` | 1 | `3'b100` | `dd0aed40fe9b...11e9` |
| **AV05** | Malformed Protocol Type | L2 Frame Syntax | 1,876 | 448 | 449 | 1 | 0 | `0x00` | 1 | `3'b101` | `7316c67b1284...7ed2` |
| **AV06** | Constant Field Corruption | L2 Frame Syntax | 1,876 | 763 | 764 | 1 | 0 | `0x00` | 1 | `3'b110` | `6d79bfd9fb40...9185` |
| **AV07** | Frame Truncation Underflow | L2 Framing Boundary | 1,048 | 1,040 | 1,041 | 1 | 0 | `0x00` | 1 | `3'b111` | `19cb94900c21...10ea` |
| **AV08** | Frame Overrun Overflow | L2 Framing Boundary | 1,885 | 1,816 | 1,817 | 1 | 0 | `0x00` | 1 | `3'b111` | `6f0d379d7499...33f0` |

*Provenential Metadata*: Authoritative Execution Run ID `WO011R1-FINAL-20260927-225358`, Total Clock Cycles: 10,737, Total Signal Evaluations: 118,107, Trace Concordance: 100%, Root Anchor: `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0`, Ledger SHA-256: `04e154c2a9fe5d5ec6c7ce9cd19ffbb8732a4cd070367478ad447136328d1a0c`.
