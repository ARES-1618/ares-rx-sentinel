# ARES-RX Sentinel — Verification Strategy
**Document Version:** 1.0.0  
**Classification:** Core Verification Strategy  
**Status:** Approved by Technical Architect  

---

## 1. Dual-Track Comparative Verification ($B \leftrightarrow S$)

Strategi pembuktian ARES-RX Sentinel menggunakan metode komparasi ganda:
- **Kondisi Kontrol ($B$)**: Desain referensi baseline `tt07-bep-decode`.
- **Kondisi Eksperimen ($S$)**: ARES-RX Sentinel (Baseline + Sentinel Layers).

Setiap attack vector dijalankan secara simultan terhadap $B$ dan $S$ menggunakan testbench Cocotb yang identik untuk mendokumentasikan perbedaan respon secara objektif.

```
                            Adversarial Stimulus
                           (AV01 s/d AV08 / Real CSV)
                                      │
                     ┌────────────────┴────────────────┐
                     │                                 │
                     ▼                                 ▼
             Baseline Design (B)               ARES Sentinel (S)
                     │                                 │
                     ▼                                 ▼
           Failure Observation               Defensive Enforcement
        (Silent corruption / Reset)        (Isolation / Tamper Alert)
                     │                                 │
                     └────────────────┬────────────────┘
                                      ▼
                           Comparative Evidence Log
                           & Waveform Proof (VCD)
```

---

## 2. Taksonomi Suite Attack Vector (AV01 - AV08)

| ID Vektor | Kategori Serangan | Target Lapisan | Indikator Keberhasilan Pengujian |
|---|---|---|---|
| **AV01** | Short Pulse / Runt Glitch | Layer 1 | Deteksi $100\%$, `temporal_fault = 1`, `tamper_alert = 1`, output data zero |
| **AV02** | Stretched / Long Pulse | Layer 1 | Deteksi interval mid-band dan timeout $\ge 21$ cycles |
| **AV03** | Missing Edge Transisi | Layer 1 | Deteksi desinkronisasi fasa Manchester |
| **AV04** | Extra Edge / Bouncing | Layer 1 | Penolakan transisi dobel dalam satu bit-cell |
| **AV05** | Phase Drift / Clock Skew | Layer 1 | Lolos jika dalam toleransi $\pm 11.1\%$, ditolak jika melampaui |
| **AV06** | Continuous Hash / Jamming| Layer 1 & 3 | Zeroization bus, tidak ada loop reset parasitik |
| **AV07** | Frame Syntax Corruption | Layer 2 | Penolakan preamble/constant tidak cocok |
| **AV08** | Pristine Valid Replay | Layer 1, 2, 3 | Penerimaan data $100\%$ akurat, 0 false alarm |

---

## 3. Alur Eksekusi Otomasi Uji (Automated Verification Flow)

1. **Unit Test Level**: Pengujian modul terisolasi (`ares_timing_sentinel`, `ares_frame_fsm`, `ares_isolation_gate`).
2. **Top-Level Integration Test**: Pengujian top-level wrapper dengan injektor stimulus Cocotb.
3. **Hardware Capture Regression**: Menjalankan seluruh dataset riil (`transmission_digital_hs.csv`, `noise.csv`, `start_mangled.csv`, `hs_long/*.csv`).
4. **Waveform Artifact Generation**: Menghasilkan file VCD/FST teranotasi untuk setiap skenario serangan sebagai bukti verifikasi proposal.
