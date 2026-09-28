# Figure 3: Threat Latching & Output Isolation Timing Diagram

**Figure ID**: `FIG-03`  
**Target Paper Section**: Section III (Threat Model & Security Properties) & Section VIII (Results)  
**Caption**: *Waveform timing relation demonstrating synchronous single-cycle fault latching ($T_{\text{latch}}=1$) and zero-additional-cycle combinational bus zeroization ($T_{\text{isolate}}=0, T_{\text{safe}}=0$).*

```text
Clock Cycle:       | N-1              | N (Condition)    | N+1 (Latched)    | N+2              |
                   |                  |                  |                  |                  |
clk                _/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_
                   |                  |                  |                  |                  |
rx_in              XXXXXXXXXXXXXXX    [ RUNT GLITCH <8 ] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                   |                  |                  |                  |                  |
cycle_counter      [   5   ][   6   ] [   7   ] (PULSE)  [   0   ][   1   ] [   2   ][   3   ]
                   |                  |                  |                  |                  |
fault_condition    ___________________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\_____________________________________
                   (Combinational internal strobe asserted at Cycle N)
                   |                  |                  |                  |                  |
tamper_alert_r     ______________________________________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
                   (Synchronously latched at Cycle N+1: T_latch = 1 clock cycle)
                   |                  |                  |                  |                  |
fault_code_r[2:0]  [    3'b000 (NONE)                    ][     3'b001 (FAULT_RUNT)           ]
                   |                  |                  |                  |                  |
raw_decoder_data   [    0x55 (Unsafe/Garbage Data)       ][     0x55 / Random Transitions     ]
                   |                  |                  |                  |                  |
safe_data_out[7:0] [    0x55                             ][     0x00 (FAIL-SAFE ZEROIZED)     ]
                   (Zeroized combinational bus clamping active on Cycle N+1: T_isolate = 0)
```
