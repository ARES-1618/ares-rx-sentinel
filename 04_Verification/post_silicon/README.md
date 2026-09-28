# ARES-RX Sentinel — Post-Silicon Laboratory Bring-Up Harness
## Directory: `04_Verification/post_silicon/`

This directory contains the physical test runner scripts and firmware to validate fabricated **SkyWater 130nm TT08** silicon chips for **ARES-RX Sentinel** on a laboratory benchtop.

---

## 1. Directory Assets

* [`rp2040_stimulus_generator.py`](rp2040_stimulus_generator.py): Python generator that produces calibrated CSV test vectors and C header definitions.
* [`stimulus_vectors.h`](stimulus_vectors.h): C array of nominal and attack pulse durations for embedded controllers.
* [`rp2040_bringup_main.c`](rp2040_bringup_main.c): Autonomous benchtop test runner firmware for the Raspberry Pi Pico (RP2040).
* [`nominal_stimulus.csv`](nominal_stimulus.csv): 451-transition CSV vector for Saleae Logic or arbitrary waveform generators.
* [`runt_glitch_stimulus.csv`](runt_glitch_stimulus.csv): Adversarial runt-pulse glitch test vector.

---

## 2. Wiring Connections (RP2040 -> TT08 Demo Board Carrier)

| Raspberry Pi Pico Pin | Direction | TT08 Chip Pin | Description |
| :--- | :--- | :--- | :--- |
| `GPIO 2` | Output | `clk` | Master Clock ($20\,\text{kHz}$) |
| `GPIO 3` | Output | `rst_n` | Active-low hardware reset |
| `GPIO 4` | Output | `ui_in[0]` (`rx_in`) | Calibrated baseband pulse stream |
| `GPIO 5` | Input  | `uio[6]` (`tamper_alert`) | Hardware tamper interrupt monitor |
| `GPIO 6` | Input  | `uio[7]` (`reception_active`)| Layer-1 envelope monitor |
| `GPIO 8..15` | Input  | `uo_out[7:0]` | Safe 8-bit parallel bus |
| `GND` | Common | `GND` | Ground reference |

---

## 3. How to Run the Post-Silicon Test

1. **Compile & Flash RP2040 Firmware:**
   ```bash
   mkdir build && cd build
   cmake ..
   make
   # Copy rp2040_bringup_main.uf2 to Raspberry Pi Pico in BOOTSEL mode
   ```

2. **Open Serial Terminal (USB-CDC):**
   ```bash
   minicom -b 115200 -D /dev/ttyACM0
   ```

3. **Expected Output:**
   ```text
   ==============================================================
      ARES-RX SENTINEL: PHYSICAL SILICON POST-BRINGUP RUNNER     
      Target: SkyWater 130nm TT08 ASIC Test Coupon               
   ==============================================================

   [TEST 1] Executing Nominal 192-bit Transmission Test...
            Output Data Bus: 0x15 | Tamper Strobe: 0
            -> RESULT: PASS (Zero false alarm)

   [TEST 2] Executing Adversarial Runt-Pulse Glitch Injection Test...
            Output Data Bus: 0x00 | Tamper Strobe: 1
            -> RESULT: PASS (Runt trapped in 1 cycle, bus zeroized)

   --------------------------------------------------------------
   >>> ALL SILICON BENCHTOP ACCEPTANCE TESTS PASSED (100%) <<<
   --------------------------------------------------------------
   ```
