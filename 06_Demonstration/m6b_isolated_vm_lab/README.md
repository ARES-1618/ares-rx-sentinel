# Milestone M6-B: Isolated Network Namespace & Cyber-Physical Demonstrator Lab

## Architectural Demarcation & Lab Setup

Milestone M6-B transitions from the single-process socket prototype (Milestone M6-A) to an **isolated multi-domain security evaluation lab** with kernel-level network namespaces, traffic-controlled physical propagation delay/jitter emulation, and an immutable forensic evidence chain.

```text
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│       ATTACKER VM / NS          │                 │       RECEIVER VM / NS          │
│   (ns_attacker: 192.168.100.10) │                 │   (ns_receiver: 192.168.100.20) │
│                                 │                 │                                 │
│  [attacker_vm_node.py]          │                 │  [receiver_vm_node.py]          │
│   - Telemetry Stream Generator  │                 │   - Baseband Digital Ingest     │
│   - AV00 Nominal Frame          │                 │   - ARES Sentinel Model         │
│   - AV01..AV08 Adversarial Bat. │                 │   - Layer-3 Hardware Zeroize    │
└────────────────┬────────────────┘                 └────────────────▲────────────────┘
                 │                                                   │
                 │              ┌──────────────────────┐             │
                 └─────────────►│ Virtual Bridge br_ares├─────────────┘
                                │ tc netem: 5ms delay  │
                                │           1.2ms jit  │
                                └──────────────────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │   EVIDENCE LEDGER    │
                                │ (evidence_ledger.py) │
                                │ SHA-256 Hash Chained │
                                └──────────────────────┘
```

---

## Evaluation Results Matrix (Evaluated Scenarios AV00–AV08)

| Vector Code | Demarcation Layer | Physical Attack Description | `tamper_alert` | `safe_data_out` | Demarcation Decision |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **AV00** | Nominal Baseline | 192-bit standard Manchester broadcast | **`0`** | `0xAA` | **ACCEPTED_NOMINAL** |
| **AV01** | Layer-1 Physical | 3-cycle baseband runt glitch ($N \le 7$) | **`1`** | **`0x00`** | **MITIGATED_TRAPPED** |
| **AV02** | Layer-1 Physical | 13-cycle mid-band phase desync ($11 \le N \le 15$) | **`1`** | **`0x00`** | **MITIGATED_TRAPPED** |
| **AV03** | Layer-1 Physical | 30-cycle missing-edge gap resumption ($N \ge 21$) | **`1`** | **`0x00`** | **MITIGATED_TRAPPED** |
| **AV04** | Layer-2 Syntax | 32-bit corrupted preamble header | **`1`** | **`0x00`** | **MITIGATED_TRAPPED** |
| **AV05** | Layer-2 Syntax | Malformed protocol type identifier | **`1`** | **`0x00`** | **MITIGATED_TRAPPED** |
| **AV06** | Layer-2 Syntax | Protocol constant corruption | **`1`** | **`0x00`** | **MITIGATED_TRAPPED** |
| **AV07** | Layer-2 Syntax | Frame truncation underflow (< 192 bits) | **`1`** | **`0x00`** | **MITIGATED_TRAPPED** |
| **AV08** | Layer-2 Syntax | Frame overrun overflow (> 192 bits) | **`1`** | **`0x00`** | **MITIGATED_TRAPPED** |

### Defensible Epistemic Claim Boundaries:
1. **Mitigation Scope**: 100% mitigation verified across the evaluated AV00–AV08 demonstrator attack vectors. This is an empirical evaluation of specific tested vectors and **does NOT constitute an absolute universal attack-prevention guarantee**.
2. **Audit Ledger**: Implemented as a **tamper-evident SHA-256 hash-chained forensic audit ledger** (FIPS 180-4), mathematically verified with unbroken hash links.
