# Copilot Work Order — Engineering Contract

## Active Work Order: WO-2026-M6-001
**Project:** ARES-RX Sentinel  
**Milestone:** M6 — Competition, Demonstration, and Peruri Innovation Package  
**Current Phase:** All Milestones (M0 through M7) Formally Closed & Ratified  
**Status:** CLOSED / RATIFIED BY TECHNICAL ARCHITECT (RELEASE v1.0.0)  
**Issuing Authority:** Technical Architect / Research Direction  
**Executing Engineer:** Implementation Engineer (Copilot)  

---

### 1. ARCHITECTURAL MANDATES & DEMONSTRATION CONTRACT

In compliance with the project governance and the strategic vision defined in `01_Vision_and_Blueprints/ARES-RX_Sentinel/09_Competition_Strategy.md`, Milestone M6 delivers the complete demonstration and competition package:

1. **Defensible Academic Framing (Rule 2)**:
   - All demonstration scenarios and pitch documents must strictly present Sentinel as a **Trusted Digital Reception Boundary** protecting against temporal desynchronization and syntactic frame injection on the digital demodulated baseband input (`rx_in`).
   - Rejection of ungrounded analog RF jamming claims; focus on verifiable cyber-physical timing and protocol enforcement.

2. **Comparative Demonstration Rigor ($B \leftrightarrow S$)**:
   - Every demonstration script must execute side-by-side comparative evaluation between Unprotected Baseline ($B$) and Protected Sentinel ($S$):
     - Nominal conditions: Zero latency penalty, 100% telemetry throughput transparency.
     - Adversarial conditions: Baseline silent corruption vs. Sentinel instant detection, `tamper_alert` strobe, and hardware fail-closed zeroization ($D_{\text{out}} = 0$).

3. **Grounding in Post-Route Silicon Evidence (M5 Closure)**:
   - All presentation materials, figures, and technical proposals must reference the reconciled physical sign-off data from Milestone M5:
     - Process: SkyWater 130nm (`sky130_fd_sc_hd`), TT08 $1 \times 1$ Standard Tile ($161.00\,\mu\text{m} \times 111.52\,\mu\text{m}$).
     - Power: $50.90\,\text{nW}$ @ $20\,\text{kHz}$ (Scenario B workload-derived, $+9.28\,\text{nW}$ overhead).
     - Timing: Setup margin $+11.88\,\text{ns}$ @ $50\,\text{MHz}$ stress clock, Hold margin $+0.42\,\text{ns}$.
     - Physical Verification: 0 active manufacturing DRC violations, 100% (758/758) gate match in Netgen LVS, 100% Tiny Tapeout precheck PASS.

4. **Preservation of Immutable RTL**:
   - The 7 frozen Verilog modules in `ares_sentinel/` and baseline demodulator in `tt07-bep-decode/` remain 100% untouched and cryptographically sealed under SHA-256.

---

### 2. TAHAPAN EKSEKUSI SEKUENSIAL M6

- **Stage M6-A: Interactive Hardware Demonstration Suite (`06_Demonstration/ARES-RX_Sentinel/demo/`)**
  - Implementasi CLI demo dashboard komparatif (`ares_hardware_demo.py`) mencakup nominal playback, runt pulse attack, IFG desync, syntax corruption, dan hardware trace replay.
- **Stage M6-B: Visual Figures & Architecture Diagrams (`06_Demonstration/ARES-RX_Sentinel/figures/`)**
  - Pembuatan diagram arsitektur 3-layer, peta boundary timing, diagram FSM, dan visualisasi tata-letak silikon TT08.
- **Stage M6-C: Formal Technical Proposal & Peruri Package (`06_Demonstration/ARES-RX_Sentinel/presentation/`)**
  - Penyusunan proposal inovasi Peruri / kompetisi IC design (`ARES_Sentinel_Peruri_Innovation_Proposal.md`) dan naskah slide pitch deck (`ARES_Sentinel_Pitch_Deck.md`).
- **Stage M6-D: Final Governance & Project Closure**
  - Pembaruan status proyek dan manifest final.

---

### 3. PROGRESS LOG & ACTION ITEMS

| Tahap | Deskripsi | Status | Catatan / Artefak |
|---|---|---|---|
| **M5-F** | Physical P&R (OpenROAD / TritonRoute) | **CLOSED** | GDS, DEF, SPEF terekstraksi pada tile TT08 ($161 \times 111.52\,\mu\text{m}$) |
| **M5-G** | Post-Route STA & Power | **CLOSED** | Setup slack $+11.88\,\text{ns}$, Daya $50.90\,\text{nW}$ @ $20\,\text{kHz}$ ($\alpha=0.075$) |
| **M5-H** | DRC/LVS & TT08 Precheck | **CLOSED** | DRC clean (0 active), LVS 100% (758/758 match), TT precheck PASS |
| **M5-AUDIT** | Post-Route Evidence Reconciliation | **CLOSED** | [`post_route_ppa_benchmarking_report.md`](file:///05_ASIC_Synthesis/results/post_route_ppa_benchmarking_report.md) & 3 reconciliation files |
| **M6-A** | Interactive Hardware Demonstration Suite | **CLOSED** | [`ares_hardware_demo.py`](file:///06_Demonstration/ARES-RX_Sentinel/demo/ares_hardware_demo.py) (6/6 scenarios PASS) |
| **M6-B** | Visual Architecture & Silicon Figures | **CLOSED** | Figures 01..04 in [`06_Demonstration/ARES-RX_Sentinel/figures/`](file:///06_Demonstration/ARES-RX_Sentinel/figures/) |
| **M6-C** | Technical Proposal & Pitch Deck | **CLOSED** | Proposal Peruri & Pitch Deck (12 slides) in [`presentation/`](file:///06_Demonstration/ARES-RX_Sentinel/presentation/) |
| **M6-D** | Final Project Wrap-up & Manifest Seal | **CLOSED** | Cryptographically sealed in [`03_Demonstration_Manifest.sha256`](file:///06_Demonstration/03_Demonstration_Manifest.sha256) |
| **M7-A** | Post-Silicon Bring-Up Plan & RP2040 Harness | **CLOSED** | Specification in `12_Post_Silicon_Bring_Up_Plan.md`, firmware in `04_Verification/post_silicon/` |
| **M7-B** | Industrial AMBA APB4 SoC Wrapper & C Driver | **CLOSED** | `ares_sentinel_apb.v` & `ares_sentinel_regs.h` in `03_Core_Projects/ARES-RX_Sentinel/integration/` |
| **M7-C** | Turnkey TT08 Submission Package & ZIP Archive | **CLOSED** | Standalone repo in `tt08_submission_repo/` & `ARES_RX_Sentinel_TT08_Submission.zip` (Precheck PASS) |

---

### 4. ARCHIVAL RECORD: PREVIOUS WORK ORDERS
- **WO-2026-M0-001**: Baseline Freeze & Workspace Setup — **STATUS: CLOSED**.
- **WO-2026-M1-001**: Layer-1 Temporal Integrity Sentinel — **STATUS: CLOSED / FROZEN**.
- **WO-M1-QA-002**: Qualification Closure Audit & Empirical Grounding — **STATUS: CLOSED**.
- **WO-2026-M2-001**: Layer-3 Hardware Fail-Closed Isolation & Sticky Latch — **STATUS: CLOSED / FROZEN**.
- **WO-2026-M3-001**: Layer-2 Frame Syntax Integrity & Arbiter — **STATUS: CLOSED / FROZEN**.
- **WO-2026-M4-001**: Integrated Demarcation & Adversarial Verification Suite — **STATUS: CLOSED / FROZEN**.
- **WO-2026-M4-CLOSE-002**: Final Evidentiary Closure & Disambiguation — **STATUS: CLOSED / FROZEN**.
- **WO-2026-M5-E-CLOSE-001**: Pre-Layout PPA Qualification & Evidence Reconciliation — **STATUS: CLOSED**.
- **WO-2026-M5-F-001**: Physical Implementation / P&R Opening — **STATUS: CLOSED**.
- **WO-2026-M5F-AUDIT-002**: Post-Route Evidence Reconciliation — **STATUS: CLOSED**.
