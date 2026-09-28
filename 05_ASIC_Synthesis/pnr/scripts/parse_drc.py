#!/usr/bin/env python3
import sys

if len(sys.argv) < 2:
    print("Usage: parse_drc.py <drc_log>")
    sys.exit(1)

with open(sys.argv[1]) as f:
    lines = f.readlines()

if not lines:
    print("Empty log")
    sys.exit(0)

print(lines[0].strip())
if len(lines) > 1:
    print(lines[1].strip())

for line in lines[2:]:
    if " : " in line:
        rule, coords = line.split(" : ", 1)
        count = coords.count("{")
        print(f"  {rule}: {count}")
