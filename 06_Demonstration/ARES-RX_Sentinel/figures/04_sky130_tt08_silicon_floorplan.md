# ARES-RX Sentinel — SkyWater 130nm TT08 Physical Silicon Floorplan
## Document: `06_Demonstration/ARES-RX_Sentinel/figures/04_sky130_tt08_silicon_floorplan.md`
**Technology:** SkyWater 130nm High-Density CMOS (`sky130_fd_sc_hd`)  
**Silicon Envelope:** Tiny Tapeout TT08 $1 \times 1$ Standard Tile ($161.00\,\mu\text{m} \times 111.52\,\mu\text{m}$)  
**Total Silicon Area:** $17,954.72\,\mu\text{m}^2$  

---

## 1. Physical Tile Floorplan & Pinout Map

```text
                               161.00 um
  +-------------------------------------------------------------------+
  |               TOP EDGE: VPWR (1.8V) / VGND (0.0V) PDN             |
  |  +-------------------------------------------------------------+  |
  |  | CORE SITE: 146.92 um x 89.76 um (13,187.54 um^2)            |  |
  |  |                                                             |  |
u |  |  [Layer 1: Temporal Sentinel]    [Baseline Demodulator]     |  | u
i |  |   - 103 stdcells                  - 594 stdcells            |  | o
_ |  |   - 8-bit interval counter        - 97-bit shift register   |  | _
i |  |   - Discrete window decoders      - Clock demodulator       |  | o
n |  |                                                             |  | u
  |  |  [Layer 2: Syntax Monitor]       [Clock Tree Buffers]       |  | t
[ |  |   - 74 stdcells                   - 17 clkbuf cells         |  | [
7 |  |   - 192-bit state machine         - Balanced H-Tree skew    |  | 7
: |  |   - Grammar comparator                                      |  | :
0 |  |                                  [Layer 3: Isolation Gate]  |  | 0
] |  |  [225 Substrate Tap Cells]        - Combinational clamping  |  | ]
  |  |  [78 Decap Endcap Cells]          - Sticky fault latch      |  |  
  |  |  [1,547 Row Filler Cells]         - 37 stdcells             |  |  
  |  +-------------------------------------------------------------+  |
  |             BOTTOM EDGE: uio[7:0] BIDIRECTIONAL PINS              |
  +-------------------------------------------------------------------+
                                111.52 um
```

---

## 2. Tiny Tapeout TT08 Pinframe Assignment

| Pin Group | Pin Name | Direction | Signal Function | Security / Functional Role |
| :--- | :--- | :---: | :--- | :--- |
| **Clock & Reset** | `clk` | Input | Master System Clock | $20.00\,\text{kHz}$ nominal protocol clock ($T = 50\,\mu\text{s}$) |
| | `rst_n` | Input | Active-Low Reset | Asynchronous system reset and fault latch clearing |
| | `ena` | Input | Design Enable | Tiny Tapeout tile enable signal |
| **Primary Inputs** | `ui_in[0]` | Input | `rx_in` (Baseband CMOS) | Demodulated digital Manchester signal from receiver IC |
| | `ui_in[3:1]`| Input | Unused / Reserved | Internally tied to `_unused` reduction logic |
| | `ui_in[7:4]`| Input | `address[3:0]` | Baseline parallel readout byte address selector |
| **Primary Outputs**| `uo_out[7:0]`| Output | `data_out[7:0]` | **Isolated Safe Data Bus** (Clamped to `0x00` on attack) |
| **Bidirectional** | `uio[0]` | Output | `tamper_alert` | **Hardware Security Interrupt** (Asserts high on tamper) |
| | `uio[1]` | Output | `reception_active` | Layer-1 active transmission envelope indicator |
| | `uio[2]` | Output | `l1_temporal_fault` | Real-time temporal anomaly indicator pulse |
| | `uio[3]` | Output | `l2_syntax_fault` | Real-time syntax anomaly indicator pulse |
| | `uio[4]` | Output | `l3_isolated` | Hardware isolation status level |
| | `uio[5]` | Output | `baseline_full` | Legacy demodulator full flag (diagnostic) |
| | `uio[6]` | Output | `baseline_clock` | Recovered Manchester clock (diagnostic) |
| | `uio[7]` | Output | `baseline_data` | Recovered Manchester data bit (diagnostic) |

---

## 3. Power Distribution Network (PDN) & Metal Stack

```text
Layer Stack (SkyWater 130nm 5-Metal Process):
  met5 (Top)       : Top-level VDD/VSS supply interface straps (Width: 1.60 um)
  met4 (Vertical)  : Vertical power/ground distribution trunks (Width: 1.60 um, Pitch: 38.87 um)
  met3 (Horizontal): Long-distance signal routing & clock trunk distribution
  met2 (Vertical)  : Local signal interconnect & cell pin connection
  met1 (Horizontal): Standard cell follow-rails (Width: 0.48 um, Pitch: 5.44 um)
  li1  (Local)     : Transistor-level routing inside standard cell macros
```

### Physical Latch-up Protection & Design Rules
- **Substrate Tap Density:** 225 tap cells placed uniformly every $\le 14\,\mu\text{m}$ across all 33 rows. Maximum well-tie rule is $15\,\mu\text{m}$, giving $> 7\%$ design safety margin against CMOS latch-up.
- **Clock Tree Synthesis (CTS):** 17 distributed clock buffers (`sky130_fd_sc_hd__clkbuf_2/16`) maintain clock skew under **$0.08\,\text{ns}$** ($0.4\%$ of the $20\,\text{ns}$ stress clock and $0.00016\%$ of the $20\,\text{kHz}$ operational clock).
