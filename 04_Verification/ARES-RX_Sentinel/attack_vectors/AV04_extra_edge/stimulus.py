"""
AV04 Extra Edge Stimulus Generator
Inserts an extra edge inside a Manchester bit interval.
"""

def generate_av04_stimulus():
    stream = []
    # 2 nominal half-bits
    stream.extend([1] * 9)
    stream.extend([0] * 9)
    # EXTRA EDGE: split half-bit into 4 cycles high, 5 cycles low
    stream.extend([1] * 4)
    stream.extend([0] * 5)
    stream.extend([1] * 9)
    return stream

if __name__ == "__main__":
    s = generate_av04_stimulus()
    print(f"Generated AV04 stimulus with {len(s)} samples.")
