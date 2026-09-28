"""
AV06 Burst Glitch Stimulus Generator
Generates high-frequency noise bursts matching real AGC chatter.
"""
import random

def generate_av06_stimulus(num_pulses=50):
    random.seed(42)
    stream = []
    level = 0
    for _ in range(num_pulses):
        duration = random.choice([1, 2, 3, 4])
        level = 1 - level
        stream.extend([level] * duration)
    return stream

if __name__ == "__main__":
    s = generate_av06_stimulus()
    print(f"Generated AV06 burst stimulus with {len(s)} samples.")
