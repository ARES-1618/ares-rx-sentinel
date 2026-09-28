"""
AV01 Short Pulse / Glitch Injection Stimulus Generator
Generates digital bitstream with illegal runt pulses (N <= 7 clock cycles, < 400 us).
"""
import numpy as np

def generate_av01_stimulus(clock_period_us=50.0):
    # Nominal half-bit: 9 cycles (450 us), full-bit: 18 cycles (900 us)
    # Inject a 2-cycle glitch (100 us) inside preamble
    stream = []
    # 4 nominal half-bits
    for _ in range(4):
        stream.extend([1] * 9)
        stream.extend([0] * 9)
    # GLITCH: 2 cycles high, then low
    stream.extend([1] * 2)
    stream.extend([0] * 9)
    return stream

if __name__ == "__main__":
    s = generate_av01_stimulus()
    print(f"Generated AV01 stimulus with {len(s)} samples.")
