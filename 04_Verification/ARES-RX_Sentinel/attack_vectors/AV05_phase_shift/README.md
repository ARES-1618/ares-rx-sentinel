# AV05: Phase Shift / Frequency Drift Attack Vector

## 1. Description
Simulates transmitter oscillator frequency drift due to temperature or supply voltage sag, creating clock skew.

## 2. Stimulus
- Skenario A (Within Tolerance): Jitter $\pm 1$ cycle ($N_{HB} = 8$ or $10$).
- Skenario B (Exceeding Tolerance): Severe drift ($N_{HB} = 7$ or $12$).

## 3. Expected Outcome
- **Within Tolerance**: Lolos tanpa false alarm ($V_{physical} = 1$).
- **Exceeding Tolerance**: Ditolak seketika oleh Layer 1 Sentinel (`temporal_fault = 1`).
