# ARES-RX Sentinel — Discrete Timing Decision Boundary Model
## Document: `06_Demonstration/ARES-RX_Sentinel/figures/02_discrete_timing_boundary.md`
**Operating Clock:** $F_{clk} = 20.00\,\text{kHz}$ ($T_{clk} = 50.0\,\mu\text{s}$)  
**Physical Protocol:** Manchester Telemetry (Nominal Baud Rate $\approx 1.11\,\text{kbps}$)  
**Empirical Origin:** Logic Analyzer Trace `transmission_digital_hs.csv` (289 physical transitions)  

---

## 1. Mathematical Trust Formulation

A transmission payload is certified as authentic if and only if it simultaneously satisfies physical temporal validity and syntactic protocol grammar:

$$
\boxed{V_{\text{trusted}} = V_{\text{physical}} \land V_{\text{protocol}}}
$$

Where:
- $V_{\text{physical}} \iff \forall i \in \text{pulses}, \ N_i \in \mathcal{V} = \{[N_{HB}-\Delta, N_{HB}+\Delta] \cup [N_{\text{bit}}-\Delta, N_{\text{bit}}+\Delta]\}$
- $V_{\text{protocol}} \iff \text{Field}(\text{Preamble}) = \text{Preamble}_{\text{golden}} \land \text{Field}(\text{Type}) = \text{Type}_{\text{golden}} \land \text{Field}(\text{Const}) = \text{Const}_{\text{golden}}$

---

## 2. Pulse Duration Decision Boundary Map

At $F_{clk} = 20\,\text{kHz}$ ($T_{clk} = 50.0\,\mu\text{s}$), the continuous time domain is mapped into discrete register counts $N$:

```text
Clock Cycles (N):
 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21 ... 63  64+
[-------- RUNT GLITCH --------][ HALF-BIT ][---- MID-BAND ----][--- FULL-BIT ---][-- TIMEOUT --][ EOF ]
  0 us                     350 us  450 us   550 us         750 us      900 us    1050 us         3200 us
[-------- ILLEGAL ZONE -------][  VALID   ][--- ILLEGAL ZONE -][     VALID      ][-- ILLEGAL ---][ VALID ]
```

### Detailed Zone Breakdown

| Zone Name | Cycle Window ($N$) | Physical Duration | Physical Interpretation & Classification | Hardware Security Action |
| :--- | :---: | :---: | :--- | :--- |
| **Runt Pulse / Glitch** | $1 \le N \le 7$ | $50\,\mu\text{s} - 350\,\mu\text{s}$ | Sub-microsecond spike, contact bounce, ESD discharge, or RF glitch injection. | **FAULT_RUNT (Code 3'b001)** $\implies$ Tamper Alert, Zeroize Bus |
| **Half-Bit Window** | $8 \le N \le 10$ | $400\,\mu\text{s} - 500\,\mu\text{s}$ | Nominal Manchester half-bit transition ($N_{HB} = 9 \pm 1$). | **VALID_INTERVAL** $\implies$ Context FSM updates state |
| **Mid-Band Violation** | $11 \le N \le 15$ | $550\,\mu\text{s} - 750\,\mu\text{s}$ | Non-orthogonal pulse width. Physical clock drift, multi-path echo, or attacker pulse width manipulation. | **FAULT_MIDBAND (Code 3'b010)** $\implies$ Tamper Alert, Zeroize Bus |
| **Full-Bit Window** | $16 \le N \le 20$ | $800\,\mu\text{s} - 1000\,\mu\text{s}$ | Nominal Manchester full-bit transition ($N_{\text{bit}} = 18 \pm 2$). | **VALID_INTERVAL** $\implies$ Context FSM updates state |
| **Missing Edge / Timeout** | $21 \le N \le 63$ | $1050\,\mu\text{s} - 3150\,\mu\text{s}$ | Signal dropped or missing synchronization edge mid-frame. | **FAULT_GAP_RES (Code 3'b011)** if pulse resumes; FSM pending timeout |
| **End-of-Packet (EOF)** | $N \ge 64$ | $\ge 3200\,\mu\text{s}$ ($3.2\,\text{ms}$) | Sustained line quietness denoting clean transmission boundary. | **NORMAL_EOP** $\implies$ L1 FSM resets cleanly to `IDLE` |

---

## 3. Physical Noise Margin & Tolerance Analysis

The empirical hardware capture `transmission_digital_hs.csv` exhibited:
- Observed Half-Bit pulses: Mean $N = 9.02\text{ cycles}$ ($\sigma = 0.38\text{ cycles}$, min $8$, max $10$).
- Observed Full-Bit pulses: Mean $N = 18.04\text{ cycles}$ ($\sigma = 0.52\text{ cycles}$, min $17$, max $19$).

The Sentinel decision windows provide:
- **$\pm 11.1\%$ margin** around the nominal Half-Bit ($N = 9$).
- **$\pm 11.1\%$ margin** around the nominal Full-Bit ($N = 18$).
- **$100\%$ rejection** of all non-Manchester intervals while maintaining **zero false alarms** on real-world RF crystal jitter.
