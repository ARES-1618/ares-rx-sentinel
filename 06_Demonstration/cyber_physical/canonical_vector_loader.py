#!/usr/bin/env python3
"""
================================================================================
ARES-RX Sentinel — Single Canonical Stimulus Source Loader
Work Order: WO-2026-M6-ARCH-009
Authority: Technical Architect / Research Direction

Purpose:
  Provides the single, authoritative Python access layer to
  AV_Canonical_Vector_Manifest.yaml. Ensures zero vector reconstruction
  or manual duplication across testbenches, simulation runners, and demonstrator
  nodes.
================================================================================
"""

import os
import yaml
import json
import hashlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "AV_Canonical_Vector_Manifest.yaml")

_CACHED_MANIFEST = None

def load_canonical_manifest():
    global _CACHED_MANIFEST
    if _CACHED_MANIFEST is None:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            _CACHED_MANIFEST = yaml.safe_load(f)
    return _CACHED_MANIFEST

def get_canonical_vector(vector_id):
    manifest = load_canonical_manifest()
    for v in manifest.get("vectors", []):
        if v["id"] == vector_id:
            # Validate hash integrity upon access
            profile_bytes = json.dumps(v["cycles_profile"], separators=(',', ':')).encode('utf-8')
            computed_sha = hashlib.sha256(profile_bytes).hexdigest()
            if computed_sha != str(v["vector_stimulus_sha256"]):
                raise ValueError(
                    f"Integrity violation in canonical manifest for {vector_id}! "
                    f"Expected: {v['vector_stimulus_sha256']}, Computed: {computed_sha}"
                )
            return v
    raise KeyError(f"Vector {vector_id} not found in canonical manifest.")

def get_all_canonical_vectors():
    manifest = load_canonical_manifest()
    return manifest.get("vectors", [])

if __name__ == "__main__":
    vectors = get_all_canonical_vectors()
    print("=" * 90)
    print(" ARES-RX SENTINEL: SINGLE CANONICAL STIMULUS MANIFEST AUDIT (WO-2026-M6-ARCH-009)")
    print("=" * 90)
    print(f"{'ID':<6} | {'Name':<35} | {'Cycles':<8} | {'Stimulus SHA-256':<20} | Status")
    print("-" * 90)
    for v in vectors:
        v_data = get_canonical_vector(v["id"])
        h = v_data["vector_stimulus_sha256"]
        print(f"{v['id']:<6} | {v['name']:<35} | {v['total_cycles']:<8} | {h[:8]}...{h[-6:]} | AUTHENTIC")
    print("=" * 90)
    print(f"Total Canonical Vectors: {len(vectors)} | Source: {MANIFEST_PATH}")
