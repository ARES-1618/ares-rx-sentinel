# AV08: Valid Frame Replay / Golden Nominal Vector

## 1. Description
Tests the system under pristine, nominal over-the-air RF transmissions. This vector verifies that ARES-RX Sentinel has **Zero False Positives / Zero False Isolation** when receiving legitimate data packets from legitimate transmitters.

## 2. Stimulus
Uses the exact Digilent Discovery 3 hardware capture from `transmission_digital_hs.csv` with valid Manchester biphase timing and correct preamble/trailer structure.

## 3. Expected Outcome
- **Layer 1**: $V_{physical} = 1$ (All intervals within $\mathcal{V} = [8,10] \cup [16,20]$).
- **Layer 2**: $V_{protocol} = 1$ (Preamble `0xAAAAAAAA`, Type `0xD391`, Constant `0x0DFFFFFE` valid).
- **Layer 3**: $V_{trusted} = 1$, `tamper_alert = 0`. Full 96-bit sensor payload passed accurately to `parallel_out`.
