#!/usr/bin/env python3
"""
Convert OpenROAD powered post-route Verilog (top_routed_pwr.v) to SPICE netlist
matching the exact subcircuit port signatures extracted by Magic.
"""
import re
import sys

def main():
    spice_extracted_path = "05_ASIC_Synthesis/pnr/results/top/top_extracted_clean.spice"
    vlog_pwr_path = "05_ASIC_Synthesis/pnr/results/top/top_routed_pwr.v"
    out_spice_path = "05_ASIC_Synthesis/pnr/results/top/top_routed_pwr.spice"

    # Step 1: Parse subcircuit port orders from extracted SPICE (handling + continuations)
    subckt_ports = {}
    current_cell = None
    in_header = False
    with open(spice_extracted_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(".subckt"):
                parts = line.split()
                current_cell = parts[1]
                subckt_ports[current_cell] = parts[2:]
                in_header = True
            elif line.startswith("+") and current_cell is not None and in_header:
                subckt_ports[current_cell].extend(line[1:].split())
            elif line.startswith(".ends"):
                current_cell = None
                in_header = False
            elif not line.startswith("+"):
                in_header = False

    print(f"Loaded {len(subckt_ports)} subcircuit definitions from extracted SPICE.")

    # Step 2: Parse Verilog module
    with open(vlog_pwr_path, "r") as f:
        content = f.read()

    # Normalize newlines
    content = content.replace("\r\n", "\n")

    # Extract module ports
    mod_match = re.search(r'module\s+tt_um_ares_sentinel_project\s*\((.*?)\);', content, re.DOTALL)
    if not mod_match:
        print("Error: Could not find module header")
        sys.exit(1)

    top_ports = subckt_ports.get("tt_um_ares_sentinel_project", [])
    print(f"Top module ports ({len(top_ports)}): {top_ports[:10]}...")

    # Parse all instances
    # Pattern: <cell_type> <inst_name> ( <connections> );
    inst_pattern = re.compile(r'^\s*(sky130_fd_sc_hd__\w+)\s+(\S+)\s*\((.*?)\);', re.MULTILINE | re.DOTALL)

    out_lines = []
    out_lines.append("* SPICE netlist generated from top_routed_pwr.v for Netgen LVS")
    out_lines.append("* Standard: SkyWater 130nm (sky130_fd_sc_hd)")
    out_lines.append("")

    # Include the subckt declarations as blackbox
    for cell_name, ports in subckt_ports.items():
        if cell_name != "tt_um_ares_sentinel_project":
            out_lines.append(f".subckt {cell_name} {' '.join(ports)}")
            out_lines.append(".ends")
            out_lines.append("")

    # Top subcircuit
    out_lines.append(f".subckt tt_um_ares_sentinel_project {' '.join(top_ports)}")

    num_instances = 0
    for match in inst_pattern.finditer(content):
        cell_type = match.group(1)
        inst_name = match.group(2)
        conns_text = match.group(3)

        # Parse port connections: .PORT(NET)
        # Port connection pattern: .(\w+)\s*\(\s*(.*?)\s*\)
        # Net can be \escaped.id [idx] or normal_net
        port_conns = {}
        for conn_match in re.finditer(r'\.(\w+)\s*\(\s*([^)]*?)\s*\)', conns_text):
            p_name = conn_match.group(1)
            raw_net = conn_match.group(2).strip()
            # Normalize net name:
            # e.g., \u_base_fsm.state [1] -> u_base_fsm.state[1]
            # \u_sentinel_top.u_timing_sentinel.interval_counter [7] -> u_sentinel_top.u_timing_sentinel.interval_counter[7]
            norm_net = re.sub(r'^\\', '', raw_net)
            norm_net = re.sub(r'\s+\[', '[', norm_net)
            if norm_net == "":
                norm_net = "0"
            port_conns[p_name] = norm_net

        # Order ports according to subckt definition
        expected_ports = subckt_ports.get(cell_type)
        if not expected_ports:
            print(f"Warning: Unknown cell type {cell_type}")
            continue

        ordered_nets = []
        for ep in expected_ports:
            net = port_conns.get(ep)
            if not net:
                net = f"{inst_name}/{ep}"
            ordered_nets.append(net)

        out_lines.append(f"X{inst_name} {' '.join(ordered_nets)} {cell_type}")
        num_instances += 1

    out_lines.append(".ends")
    out_lines.append("")

    with open(out_spice_path, "w") as f:
        f.write("\n".join(out_lines))

    print(f"Successfully generated {out_spice_path} with {num_instances} instances.")

if __name__ == "__main__":
    main()
