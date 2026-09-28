"""
AV03 Missing Edge Stimulus Generator
Skips a required mid-bit Manchester transition.
"""

def generate_av03_stimulus():
    stream = []
    # 4 nominal half-bits
    for _ in range(4):
        stream.extend([1] * 9)
        stream.extend([0] * 9)
    # MISSING EDGE: keeps line at 0 for 14 cycles (falls in illegal mid-band 11-15 cycles)
    stream.extend([0] * 14)
    stream.extend([1] * 9)
    return stream

if __name__ == "__main__":
    s = generate_av03_stimulus()
    print(f"Generated AV03 stimulus with {len(s)} samples.")
