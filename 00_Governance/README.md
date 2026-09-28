# ARES SEMIKONDUKTOR TECHNOLOGY — Governance Framework

## 1. Mandat & Pemisahan Otoritas

Proyek ini menerapkan pemisahan ketat antara **Otoritas Desain** dan **Otoritas Implementasi**:

```
                 ARES TECHNICAL ARCHITECTURE
                           │
                           ▼
             Technical Architect / Research
             (Requirements, Physics, Threat, Specs)
                           │
                           ▼
                  Design Specification
                           │
                           ▼
               Copilot / Implementation
              (RTL, Testbench, Build, Evidence)
                           │
                           ▼
                 Verification Evidence
                           │
                           ▼
               Architect Review & Sign-Off
```

### Otoritas Desain (Technical Architect)
- Menentukan **apa** yang dibangun dan **mengapa**.
- Menetapkan asumsi fisik, boundary sinyal, dan toleransi waktu.
- Menyusun Threat Model, Arsitektur RTL, Security Model, dan Kontrak Layer.
- Menentukan kriteria PASS/FAIL dan matriks verifikasi.
- Menerbitkan **Work Order** resmi sebelum implementasi dimulai.

### Otoritas Implementasi (Implementation Engineer / Copilot)
- Menulis kode RTL SystemVerilog/Verilog sesuai spesifikasi kontrak.
- Membangun testbench Cocotb dan otomasi simulasi.
- Mengumpulkan bukti verifikasi (log simulasi, waveform VCD/FST, sintesis PPA).
- Dilarang mengubah dokumen spesifikasi, memperluas cakupan tanpa izin, atau memodifikasi baseline referensi.

---

## 2. Struktur Direktori Workspace

- `00_Governance/`: Kontrak kerja, status milestone, decision log, dan requirements traceability.
- `01_Vision_and_Blueprints/`: Blueprints arsitektur, threat model, timing model, dan spesifikasi formal.
- `02_References/`: Literatur ilmiah, datasheet komponen RF, repositori upstream TinyTapeout, dan dokumen Peruri.
- `03_Core_Projects/`:
  - `tt07-bep-decode/`: Baseline referensi immutable ($B$).
  - `ares_sentinel/`: Modul enhancement ARES-RX Sentinel ($S$).
  - `integration/`: Top-level ASIC wrapper untuk Tiny Tapeout.
- `04_Verification/`: Attack vectors (AV01 - AV08), Cocotb regression suite, waveform dumps, dan hasil pengujian.
- `05_Synthesis_and_PPA/`: Skrip OpenLane/Yosys, laporan timing, luas area (die utilization), dan konsumsi daya.
- `06_Demonstration/`: Materi presentasi, visualisasi arsitektur, dan demonstrasi kejuaraan.
- `99_Archive/`: Cadangan arsip dan modul komplementer.
