#!/usr/bin/env python3
"""
Adversarial Verification Suite for ARES-RX Sentinel HTML Presentation Deck
Target File: 08_Slides/ARES_RX_Sentinel_Presentation.html
Challenger: Challenger 1 (M3) (teamwork_preview_challenger_m3_1)

Empirical Verification Requirements:
1. File size < 5MB
2. Exact slide count = 18 slides (containers, IDs, JS navigation totalSlides)
3. Exact metric strings:
   - "57.90 nW" (and power breakdown: 12.0 nW / 12.00 nW, 42.8 nW / 42.80 nW, 3.1 nW / 3.10 nW, baseline 45.20 nW, overhead +12.70 nW / +28.1%)
   - "758" logic cells / standard cells
   - "6,477.46 µm²" or "6477.46"
   - "123.15 MHz" Fmax
   - "+11.88 ns" setup slack
   - "0 DRC" violations
   - "100% LVS" (758/758 or 764/764 total netgen instances)
   - "100%" detection rate AV01-AV08
   - "0%" false alarm AV00
   - "T_latch = 1" cycle (or T_{latch}=1, or T_latch=1)
   - "T_isolate = 0" cycles (or T_{isolate}=0, or T_isolate=0)
   - SHA-256 anchor 6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0
   - RTL snippet: `assign safe_data_out = (tamper_alert_r) ? 8'h00 : raw_decoder_data;`
4. Formula checks:
   - V_{trusted} = V_{physical} \\land V_{protocol}
   - N_{HB} in [8,10]
   - N_{BIT} in [16,20]
5. Adversarial epistemic check:
   - Prohibited claims that 57.90 nW is measured silicon power
   - Prohibited tapeout/foundry/Peruri overclaims
   - Verification of mandatory epistemic disclaimers
"""

import sys
import os
import re
import html
from pathlib import Path
from html.parser import HTMLParser

# Force UTF-8 on Windows stdout
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(r"c:\Users\ahmad\OneDrive\Vscode\03_Core_Projects\ARES SEMIKONDUKTOR TECHNOLOGY")
TARGET_PATH = REPO_ROOT / "08_Slides" / "ARES_RX_Sentinel_Presentation.html"

results = []
passed_count = 0
failed_count = 0

def check(test_id: str, title: str, cond: bool, details: str = ""):
    global passed_count, failed_count
    if cond:
        passed_count += 1
        status = "PASS"
    else:
        failed_count += 1
        status = "FAIL"
    msg = f"[{status}] {test_id}: {title} | {details}"
    print(msg)
    results.append({"id": test_id, "title": title, "status": status, "details": details})

print("=" * 90)
print("ADVERSARIAL STRESS TEST: ARES-RX SENTINEL HTML PRESENTATION (M3)")
print(f"Target: {TARGET_PATH}")
print("=" * 90)

# Check target file existence
if not TARGET_PATH.exists():
    check("ADV-0.1", "Target File Exists", False, f"File missing: {TARGET_PATH}")
    sys.exit(1)

# Read file contents
file_bytes = TARGET_PATH.read_bytes()
file_size_bytes = len(file_bytes)
try:
    html_text = file_bytes.decode("utf-8")
except UnicodeDecodeError as e:
    check("ADV-0.2", "Target UTF-8 Decodable", False, f"UTF-8 decode failed: {e}")
    sys.exit(1)

print(f"File Size: {file_size_bytes:,} bytes ({file_size_bytes / (1024*1024):.3f} MB)")
print(f"Line Count: {len(html_text.splitlines()):,} lines")

# -----------------------------------------------------------------------------
# Module 1: File Size Verification (< 5MB)
# -----------------------------------------------------------------------------
print("\n--- Module 1: File Size Verification ---")
MAX_ALLOWED_SIZE = 5 * 1024 * 1024  # 5MB
check("ADV-1.1", "File Size < 5MB", file_size_bytes < MAX_ALLOWED_SIZE,
      f"Size: {file_size_bytes:,} bytes (< 5,242,880 bytes)")
check("ADV-1.2", "File Size Non-Trivial (> 10KB)", file_size_bytes > 10 * 1024,
      f"Size: {file_size_bytes:,} bytes")

# -----------------------------------------------------------------------------
# Module 2: Exact Slide Count = 18 Slides
# -----------------------------------------------------------------------------
print("\n--- Module 2: Exact Slide Count Verification ---")

# Parse HTML DOM using HTMLParser
class SlideDOMParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slides = []
        self.current_slide = None
        self.current_tag_stack = []
        self.in_title = False
        self.current_title = ""

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get("class", "").split()
        tag_id = attr_dict.get("id", "")
        
        # Check if entering a slide container
        if "slide" in classes:
            self.current_slide = {
                "id": tag_id,
                "classes": classes,
                "tag": tag,
                "attrs": attr_dict,
                "text": []
            }
            self.slides.append(self.current_slide)

        if "slide-title" in classes:
            self.in_title = True
            self.current_title = ""

        self.current_tag_stack.append((tag, attr_dict))

    def handle_endtag(self, tag):
        if self.in_title:
            self.in_title = False
            if self.current_slide:
                self.current_slide["title"] = self.current_title.strip()
        if self.current_tag_stack:
            self.current_tag_stack.pop()

    def handle_data(self, data):
        if self.in_title:
            self.current_title += data
        if self.current_slide:
            self.current_slide["text"].append(data)

parser = SlideDOMParser()
parser.feed(html_text)

slide_count = len(parser.slides)
check("ADV-2.1", "Exact Slide Count = 18", slide_count == 18, f"Found {slide_count} slides")

# Check slide IDs sequential slide-1 to slide-18
slide_ids = [s["id"] for s in parser.slides]
expected_ids = [f"slide-{i}" for i in range(1, 19)]
check("ADV-2.2", "Slide IDs sequential slide-1 to slide-18",
      slide_ids == expected_ids,
      f"IDs: {slide_ids}")

# Check JavaScript totalSlides variable
js_total_slides = re.findall(r"const\s+totalSlides\s*=\s*(\d+);|let\s+totalSlides\s*=\s*(\d+);|totalSlides\s*=\s*(\d+);", html_text)
total_slides_val = None
if js_total_slides:
    for match in js_total_slides[0]:
        if match:
            total_slides_val = int(match)
check("ADV-2.3", "JavaScript totalSlides == 18", total_slides_val == 18,
      f"JS totalSlides parsed as: {total_slides_val}")

# Check slide counter DOM elements
counter_match = re.search(r'class=[\"\'][^\"\']*slide-counter[^\"\']*[\"\'][^>]*>(.*?)</div>', html_text, re.DOTALL)
check("ADV-2.4", "Slide Counter Element Exists with / 18",
      counter_match is not None and "18" in (counter_match.group(0) if counter_match else ""),
      f"Counter DOM: {counter_match.group(0).strip() if counter_match else 'None'}")

print(f"Discovered Slides ({len(parser.slides)}):")
for i, s in enumerate(parser.slides, 1):
    title = s.get("title", "").replace("\n", " ").strip()
    print(f"  Slide {i:02d} [{s['id']}]: {title}")

# -----------------------------------------------------------------------------
# Module 3: Exact Metric Strings Verification
# -----------------------------------------------------------------------------
print("\n--- Module 3: Exact Metric Strings Verification ---")

metric_tests = [
    # (ID, Metric Name, Regex pattern, description)
    ("ADV-3.1", "Power: 57.90 nW", r"57\.90\s*nW", "57.90 nW operating power estimate"),
    ("ADV-3.2", "Power Breakdown: 12.0 nW Sequential", r"12\.00?\s*nW", "Sequential power 12.00 nW"),
    ("ADV-3.3", "Power Breakdown: 42.8 nW Combinational", r"42\.80?\s*nW", "Combinational power 42.80 nW"),
    ("ADV-3.4", "Power Breakdown: 3.1 nW Leakage", r"3\.10?\s*nW", "Leakage power 3.10 nW"),
    ("ADV-3.5", "Power Baseline: 45.20 nW", r"45\.20\s*nW", "Baseline power 45.20 nW"),
    ("ADV-3.6", "Power Overhead: +12.70 nW / +28.1%", r"\+?12\.70\s*nW|\+?28\.1\s*%", "Power overhead +12.70 nW (+28.1%)"),
    ("ADV-3.7", "Logic Cells: 758", r"758\s*(?:logic\s*cells|standard\s*cells|sel\s*standar|cells|gates)", "758 logic/standard cells"),
    ("ADV-3.8", "Die Area: 6,477.46 µm²", r"6[,\.]?477\.46\s*(?:µm²|um²|&mu;m²|\\mu m\^2)", "Standard cell area 6,477.46 µm²"),
    ("ADV-3.9", "Fmax: 123.15 MHz", r"123\.15\s*MHz", "Fmax 123.15 MHz"),
    ("ADV-3.10", "Setup Slack: +11.88 ns", r"\+11\.88\s*ns", "Setup slack +11.88 ns"),
    ("ADV-3.11", "0 DRC Violations", r"0\s*(?:active\s*)?DRC", "0 DRC violations"),
    ("ADV-3.12", "100% LVS Match", r"100%\s*(?:Match\s*)?LVS|LVS\s*(?:Match\s*)?100%|100%\s*Match\s*\(\d+/\d+\)", "100% LVS match"),
    ("ADV-3.13", "100% Detection Rate", r"100(?:\.0)?%\s*(?:deteksi|detection|tingkat\s*deteksi)", "100% detection rate AV01-AV08"),
    ("ADV-3.14", "0% False Alarms", r"0(?:\.0)?%\s*(?:false\s*alarm|alarm\s*palsu|salah\s*alarm)", "0% false alarm AV00"),
    ("ADV-3.15", "T_latch = 1", r"T_\{?(?:\\text\{)?latch\}?\}?\s*=\s*1|T_latch\s*=\s*1|Tlatch\s*=\s*1", "T_latch = 1 cycle latency"),
    ("ADV-3.16", "T_isolate = 0", r"T_\{?(?:\\text\{)?isolate\}?\}?\s*=\s*0|T_isolate\s*=\s*0|Tisolate\s*=\s*0", "T_isolate = 0 cycle latency"),
    ("ADV-3.17", "SHA-256 Ledger Anchor", r"6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0",
     "Cryptographic anchor hash"),
    ("ADV-3.18", "RTL Safe Data Out Snippet",
     r"assign\s+safe_data_out\s*=\s*\(?tamper_alert_r\)?\s*\?\s*8'h00\s*:\s*raw_decoder_data\s*;",
     "Zeroization RTL code snippet"),
]

for test_id, name, pattern, desc in metric_tests:
    matches = re.findall(pattern, html_text, re.IGNORECASE)
    check(test_id, f"Metric Match: {name}", len(matches) > 0,
          f"Found {len(matches)} occurrences (pattern: '{pattern}')")

# Check verbatim RTL snippet
verbatim_rtl = "assign safe_data_out = (tamper_alert_r) ? 8'h00 : raw_decoder_data;"
has_verbatim_rtl = verbatim_rtl in html_text
check("ADV-3.19", "Verbatim RTL Snippet Match", has_verbatim_rtl,
      f"Exact match for: `{verbatim_rtl}`: {has_verbatim_rtl}")

# -----------------------------------------------------------------------------
# Module 4: Mathematical Formulas KaTeX Verification
# -----------------------------------------------------------------------------
print("\n--- Module 4: Mathematical Formula Verification ---")

# 1. V_{trusted} = V_{physical} \land V_{protocol}
formula_1_patterns = [
    r"V_\{?\\?text\{trusted\}\}?\s*=\s*V_\{?\\?text\{physical\}\}?\s*\\land\s*V_\{?\\?text\{protocol\}\}?",
    r"V_\{trusted\}\s*=\s*V_\{physical\}\s*\\land\s*V_\{protocol\}",
    r"V_\{?trusted\}?\s*=\s*V_\{?physical\}?\s*(?:\\land|\land|∧)\s*V_\{?protocol\}?",
]
f1_found = any(re.search(pat, html_text) for pat in formula_1_patterns)
check("ADV-4.1", "Formula: V_trusted = V_physical ∧ V_protocol", f1_found,
      "Found trust formulation formula in KaTeX/LaTeX syntax")

# 2. N_{HB} \in [8, 10]
formula_2_patterns = [
    r"N_\{?\\?text\{HB\}\}?\s*\\in\s*\[\s*8\s*,\s*10\s*\]",
    r"N_\{HB\}\s*\\in\s*\[\s*8\s*,\s*10\s*\]",
    r"N_\{?HB\}?\s*(?:\\in|∈)\s*\[\s*8\s*,\s*10\s*\]",
    r"N\s*\\in\s*\[\s*8\s*,\s*10\s*\]",
    r"NHB\s*\[\s*8\s*,\s*10\s*\]",
]
f2_found = any(re.search(pat, html_text) for pat in formula_2_patterns)
check("ADV-4.2", "Formula: N_HB ∈ [8,10]", f2_found,
      "Found Manchester half-bit window constraint formula")

# 3. N_{BIT} \in [16, 20]
formula_3_patterns = [
    r"N_\{?\\?text\{BIT\}\}?\s*\\in\s*\[\s*16\s*,\s*20\s*\]",
    r"N_\{BIT\}\s*\\in\s*\[\s*16\s*,\s*20\s*\]",
    r"N_\{?BIT\}?\s*(?:\\in|∈)\s*\[\s*16\s*,\s*20\s*\]",
    r"N\s*\\in\s*\[\s*16\s*,\s*20\s*\]",
    r"NBIT\s*\[\s*16\s*,\s*20\s*\]",
]
f3_found = any(re.search(pat, html_text) for pat in formula_3_patterns)
check("ADV-4.3", "Formula: N_BIT ∈ [16,20]", f3_found,
      "Found full-bit window constraint formula")

# KaTeX CDN & render script check
check("ADV-4.4", "KaTeX CSS CDN Link Present",
      "katex.min.css" in html_text, "Found KaTeX stylesheet")
check("ADV-4.5", "KaTeX JS CDN & Auto-render Present",
      "katex.min.js" in html_text and "auto-render" in html_text,
      "Found KaTeX JS scripts")

# -----------------------------------------------------------------------------
# Module 5: Adversarial Epistemic Checks (Negative & Positive Sweeps)
# -----------------------------------------------------------------------------
print("\n--- Module 5: Adversarial Epistemic Verification ---")

def clean_html(text: str) -> str:
    # replace HTML tags with space
    t = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', t)

plain_text = clean_html(html_text)

# Forbidden power claims in English
prohibited_power_exact_en = [
    (r"\bmeasured\s+silicon\s+power\b", "measured silicon power"),
    (r"\bsilicon\s+operational\s+power\b", "silicon operational power"),
    (r"\bfabricated-chip\s+power\b", "fabricated-chip power"),
    (r"\bsilicon-confirmed\s+power\b", "silicon-confirmed power"),
    (r"\bactual\s+silicon\s+deployment\b", "actual silicon deployment"),
]

# Forbidden power claims in Indonesian
prohibited_power_exact_id = [
    (r"\bpengukuran\s+daya\s+silikon\b", "pengukuran daya silikon"),
    (r"\bdaya\s+silikon\s+terukur\b", "daya silikon terukur"),
    (r"\bdaya\s+operasional\s+silikon\b", "daya operasional silikon"),
    (r"\bdaya\s+chip\s+terfabrikasi\b", "daya chip terfabrikasi"),
    (r"\bhasil\s+ukur\s+silikon\b", "hasil ukur silikon"),
    (r"\bdaya\s+terukur\s+pada\s+silikon\b", "daya terukur pada silikon"),
]

def check_affirmative_claim(pattern: str, text: str) -> list:
    violating = []
    for m in re.finditer(pattern, text, re.IGNORECASE):
        # Examine a broad window around the match
        start = max(0, m.start() - 250)
        end = min(len(text), m.end() + 250)
        window = text[start:end]
        
        # Check if the context contains explicit negation, prohibition, or future roadmap language
        is_negated = bool(re.search(
            r"(?:dilarang\s+keras|dilarang|bukan|bukanlah|tidak|not\s+a|never|\[x\]|not\s+available|belum\s+tersedia)",
            window, re.IGNORECASE
        ))
        is_future = bool(re.search(
            r"(?:fase\s+1|q4\s+2026|roadmap|target|rencana|bringing-up|bring-up)",
            window, re.IGNORECASE
        ))
        
        if not (is_negated or is_future):
            violating.append(window.strip())
    return violating

# Negative sweeps
for pattern, label in prohibited_power_exact_en:
    violations = check_affirmative_claim(pattern, plain_text)
    check(f"ADV-5.EN-{label[:10]}", f"No Prohibited Affirmative Claim: '{label}'",
          len(violations) == 0,
          f"Violations: {len(violations)}" + (f" -> {violations[:1]}" if violations else " (Clean - only in disclaimer/negation)"))

for pattern, label in prohibited_power_exact_id:
    violations = check_affirmative_claim(pattern, plain_text)
    check(f"ADV-5.ID-{label[:10]}", f"No Prohibited Affirmative Claim: '{label}'",
          len(violations) == 0,
          f"Violations: {len(violations)}" + (f" -> {violations[:1]}" if violations else " (Clean - only in disclaimer/negation)"))

# Positive sweeps: Mandatory Epistemic Disclaimers
disclaimer_checks = [
    ("Post-Route VCD Workload Estimate", r"estimasi\s+daya\s+pasca-layout|post-route[^\.\n<]{0,60}(?:estimate|estimasi)", "Declared as post-route estimate"),
    ("Explicit Not Silicon Measurement Disclaimer", r"bukan[^\.\n<]{0,60}(?:pengukuran|hasil\s*ukur)[^\.\n<]{0,40}silikon|not\s+a\s+fabricated-silicon", "Explicit 'BUKAN pengukuran daya silikon'"),
    ("Silicon Measurement Status: NOT AVAILABLE", r"(?:pengukuran\s+silikon|silicon\s+power\s+measurement)[^\.\n<]{0,60}(?:not\s+available|belum\s+tersedia)", "Silicon measurement NOT AVAILABLE"),
    ("TT08 Fabrication PENDING", r"(?:tt08|fabrication)[^\.\n<]{0,60}(?:pending|menunggu)", "TT08 Fabrication PENDING"),
]

for d_id, d_pattern, d_desc in disclaimer_checks:
    m = re.search(d_pattern, plain_text, re.IGNORECASE)
    snippet = m.group(0) if m else 'NOT FOUND'
    check(f"ADV-5.DISC-{d_id[:8]}", f"Mandatory Disclaimer: {d_id}",
          m is not None, f"Found match: '{snippet}'")

# Check no false claim of Tiny Tapeout Portal Acceptance or Foundry Sign-off
portal_false_claim = re.search(r"portal\s+tiny\s*tapeout\s+(?:diterima|accepted|approved|signed-off)", plain_text, re.IGNORECASE)
check("ADV-5.PORTAL_CLAIM", "No False Tiny Tapeout Acceptance Claim",
      portal_false_claim is None,
      f"Portal claim: {portal_false_claim.group(0) if portal_false_claim else 'None (Clean)'}")

# -----------------------------------------------------------------------------
# Module 6: Structural & Presentation Quality Checks
# -----------------------------------------------------------------------------
print("\n--- Module 6: Structural & Presentation Quality Checks ---")

# Theme CSS Variables
theme_vars = [
    "--bg-primary", "--bg-slide", "--bg-card", "--accent-cyan",
    "--accent-green", "--accent-orange", "--accent-yellow",
    "--text-primary", "--text-muted", "--border-glow", "--font-mono"
]
missing_vars = [v for v in theme_vars if v not in html_text]
check("ADV-6.1", "Cybersecurity Dark Theme CSS Variables",
      len(missing_vars) == 0,
      f"Missing vars: {missing_vars}" if missing_vars else "All 11 theme variables present")

# JavaScript Navigation and Event Listeners
nav_features = [
    ("ArrowKey Navigation", r"keydown.*(?:ArrowRight|ArrowLeft|37|39)"),
    ("Fullscreen Toggle", r"(?:requestFullscreen|fullscreenElement|toggleFullscreen)"),
    ("Next/Prev Functions", r"showSlide|nextSlide|prevSlide"),
    ("Mermaid CDN/Init", r"mermaid\.min\.js|mermaid\.initialize"),
]
for feat_name, feat_pattern in nav_features:
    m = re.search(feat_pattern, html_text, re.DOTALL | re.IGNORECASE)
    check(f"ADV-6.NAV-{feat_name[:8]}", f"Interactive Feature: {feat_name}",
          m is not None, f"Found match for {feat_pattern}")

# Check for unrendered template placeholders
placeholder_patterns = [
    r"\{\{[^\}]+\}\}",
    r"\[TBD\]",
    r"\[TODO\]",
    r"\[FIXME\]",
    r"\[placeholder\]",
    r"\bundefined\b(?!\.js)",
    r"\bNaN\b",
]
found_placeholders = []
for p in placeholder_patterns:
    for m in re.finditer(p, html_text):
        found_placeholders.append(m.group(0))

check("ADV-6.NO_PLACEHOLDERS", "No Unresolved Template Placeholders",
      len(found_placeholders) == 0,
      f"Found {len(found_placeholders)} placeholders: {found_placeholders[:5]}")

# -----------------------------------------------------------------------------
# Summary & Verdict
# -----------------------------------------------------------------------------
print("\n" + "=" * 90)
print(f"VERIFICATION SUMMARY: {passed_count} PASSED, {failed_count} FAILED out of {len(results)} tests")
print("=" * 90)

if failed_count == 0:
    print("FINAL VERDICT: APPROVE")
else:
    print("FINAL VERDICT: REQUEST_CHANGES")
