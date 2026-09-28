# Table 3: Physical Implementation & Sign-off Scorecard

**Table ID**: `TAB-03`  
**Target Paper Section**: Section VII (Physical Design & PPA Characterization)  
**Caption**: *Comprehensive post-route physical implementation parameters and sign-off metrics for baseline demodulator versus protected ARES-RX Sentinel in SkyWater 130nm CMOS.*

| Metric Category & Parameter | Baseline (`tt07-bep-decode`) | ARES Sentinel Top | Overhead / Delta ($\Delta$) | Provenance & EDA Tool |
| :--- | :---: | :---: | :---: | :--- |
| **Gross Die Envelope ($A_{\text{tile}}$)** | $161.00 \times 111.52\,\mu\text{m}$ | $161.00 \times 111.52\,\mu\text{m}$ | $0.00\,\mu\text{m}$ | Standard TT08 1x1 Tile |
| **Gross Tile Area ($A_{\text{tile}}$)** | $17,954.72\,\mu\text{m}^2$ | $17,954.72\,\mu\text{m}^2$ | $0.00\,\mu\text{m}^2$ | Silicon envelope boundary |
| **Gross Core Region ($A_{\text{core}}$)** | $16,493.32\,\mu\text{m}^2$ | $16,493.32\,\mu\text{m}^2$ | $0.00\,\mu\text{m}^2$ | $[2.76, 2.72]$ to $[158.24, 108.80]\,\mu\text{m}$ |
| **Fixed Tap / Decap Area ($A_{\text{fixed}}$)** | $574.30\,\mu\text{m}^2$ | $574.30\,\mu\text{m}^2$ | $0.00\,\mu\text{m}^2$ | 225 taps + 78 decaps = 303 cells |
| **Net Placeable Core Area ($A_{\text{placeable\_net}}$)**| $15,919.02\,\mu\text{m}^2$ | $15,919.02\,\mu\text{m}^2$ | $0.00\,\mu\text{m}^2$ | $A_{\text{core}} - A_{\text{fixed}}$ |
| **Movable Placed Cell Area** | $7,945.12\,\mu\text{m}^2$ | $10,186.02\,\mu\text{m}^2$ | $+2,240.90\,\mu\text{m}^2$ | Movable stdcells + CTS buffers |
| **Net Functional Logic Cell Area ($A_{\text{logic}}$)**| $5,017.31\,\mu\text{m}^2$ | $6,477.46\,\mu\text{m}^2$ | $+1,460.15\,\mu\text{m}^2$ | Pure synthesized functional gates |
| **Total Functional Logic Cells** | 594 | 758 | $+164$ cells | Synthesized Verilog instances |
| **Clock Tree Buffers (CTS)** | 9 | 17 | $+8$ buffers | TritonCTS balanced distribution |
| **Total Placed Instances** | 603 | 766 | $+163$ instances | Placed gate instances |
| **[Tier 1] Reported Core Utilization** | **49.91%** | **63.99%** | $+14.08\%$ | OpenROAD RePlAce `[INFO GPL-0019]` |
| **[Tier 2] Gross Core Box Utilization**| **48.17%** | **61.76%** | $+13.59\%$ | Movable cells / $A_{\text{core}}$ |
| **[Tier 3] Gross Tile Logic Utilization**| **27.94%** | **36.08%** | $+8.14\%$ | $A_{\text{logic}} / A_{\text{tile}}$ |
| **[Tier 4] Gross Tile Placed Utilization**| **44.25%** | **56.73%** | $+12.48\%$ | Placed area / $A_{\text{tile}}$ |
| **Total Routed Wirelength** | $21,208\,\mu\text{m}$ (4,803 vias) | $19,988\,\mu\text{m}$ (5,970 vias) | $-1,220\,\mu\text{m}$ | TritonRoute |
| **Setup Slack @ 50 MHz (Reg-to-Reg)** | $+12.07\,\text{ns}$ ($F_{\text{max}}=126.1\,\text{MHz}$) | $+11.88\,\text{ns}$ ($F_{\text{max}}=123.15\,\text{MHz}$) | $-0.19\,\text{ns}$ | OpenSTA 2.0.17 |
| **Setup Slack @ 50 MHz (IO-Constrained)**| $+7.58\,\text{ns}$ ($F_{\text{max}}=80.52\,\text{MHz}$) | $+7.29\,\text{ns}$ ($F_{\text{max}}=78.68\,\text{MHz}$) | $-0.29\,\text{ns}$ | OpenSTA 2.0.17 |
| **Hold Slack @ 50 MHz (Min Delay)** | $+0.47\,\text{ns}$ | $+0.42\,\text{ns}$ | $-0.05\,\text{ns}$ | OpenSTA 2.0.17 (MET) |
| **Worst Negative Slack (WNS)** | $0.00\,\text{ns}$ | $0.00\,\text{ns}$ | $0.00\,\text{ns}$ | Zero violations |
| **Detailed Route DRC Violations** | 0 violations | 0 violations | 0 violations | TritonRoute |
| **Magic Sign-off DRC Violations** | 859 raw / 0 active | 874 raw / 0 active | 0 active | 874 raw waived under policy |
| **Netgen 1.5.133 LVS Sign-off** | 100% Match | 100% Match | 100% Match | 764 dev, 776 nets, 45 pins |
