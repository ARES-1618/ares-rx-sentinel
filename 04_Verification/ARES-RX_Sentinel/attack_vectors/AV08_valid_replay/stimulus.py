"""
AV08 Valid Replay Stimulus Generator
Loads ground-truth hardware logic analyzer captures for nominal regression.
"""
import os, csv

def load_nominal_hardware_stream():
    csv_path = os.path.join(
        os.path.dirname(__file__),
        "../../../03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/test/data/transmission_digital_hs.csv"
    )
    stream = []
    if os.path.exists(csv_path):
        with open(csv_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and not row[0].startswith("#") and row[0] != "Time (s)":
                    stream.append(int(row[2])) # DIO 0
    return stream

if __name__ == "__main__":
    s = load_nominal_hardware_stream()
    print(f"Loaded AV08 nominal capture with {len(s)} physical samples.")
