#!/usr/bin/env python3
"""
Adversarial Verification Suite for ARES-RX Sentinel Technical Presentation Deck
Target File: 07_Presentation/ARES_Sentinel_Peruri_Technical_Deck.md
Reference Baseline: 05_ASIC_Synthesis/tt08_submission_repo/README.md
Challenger: Challenger 2 (M2) (teamwork_preview_challenger_m2_2)

This script performs:
1. Negative sweeps for prohibited power phrasing in English and Indonesian.
2. Unauthorized claims of Tiny Tapeout acceptance / Peruri approval / procurement.
3. Cross-check of technical metrics against finalized Phase 1 README.md.
4. Slide structure, source attribution, and epistemic boundary verification.
5. Immutability verification of M4 RTL, M5 metadata, and M6 evidence ledger.
"""

import sys
import os
import re
import json
import hashlib
import subprocess
from pathlib import Path

# Force UTF-8 encoding on standard output for Windows console
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(r"c:\Users\ahmad\OneDrive\Vscode\03_Core_Projects\ARES SEMIKONDUKTOR TECHNOLOGY")
DECK_PATH = REPO_ROOT / "07_Presentation" / "ARES_Sentinel_Peruri_Technical_Deck.md"
README_PATH = REPO_ROOT / "05_ASIC_Synthesis" / "tt08_submission_repo" / "README.md"
M4_VERIFY_SCRIPT = REPO_ROOT / "00_Governance" / "verify_m4_hashes.py"
INFO_MD_PATH = REPO_ROOT / "05_ASIC_Synthesis" / "tt08_submission_repo" / "docs" / "info.md"
INFO_YAML_PATH = REPO_ROOT / "05_ASIC_Synthesis" / "tt08_submission_repo" / "info.yaml"
LEDGER_PATH = REPO_ROOT / "06_Demonstration" / "m6b_isolated_vm_lab" / "m6_unified_evidence_ledger.jsonl"

EXPECTED_LEDGER_ANCHOR = "6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0"
EXPECTED_CI_GDS_RUN = "36320019363"
EXPECTED_CI_TEST_RUN = "36320019357"
EXPECTED_M5_COMMIT = "a748738cf665e63bc9c215748ee5bead18422665"
EXPECTED_M6_RUN_ID = "WO011R1-FINAL-20260927-225358"
EXPECTED_INFO_MD_SHA256 = "0888d516933a06a5db558d7597fd8339dda1cc495ceacff425d1aec93b213085"
EXPECTED_INFO_YAML_SHA256 = "a20b570e89511a221e05005778885702fe45651d024f178f7463ee1f0fe0ff82"

results = []
passed = 0
failed = 0

def check(test_id: str, title: str, cond: bool, details: str = ""):
    global passed, failed
    if cond:
        passed += 1
        status = "PASS"
    else:
        failed += 1
        status = "FAIL"
    msg = f"[{status}] {test_id}: {title} | {details}"
    print(msg)
    results.append({"id": test_id, "title": title, "status": status, "details": details})

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("=" * 90)
print("ADVERSARIAL STRESS TEST: ARES-RX SENTINEL PERURI TECHNICAL DECK (M2)")
print(f"Target:    {DECK_PATH}")
print(f"Reference: {README_PATH}")
print("=" * 90)

# Check target existence
if not DECK_PATH.exists():
    check("ADV-0.1", "Target File Exists", False, f"File missing: {DECK_PATH}")
    sys.exit(1)
if not README_PATH.exists():
    check("ADV-0.2", "Reference README Exists", False, f"File missing: {README_PATH}")
    sys.exit(1)

with open(DECK_PATH, "r", encoding="utf-8") as f:
    deck_text = f.read()

with open(README_PATH, "r", encoding="utf-8") as f:
    readme_text = f.read()

lines = deck_text.splitlines()
check("ADV-0.3", "Target File Size & Content", len(lines) > 200, f"{len(lines)} lines, {len(deck_text)} bytes")

# -----------------------------------------------------------------------------
# Module 1: Negative Regex Sweeps for Prohibited Power Phrasing
# -----------------------------------------------------------------------------
print("\n--- Module 1: Prohibited Power Phrasing Sweeps (English & Indonesian) ---")

prohibited_power_exact_en = [
    r"\bmeasured\s+silicon\s+power\b",
    r"\bsilicon\s+operational\s+power\b",
    r"\bfabricated-chip\s+power\b",
    r"\bsilicon-confirmed\s+power\b",
    r"\bactual\s+silicon\s+deployment\b",
]

for pat in prohibited_power_exact_en:
    matches = list(re.finditer(pat, deck_text, re.IGNORECASE))
    check(f"ADV-1.EN.{pat[:15].strip(r'b')}", f"No Prohibited English Power Term: '{pat}'", len(matches) == 0,
          f"Found {len(matches)} matches: {[m.group(0) for m in matches]}")

prohibited_power_exact_id = [
    r"\bdaya\s+silikon\s+terukur\b",
    r"\bdaya\s+operasional\s+silikon\b",
    r"\bdaya\s+chip\s+fabrikasi\b",
]

for pat in prohibited_power_exact_id:
    matches = list(re.finditer(pat, deck_text, re.IGNORECASE))
    check(f"ADV-1.ID.{pat[:15].strip(r'b')}", f"No Prohibited Indonesian Power Term: '{pat}'", len(matches) == 0,
          f"Found {len(matches)} matches: {[m.group(0) for m in matches]}")

# Contextual Indonesian check for "pengukuran daya silikon" or "pengukuran silicon"
# These phrases are permitted ONLY if negated (e.g., "bukan pengukuran daya silikon", "belum tersedia")
pengukuran_occurrences = list(re.finditer(r"([^.\n]*pengukuran[^.\n]*(?:daya|silikon|silicon)[^.\n]*)", deck_text, re.IGNORECASE))
unnegated_pengukuran = []
allowed_negations = ["bukan", "not available", "belum tersedia", "tidak boleh", "akan dilakukan pasca", "belum", "tidak ada"]

for occ in pengukuran_occurrences:
    text_snippet = occ.group(1).strip()
    is_negated = any(neg in text_snippet.lower() for neg in allowed_negations)
    if not is_negated:
        unnegated_pengukuran.append(text_snippet)

check("ADV-1.ID.PENGUKURAN", "Contextual Pengukuran Daya/Silikon Strictly Negated",
      len(unnegated_pengukuran) == 0,
      f"Violations: {unnegated_pengukuran}" if unnegated_pengukuran else f"All {len(pengukuran_occurrences)} instances properly negated")

# Verify power classification requirement
# Whenever 57.90 nW appears, verify it is labeled as estimasi / estimate / post-route
power_57_matches = list(re.finditer(r"([^.\n]*57\.90[^.\n]*)", deck_text))
unqualified_57 = []
for m in power_57_matches:
    line = m.group(1)
    if not any(k in line.lower() for k in ["estimasi", "estimate", "overhead", "vcd", "simulasi", "post-route", "primer"]):
        unqualified_57.append(line.strip())

check("ADV-1.PWR.57_QUALIFIED", "57.90 nW Strictly Qualified as Estimate / Post-Route",
      len(unqualified_57) == 0,
      f"Unqualified instances: {unqualified_57}" if unqualified_57 else f"All {len(power_57_matches)} instances correctly qualified")

# Verify secondary power 50.90 nW is separated
has_50_90 = "50.90 nW" in deck_text
is_secondary = "Secondary static activity sweep" in deck_text or "Estimasi Daya Sekunder" in deck_text
check("ADV-1.PWR.50_SECONDARY", "50.90 nW Secondary Disaggregation", has_50_90 and is_secondary,
      "50.90 nW clearly marked as secondary static activity sweep")

# -----------------------------------------------------------------------------
# Module 2: Unauthorized Claims of Acceptance / Approval Sweeps
# -----------------------------------------------------------------------------
print("\n--- Module 2: Acceptance & Approval Claim Sweeps ---")

# Tiny Tapeout Portal Acceptance claims:
# Look for claims that Tiny Tapeout portal or shuttle has accepted / approved the design
# Exclude explicit disclaimers ("≠ Tiny Tapeout Portal Accepted", "BUKAN tanda terima penerimaan portal", "Status Portal: PENDING")
portal_accept_patterns = [
    r"portal\s+(?:telah\s+)?(?:menerima|diterima|menyetujui|disetujui|accepted|approved)",
    r"tiny\s+tapeout\s+(?:telah\s+)?(?:menerima|diterima|menyetujui|disetujui|accepted|approved)\s+(?:desain|submission|portal)",
    r"(?:accepted|approved)\s+by\s+tiny\s+tapeout",
]
unauthorized_portal_claims = []
disclaimer_keywords = ["≠", "!=", "bukan", "not", "pending", "menunggu", "sebelum"]
for pat in portal_accept_patterns:
    for occ in re.finditer(pat, deck_text, re.IGNORECASE):
        start_line = deck_text.rfind("\n", 0, occ.start()) + 1
        end_line = deck_text.find("\n", occ.end())
        if end_line == -1: end_line = len(deck_text)
        line = deck_text[start_line:end_line]
        if not any(k in line.lower() for k in disclaimer_keywords):
            unauthorized_portal_claims.append(line.strip())

check("ADV-2.PORTAL.CLAIM", "No False Tiny Tapeout Portal Acceptance Claims",
      len(unauthorized_portal_claims) == 0,
      f"Violations: {unauthorized_portal_claims}" if unauthorized_portal_claims else "Zero false portal acceptance claims")

# Verify explicit TT08 portal PENDING status
portal_pending_found = bool(re.search(r"Status\s+Portal\s+Tiny\s+Tapeout[:\s\*]+PENDING", deck_text, re.IGNORECASE)) or \
                       ("Portal Submission" in deck_text and "PENDING" in deck_text)
check("ADV-2.PORTAL.PENDING", "Explicit TT08 Portal Status Declared PENDING",
      portal_pending_found, "Tiny Tapeout portal explicitly stated as PENDING")

# Peruri Approval / Procurement claims:
peruri_claims_patterns = [
    r"(?:disetujui|disahkan|diterima|diadopsi|disertifikasi|kontrak|pengadaan)\s+(?:oleh\s+)?peruri",
    r"peruri\s+(?:telah\s+)?(?:menyetujui|menerima|mengesahkan|mengadopsi|menyertifikasi)",
    r"peruri\s+(?:formal\s+)?(?:acceptance|approval|procurement|certification)",
]
unauthorized_peruri_claims = []
for pat in peruri_claims_patterns:
    for occ in re.finditer(pat, deck_text, re.IGNORECASE):
        start_line = deck_text.rfind("\n", 0, occ.start()) + 1
        end_line = deck_text.find("\n", occ.end())
        if end_line == -1: end_line = len(deck_text)
        line = deck_text[start_line:end_line]
        if not any(k in line.lower() for k in ["bukan", "not claimed", "tidak diklaim", "untuk dievaluasi", "rekomendasi", "proposal", "audiens"]):
            unauthorized_peruri_claims.append(line.strip())

check("ADV-2.PERURI.CLAIM", "No Unauthorized Peruri Approval / Procurement Claims",
      len(unauthorized_peruri_claims) == 0,
      f"Violations: {unauthorized_peruri_claims}" if unauthorized_peruri_claims else "Zero unauthorized Peruri approval claims")

# Check explicit disclaimer on Peruri approval
peruri_disclaimer = bool(re.search(r"Persetujuan\s*/\s*Sertifikasi\s+Peruri[:\s\*]+NOT CLAIMED", deck_text, re.IGNORECASE)) or \
                    ("bukan sertifikasi kelulusan resmi Peruri" in deck_text)
check("ADV-2.PERURI.DISCLAIMER", "Explicit Peruri Non-Acceptance Disclaimer Present",
      peruri_disclaimer, "Peruri approval/certification disclaimed as NOT CLAIMED")

# Check Silicon Physical Status: TT08 PENDING, Physical Silicon NOT AVAILABLE
silicon_pending = ("TT08 Fabrication PENDING" in deck_text or "TT08 PENDING" in deck_text)
silicon_not_avail = ("Pengukuran daya silikon = NOT AVAILABLE" in deck_text or "NOT AVAILABLE" in deck_text)
check("ADV-2.SILICON.STATUS", "Silicon Fabrication PENDING & Silicon Measurement NOT AVAILABLE",
      silicon_pending and silicon_not_avail,
      f"silicon_pending={silicon_pending}, silicon_not_avail={silicon_not_avail}")

# -----------------------------------------------------------------------------
# Module 3: Technical Metrics Cross-Check Against Finalized Phase 1 README.md
# -----------------------------------------------------------------------------
print("\n--- Module 3: Technical Metrics Cross-Check Against Phase 1 README ---")

metrics_to_cross_check = [
    ("Area (6,477.46)", r"6,477\.46", "6,477.46"),
    ("Logic Cell Count", r"758", "758"),
    ("Max Frequency F_max", r"123\.7", "123.7 MHz"),
    ("Cycle Count", r"10,737", "10,737"),
    ("Signal Evaluations", r"118,107", "118,107"),
    ("Tile Dimensions (161x111)", r"161\.00.*111\.52", "161.00 x 111.52"),
    ("Gross Tile Area", r"17,954\.72", "17,954.72"),
    ("Setup Slack (+11.88)", r"\+11\.88", "+11.88 ns"),
    ("Hold Slack (+0.42)", r"\+0\.42", "+0.42 ns"),
    ("Netgen Devices (764)", r"764/764", "764/764"),
    ("Netgen Nets (776)", r"776/776", "776/776"),
    ("Netgen Pins (45)", r"45/45", "45/45"),
    ("DRC Violations", r"0\s+active\s+violations", "0 active violations"),
    ("Primary Power", r"57\.90\s*nW", "57.90 nW"),
    ("Secondary Power", r"50\.90\s*nW", "50.90 nW"),
    ("CI GDS Run ID", EXPECTED_CI_GDS_RUN, EXPECTED_CI_GDS_RUN),
    ("CI Test Run ID", EXPECTED_CI_TEST_RUN, EXPECTED_CI_TEST_RUN),
    ("Ledger Anchor", EXPECTED_LEDGER_ANCHOR, EXPECTED_LEDGER_ANCHOR),
    ("M5 Commit", EXPECTED_M5_COMMIT, EXPECTED_M5_COMMIT),
    ("M6 Run ID", EXPECTED_M6_RUN_ID, EXPECTED_M6_RUN_ID),
]

for name, pat, expected_val in metrics_to_cross_check:
    in_deck = bool(re.search(pat, deck_text, re.IGNORECASE))
    in_readme = bool(re.search(pat, readme_text, re.IGNORECASE))
    check(f"ADV-3.METRIC.{name[:14]}", f"Cross-check: {name}", in_deck and in_readme,
          f"Expected: {expected_val} | In Deck: {in_deck}, In README: {in_readme}")

# Cross-check Canonical Attack Vectors AV00 to AV08 in both documents
print("\n--- Cross-checking Canonical Vectors AV00 to AV08 ---")
vectors = [f"AV0{i}" for i in range(9)]
all_vectors_present = True
missing_vectors = []
for v in vectors:
    v_deck = v in deck_text
    v_readme = v in readme_text
    if not (v_deck and v_readme):
        all_vectors_present = False
        missing_vectors.append(v)

check("ADV-3.VECTORS.CONCORDANCE", "Canonical Vectors AV00–AV08 in Both Docs",
      all_vectors_present,
      f"All 9 vectors present" if all_vectors_present else f"Missing: {missing_vectors}")

# Check individual vector verdicts in deck
v_verdicts_correct = True
unmatched_verdicts = []
expected_verdicts = {
    "AV00": "ACCEPTED_NOMINAL",
    "AV01": "MITIGATED_TRAPPED",
    "AV02": "MITIGATED_TRAPPED",
    "AV03": "MITIGATED_TRAPPED",
    "AV04": "MITIGATED_TRAPPED",
    "AV05": "MITIGATED_TRAPPED",
    "AV06": "MITIGATED_TRAPPED",
    "AV07": "MITIGATED_TRAPPED",
    "AV08": "MITIGATED_TRAPPED",
}
for v, verd in expected_verdicts.items():
    pattern = rf"{v}.*?{verd}"
    if not re.search(pattern, deck_text, re.DOTALL):
        v_verdicts_correct = False
        unmatched_verdicts.append(f"{v}->{verd}")

check("ADV-3.VECTORS.VERDICTS", "Vector Table Verdicts Match Specifications",
      v_verdicts_correct,
      "All 9 vector verdicts match expected" if v_verdicts_correct else f"Unmatched: {unmatched_verdicts}")

# -----------------------------------------------------------------------------
# Module 4: Slide Structure, Provenance Citations & Epistemic Boundaries
# -----------------------------------------------------------------------------
print("\n--- Module 4: Slide Structure & Provenance Attributions ---")

slide_headers = list(re.finditer(r"^# SLIDE (\d+):\s*(.+)$", deck_text, re.MULTILINE))
check("ADV-4.SLIDE_COUNT", "Technical Deck Slide Count >= 12", len(slide_headers) >= 12,
      f"Found {len(slide_headers)} slides")

slide_numbers = [int(m.group(1)) for m in slide_headers]
check("ADV-4.SLIDE_ORDER", "Slides Sequentially Numbered 1 to 12",
      slide_numbers == list(range(1, 13)), f"Actual slide numbers: {slide_numbers}")

# Slide source attributions check
slides_dict = {}
for i in range(len(slide_headers)):
    s_num = int(slide_headers[i].group(1))
    start_pos = slide_headers[i].start()
    end_pos = slide_headers[i+1].start() if i + 1 < len(slide_headers) else len(deck_text)
    slides_dict[s_num] = deck_text[start_pos:end_pos]

missing_sources = []
for s_num, content in slides_dict.items():
    if not re.search(r"(\*Sumber:|Sumber:)", content):
        missing_sources.append(s_num)

check("ADV-4.SOURCES_PER_SLIDE", "Every Slide Has Explicit Source Attribution",
      len(missing_sources) == 0,
      f"Missing on slides: {missing_sources}" if missing_sources else "All 12 slides cite sources")

# Mandatory Epistemic Invariance Axiom check
axiom_present = ("M6 Evidence Sealed ≠ Tiny Tapeout Portal Accepted ≠ Silicon Validated" in deck_text) and \
                ("Bukti M6 Tersegel ≠ Diterima Portal Tiny Tapeout ≠ Tervalidasi Silikon" in deck_text)
check("ADV-4.EPISTEMIC_AXIOM", "Mandatory Epistemic Invariance Axiom in EN & ID",
      axiom_present, "Both English and Indonesian axiom formulations present")

# -----------------------------------------------------------------------------
# Module 5: Immutability Seals & Programmatic Verification
# -----------------------------------------------------------------------------
print("\n--- Module 5: Immutability Seals & Programmatic Verification ---")

# Execute verify_m4_hashes.py
try:
    proc = subprocess.run([sys.executable, str(M4_VERIFY_SCRIPT)],
                          capture_output=True, text=True, check=True, cwd=str(REPO_ROOT))
    stdout_m4 = proc.stdout
    # Count occurrences of MATCH [3-WAY FROZEN]
    matches_count = stdout_m4.count("MATCH [3-WAY FROZEN]")
    has_audit_summary = "100% BIT-FOR-BIT 3-WAY MATCH" in stdout_m4
    m4_pass = (matches_count == 7) and has_audit_summary and (proc.returncode == 0)
    check("ADV-5.M4_HASHES", "verify_m4_hashes.py Confirms 7/7 MATCH [3-WAY FROZEN]",
          m4_pass, f"Matches: {matches_count}/7, returncode: {proc.returncode}")
except Exception as e:
    check("ADV-5.M4_HASHES", "verify_m4_hashes.py Execution", False, str(e))

# Check info.md SHA-256 seal
info_md_actual = sha256_file(INFO_MD_PATH)
check("ADV-5.INFO_MD_SEAL", "docs/info.md SHA-256 Hash Seal",
      info_md_actual == EXPECTED_INFO_MD_SHA256,
      f"Expected: {EXPECTED_INFO_MD_SHA256} | Actual: {info_md_actual}")

# Check info.yaml SHA-256 seal
info_yaml_actual = sha256_file(INFO_YAML_PATH)
check("ADV-5.INFO_YAML_SEAL", "info.yaml SHA-256 Hash Seal",
      info_yaml_actual == EXPECTED_INFO_YAML_SHA256,
      f"Expected: {EXPECTED_INFO_YAML_SHA256} | Actual: {info_yaml_actual}")

# Verify M6 ledger file integrity & anchor
if LEDGER_PATH.exists():
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger_lines = [json.loads(line) for line in f if line.strip()]
    ledger_records_count = len(ledger_lines)
    last_record_hash = ledger_lines[-1].get("record_hash", "") if ledger_lines else ""
    check("ADV-5.M6_RECORD_COUNT", "M6 Evidence Ledger Record Count == 9",
          ledger_records_count == 9, f"Record count: {ledger_records_count}")
    check("ADV-5.M6_LEDGER_ANCHOR", "M6 Final Ledger Record Hash == Expected Anchor",
          last_record_hash == EXPECTED_LEDGER_ANCHOR,
          f"Expected: {EXPECTED_LEDGER_ANCHOR} | Actual: {last_record_hash}")
else:
    check("ADV-5.M6_LEDGER", "M6 Ledger File Exists", False, f"Missing: {LEDGER_PATH}")

print("\n" + "=" * 90)
print(f"ADVERSARIAL VERIFICATION SUMMARY: Total={passed + failed} | Passed={passed} | Failed={failed}")
if failed == 0:
    print("VERDICT: APPROVE")
else:
    print("VERDICT: REQUEST_CHANGES")
print("=" * 90)

if failed > 0:
    sys.exit(1)
else:
    sys.exit(0)
