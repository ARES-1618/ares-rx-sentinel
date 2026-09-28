# AV04: Extra Edge / Contact Bouncing Attack Vector

## 1. Description
Simulates rapid contact bouncing or high-frequency digital noise spikes that insert an extra transition inside an active Manchester symbol.

## 2. Stimulus
Inserts a spurious transition (0 -> 1 -> 0) at cycle 4 within a 9-cycle half-bit period.

## 3. Expected Outcome
- **Baseline ($B$)**: Double clocking or phase inversion of deserializer.
- **Sentinel ($S$)**: Detected as runt pulse ($N=4 \le 7$), `temporal_fault = 1`, immediate zeroization.
