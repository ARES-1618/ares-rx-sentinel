# Figure 2: Detailed Microarchitectural Submodule Decomposition

**Figure ID**: `FIG-02`  
**Target Paper Section**: Section V (RTL Implementation & Hardware Circuitry)  
**Caption**: *Submodule structural interconnection and datapath decomposition of `ares_sentinel_top`, detailing hardware counters, comparison registers, and MUX structures.*

```text
+===================================================================================================+
|                                    ares_sentinel_top (758 Cells)                                  |
|                                                                                                   |
|  clk (20 kHz) -------------------------------------------------------------+                      |
|  rst_n --------------------------------------------------------------------+                      |
|                                                                            |                      |
|               +----------------------+                                     |                      |
|  rx_in ------>|  ares_edge_detector  |-- edge_detected                     |                      |
|               |  (2x FF Sync + XOR)  |-- edge_type (Rise/Fall)             |                      |
|               +----------+-----------+                                     |                      |
|                          |                                                 |                      |
|                          v                                                 |                      |
|               +----------------------+                                     |                      |
|               | ares_temporal_       |-- fault_runt (width < 8 cyc)        |                      |
|               | watchdog             |-- fault_midband (8 < width < 16)    |                      |
|               | (6-bit HW Counter)   |-- fault_gap_res (gap resumption)    |                      |
|               +----------+-----------+                                     |                      |
|                          |                                                 |                      |
|                          v                                                 v                      |
|               +----------------------+                          +----------------------+          |
|               | ares_frame_validator |                          |   tt07-bep-decode    |          |
|               | (Preamble 32'hAAAA,  |-- fault_preamble         |   (Demodulator Core) |          |
|               |  Type ID, Constant,  |-- fault_type             |                      |          |
|               |  Length Tracker)     |-- fault_const            +----------+-----------+          |
|               +----------+-----------+-- fault_trailer                     | raw_data[7:0]        |
|                          |                                                 |                      |
|                          +-----------------------+                         |                      |
|                                                  |                         |                      |
|                                                  v                         v                      |
|                                       +--------------------+     +-------------------+            |
|                                       | ares_fault_        |     | ares_isolation_   |            |
|                                       | controller         |====>| gate              |===> safe_  |
|                                       | (Priority Encoder  |     | (8-bit Zero MUX)  |     bus    |
|                                       |  & Sticky Latch)   |     +-------------------+     [7:0]  |
|                                       +----------+---------+                                      |
|                                                  | tamper_alert_r (T_latch = 1)                   |
|                                                  +----------------------------------------------->|
+===================================================================================================+
```
