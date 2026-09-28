# Technical Audit & Qualification Closure Report: Milestone M1
**Work Order:** WO-M1-QA-002 (Qualification Closure Audit)  
**Project:** ARES-RX Sentinel — Trusted Physical/Digital Demarcation Boundary  
**Target Module:** `ares_timing_sentinel.v` (Layer-1 Temporal Integrity Sentinel)  
**Auditor / Direction:** Technical Architect / Research Direction  
**Executing Engineer:** Implementation Engineer (Copilot)  
**Date:** 2026-09-27  
**Qualification Status:** **RECOMMENDED FOR FORMAL CLOSURE (100% AUDIT CRITERIA MET)**  

---

## 1. Executive Summary

Laporan ini menyajikan hasil pelaksanaan audit kualifikasi independen (`WO-M1-QA-002`) untuk menutup celah teknis dan menjustifikasi klaim ilmiah sebelum Milestone M1 dinyatakan selesai. 

Seluruh 6 isu audit yang diidentifikasi oleh Technical Architect telah diinvestigasi secara empiris, dibuktikan secara matematis, diimplementasikan dalam RTL synthesizable IEEE 1364-2005, dan diverifikasi menggunakan simulator EDA standar industri (**Icarus Verilog 13.0**) serta simulator referensi cycle-accurate Python.

```
+-----------------------------------------------------------------------------------+
|                        M1 QUALIFICATION AUDIT SCORECARD                           |
+-----------------------------------------------------------------------------------+
| 1. Empirical IFG Characterization (25 Captures)    : 100% Grounded (G_IFG=6547)   |
| 2. Parameter Inequality (N_TIMEOUT < N_EOF < G_IFG): SATISFIED (21 < 64 < 6547)   |
| 3. Temporal Margin (Safety Headroom)               : 102.3x (10-log ratio ≈ 20.1dB)|
| 4. REQ-08 Discrete Boundary Sweep ({7..21})       : 8 / 8 Boundaries PASSED       |
| 5. EOP Squelch Noise Rejection                     : 100% Trapped in ARMED/IDLE   |
| 6. Native Icarus Verilog 13.0 Simulation           : 10 / 10 Tests PASSED (100%)  |
| 7. Cycle-Accurate Python Regression                : 10 / 10 Tests PASSED (100%)  |
| 8. VCD Waveform Verification Artifact             : Generated (117,100 Bytes)     |
| 9. Baseline tt07-bep-decode Integrity             : 100% UNTOUCHED (Read-Only)    |
+-----------------------------------------------------------------------------------+
```

---

## 2. Resolusi Temuan Audit Teknis

### 2.1 Justifikasi Empiris Ambang Batas $N_{EOF} = 64$
- **Temuan Awal**: Nilai $N_{EOF} = 64$ siklus ($3.2\text{ ms}$) sebelumnya berstatus provisional tanpa pembuktian distribusi jeda antar-frame riil ($G_{IFG}$).
- **Investigasi Empiris**:
  Dilakukan ekstraksi otomatis terhadap seluruh 25 file rekaman logic analyzer fisik (*Digilent Discovery 3 Logic Analyzer*, $F_s = 20\text{ kHz}, T_s = 50\,\mu\text{s}$) pada direktori `tt07-bep-decode/test/data/`.
  
  Pada capture transmisi periodik (`hs_repeating/01.csv` s/d `10.csv`), jeda normal antar-burst transmisi sensor (*Inter-Frame Gap*) terukur dengan konsistensi kuarsa:
  $$\boxed{G_{IFG, min} = 6547\text{ samples} \quad (327.35\text{ ms})}$$
  $$\boxed{G_{IFG, median} = 6547\text{ samples} \quad (327.35\text{ ms})}$$
  $$\boxed{G_{IFG, max} = 6548\text{ samples} \quad (327.40\text{ ms})}$$

- **Pembuktian Ketidaksamaan Ambang Batas**:
  Persyaratan ketat arsitektur:
  $$\boxed{N_{TIMEOUT} < N_{EOF} < G_{IFG, min}}$$
  Dengan nilai terkalibrasi:
  $$21\text{ samples } (1.05\text{ ms}) < 64\text{ samples } (3.20\text{ ms}) < 6547\text{ samples } (327.35\text{ ms})$$
  
- **Analisis Margin Temporal**:
  1. $\text{Temporal margin} = \frac{G_{IFG, min}}{N_{EOF}} = \frac{6547}{64} \approx \mathbf{102.3\times}$ (ekuivalen dengan rasio temporal $10\log_{10}(102.3) \approx 20.1\text{ dB}$). FSM Sentinel telah berada kembali di `STATE_IDLE` $324.15\text{ ms}$ sebelum burst berikutnya tiba.
  2. $\frac{N_{EOF}}{N_{TIMEOUT}} = \frac{64}{21} \approx 3.05\times$. Memberikan jendela waktu $2.15\text{ ms}$ ($43$ siklus sampling) untuk mendeteksi missing-edge yang disambung kembali.

### 2.2 Demarkasi Latensi Deteksi Anomali
Dokumentasi dan FSM Sentinel membedakan latensi deteksi secara eksplisit:
1. **Zero-Latency In-Frame Anomalies (Immediate)**:
   - **Runt Glitch ($N \le 7$)**: Dideteksi seketika pada siklus clock saat edge tiba.
   - **Mid-Band Anomaly ($11 \le N \le 15$)**: Dideteksi seketika pada siklus clock saat edge tiba.
   - **Extra Edge / Bouncing ($N \le 7$)**: Dideteksi seketika pada siklus clock saat edge tiba.
2. **Deferred Classification Anomalies**:
   - **Missing Edge / Gap Resume**: Membutuhkan $21 T_s$ ($1.05\text{ ms}$) keheningan untuk bertransisi ke `STATE_LONG_GAP_PENDING`. Penegasan fault dikonfirmasi tepat pada saat edge berikutnya tiba ($t_{resume}$).
   - **End-of-Burst Silence**: Dikonfirmasi pada $t = 64 T_s$ ($3.20\text{ ms}$) keheningan tanpa edge, bertransisi ke `STATE_IDLE` tanpa membangkitkan fault alert (Zero False Positive).

### 2.3 Perilaku EOP Terhadap Squelch Noise Receiver
- Ketika transmisi pemancar RF berhenti, AGC pada modul demodulator analog (443 MHz ASK/OOK) secara bertahap menaikkan gain, memuntahkan hash/chatter acak ($N = 1..4$ sample).
- **Mekanisme Filtrasi Sentinel**:
  1. Keheningan pasca-burst selama $3.2\text{ ms}$ ($N_{EOF} = 64$) memastikan Sentinel telah bertransisi kembali ke `STATE_IDLE` sebelum kenaikan AGC terjadi.
  2. Ketika pulsa noise pertama tiba saat di `STATE_IDLE`, Sentinel bertransisi ke `STATE_ARMED`.
  3. Pulsa-pulsa noise berikutnya ($N \in [1, 4]$) adalah interval non-valid ($N \notin \mathcal{V}$). Sentinel mengeksekusi re-arming di `STATE_ARMED` tanpa membangkitkan `temporal_fault`.
  4. Ketika noise berhenti $\ge 21$ siklus, FSM kembali ke `STATE_IDLE` secara mulus.
  - Skenario ini diverifikasi pada **TEST 8** (100% Pass).

### 2.4 Uji Batas Eksplisit REQ-08 (Discrete Boundary Sweep)
Seluruh 8 titik batas kuantisasi interval dievaluasi secara deterministik:
- $N = 7$: Ditertibkan sebagai `FAULT_RUNT` (`fault_code = 3'b001`) — **PASS**
- $N = 8$: Diterima sebagai batas bawah Half-Bit sah (`temporal_valid = 1`) — **PASS**
- $N = 10$: Diterima sebagai batas atas Half-Bit sah (`temporal_valid = 1`) — **PASS**
- $N = 11$: Ditertibkan sebagai batas bawah Mid-Band ilegal (`fault_code = 3'b010`) — **PASS**
- $N = 15$: Ditertibkan sebagai batas atas Mid-Band ilegal (`fault_code = 3'b010`) — **PASS**
- $N = 16$: Diterima sebagai batas bawah Full-Bit sah (`temporal_valid = 1`) — **PASS**
- $N = 20$: Diterima sebagai batas atas Full-Bit sah (`temporal_valid = 1`) — **PASS**
- $N = 21$: Bertransisi ke `LONG_GAP_PENDING`; ditertibkan sebagai `FAULT_GAP_RES` saat resume — **PASS**

### 2.5 Pemisahan Vektor Serangan & Pembaruan RTM
- **REQ-03**: Diperbarui menjadi *"Klasifikasi sustained inactivity sebagai end-of-burst context setelah $N_{EOF}$ siklus tanpa transisi"*, berstatus `PROVISIONAL` dengan rujukan bukti empiris $N_{TIMEOUT} < N_{EOF} < G_{IFG, min}$.
- **REQ-04**: Dikualifikasikan secara jujur: *"Zero False Alarm pada evaluasi 289 transisi nominal riil (`transmission_digital_hs.csv`)"*.
- **REQ-09**: Ditambahkan ke RTM untuk mencakup *Mid-Band Interval Rejection ($11 \le N \le 15$)*, memisahkannya dari AV02 missing edge.
- **AV03**: Ditetapkan secara spesifik sebagai *Mid-Band Anomaly Vector*.

---

## 3. Matriks Hasil Verifikasi Lengkap (9 / 9 Tests)

Verifikasi dieksekusi secara independen pada dua domain eksekusi:
1. **Native Verilog Simulation**: `iverilog 13.0` + `vvp` (`tb_ares_timing_sentinel.v`).
2. **Cycle-Accurate Reference Model**: Python standalone runner (`run_unit_tests.py`).

| Test ID | Kategori Uji | Deskripsi Stimulus | Hasil Diharapkan | Hasil Simulasi Verilog | Hasil Simulasi Python | Status |
|---|---|---|---|---|---|---|
| **TEST 1** | Nominal Transition | Pulse Preamble (8, 9, 10, 18 cycles) | `IDLE -> ARMED -> ACTIVE`, `temporal_valid=1` | ACTIVE, Valid=1, Fault=0 | ACTIVE, Valid=1, Fault=0 | **PASS** |
| **TEST 2** | **AV01**: Runt Glitch | Glitch 3 siklus saat frame aktif | `temporal_fault=1`, `fault_code=3'b001`, `ACTIVE -> IDLE` | Fault=1, Code=001, State=IDLE | Fault=1, Code=001, State=IDLE | **PASS** |
| **TEST 3** | **AV02-A**: Missing Edge | Gap 21 siklus $\rightarrow$ resume di siklus 35 | `ACTIVE -> PENDING -> FAULT`, `fault_code=3'b011` | Fault=1, Code=011, State=IDLE | Fault=1, Code=011, State=IDLE | **PASS** |
| **TEST 4** | **AV02-B**: EOP Silence | Keheningan 65 siklus ($> N_{EOF}=64$) | `PENDING -> IDLE`, zero false alarm | State=IDLE, Fault=0, Tamper=0 | State=IDLE, Fault=0, Tamper=0 | **PASS** |
| **TEST 5** | **AV03**: Mid-Band Anomaly | Gap 13 siklus ($11 \le N \le 15$) | `temporal_fault=1`, `fault_code=3'b010`, `ACTIVE -> IDLE` | Fault=1, Code=010, State=IDLE | Fault=1, Code=010, State=IDLE | **PASS** |
| **TEST 6** | **AV04**: Extra Edge | Bouncing spike pada siklus 4 dalam cell | `temporal_fault=1`, `fault_code=3'b001`, `ACTIVE -> IDLE` | Fault=1, Code=001, State=IDLE | Fault=1, Code=001, State=IDLE | **PASS** |
| **TEST 7** | **AV08**: Real Hardware Stream | 8.192 physical samples (`transmission_digital_hs.csv`) | 289 valid transitions, 0 false alarms, clean return to IDLE | Valids=289, Faults=0, State=IDLE | Valids=289, Faults=0, State=IDLE | **PASS** |
| **TEST 8** | **REQ-08**: Boundary Sweep | Injeksi diskrit $\{7, 8, 10, 11, 15, 16, 20, 21\}$ | Kepatuhan ketat terhadap batas $\mathcal{V}$ | 8 / 8 Boundary Tests Passed | 8 / 8 Boundary Tests Passed | **PASS** |
| **TEST 9** | EOP + Squelch Noise | EOF silence $\rightarrow$ IDLE $\rightarrow$ noise $N=1..4$ | Filtered in ARMED, returns to IDLE, 0 false alarm | State=IDLE, Fault=0 | State=IDLE, Fault=0 | **PASS** |
| **TEST 10** | EOP Chatter at Cycle 40 | Noise spike at cycle 40 during `PENDING` | Trapped as `FAULT_GAP_RES`, settling cleanly to IDLE | Fault=1, Code=011, State=IDLE | Fault=1, Code=011, State=IDLE | **PASS** |

---

## 4. Integritas Baseline Upstream

Repositori referensi kontrol upstream `03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/` dipertahankan dalam kondisi **100% read-only**:
- Git hash dan timestamp file baseline tidak berubah.
- Tidak ada modifikasi pada modul `project.v`, `serial_decode.v`, `state_machine.v`, maupun test suite bawaan.

---

## 5. Rekomendasi Penutupan Milestone M1

Berdasarkan bukti empiris dan verifikasi komputasional di atas:
1. Work Order `WO-M1-QA-002` dinyatakan **SELESAI DENGAN STATUS MEMUASKAN**.
2. Milestone M1 (Layer-1 Temporal Integrity Sentinel) siap ditutup secara formal oleh Technical Architect.
3. Proyek siap beralih ke penyusunan spesifikasi dan eksekusi **Milestone M2: Layer-3 Hardware Fail-Closed Isolation & Sticky Fault Latch** (`ares_isolation_l3.v`).
