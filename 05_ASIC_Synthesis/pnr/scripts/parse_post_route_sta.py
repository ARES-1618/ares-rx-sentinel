#!/usr/bin/env python3
import sys
import re

with open("05_ASIC_Synthesis/pnr/results/post_route_sta_reports.txt") as f:
    text = f.read()

designs = text.split("POST-ROUTE DESIGN:")
for d in designs[1:]:
    header = d.splitlines()[0].strip()
    print("================================================================================")
    print("DESIGN:", header)
    print("================================================================================")
    
    sections = re.split(r'>>>\s+', d)
    for s in sections[1:]:
        lines = s.strip().splitlines()
        title = lines[0].strip()
        
        # Check for timing slack
        slacks = [l.strip() for l in lines if "slack (" in l]
        if slacks:
            print(f"\n[{title}]")
            for sl in slacks:
                print(f"  {sl}")
        
        # Check for power
        if "Activity Scenario:" in title or "Total" in s:
            total_power_line = [l.strip() for l in lines if l.strip().startswith("Total")]
            if total_power_line:
                print(f"  {title}: {total_power_line[0]}")
