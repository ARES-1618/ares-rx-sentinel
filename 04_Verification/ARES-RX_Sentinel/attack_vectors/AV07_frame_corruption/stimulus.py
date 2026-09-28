"""
AV07 Frame Corruption Stimulus Generator
Generates valid Manchester timing with invalid protocol framing syntax.
"""

def generate_av07_stimulus():
    # Manchester encode a corrupt preamble (all zeros instead of alternating 1010)
    # Bit 0 = 0 -> 1 (low for 9 cyc, high for 9 cyc)
    stream = []
    for _ in range(32): # Corrupt preamble: sequence of zeros
        stream.extend([0] * 9)
        stream.extend([1] * 9)
    return stream

if __name__ == "__main__":
    s = generate_av07_stimulus()
    print(f"Generated AV07 stimulus with {len(s)} samples.")
