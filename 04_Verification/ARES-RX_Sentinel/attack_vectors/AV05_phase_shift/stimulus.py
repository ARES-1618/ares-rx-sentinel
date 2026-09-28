"""
AV05 Phase Shift / Drift Stimulus Generator
Generates streams with controlled jitter to test boundary limits.
"""

def generate_av05_stimulus(scenario="within_tolerance"):
    stream = []
    if scenario == "within_tolerance":
        # Alternating 8 and 10 cycle half-bits (allowed)
        for _ in range(4):
            stream.extend([1] * 8)
            stream.extend([0] * 10)
    else:
        # Severe drift: 7 cycle half-bit (illegal)
        stream.extend([1] * 9)
        stream.extend([0] * 7)
    return stream

if __name__ == "__main__":
    s1 = generate_av05_stimulus("within_tolerance")
    s2 = generate_av05_stimulus("exceeding_tolerance")
    print(f"Generated AV05 within ({len(s1)}) and exceeding ({len(s2)}) samples.")
