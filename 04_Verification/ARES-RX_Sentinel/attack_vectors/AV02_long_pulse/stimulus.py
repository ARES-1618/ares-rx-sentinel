"""
AV02 Long Gap Ambiguity Stimulus Generator
Provides test vectors for:
- AV02-A: Missing Edge with Signal Resume
- AV02-B: Normal Packet Termination Silence
"""

def generate_av02_a_stimulus():
    """Missing edge in active burst: gap of 35 cycles followed by edge resume."""
    stream = []
    # 4 nominal half-bits
    for _ in range(4):
        stream.extend([1] * 9)
        stream.extend([0] * 9)
    # Long gap: 35 cycles of constant low
    stream.extend([0] * 35)
    # Edge resumes
    stream.extend([1] * 9)
    stream.extend([0] * 9)
    return stream

def generate_av02_b_stimulus(eof_cycles=64):
    """Normal packet termination: active burst followed by prolonged silence >= N_EOF."""
    stream = []
    # 4 nominal half-bits
    for _ in range(4):
        stream.extend([1] * 9)
        stream.extend([0] * 9)
    # Prolonged silence exceeding N_EOF
    stream.extend([0] * (eof_cycles + 10))
    return stream

if __name__ == "__main__":
    sa = generate_av02_a_stimulus()
    sb = generate_av02_b_stimulus()
    print(f"Generated AV02-A ({len(sa)} samples) and AV02-B ({len(sb)} samples).")
