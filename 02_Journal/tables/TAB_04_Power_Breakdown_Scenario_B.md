# Table 4: Post-Route Power Breakdown & Overhead Characterization

**Table ID**: `TAB-04`  
**Target Paper Section**: Section VII (Power Characterization)  
**Caption**: *Authoritative post-route power characterization under authentic simulation switching activity (Scenario B, $\alpha_{\text{rx\_in}}=0.1418$) comparing baseline demodulator versus protected ARES-RX Sentinel across operational and stress clock regimes.*

| Operating Condition & Power Component | Baseline (`tt07-bep-decode`) | ARES Sentinel Top | Security Overhead ($\Delta$) | Overhead Ratio (%) |
| :--- | :---: | :---: | :---: | :---: |
| **OPERATIONAL REGIME: 20 kHz (T = 50.00 µs)** | | | | |
| Sequential Dynamic Power | $10.0\,\text{nW}$ (22.1%) | $12.0\,\text{nW}$ (20.7%) | $+2.0\,\text{nW}$ | $+20.0\%$ |
| Combinational Dynamic Power | $32.7\,\text{nW}$ (72.3%) | $42.8\,\text{nW}$ (73.9%) | $+10.1\,\text{nW}$ | $+30.9\%$ |
| Total Dynamic Switching Power | $42.7\,\text{nW}$ (94.4%) | $54.8\,\text{nW}$ (94.7%) | $+12.1\,\text{nW}$ | $+28.3\%$ |
| Static Leakage Power | $2.52\,\text{nW}$ (5.6%) | $3.10\,\text{nW}$ (5.3%) | $+0.58\,\text{nW}$ | $+23.0\%$ |
| **TOTAL OPERATIONAL POWER** | **45.20 nW** | **57.90 nW** | **+12.70 nW** | **+28.1%** |
| **STA STRESS REGIME: 50 MHz (T = 20.00 ns)** | | | | |
| Sequential Dynamic Power | $22.6\,\mu\text{W}$ | $29.9\,\mu\text{W}$ | $+7.3\,\mu\text{W}$ | $+32.3\%$ |
| Combinational Dynamic Power | $80.9\,\mu\text{W}$ | $108.0\,\mu\text{W}$ | $+27.1\,\mu\text{W}$ | $+33.5\%$ |
| Total Dynamic Switching Power | $103.50\,\mu\text{W}$ | $137.90\,\mu\text{W}$ | $+34.40\,\mu\text{W}$ | $+33.2\%$ |
| Static Leakage Power | $2.52\,\text{nW}$ | $3.10\,\text{nW}$ | $+0.58\,\text{nW}$ | $+23.0\%$ |
| **TOTAL STRESS POWER** | **103.50 µW** | **138.00 µW** | **+34.50 µW** | **+33.3%** |

*Epistemic Note*: All power numbers are post-route VCD-workload-derived estimates in open-source SkyWater 130nm CMOS (`sky130_fd_sc_hd`, TT, 25°C, 1.80V) with OpenRCX 3D parasitic extraction. Measured silicon power is currently pending manufacturing. Secondary static sensitivity sweep (Scenario A, $\alpha=0.075$) yields 50.90 nW.
