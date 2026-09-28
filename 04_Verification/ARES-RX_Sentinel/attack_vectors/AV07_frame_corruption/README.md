# AV07: Frame Protocol Corruption Attack Vector

## 1. Description
Simulates an attack or channel corruption where timing transitions are legally spaced ($N_{edge} \in \mathcal{V}$), but the frame structural syntax (Preamble or Constant trailer) is corrupted. This specifically exercises **Layer 2 (Frame Protocol Integrity)**.

## 2. Stimulus
Generates a 96-bit preamble sequence where the sync word `0xAAAAAAAA` is altered to `0x55555555` or random data.

## 3. Expected Outcome
- **Layer 1**: Passes without error ($V_{physical} = 1$).
- **Layer 2**: Detects syntax mismatch, asserts `protocol_fault = 1`, FSM transitions to `STATE_FAULT`.
- **Layer 3**: Dual-condition failure ($V_{trusted} = 0 \land 1 = 0$), output remains locked to `0x00`.
