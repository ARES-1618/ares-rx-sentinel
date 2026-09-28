# Milestone M2 Verification Summary: Layer-3 Hardware Fail-Closed Isolation
**Work Order:** WO-2026-M2-001  
**Project:** ARES-RX Sentinel — Trusted Physical/Digital Demarcation Boundary  
**Modules Under Test:** `ares_fault_latch.v`, `ares_isolation_gate.v`, `ares_isolation_l3.v`  
**Architecture:** Sequential Sticky Fault Latch + Pure Combinational Zeroization Gate  
**Authority:** Technical Architect / Research Direction  
**Executing Engineer:** Implementation Engineer (Copilot)  
**Date:** 2026-09-27  
**Milestone Status:** **CLOSED (Officially Signed Off by Technical Architect)**  
**Verification Result:** **M2 telah diimplementasikan dan diverifikasi melalui native RTL simulation serta cycle-accurate regression (5/5 Tests Passed on both Icarus Verilog 13.0 and Python)**  

---

## 1. Executive Summary

Milestone M2 merealisasikan subsistem penegakan keamanan perangkat keras (*Hardware Security Enforcement Perimeter*) yang memisahkan ranah **Deteksi (M1)** dari ranah **Penegakan (M2)**:
$$\boxed{M1 = \text{Detection}} \quad \longrightarrow \quad \boxed{M2 = \text{Enforcement}} \quad \longrightarrow \quad \boxed{M3 = \text{Frame Integrity}}$$

Modul Layer-1 (`ares_timing_sentinel.v`) dipertahankan secara absolut sebagai **frozen engineering baseline** (tanpa modifikasi). Subsistem Layer-3 mengisolasi seluruh data keluaran seketika setelah pulsa anomali tertangkap.

```
+-----------------------------------------------------------------------------------------+
|                              M2 VERIFICATION SCORECARD                                  |
+-----------------------------------------------------------------------------------------+
| 1. Pure Combinational Zeroization Latency      : 0 Extra Clock Cycles PASSED            |
| 2. Normal Data Passthrough (fault_latched=0)   : 100% Transparent PASSED                |
| 3. Tamper Alert Hardware Assertion            : Synchronous with Latch PASSED          |
| 4. Post-Fault Ingestion Leakage Check          : No observed leakage during the         |
|                                                  evaluated 1,000-cycle regression PASSED|
| 5. First-Cause Diagnostic Code Latching        : First triggering code preserved PASSED |
| 6. Active-Low Asynchronous Reset Recovery     : Clean Restoration (rst_n=0) PASSED     |
| 7. Native Icarus Verilog 13.0 Simulation       : 5 / 5 Tests PASSED (100%)              |
| 8. Cycle-Accurate Python Regression            : 5 / 5 Tests PASSED (100%)              |
| 9. VCD Waveform Verification Artifact         : Generated (50,526 Bytes)               |
| 10. M1 Sentinel & Baseline Immutability        : 100% UNTOUCHED (Read-Only)             |
+-----------------------------------------------------------------------------------------+
```

> [!NOTE]
> **Metodologi Verifikasi**: Hasil di atas membuktikan kepatuhan fungsional terhadap seluruh rangkaian stimulus uji yang dievaluasi pada simulator native Icarus Verilog 13.0 dan model referensi cycle-accurate Python. Hasil ini tidak diklaim sebagai formal mathematical proof (seperti SymbiYosys / model checking).

---

## 2. Test Execution Matrix

| Test ID | Kategori Uji | Deskripsi Stimulus | Properti Verifikasi yang Dibuktikan | Hasil Verilog | Hasil Python | Status |
|---|---|---|---|---|---|---|
| **TEST 1** | Normal Passthrough | Injeksi data `0xA5`, `0x5A` saat `fault_latched = 0` | $data_{out} = decoded\_data \land tamper\_alert = 0$ | DataOut=0xA5/0x5A, Alert=0 | DataOut=0xA5/0x5A, Alert=0 | **PASS** |
| **TEST 2** | Instant Zeroization | Strobe `temporal_fault = 1` dengan `fault_code = 3'b001` | Zero extra cycle latency: $fault\_latched \implies data_{out} = 0x00$ | DataOut=0x00, Alert=1, Code=001 | DataOut=0x00, Alert=1, Code=001 | **PASS** |
| **TEST 3** | First-Fault Invariant | Injeksi fault beruntun: `001` $\rightarrow$ `010` $\rightarrow$ `011` | $CodeLatch_{next} = CodeLatch$ saat $FaultLatch = 1$ | Code tetap 001 | Code tetap 001 | **PASS** |
| **TEST 4** | Post-Fault Isolation | Streaming 1.000 siklus data acak paska-fault | No observed leakage: $fault\_latched \implies data_{out} = 0 \land valid_{out} = 0$ | 0 Leakage across 1,000 cycles | 0 Leakage across 1,000 cycles | **PASS** |
| **TEST 5** | Reset Recovery | Penegasan `rst_n = 0` lalu kirim data `0x3C` | Reset clears: $Reset \implies fault\_latched = 0 \land DataOut = in$ | DataOut=0x3C, Alert=0 | DataOut=0x3C, Alert=0 | **PASS** |

---

## 3. Spesifikasi Formal & Perilaku RTL

### 3.1 Semantik Reset: Active-Low Asynchronous Reset
Modul `ares_fault_latch.v` dan `ares_isolation_l3.v` menggunakan semantik **Active-Low Asynchronous Reset**:
```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        fault_latched      <= 1'b0;
        latched_fault_code <= 3'b000;
    end else begin
        // clocked synchronous evaluation
    end
end
```
Kriteria penerimaan pemulihan reset (*Reset Recovery Invariant*):
$$
rst\_n = 0 \implies
\begin{cases}
fault\_latched = 0 \\
latched\_fault\_code = 3\text{'b}000 \\
tamper\_alert = 0
\end{cases}
$$
Ketika `rst_n` aktif rendah ($0$), seluruh status keamanan dan diagnostik kembali ke kondisi aman secara asinkron tanpa menunggu clock edge berikutnya.

### 3.2 Zero Additional Clock-Cycle Zeroization
Gerbang isolasi (`ares_isolation_gate.v`) murni kombinasional:
```verilog
assign out_data     = fault_latched ? {DATA_WIDTH{1'b0}} : in_data;
assign out_valid    = fault_latched ? 1'b0               : in_valid;
assign tamper_alert = fault_latched;
```
Security Invariant:
$$
fault\_latched = 1 \implies data\_out = 0 \land out\_valid = 0 \land tamper\_alert = 1
$$
Begitu register sekuensial `ares_fault_latch` memperbarui `fault_latched` pada clock edge, keluaran seketika terisolasi tanpa ada delay siklus clock tambahan.

### 3.3 First-Cause Latching & Kontrak Fault-Code Validity
```verilog
if (set_fault) begin
    fault_latched <= 1'b1;
    if (!fault_latched) begin
        latched_fault_code <= fault_code_in;
    end
end
```
Kontrak kelas fault code yang dikunci:
- `3'b000`: `FAULT_NONE` (Normal / No Fault).
- `3'b001 .. 3'b111`: Kelas fault valid (M1 temporal runt/mid-band/gap-resume, M3 frame syntax violations).
- **Invarian Validitas**:
  $$set\_fault = 1 \implies fault\_code \neq 3\text{'b}000$$

### 3.4 Kontrak Arbitrasi Fault Simultan (Simultaneous Fault Arbitration)
Apabila `temporal_fault` (Layer-1) dan `frame_fault` (Layer-2) aktif secara bersamaan pada siklus clock yang sama ($set\_fault = 1$ simultan):
- Penentuan `fault_code` pemicu harus diselesaikan oleh **upstream fault arbiter / priority encoder** sebelum diteruskan ke pin `fault_code_in` pada `ares_fault_latch`.
- Prioritas default arsitektur:
  $$\text{Priority 1 (Tertinggi)}: \text{Layer-1 Temporal Violation (Integritas Fisik)}$$
  $$\text{Priority 2}: \text{Layer-2 Frame Syntax Violation (Integritas Protokol)}$$
  Hal ini menjamin bahwa anomali level fisik/sinyal yang mendasari selalu tercatat sebagai akar penyebab utama (*primary cause*) sebelum anomali struktur frame turunan.

---

## 4. Integritas Kontrol Upstream & Baseline M1

- **Modul M1 (`ares_timing_sentinel.v`)**: Dibiarkan utuh tanpa perubahan (0 baris dimodifikasi, frozen baseline).
- **Baseline Upstream (`tt07-bep-decode`)**: Terjaga 100% read-only (`working tree clean`).
