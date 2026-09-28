# ARES-RX Sentinel — Acceptance Criteria
**Document Version:** 1.0.0  
**Classification:** Core Governance & Acceptance Standard  
**Status:** Approved by Technical Architect  

---

## 1. Kriteria Keberhasilan Fungsional & Fisik

### AC-01: Verifikasi Baseline Kontrol ($B$)
- [x] Baseline `tt07-bep-decode` lulus pengujian nominal Cocotb dengan dataset riil (`transmission_digital_hs.csv`).
- [x] Dokumentasi kelemahan baseline tercatat dengan bukti waveform failure saat diinjeksi glitch 1-cycle.

### AC-02: Layer-1 Temporal Integrity
- [x] Deteksi glitch deterministik: Setiap pulsa $N \le 7$ clock cycles ($< 400\,\mu\text{s}$) memicu `temporal_fault = 1` tanpa terkecuali.
- [x] Deteksi mid-band deterministik: Setiap interval $11 \le N \le 15$ cycles ($550 - 750\,\mu\text{s}$) memicu `temporal_fault = 1`.
- [x] Deteksi timeout deterministik: Kondisi diam $\ge 21$ cycles ($1050\,\mu\text{s}$) saat transmisi aktif memicu `temporal_fault = 1`.
- [x] Zero false alarm: Tidak ada false positive alarm saat menerima sinyal valid nominal dengan deviasi jitter $\le \pm 11.1\%$.

### AC-03: Layer-2 Frame Syntax Integrity
- [x] Preamble check: Mengunci deteksi hanya jika 32-bit `0xAAAAAAAA` cocok sempurna.
- [x] Constant check: Mengkonfirmasi trailer 32-bit `0x0DFFFFFE`.
- [x] Sintaks anomali: Frame dengan preamble atau trailer cacat langsung masuk ke `STATE_FAULT`.

### AC-04: Layer-3 Hardware Fail-Closed Isolation
- [x] Zeroization: Saat `temporal_fault` atau `protocol_fault` aktif, pin `parallel_out` dipaksa ke `0x00`.
- [x] Sticky Latch: Pin `tamper_alert` bertahan pada logika `1` meskipun sinyal input kembali ke kondisi idle atau nominal, hingga diberi hard reset `rst_n = 0`.

---

## 2. Kriteria Keberhasilan PPA & Silikon (Tiny Tapeout TT07/TT08)

### AC-05: Area Silikon
- [x] Sentinel logic overhead tidak melebihi $1 \times 1$ tile Tiny Tapeout ($160 \times 100\,\mu\text{m}^2$). Terverifikasi: $161 \times 111.52\,\mu\text{m}$, standard cell area $6,477.46\,\mu\text{m}^2$.
- [x] Total cell count tambahan untuk modul Sentinel $\le 120$ standard cells pada PDK SkyWater 130nm. Terverifikasi: 112 cells untuk modul Sentinel.

### AC-06: Timing Slack
- [x] Setup dan hold timing slack positif pada frekuensi clock operasional ($20.0\text{ kHz}$) dan pada corner uji $50\text{ MHz}$ (maksimal clock Tiny Tapeout). Terverifikasi: Setup $+11.88\,\text{ns}$ @ $50\,\text{MHz}$ ($F_{\max} \approx 123.7\,\text{MHz}$), Hold $+0.42\,\text{ns}$.
- [x] Zero setup/hold violations pasca-sintesis OpenLane / OpenROAD.

---

## 3. Kriteria Keberhasilan Pembuktian Adversarial

### AC-07: Matriks Uji AV01 s/d AV08
- [x] Semua 8 skenario vektor serangan memiliki file stimulus executable, file expected, dan log hasil verifikasi yang berstatus **PASS** (13 Core Tests TC01–TC13).
- [x] Tersedia waveform VCD komparatif yang membuktikan keunggulan pertahanan $S$ dibanding kerentanan $B$ (`ares_sentinel_integrated.vcd`).
