#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from collections import Counter

if len(sys.argv) < 2:
    print("Usage: parse_klayout_drc.py <drc_xml_file>")
    sys.exit(1)

xml_file = sys.argv[1]
try:
    tree = ET.parse(xml_file)
    root = tree.getroot()
except Exception as e:
    print(f"Error parsing {xml_file}: {e}")
    sys.exit(1)

counts = Counter()
for item in root.findall(".//item"):
    cat = item.find("category")
    counts[cat.text if cat is not None else "unknown"] += 1

total = sum(counts.values())
print(f"Total DRC Violations in {xml_file}: {total}")
for k, v in counts.most_common():
    print(f"  {k}: {v}")
