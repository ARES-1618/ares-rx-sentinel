# Metric Authority Register (MAR) — ARES-RX Sentinel

**Document ID**: `ARES-RC-MAR-001`  
**Version**: `1.0.0-LOCKED`  
**Classification**: Authoritative Empirical Benchmark Ledger  
**Status**: **FROZEN / BINDING NUMERICAL SOURCE OF TRUTH**  

---

## 1. Physical Geometry & Floorplanning (SkyWater 130nm `sky130_fd_sc_hd`)

| Parameter | Baseline (`tt07-bep-decode`) | ARES Sentinel Top (`tt_um_ares_sentinel_project`) | Delta ($\Delta$) | Unit / Source |
| :--- | :---: | :---: | :---: | :--- |
| **Gross Die Envelope ($A_{\text{tile}}$)** | $161.00 \times 111.52$ | $161.00 \times 111.52$ | $0.00$ | $\mu\text{m} \times \mu\text{m}$ (TT08 $1 \times 1$ Standard Tile) |
| **Gross Tile Area ($A_{\text{tile}}$)** | $17,954.72$ | $17,954.72$ | $0.00$ | $\mu\text{m}^2$ (`DieArea: 0 0 to 161000 111520`) |
| **Gross Core Region ($A_{\text{core}}$)** | $16,493.32$ | $16,493.32$ | $0.00$ | $\mu\text{m}^2$ ($[2.76, 2.72]$ to $[158.24, 108.80]\,\mu\text{m}$) |
| **Fixed Non-Placeable Area ($A_{\text{fixed}}$)** | $574.30$ | $574.30$ | $0.00$ | $\mu\text{m}^2$ (225 well taps + 78 decaps = 303 cells) |
| **Net Placeable Core Area ($A_{\text{placeable\_net}}$)**| $15,919.02$ | $15,919.02$ | $0.00$ | $\mu\text{m}^2$ ($A_{\text{core}} - A_{\text{fixed}}$) |
| **Movable Placed Cell Area (`PlaceInstsArea`)**| $7,945.12$ | $10,186.02$ | $+2,240.90$ | $\mu\text{m}^2$ (Movable standard cells + CTS buffers) |
| **Net Logic Cell Area ($A_{\text{logic}}$)** | $5,017.31$ | $6,477.46$ | $+1,460.15$ | $\mu\text{m}^2$ (Pure combinational + sequential gates) |
| **Core Whitespace (Filler Area)** | $7,973.90$ | $5,733.00$ | $-2,240.90$ | $\mu\text{m}^2$ (Filled with 1,547 filler cells) |

---

## 2. Standard Cell Instance Composition

| Cell Category | Baseline | ARES Sentinel Top | Overhead ($\Delta$) | Description / Function |
| :--- | :---: | :---: | :---: | :--- |
| **Movable Standard Cells** | 585 | 741 | $+156$ | Core functional combinational & sequential cells |
| **Constant Tie Cells (`conb`)** | 9 | 8 | $-1$ | High/Low tie drivers (`sky130_fd_sc_hd__conb_1`) |
| **Total Functional Logic Cells** | **594** | **758** | **+164** | Synthesized Verilog logic instances |
| **Clock Tree Buffers (CTS)** | 9 | 17 | $+8$ | Clock tree distribution (`clkbuf_leaf`, etc.) |
| **Total Placed Instances** | **603** | **766** | **+163** | Movable logic + CTS + tie cells |
| **Physical Tap Cells** | 225 | 225 | $0$ | Well and substrate tap cells (`tapvpwrvgnd_1`) |
| **Decoupling Capacitors (Decap)** | 78 | 78 | $0$ | Core power rail stability (`decap_3/4/6/8/12`) |
| **Physical Filler Cells** | 1,770 | 1,547 | $-223$ | Row continuity fillers (`fill_1/2/4/8`) |
| **Total Silicon Physical Shapes** | **2,676** | **2,616** | **-60** | All placed GDS layout structures |

---

## 3. Four-Tier Silicon Utilization Hierarchy

| Utilization Tier | Mathematical Formula | Baseline | Sentinel Top | Provenance Engine & Semantic Meaning |
| :--- | :--- | :---: | :---: | :--- |
| **[Tier 1] Reported Core Utilization** | $\frac{\text{PlaceInstsArea}}{A_{\text{placeable\_net}}}$ | **49.91%** | **63.99%** | OpenROAD RePlAce `[INFO GPL-0019]` Net placement density |
| **[Tier 2] Recomputed Gross Core Util.** | $\frac{\text{PlaceInstsArea}}{A_{\text{core}}}$ | **48.17%** | **61.76%** | Core area bounding box ratio (including fixed tap/decap) |
| **[Tier 3] Gross Tile Logic Utilization** | $\frac{A_{\text{logic}}}{A_{\text{tile}}}$ | **27.94%** | **36.08%** | Net functional gate area divided by full $1 \times 1$ tile area |
| **[Tier 4] Gross Tile Placed Utilization**| $\frac{\text{PlaceInstsArea}}{A_{\text{tile}}}$ | **44.25%** | **56.73%** | Total placed cell area divided by full $1 \times 1$ tile area |

---

## 4. Static Timing Analysis (STA) & Frequency Limits

*Characterized at SkyWater 130nm TT / 25°C / 1.80V with OpenRCX 3D parasitic extraction.*

| Timing Parameter | Baseline (`tt07-bep-decode`) | ARES Sentinel Top | Slack Margin | Limiting Path Description |
| :--- | :---: | :---: | :---: | :--- |
| **Protocol Operational Clock ($F_{\text{clk}}$)** | $20\,\text{kHz}$ ($T=50.00\,\mu\text{s}$) | $20\,\text{kHz}$ ($T=50.00\,\mu\text{s}$) | MET | Nominal baseband demodulation clock |
| **STA Stress Constraint Clock ($F_{\text{stress}}$)**| $50\,\text{MHz}$ ($T=20.00\,\text{ns}$) | $50\,\text{MHz}$ ($T=20.00\,\text{ns}$) | MET | Static timing closure stress target |
| **Setup Slack @ 50 MHz (Reg-to-Reg)** | $+12.07\,\text{ns}$ | **$+11.88\,\text{ns}$** | MET | Internal core register-to-register paths |
| **Setup Slack @ 50 MHz (IO-Constrained)**| $+7.58\,\text{ns}$ | **$+7.29\,\text{ns}$** | MET | External pin-to-register / register-to-pin |
| **Hold Slack @ 50 MHz (Min Delay)** | $+0.47\,\text{ns}$ | **$+0.42\,\text{ns}$** | MET | Minimum path delay across all registers |
| **Worst Negative Slack (WNS)** | $0.00\,\text{ns}$ | **$0.00\,\text{ns}$** | MET | Zero timing violations reported |
| **Total Negative Slack (TNS)** | $0.00\,\text{ns}$ | **$0.00\,\text{ns}$** | MET | Zero path delay violations |
| **Maximum Frequency (Reg-to-Reg, $F_{\text{max,reg}}$)**| $126.10\,\text{MHz}$ | **$123.15\,\text{MHz}$** | — | $F_{\text{max}} = 1 / (T_{\text{clk}} - \text{slack}) = 1 / 8.12\,\text{ns}$ |
| **Maximum Frequency (IO-Constrained, $F_{\text{max,io}}$)**| $80.52\,\text{MHz}$ | **$78.68\,\text{MHz}$** | — | $F_{\text{max}} = 1 / (T_{\text{clk}} - \text{slack}) = 1 / 12.71\,\text{ns}$ |

---

## 5. Power Characterization (Post-Route OpenSTA 2.0.17)

### 5.1 Scenario B: Authoritative VCD-Workload-Derived Post-Route Power Estimate
*Derived from full simulation waveform `ares_sentinel_integrated.vcd` (16,695 clock cycles, $\alpha_{\text{rx\_in}} = 0.1418$).*

| Operating Point & Component | Baseline | ARES Sentinel Top | Security Overhead ($\Delta$) | Overhead Percentage |
| :--- | :---: | :---: | :---: | :---: |
| **OPERATIONAL: 20 kHz (T = 50.00 µs)** | | | | |
| Sequential Dynamic Power | $10.0\,\text{nW}$ (22.1%) | $12.0\,\text{nW}$ (20.7%) | $+2.0\,\text{nW}$ | $+20.0\%$ |
| Combinational Dynamic Power | $32.7\,\text{nW}$ (72.3%) | $42.8\,\text{nW}$ (73.9%) | $+10.1\,\text{nW}$ | $+30.9\%$ |
| Total Dynamic Switching Power | $42.7\,\text{nW}$ (94.4%) | $54.8\,\text{nW}$ (94.7%) | $+12.1\,\text{nW}$ | $+28.3\%$ |
| Static Leakage Power | $2.52\,\text{nW}$ (5.6%) | $3.10\,\text{nW}$ (5.3%) | $+0.58\,\text{nW}$ | $+23.0\%$ |
| **TOTAL OPERATIONAL POWER** | **45.20 nW** | **57.90 nW** | **+12.70 nW** | **+28.1%** |
| **STRESS TARGET: 50 MHz (T = 20.00 ns)** | | | | |
| Sequential Dynamic Power | $22.6\,\mu\text{W}$ | $29.9\,\mu\text{W}$ | $+7.3\,\mu\text{W}$ | $+32.3\%$ |
| Combinational Dynamic Power | $80.9\,\mu\text{W}$ | $108.0\,\mu\text{W}$ | $+27.1\,\mu\text{W}$ | $+33.5\%$ |
| Total Dynamic Switching Power | $103.5\,\mu\text{W}$ | $137.9\,\mu\text{W}$ | $+34.4\,\mu\text{W}$ | $+33.2\%$ |
| Static Leakage Power | $2.52\,\text{nW}$ | $3.10\,\text{nW}$ | $+0.58\,\text{nW}$ | $+23.0\%$ |
| **TOTAL STRESS POWER** | **103.50 µW** | **138.00 µW** | **+34.50 µW** | **+33.3%** |

### 5.2 Scenario A: Static Assumption Sensitivity Sweeps
*Evaluated under uniform input toggle activity ($\text{duty} = 0.5$).*

| Activity Condition | Baseline @ 20 kHz | Sentinel Top @ 20 kHz | Baseline @ 50 MHz | Sentinel Top @ 50 MHz | Overhead (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Tool Default ($\alpha$ unconstrained) | $24.1\,\text{nW}$ | $30.6\,\text{nW}$ | $56.4\,\mu\text{W}$ | $72.3\,\mu\text{W}$ | $+27.0\%$ |
| Low Activity ($\alpha = 0.05$) | $35.6\,\text{nW}$ | $44.5\,\text{nW}$ | $84.8\,\mu\text{W}$ | $108.0\,\mu\text{W}$ | $+25.0\%$ |
| **Nominal Activity ($\alpha = 0.075 - 0.10$)** | $47.1\,\text{nW}$ | **50.90 nW** / $58.3\,\text{nW}$ | $113.0\,\mu\text{W}$ | $143.0\,\mu\text{W}$ | $+23.8\%$ |
| Elevated Activity ($\alpha = 0.20$) | $70.1\,\text{nW}$ | $86.0\,\text{nW}$ | $170.0\,\mu\text{W}$ | $213.0\,\mu\text{W}$ | $+22.7\%$ |

---

## 6. Physical Verification & Sign-Off Quality

| Sign-Off Metric | Value | Engine | Audit Verdict |
| :--- | :---: | :---: | :--- |
| **Total Routed Wirelength** | $19,988\,\mu\text{m}$ | TritonRoute | Clean routing closure |
| **Total Via Count** | 5,970 vias | TritonRoute | Multi-layer interconnect |
| **Global 2D Routing Congestion** | 0 overcongested tiles | FastRoute | PASS (0% routing overflow) |
| **Detailed Routing DRC Violations**| 0 violations | TritonRoute | PASS (clean detailed route) |
| **Raw Magic DRC Violations** | 874 violations | Magic 8.3.678 | Categorized pad/halo overlap |
| **Waived Magic DRC Violations** | 874 violations | Documented waiver policy | Formally reconciled |
| **Active Un-waived DRC Violations**| **0 violations** | Magic 8.3.678 | **PASS / CLEAN SIGN-OFF** |
| **Layout vs. Schematic (LVS)** | **100% Match** | Netgen 1.5.133 | **PASS (764/764 dev, 776/776 net, 45/45 pin)** |
| **Tiny Tapeout Submission Precheck**| **PASS 100%** | TT08 Precheck Tool | Local qualification complete |

---

## 7. M6 Cyber-Physical Verification & Cryptographic Provenance

| Parameter | Value | Reference Artifact / Anchor |
| :--- | :--- | :--- |
| **Canonical Test Vectors Evaluated** | 9 vectors ($AV00$ nominal + $AV01..AV08$ attacks) | `AV_Canonical_Vector_Manifest.yaml` |
| **Total Simulation Cycles** | 10,737 discrete clock cycles | `m6_final_run_manifest.json` |
| **Cycle-by-Cycle Signal Evaluations**| 118,107 evaluations ($10,737 \times 11$ signals) | `m6_final_run_manifest.json` |
| **Trace Concordance Rate** | **100.00%** (0 discrepancies observed) | Behavioral Python vs Verilog RTL comparison |
| **Fault Latching Latency ($T_{\text{latch}}$)** | Exactly 1 clock cycle ($50\,\mu\text{s}$ @ 20 kHz) | $T_{\text{latch}} = t_{\text{latched}} - t_{\text{condition}} = 1$ |
| **Isolation Effective Latency ($T_{\text{isolate}}$)** | Exactly 0 additional RTL cycles | $t_{\text{isolate}} = t_{\text{latched}}$ |
| **Safe Output Latency ($T_{\text{safe}}$)** | Exactly 0 additional RTL cycles | $t_{\text{safe}} = t_{\text{latched}}$, output forced to `8'h00` |
| **Mutation Testing Detection Rate** | 100% (M1, M2, M3 all successfully trapped) | `04_Verification/ARES-RX_Sentinel/` |
| **Authoritative Execution Run ID** | `WO011R1-FINAL-20260927-225358` | `m6_final_run_manifest.json` |
| **Final Merkle / Hash Chain Root Anchor** | `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0` | Ledger anchor block #8 |
| **Ledger File Content SHA-256** | `04e154c2a9fe5d5ec6c7ce9cd19ffbb8732a4cd070367478ad447136328d1a0c` | `m6_unified_evidence_ledger.jsonl` |
