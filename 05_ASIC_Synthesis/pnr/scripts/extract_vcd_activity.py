import re
import sys

def parse_vcd_activity(vcd_path):
    sym_to_name = {}
    name_to_sym = {}
    time_scale = 1e-9 # default 1ns
    
    with open(vcd_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('$var'):
                parts = line.split()
                if len(parts) >= 5:
                    var_type, size, sym, name = parts[1], parts[2], parts[3], parts[4]
                    sym_to_name[sym] = (name, int(size))
                    name_to_sym[name] = sym
            if line.startswith('$enddefinitions'):
                break
        
        # Now count toggles
        toggles = {sym: 0 for sym in sym_to_name}
        last_val = {}
        current_time = 0
        max_time = 0
        
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                current_time = int(line[1:])
                if current_time > max_time:
                    max_time = current_time
                continue
            if line.startswith(('0', '1', 'x', 'z', 'X', 'Z')):
                val = line[0]
                sym = line[1:]
                if sym in toggles:
                    if sym in last_val and last_val[sym] != val and val in ('0', '1'):
                        toggles[sym] += 1
                    last_val[sym] = val
            elif line.startswith(('b', 'B', 'r', 'R')):
                parts = line.split()
                if len(parts) >= 2:
                    val = parts[0][1:]
                    sym = parts[1]
                    if sym in toggles:
                        if sym in last_val and last_val[sym] != val:
                            toggles[sym] += 1
                        last_val[sym] = val

    print(f"Simulation max time: {max_time} (time units)")
    clk_sym = name_to_sym.get('clk')
    clk_toggles = toggles.get(clk_sym, 0)
    total_cycles = clk_toggles // 2
    print(f"Clock toggles: {clk_toggles} -> Total Clock Cycles: {total_cycles}")
    
    print("\n=== Signal Activity Factors (Workload: ares_sentinel_integrated.vcd) ===")
    print(f"{'Signal Name':<30} {'Width':<6} {'Toggles':<10} {'Transitions/Cycle':<20} {'Toggle Rate (alpha)':<20}")
    print("-" * 90)
    
    results = []
    for sym, (name, width) in sym_to_name.items():
        t = toggles[sym]
        trans_per_cycle = t / total_cycles if total_cycles > 0 else 0
        # alpha is defined as probability of transition per clock cycle = trans_per_cycle / 2 (or trans_per_cycle)
        # In OpenSTA set_power_activity: -activity is transitions per clock cycle!
        alpha = trans_per_cycle
        results.append((name, width, t, trans_per_cycle, alpha))
    
    # Sort by toggles descending
    results.sort(key=lambda x: x[2], reverse=True)
    for name, width, t, trans_per_cycle, alpha in results[:40]:
        print(f"{name:<30} {width:<6} {t:<10} {trans_per_cycle:<20.4f} {alpha:<20.4f}")

    # Specific important signals
    target_sigs = ['clk', 'rx_in', 'serial_data', 'serial_clock', 'reception_active', 'tamper_alert', 'out_valid', 'frame_complete', 'temporal_fault', 'frame_fault']
    print("\n=== Target Protocol Signals ===")
    for ts in target_sigs:
        found = False
        for name, width, t, trans_per_cycle, alpha in results:
            if name == ts:
                print(f"  {name:<25}: toggles={t:<8} activity(trans/clk)={trans_per_cycle:.4f}")
                found = True
                break
        if not found:
            print(f"  {ts:<25}: [Not explicitly in top VCD]")

parse_vcd_activity('/mnt/c/Users/ahmad/OneDrive/Vscode/03_Core_Projects/ARES SEMIKONDUKTOR TECHNOLOGY/04_Verification/ARES-RX_Sentinel/waveforms/ares_sentinel_integrated.vcd')
