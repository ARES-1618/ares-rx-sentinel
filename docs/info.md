# ARES-RX Sentinel: Silicon-Level Trusted Digital Reception Boundary

## How It Works

ARES-RX Sentinel is a first-in-class, silicon-level hardware security boundary designed to protect edge microcontrollers and Sub-GHz RF receivers (e.g. 433.92 MHz ISM Band) against physical baseband glitches, clock desynchronization, and malformed frame injection attacks.

Unlike software-based packet validators that execute on a host CPU and are susceptible to buffer overflows or denial-of-service interrupt storms, ARES-RX Sentinel enforces physical and syntactic trust directly at the digital baseband boundary in discrete silicon logic before data touches host memory.

It enforces a dual-condition mathematical trust formulation:
$$V_{\text{trusted}} = V_{\text{physical}} \land V_{\text{protocol}}$$

### 3-Layer Defense-in-Depth Architecture:
1. **Layer 1: Temporal Integrity Sentinel (`ares_timing_sentinel.v`)**
   - Continuously measures pulse durations on `rx_in` using a 20 kHz nominal clock ($T_{\text{clk}} = 50.0\,\mu\text{s}$).
   - Validates that half-bit ($N_{\text{HB}} \in [8..10]$ cycles) and full-bit ($N_{\text{BIT}} \in [16..20]$ cycles) Manchester intervals conform to strict physical bounds.
   - Rejects runt glitches ($N \le 7$ cycles), mid-band desync ($11 \le N \le 15$ cycles), and missing-edge timeouts ($N \ge 21$ cycles).
   - Tracks reception envelope (`reception_active`) and qualifies End-of-Packet ($N_{\text{EOF}} = 64$ silence cycles).

2. **Layer 2: Frame Syntax Monitor (`ares_frame_fsm.v`)**
   - Autonomous bit counter ($0 \dots 191$) synchronous to the demodulator sample clock.
   - On-the-fly verification of static fields: Preamble (`32'hAAAAAAAA`), Type 1/2 (`16'hD391`), and Protocol Constant (`32'h0DFFFFFE`).
   - Dynamic payload passthrough (bits 96..167 for Thermostat ID and temperature telemetry).
   - Traps frame truncation and post-192-bit frame overrun attacks.

3. **Layer 3: Hardware Fail-Closed Isolation (`ares_isolation_l3.v`)**
   - Upstream priority arbiter resolves same-cycle faults ($L1 > L2$).
   - Asynchronous sticky fault latch preserves first-cause error state.
   - High-speed combinational zeroization gate forces the output data bus to `8'h00` within exactly **1 clock cycle**.
   - Non-maskable hardware alarm strobe on `uio_out[6]` (`tamper_alert`).

---

## Post-Route Silicon Benchmark (SkyWater 130nm TT08)

* **Die Dimensions:** $161.00\,\mu\text{m} \times 111.52\,\mu\text{m}$ ($1 \times 1$ Standard Tile)
* **Standard Cell Area:** $6,477.46\,\mu\text{m}^2$ ($36.08\%$ gross tile fraction)
* **Total Placed Area:** $10,186.02\,\mu\text{m}^2$ ($56.73\%$, 758 logic cells & clock buffers)
* **Operating Power:** $\mathbf{50.90\,\text{nW}}$ @ $20\,\text{kHz}$ ($1.8\,\text{V}$, $\alpha = 0.075$, duty 0.50)
* **Timing Margins:** Setup Slack $+11.88\,\text{ns}$ @ $50\,\text{MHz}$ stress test ($F_{\max} \approx 123.7\,\text{MHz}$), Hold Slack $+0.42\,\text{ns}$
* **Physical Sign-Off:** 0 Active DRC violations, 100% LVS Match (758/758 gates)

---

## How to Test

### 1. Nominal Transmission Test
1. Set `rst_n = 0` for 10 cycles, then release `rst_n = 1` with `halt = 0` (pin `ui_in[2] = 0`).
2. Stream a nominal 192-bit Manchester frame on `rx_in` (pin `ui_in[0]`) at 20 kHz with `halt = 0` (preamble `0xAAAAAAAA`, types `0xD391`, constant `0x0DFFFFFE`, dynamic telemetry payload, and trailers).
3. Observe `reception_active` (pin `uio_out[7]`) asserted high during transmission and returning to low after 64 silence cycles.
4. Wait $\ge 65$ silence cycles for End-of-Packet (EOP) settling.
5. Confirm `tamper_alert` (pin `uio_out[6]`) remains low (`0`), verifying zero false alarms.
6. Set `halt = 1` (pin `ui_in[2] = 1`) to halt demodulation and enable safe parallel readback onto `uo_out[7:0]`.
7. Iterate `address[3:0]` (pins `ui_in[7:4]`) from `0` to `11` to read all 12 decoded telemetry payload registers (`thermostat_id`, `room_temp`, `set_temp`, `state`, and trailer bytes).

### 2. Adversarial Glitch Injection Test
1. Ensure `halt = 0` during active reception. Arm the Layer-1 temporal monitor with a valid half-bit transition ($9$ cycles high, $9$ cycles low).
2. Inject a 4-cycle runt glitch ($200\,\mu\text{s} < 8$ clock cycles minimum valid half-bit) on `rx_in`.
3. Within 1 clock cycle ($50\,\mu\text{s}$), observe `tamper_alert` (pin `uio_out[6]`) asserted and sticky-latched high (`1`).
4. Set `halt = 1` and iterate across all multiplexer read addresses (`address = 0..11`); confirm `uo_out[7:0]` is strictly zeroized to `0x00`, verifying hardware fail-closed isolation.
5. Observe that `tamper_alert` remains asserted even after `rx_in` returns to idle silence, confirming sticky latch persistence.
6. Apply `rst_n = 0` to clear the security fault state.

---

## Pinout Mapping

| Pin | Type | Signal Name | Description |
| :--- | :--- | :--- | :--- |
| `ui_in[0]` | Input | `rx_in` | Demodulated baseband digital input |
| `ui_in[2]` | Input | `halt` | Demodulator enable & readback control (`halt = 0`: active reception; `halt = 1`: readback output enable) |
| `ui_in[7:4]` | Input | `address[3:0]` | Parallel multiplexer read address (0..11 valid registers) |
| `uo_out[7:0]`| Output| `data_out[7:0]`| Safe parallel output bus (Gated by `halt`, zeroized on fault) |
| `uio_out[0]` | Output| `baseline_full`| Baseline frame complete flag |
| `uio_out[1]` | Output| `manchester_clock` | Recovered baseband sample clock |
| `uio_out[2]` | Output| `manchester_data` | Demodulated serial bitstream |
| `uio_out[3]` | Output| `transmission_begin` | Transmission detect flag |
| `uio_out[6]` | Output| `tamper_alert` | **Security alarm** (Sticky hardware latch, non-maskable) |
| `uio_out[7]` | Output| `reception_active` | Physical RF envelope active monitor |
