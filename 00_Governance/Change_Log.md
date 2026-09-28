# Change Log — ARES-RX Sentinel

All notable changes to the architecture, blueprints, governance, and verification suites will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-09-27 — TRL-7 Silicon Tape-Out & Competition Release

### Milestone M0: Baseline Freeze & Workspace Governance
- Preserved `tt07-bep-decode` as an immutable reference control ($B$) in `03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/`.
- Established 7-tier standardized repository architecture.

### Milestone M1: Layer-1 Temporal Integrity Sentinel
- Implemented `ares_timing_sentinel.v` with interval counter ($0 \dots 255$) and discrete window comparators ($N_{\text{HB}} \in [8..10]$, $N_{\text{BIT}} \in [16..20]$).
- Implemented 4-state context tracking FSM (`IDLE`, `ARMED`, `ACTIVE`, `LONG_GAP_PENDING`).
- Validated empirical timing ($F_s = 20\text{ kHz}$) and qualified EOP silence ($N_{\text{EOF}}=64$).

### Milestone M2: Layer-3 Hardware Fail-Closed Isolation
- Implemented `ares_fault_latch.v`, `ares_isolation_gate.v`, and `ares_isolation_l3.v`.
- Achieved deterministic 1-cycle combinational bus zeroization ($D_{\text{out}} = 8\text{'b}0000\_0000$) and persistent hardware tamper alarm.

### Milestone M3: Layer-2 Frame Syntax Integrity
- Implemented `ares_frame_fsm.v` with autonomous $0 \dots 191$ bit counter decoupled from baseline `full` flag.
- Validated on-the-fly static field verification (Preamble `0xAAAAAAAA`, Type `0xD391`, Constant `0x0DFFFFFE`) and dynamic payload transparency.
- Implemented `ares_fault_arbiter.v` with strict priority ($L1 > L2$).

### Milestone M4: Adversarial Verification & Demarcation Integration
- Implemented top-level integration wrapper `ares_sentinel_top.v`.
- Executed 13 Core Adversarial Tests (TC01–TC13) across Icarus Verilog RTL and Python reference model (100% pass).
- Sealed all 7 RTL modules with SHA-256 in `00_Governance/M4_Cryptographic_Manifest.sha256`.

### Milestone M5: SkyWater 130nm ASIC Synthesis & Physical P&R (TT08)
- Executed OpenROAD physical flow on SkyWater 130nm (`sky130_fd_sc_hd`) for Tiny Tapeout TT08 $1 \times 1$ Standard Tile ($161.00 \times 111.52\,\mu\text{m}$).
- Reconciled post-route PPA: $6,477.46\,\mu\text{m}^2$ standard cell area (758 gates), $50.90\,\text{nW}$ @ $20\,\text{kHz}$ ($\alpha = 0.075$, duty 0.50).
- Achieved positive timing margins ($+11.88\,\text{ns}$ setup @ $50\,\text{MHz}$, $+0.42\,\text{ns}$ hold), 0 active manufacturing DRC violations, and 100% LVS match.

### Milestone M6: Competition, Demonstration & Peruri Innovation Package
- Built interactive CLI hardware demo `ares_hardware_demo.py` (6/6 comparative scenarios pass).
- Authored 4 standardized architectural and silicon layout figures.
- Drafted formal Peruri Strategic Innovation Proposal and 12-slide executive pitch deck.
- Sealed all demonstration deliverables in `06_Demonstration/03_Demonstration_Manifest.sha256`.

### Milestone M7 & Post-Tapeout Extensions
- Formulated Post-Silicon Bring-Up Plan (`12_Post_Silicon_Bring_Up_Plan.md`) with 4 laboratory procedures and RP2040 test harness in `04_Verification/post_silicon/`.
- Designed industrial AMBA APB4 bus slave wrapper (`ares_sentinel_apb.v`) and ANSI C99 / MISRA-C driver header (`ares_sentinel_regs.h`) in `integration/`.
- Built standalone, turnkey TT08 submission repository in `05_ASIC_Synthesis/tt08_submission_repo/` and compressed distribution bundle `ARES_RX_Sentinel_TT08_Submission.zip` (Precheck: 100% PASS).
