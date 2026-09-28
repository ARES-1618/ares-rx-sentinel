"""
verify_publication_consistency.py
Automated cross-document consistency and forbidden claim audit script.
Audits Proposal, Journal, Abstract, and Control Matrices against frozen invariants.
"""

import os
import re
import sys

DOCS_TO_AUDIT = {
    "proposal": "01_Proposal/ARES_RX_Sentinel_PERURI_Proposal.md",
    "journal": "02_Journal/ARES_RX_Sentinel_Journal_Manuscript.md",
    "abstract": "03_Abstract/ARES_RX_Sentinel_Abstract.md",
}

FORBIDDEN_PATTERNS = [
    (r"silicon operational power confirmed", "Unsubstantiated silicon power claim"),
    (r"measured power on chip", "Unsubstantiated silicon measurement claim"),
    (r"silicon-proven", "Premature silicon status claim"),
    (r"anti-jamming", "Out-of-scope analog RF claim"),
    (r"RF front-end security", "Out-of-scope RF domain claim"),
    (r"filters electromagnetic interference", "Out-of-scope EMI claim"),
    (r"100% secure", "Absolute security overclaim"),
    (r"immune to all attacks", "Absolute security overclaim"),
    (r"PERURI-certified", "Fictitious institutional certification claim"),
    (r"zero-latency isolation", "Physical impossibility without cycle qualification"),
    (r"blockchain-secured", "Cryptographic mislabeling"),
    (r"hardware-in-the-loop", "Premature HIL claim for pre-silicon demonstrator"),
    (r"physical RF packet emulator", "Misleading physical RF emulation claim"),
]

def check_file(name, path):
    print(f"\n==================================================")
    print(f"AUDITING: [{name.upper()}] -> {path}")
    print(f"==================================================")
    
    if not os.path.exists(path):
        print(f"[FAIL] File not found: {path}")
        return False
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    failures = 0
    passes = 0
    
    # 1. Forbidden Claims Check
    print("\n--- 1. Forbidden Claims Audit ---")
    for pattern, reason in FORBIDDEN_PATTERNS:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            print(f"[FAIL] Found forbidden pattern '{pattern}': {reason}")
            print(f"       Context: ...{content[max(0, match.start()-30):min(len(content), match.end()+30)]}...")
            failures += 1
        else:
            passes += 1
    print(f"Forbidden patterns tested: {len(FORBIDDEN_PATTERNS)}, Violations found: {failures}")
    
    # 2. Metric Invariants Check
    print("\n--- 2. Core Metric Invariants Audit ---")
    
    # Check Power 57.90 nW / 57,90 nW
    if "57.90 nW" in content or "57,90 nW" in content or "57.9 nW" in content or "57,9 nW" in content:
        print("[PASS] Power metric 57.90 nW verified")
        passes += 1
    else:
        print("[FAIL] Missing authoritative power 57.90 nW")
        failures += 1
        
    # Check 20 kHz operating point
    if "20 kHz" in content:
        print("[PASS] Operating frequency 20 kHz verified")
        passes += 1
    else:
        print("[FAIL] Missing operating frequency 20 kHz")
        failures += 1
        
    # Check 1-cycle latching & 0-cycle isolation
    has_latch = any(p in content for p in ["T_latch = 1", "T_{latch}=1", r"T_{\text{latch}}=1", "1 siklus", "one clock cycle", "1 clock cycle", "1 cycle"])
    has_isolate = any(p in content for p in ["T_isolate = 0", "T_{isolate}=0", r"T_{\text{isolate}}=0", "0 siklus", "0 additional", "zero additional", "zero-overhead", "tanpa siklus tambahan", "zeroization (T_{isolate}=0)"])
    if has_latch and has_isolate:
        print("[PASS] Timing contract (T_latch=1, T_isolate=0) verified")
        passes += 1
    else:
        print(f"[FAIL] Missing timing contract (latch={has_latch}, isolate={has_isolate})")
        failures += 1

    # Check AV00-AV08 canonical vector count
    if ("AV00" in content and "AV08" in content) or ("8 canonical" in content or "8 skenario" in content or "9 canonical" in content or "9 vektor" in content):
        print("[PASS] Canonical test vector scope verified")
        passes += 1
    else:
        print("[FAIL] Missing canonical vector references")
        failures += 1

    # Document-specific checks for Proposal and Journal
    if name in ["proposal", "journal"]:
        # Check Net Placement Density 63.99% / 63,99%
        if "63.99%" in content or "63,99%" in content:
            print("[PASS] Net placement density 63.99% verified")
            passes += 1
        else:
            print("[FAIL] Missing net placement density 63.99%")
            failures += 1

        # Check Total Placed Cells 766 / Logic Cells 758
        if "766" in content and "758" in content:
            print("[PASS] Standard cell counts (766 placed, 758 logic) verified")
            passes += 1
        else:
            print("[FAIL] Missing cell counts 766 / 758")
            failures += 1

        # Check Setup Slack Reg-to-reg +11.88 ns / Fmax 123.15 MHz
        if ("11.88" in content or "11,88" in content) and ("123.15" in content or "123,15" in content):
            print("[PASS] Setup slack (+11.88 ns) and Fmax (123.15 MHz) verified")
            passes += 1
        else:
            print("[FAIL] Missing timing slack +11.88 ns or Fmax 123.15 MHz")
            failures += 1

        # Check Cycles 10,737 / Evaluations 118,107
        if ("10,737" in content or "10.737" in content) and ("118,107" in content or "118.107" in content):
            print("[PASS] Cycle count 10,737 and evaluations 118,107 verified")
            passes += 1
        else:
            print("[FAIL] Missing cycle count 10,737 or evaluations 118,107")
            failures += 1

        # Check Ledger Anchor Hash
        if "6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0" in content:
            print("[PASS] Cryptographic provenance root anchor verified")
            passes += 1
        else:
            print("[FAIL] Missing cryptographic root anchor")
            failures += 1

    print(f"\nAudit Summary for {name.upper()}: PASSES={passes}, FAILURES={failures}")
    return failures == 0

def main():
    all_ok = True
    for name, path in DOCS_TO_AUDIT.items():
        ok = check_file(name, path)
        if not ok:
            all_ok = False
            
    print("\n==================================================")
    if all_ok:
        print(">>> OVERALL AUDIT VERDICT: 100% CONCORDANT / ZERO VIOLATIONS <<<")
    else:
        print(">>> OVERALL AUDIT VERDICT: AUDIT FAILED WITH DISCREPANCIES <<<")
    print("==================================================")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
