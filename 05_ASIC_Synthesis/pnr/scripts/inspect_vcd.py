import re
import sys

def parse_vcd_header(vcd_path):
    signals = {}
    time_scale = '1ns'
    with open(vcd_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('$timescale'):
                # next lines or same line
                pass
            if line.startswith('$var'):
                parts = line.split()
                if len(parts) >= 5:
                    var_type, size, sym, name = parts[1], parts[2], parts[3], parts[4]
                    signals[sym] = (name, size, var_type)
            if line.startswith('$enddefinitions'):
                break
    print(f"Total signals defined: {len(signals)}")
    for sym, (name, size, var_type) in list(signals.items())[:30]:
        print(f"  sym={sym} : name={name} [size={size}, type={var_type}]")

parse_vcd_header('/mnt/c/Users/ahmad/OneDrive/Vscode/03_Core_Projects/ARES SEMIKONDUKTOR TECHNOLOGY/04_Verification/ARES-RX_Sentinel/waveforms/ares_sentinel_integrated.vcd')
