# Decision Log — ARES-RX Sentinel

## ADR-001: Demarkasi Domain Digital & Klaim Keamanan Defensibel
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Karena ASIC Tiny Tapeout menerima sinyal demodulasi digital (`ui_in[0] = rx_in`), klaim diselaraskan secara akademis menjadi: **"Trusted Digital Reception Boundary"**. Deteksi difokuskan pada anomali temporal dan struktural pada representasi digital sinyal penerimaan, bukan deteksi analog RF langsung.

---

## ADR-002: Ekstraksi Empiris Parameter Waktu (Timing Model v1.0)
- **Status**: Approved (Updated to v1.1)
- **Tanggal**: 2026-09-27
- **Keputusan**:
  - Frekuensi Sampling Capture Fisik: $F_s = 20\text{ kHz}$ ($T_s = 50\,\mu\text{s}$).
  - Interval Half-Bit Diamati: $N_{HB} \approx 9\text{ samples}$ ($450\,\mu\text{s}$) dengan empirical acceptance window $[8, 10]\text{ samples}$.
  - Interval Full-Bit Diamati: $N_{bit} \approx 18\text{ samples}$ ($900\,\mu\text{s}$) dengan empirical acceptance window $[16, 20]\text{ samples}$.
  - Baud rate nominal: $\approx 1111.11\text{ bps}$.

---

## ADR-003: Pembekuan Baseline Referensi (Control B)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Repositori upstream `tt07-bep-decode` dipindahkan ke `03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/` dan ditetapkan sebagai **immutable reference baseline ($B$)**. Modifikasi dilarang.

---

## ADR-004: Tiga Lapisan Arsitektur Sentinel
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Arsitektur ARES-RX Sentinel dibagi menjadi 3 lapisan independen:
  1. Layer 1 (Temporal Integrity)
  2. Layer 2 (Frame Protocol Integrity)
  3. Layer 3 (Hardware Isolation & Fail-Closed Enforcement)

---

## ADR-005: Pembedaan Frekuensi Sampling Fisik ($F_s$) vs Clock RTL ASIC ($F_{clk}$)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Konteks**: Nilai $20\text{ kHz}$ berasal dari capture logic analyzer (*acquisition quantum*), bukan otomatis clock internal ASIC.
- **Keputusan**: Menetapkan $F_s = 20\text{ kHz}$ ($T_s = 50\,\mu\text{s}$) sebagai *sampling reference*. Bila RTL menggunakan clock langsung $20\text{ kHz}$ (Case A), maka $F_{clk} = F_s$. Bila RTL menggunakan clock frekuensi tinggi (Case B), interval dikonversi melalui prescaler. Nilai $N_{HB}=9$ didefinisikan sebagai *observed timing quantization*.

---

## ADR-006: Context-Dependent Timeout (Penanganan Idle Time)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Konteks**: Periode diam antar-frame dapat mencapai $> 20\text{ ms} \gg 1050\,\mu\text{s}$. Jika aturan $N \ge 21 \Rightarrow \text{fault}$ aktif permanen, sistem akan false alarm saat tidak ada transmisi.
- **Keputusan**: Deteksi timeout ($N_{edge} \ge 21$) HANYA aktif saat frame sedang berlangsung (`frame_active = 1`). Saat IDLE, interval diam panjang dianggap normal.

---

## ADR-007: Logika Keamanan Tri-Part (Validity, Fault, Authorization)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Memisahkan tiga status:
  - **Validity**: $V_{trusted} = V_{physical} \land V_{protocol}$ (Kepatuhan protokol).
  - **Fault**: $\text{FaultLatch} = \text{TemporalFault} \lor \text{ProtocolFault}$ (Indikasi serangan aktif).
  - **Authorization**: $\text{DataPass} = \text{FrameValid} \land \neg \text{FaultLatch}$.
  - Ketiadaan validitas ($V_{protocol} = 0$ saat IDLE) TIDAK disamakan dengan terjadinya serangan ($\text{Tamper} = 0$).

---

## ADR-008: Pembatasan Ruang Lingkup Milestone M1 (Layer 1 Only)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Work Order M1 dibatasi secara ketat hanya pada Layer-1 Temporal Integrity (`ares_timing_sentinel.v`) dan vektor serangan AV01 s/d AV04. Layer-2 Frame FSM ditunda ke M3 untuk memastikan pengujian checkpoint eksperimental modular.

---

## ADR-009: Sticky Hardware Latch & Combinational MUX Zeroization (Milestone M2)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Mengadopsi isolasi kombinasional MUX berlatensi 1 siklus clock pada Layer 3 (`ares_isolation_gate.v`) dan penguncian kesalahan asinkron (*sticky fault latch*) yang hanya dapat dibersihkan melalui sinyal hard reset (`rst_n = 0`). Memaksa data paralel $D_{\text{out}} = 8\text{'b}0000\_0000$ seketika saat terpicu fault.

---

## ADR-010: Autonomous 192-bit Counter & Decoupling from Baseline (Milestone M3)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: `ares_frame_fsm.v` tidak boleh mengandalkan sinyal `full` milik baseline sebagai sumber kebenaran framing. Layer 2 mengimplementasikan pencacah bit internal mandiri $0 \dots 191$ sinkron dengan `serial_clock` dan memvalidasi preamble (`0xAAAAAAAA`), tipe (`0xD391`), konstanta (`0x0DFFFFFE`), serta menjebak pemotongan (*truncation*) dan bit berlebih (*overrun*) secara otonom.

---

## ADR-011: Combinational Fault Priority Arbiter (Milestone M3)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Menambahkan modul `ares_fault_arbiter.v` untuk menyelesaikan konflik pemicuan simultan pada siklus clock yang sama dengan prioritas ketat: $L1 \text{ (Temporal)} > L2 \text{ (Syntax Grammar)}$. First-cause kesalahan dipertahankan oleh latch Layer 3.

---

## ADR-012: EOP Timing Disambiguation & Normalization (Milestone M4)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Menstandarkan definisi waktu End-of-Packet (EOP) di seluruh domain simulasi Verilog dan model referensi Python menjadi $N_{\text{silence}} = T_{\text{EOP}} - T_{\text{edge}} = 64\text{ cycles}$ ($3.2\,\text{ms}$ @ $20\,\text{kHz}$). Angka historis 57/65 dihapus secara menyeluruh dari seluruh laporan penyerahan.

---

## ADR-013: Model Daya Workload-Derived Post-Route OpenSTA (Milestone M5)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Menolak estimasi daya statis default OpenSTA ($1.2\,\text{nW}$) yang tidak berbobot aktivitas. Mengadopsi estimasi daya berbasis VCD simulation trace aktual (Skenario B: $\alpha = 0.075$, duty = 0.50) yang menghasilkan disipasi daya total $50.90\,\text{nW}$ @ $20\,\text{kHz}$ ($41.62\,\text{nW}$ baseline, net overhead $+9.28\,\text{nW}$).

---

## ADR-014: Non-Invasive AMBA APB4 Bus Wrapper for SoC Integration (Milestone M7)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Untuk mendukung integrasi ke mikrokontroler aman Peruri dan prosesor RISC-V/ARM, dibuat modul pembungkus bus AMBA APB4 (`ares_sentinel_apb.v`) di direktori `integration/` tanpa memodifikasi satu baris pun kode pada 7 modul inti Verilog di `ares_sentinel/` yang telah disegel.

---

## ADR-015: Nanosecond-Calibrated RP2040 Benchtop Post-Silicon Test Harness (Milestone M7)
- **Status**: Approved
- **Tanggal**: 2026-09-27
- **Keputusan**: Validasi fisik silikon SkyWater 130nm TT08 dirancang menggunakan controller Raspberry Pi Pico (RP2040) dengan mesin Programmable I/O (PIO) untuk menghasilkan stimulus transmisi terkalibrasi nanodetik dan injeksi glitch terkontrol di laboratorium.
