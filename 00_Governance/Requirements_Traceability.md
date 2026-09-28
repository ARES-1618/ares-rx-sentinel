# Requirements Traceability Matrix (RTM) — ARES-RX Sentinel

## Traceability Chain
Setiap klaim keamanan dan fungsi dalam proposal harus memiliki rantai pembuktian yang tidak terputus:
$$\text{Requirement} \longrightarrow \text{Design Layer} \longrightarrow \text{RTL Module} \longrightarrow \text{Verification Vector} \longrightarrow \text{Evidence}$$

---

## Traceability Table

| Req ID | Requirement Statement | Design Layer | Target RTL Module | Verification Vector | Evidence Status |
|---|---|---|---|---|---|
| **REQ-01** | Deteksi runt pulse / glitch digital ($N \le 7$) | Layer 1 (Temporal) | `ares_timing_sentinel.v` | `AV01_short_pulse` | **VERIFIED (TEST-02, TEST-08 PASS)** |
| **REQ-02** | Deteksi missing edge via gap resume ($N \ge 21$) | Layer 1 (Temporal) | `ares_timing_sentinel.v` | `AV02-A` | **VERIFIED (TEST-03, TEST-08 PASS)** |
| **REQ-03** | Klasifikasi sustained inactivity sebagai end-of-burst context setelah $N_{EOF}$ siklus tanpa transisi | Layer 1 (Context) | `ares_timing_sentinel.v` | `AV02-B` | **VERIFIED (Empirically grounded: $N_{TIMEOUT} (21) < N_{EOF} (64) < G_{IFG, min} (6547)$; confirmed end-to-end multi-burst in M3 TEST-10 PASS)** |
| **REQ-04** | Zero False Alarm pada evaluasi transmisi riil nominal | Layer 1 (Temporal) | `ares_timing_sentinel.v` | `AV08_valid_replay` | **VERIFIED (TEST-07 PASS: 289 Valids, 0 False Alarms pada dataset `transmission_digital_hs.csv`)** |
| **REQ-05** | Validasi integritas struktur frame 192-bit ($32\text{b}$ Preamble, $2\times16\text{b}$ Type, $32\text{b}$ Constant, $72\text{b}$ Dynamic Payload, $24\text{b}$ Trailer, Qualified Truncation/Overrun) | Layer 2 (Frame) | `ares_frame_fsm.v`, `ares_fault_arbiter.v` | `AV07_frame_corruption`, `AV04_extra_edge` | **VERIFIED (M3 TEST 1-10 PASS: iverilog + Python, hardware regression on `transmission_digital_hs.csv`, waveform `ares_frame_fsm.vcd`)** |
| **REQ-06** | Hardware Fail-Closed Isolation ($D_{out} = 0$ saat fault) | Layer 3 (Isolation) | `ares_isolation_gate.v` | `AV01` s/d `AV07` | **VERIFIED (M2 TEST 1-5 PASS: iverilog + Python, no observed leakage across 1,000 cycles)** |
| **REQ-07** | Sticky Tamper Latch (mempertahankan alert hingga hard reset) | Layer 3 (Isolation) | `ares_fault_latch.v` | `AV06_burst_glitch` | **VERIFIED (M2 TEST 1-5 PASS: Active-Low Asynch Reset, first-cause code preserved)** |
| **REQ-08** | Toleransi empiris interval ($[8, 10] \cup [16, 20]$) teruji batas eksplisit $\{7, 8, 10, 11, 15, 16, 20, 21\}$ siklus | Layer 1 (Temporal) | `ares_timing_sentinel.v` | `AV05_phase_shift` | **VERIFIED (TEST-08 PASS)** |
| **REQ-09** | Rejeksi interval mid-band tidak valid ($11 \le N \le 15$) | Layer 1 (Temporal) | `ares_timing_sentinel.v` | `AV03_missing_edge` (Mid-Band) | **VERIFIED (TEST-05, TEST-08 PASS)** |
| **REQ-10** | Integrasi Top Wrapper Demarkasi Digital & Verifikasi Adversarial Terpadu | Integrated Top Core | `ares_sentinel_top.v` | TC01–TC13, HW Replay | **VERIFIED (100% PASS Verilog + Python, SHA-256 sealed)** |
| **REQ-11** | Implementasi Fisik Silikon SkyWater 130nm TT08 Standard Tile | Physical ASIC Core | `tt_um_ares_sentinel_project.v` | OpenROAD, Magic, Netgen, OpenSTA | **VERIFIED (0 active DRC, 100% LVS 758/758, 50.90 nW, TT08 Precheck PASS)** |
| **REQ-12** | Platform Demonstrasi Komparatif & Paket Inovasi BUMN Peruri | Demo & Presentation | `ares_hardware_demo.py`, Proposal, Deck | **VERIFIED (6/6 demo scenarios PASS, sealed in 03_Demonstration_Manifest.sha256)** |
| **REQ-13** | Perluasan Integrasi SoC Industri (AMBA APB4 Bus Wrapper & Driver C99) | SoC Integration | `ares_sentinel_apb.v`, `ares_sentinel_regs.h` | Icarus Verilog + C99 Check | **VERIFIED (0 errors elaboration, MISRA-C compliant header, zero core RTL mod)** |
| **REQ-14** | Rencana & Harness Pengujian Laboratorium Pasca-Fabrikasi | Post-Silicon Harness | `12_Post_Silicon_Bring_Up_Plan.md`, RP2040 Harness | Python & Pico C SDK | **VERIFIED (Calibrated CSV stimulus & autonomous RP2040 test runner firmware)** |

---

## Requirement Notes & Empirical Bounds
1. **REQ-03 Status**: Telah terkonfirmasi end-to-end multi-burst pada M3 TEST 10. Nilai $N_{EOF} = 64$ ($3.2\text{ ms}$) berbasis model empiris inter-frame gap ($G_{IFG, min} = 6547$ samples / $327.35\text{ ms}$) dengan margin temporal $102.3\times$, mereset FSM secara bersih ke `IDLE` tanpa memicu false alarms pada multi-burst sequence.
2. **REQ-04 Qualification**: Klaim zero false alarm dibatasi secara ketat pada evaluasi 289 transisi nominal riil dalam capture `transmission_digital_hs.csv` di bawah model akuisisi $50\,\mu\text{s}$ ($F_s = 20\text{ kHz}$).
3. **REQ-08 Boundary Completeness**: Seluruh 8 titik batas diskrit ($\{7, 8, 10, 11, 15, 16, 20, 21\}$ siklus) telah dieksekusi dan lolos pada simulasi cycle-accurate Python dan RTL synthesizable Icarus Verilog.
4. **REQ-06 & REQ-07 Qualification**: Terverifikasi melalui simulasi native RTL Icarus Verilog 13.0 dan regresi cycle-accurate Python (bukan formal mathematical proof). Menggunakan Active-Low Asynchronous Reset (`rst_n == 0`). Invarian fault code: $set\_fault = 1 \implies fault\_code \neq 3'b000$. Prioritas fault simultan diselesaikan oleh upstream encoder sebelum diteruskan ke latch.
5. **REQ-05 Qualification**: Validasi struktur frame 192-bit dieksekusi secara otonom oleh `ares_frame_fsm.v` tanpa ketergantungan pada flag `full` baseline. Preamble ($32\text{b}$, `32'hAAAAAAAA`), Type 1 ($16\text{b}$, `16'hD391`), Type 2 ($16\text{b}$, `16'hD391`), dan Constant ($32\text{b}$, `32'h0DFFFFFE`) diperiksa seketika pada saat sampel tiba (0 delay). Dynamic payload ($72\text{b}$) bersifat transparan. Protocol trailer ($24\text{b}$) memverifikasi qualified truncation (`frame_started && reception_active == 0`) dan overrun. Arbiter kombinasional murni menegakkan prioritas $L1 > L2$. Terverifikasi 10/10 PASS pada Icarus Verilog dan Python serta regresi hardware.
