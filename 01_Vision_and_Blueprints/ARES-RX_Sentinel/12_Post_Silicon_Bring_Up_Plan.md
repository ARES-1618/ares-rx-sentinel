# ARES-RX Sentinel — Post-Silicon Bring-Up & Validation Specification
## Document: `01_Vision_and_Blueprints/ARES-RX_Sentinel/12_Post_Silicon_Bring_Up_Plan.md`
**Classification:** Post-Tapeout Engineering Specification (Milestone M7 / TRL-7 Silicon Validation)  
**Target Platform:** Tiny Tapeout TT08 SkyWater 130nm ASIC Test Coupon  
**Status:** Approved by Technical Architect  
**Author:** ARES Semiconductor Engineering Team  

---

## 1. Tujuan & Ruang Lingkup Validasi Silikon

Rencana ini menetapkan metodologi pengujian laboratorium fisik (*benchtop bring-up*) untuk memvalidasi die silikon **ARES-RX Sentinel** yang difabrikasi melalui program **Tiny Tapeout TT08** pada proses **SkyWater 130nm High-Density** (`sky130_fd_sc_hd`).

### Sasaran Utama:
1. **Validasi Fungsional Fisik**: Membuktikan bahwa sirkuit logika diskrit pada wafer silikon bekerja identik dengan simulasi RTL dan *post-route* netlist (reproduksi 100% dari 6 skenario demo hardware).
2. **Karakterisasi Batas Waktu ($V_{\text{physical}}$)**: Mengukur akurasi deteksi glitch durasi mikro ($N \le 7$ siklus) dan kepatuhan jendela Manchester ($N_{\text{HB}} \in [8..10]$, $N_{\text{BIT}} \in [16..20]$) terhadap variasi tegangan ($1.62\,\text{V} - 1.98\,\text{V}$) dan suhu laboratorium ($0^\circ\text{C} - 70^\circ\text{C}$).
3. **Pengukuran Konsumsi Daya Fisik**: Mengukur disipasi daya statis (*leakage*) dan dinamis pada clock $20\,\text{kHz}$ dan $50\,\text{MHz}$ untuk memverifikasi model estimasi daya ($50.90\,\text{nW}$ @ $20\,\text{kHz}$).
4. **Verifikasi Kecepatan Maksimum ($F_{\max}$)**: Melakukan *frequency sweep* dari $20\,\text{kHz}$ hingga $\ge 100\,\text{MHz}$ untuk membuktikan setup timing margin $+11.88\,\text{ns}$.

---

## 2. Arsitektur Benchtop Test Setup

```text
+---------------------------------------------------------------------------------------+
|                              LABORATORY BENCHTOP HARNESS                              |
|                                                                                       |
|   [Host PC / Control Terminal]                                                        |
|   * Python Test Automation Script                                                     |
|   * CSV Telemetry Logger & Waveform Capture                                           |
|         │                                                                             |
|         │ USB-UART / High-Speed SPI (12 Mbps)                                         |
|         ▼                                                                             |
|   [Test Controller: Raspberry Pi Pico / RP2040]                                       |
|   * Dual ARM Cortex-M0+ Core @ 133 MHz                                                |
|   * PIO (Programmable I/O) State Machine:                                             |
|     - Nanosecond-accurate Manchester pulse generator (Stimulus)                       |
|     - Calibrated glitch injector (10 ns resolution)                                   |
|     - Synchronous 20 kHz master clock driver                                          |
|         │                                                                             |
|         ├────────────────────────────────────────┐                                    |
|         │ Stimulus & Control                     │ Telemetry Monitor                  |
|         ▼                                        ▼                                    |
|   [Tiny Tapeout TT08 Demo Board Carrier]   [Logic Analyzer: Saleae Pro 16]            |
|   * DIP Switch & Header Matrix             * 500 MS/s Real-Time Capture               |
|   * ZIF Socket / QFN Carrier Tile          * Channels:                                |
|     - Pin ui_in[0]  : rx_digital stimulus    - Ch 0: clk (20 kHz)                     |
|     - Pin ui_in[7:4]: address bus            - Ch 1: rx_in (stimulus)                 |
|     - Pin uo_out[7:0]: safe_data_out         - Ch 2: tamper_alert (uio[6])            |
|     - Pin uio_out[6]: tamper_alert           - Ch 3: reception_active (uio[7])        |
|     - Pin uio_out[7]: reception_active       - Ch 4..11: uo_out[7:0]                  |
|                                                                                       |
|   [Precision Source Measure Unit (SMU): Keithley 2450 / Nordic PPK2]                 |
|   * VDD Core Supply: 1.800 V ± 1 mV                                                   |
|   * Current Measurement Sensitivity: 10 pA - 100 mA                                   |
|   * Power Logging @ 100 kSps Sampling Rate                                            |
+---------------------------------------------------------------------------------------+
```

---

## 3. Pemetaan Pin Fisik & Konfigurasi Sinyal (TT08 Carrier)

| Nama Pin TT08 | Jenis | Sinyal Internal ARES | Fungsi pada Test Bench |
| :--- | :--- | :--- | :--- |
| `clk` | Input | Master Clock ($20\,\text{kHz} - 50\,\text{MHz}$) | Digerakkan oleh RP2040 PIO Clock Generator |
| `rst_n` | Input | Asynchronous Active-Low Reset | Kontrol hard reset untuk membersihkan sticky latch |
| `ena` | Input | Chip Enable (Active High) | Dihubungkan ke $V_{\text{DD}}$ ($1.8\,\text{V}$) |
| `ui_in[0]` | Input | `rx_digital` (Baseband Input) | Input pulsa Manchester termodulasi & injeksi glitch |
| `ui_in[7:4]` | Input | `address[3:0]` | Selektor register multiplexer baseline |
| `uo_out[7:0]` | Output| `safe_data_out[7:0]` | Bus paralel 8-bit terlindungi (harus 0x00 saat fault) |
| `uio[0]` | Output| `base_full` | Status frame lengkap dari baseline |
| `uio[1]` | Output| `manchester_clock` | Pulsa clock hasil recover baseline demodulator |
| `uio[2]` | Output| `manchester_data` | Aliran bit hasil demodulasi baseline |
| `uio[3]` | Output| `transmission_begin` | Indikator awal deteksi transmisi |
| `uio[6]` | Output| `tamper_alert` | **Sinyal Kunci**: Interupsi perangkat keras sticky latch |
| `uio[7]` | Output| `reception_active` | **Sinyal Kunci**: Amplop pemantau penerimaan Layer 1 |

---

## 4. Matriks Prosedur Pengujian Laboratorium Fisik

### Prosedur 1: Uji Imunitas Glitch & Batas Waktu Pulsa ($V_{\text{physical}}$)
1. **Tujuan**: Memverifikasi bahwa transisi pulsa di luar jendela diskrit $[8..10] \cup [16..20]$ siklus clock memicu `tamper_alert = 1` seketika.
2. **Langkah Kerja**:
   - Injeksi pulsa stimulus menggunakan RP2040 PIO dengan variasi lebar pulsa $N \in \{1, 2, 4, 7, 8, 9, 10, 11, 13, 15, 16, 18, 20, 21\}$ siklus clock.
   - Ukur latensi respons dari tepi kesalahan pulsa hingga naiknya pin `uio[6]` (`tamper_alert`).
3. **Kriteria Kelulusan**:
   - Pulsa $N \le 7$ dan $11 \le N \le 15$ wajib memicu `tamper_alert = 1` dalam $\le 1$ siklus clock ($50\,\mu\text{s}$ @ $20\,\text{kHz}$).
   - Pulsa nominal $N \in \{8, 9, 10, 16, 17, 18, 19, 20\}$ tidak boleh membunyikan alarm ($FAR = 0\%$).

### Prosedur 2: Uji Isolasi Bus Fail-Closed ($D_{\text{out}} = 0\text{x}00$)
1. **Tujuan**: Membuktikan nol kebocoran data berbahaya (*zero leakage*) pada bus output saat terjadi anomali protokol.
2. **Langkah Kerja**:
   - Kirim frame valid hingga baseline membaca data suhu `0x15` pada `uo_out`.
   - Suntikkan korupsi preamble pada siklus ke-32 atau kirim pulsa ekstra bit ke-193 (*overrun*).
   - Pantau pin `uo_out[7:0]` dengan logic analyzer.
3. **Kriteria Kelulusan**:
   - Pin `uo_out[7:0]` seketika jatuh ke `0x00` pada siklus clock saat kesalahan dideteksi.
   - Sinyal `tamper_alert` tetap terkunci tinggi (`1`) meskipun input `rx_in` kembali tenang, hingga diberi sinyal `rst_n = 0`.

### Prosedur 3: Pengukuran Daya Silikon Riil (Power Profiling)
1. **Tujuan**: Memvalidasi figur daya $50.90\,\text{nW}$ @ $20\,\text{kHz}$ dan efisiensi energi mode siaga.
2. **Langkah Kerja**:
   - Hubungkan pin catu daya $V_{\text{DD}}$ ($1.8\,\text{V}$) ke instrumen Keithley 2450 / Nordic PPK2.
   - Ukur arus diam (*quiescent current*, $I_{\text{DDQ}}$) saat `clk` berhenti.
   - Ukur arus dinamis rata-rata saat memproses transmisi frame nominal 192-bit kontinu pada clock $20\,\text{kHz}$.
3. **Kriteria Kelulusan**:
   - Arus rata-rata operasional pada $20\,\text{kHz} \le 60\,\text{nA}$ ($P \le 108\,\text{nW}$ pada $1.8\,\text{V}$, dengan target nominal $\approx 50.9\,\text{nW}$).

### Prosedur 4: Uji Stres Frekuensi Maksimum ($F_{\max}$)
1. **Tujuan**: Menguji batas kecepatan operasi silikon dan setup margin $+11.88\,\text{ns}$.
2. **Langkah Kerja**:
   - Naikkan frekuensi clock bertahap: $20\,\text{kHz} \rightarrow 1\,\text{MHz} \rightarrow 10\,\text{MHz} \rightarrow 50\,\text{MHz} \rightarrow 100\,\text{MHz} \rightarrow 120\,\text{MHz}$.
   - Eksekusi 6 skenario verifikasi pada setiap tahapan frekuensi.
3. **Kriteria Kelulusan**:
   - Sistem beroperasi tanpa kesalahan komputasi hingga minimal $50\,\text{MHz}$ (clock maksimum Tiny Tapeout).

---

## 5. Rencana Jadwal Eksekusi Pasca-Fabrikasi (Timeline)

| Minggu | Kegiatan Utama | Output & Dokumen |
| :--- | :--- | :--- |
| **W01** | Penerimaan fisik chip TT08 & inspeksi visual mikroskop | Log inspeksi die & kemasan QFN |
| **W02** | Pengujian kontinuitas, resistansi ESD, dan verifikasi $I_{\text{DDQ}}$ | Laporan *sanity check* kelistrikan |
| **W03** | Eksekusi otomatis 6 skenario uji komparatif via RP2040 | Log verifikasi fungsional silikon |
| **W04** | Karakterisasi batas timing, sweeping tegangan, dan $F_{\max}$ | Kurva karakterisasi shmoo plot |
| **W05** | Pengukuran daya ultra-rendah presisi tinggi (SMU) | Laporan perbandingan daya riil vs STA |
| **W06** | Penyusunan Berita Acara Uji Silikon & Rilis Final TRL 7 | Dokumen *Post-Silicon Validation Dossier* |

---

Dokumen ini menjadi acuan operasional laboratorium resmi saat chip fisik ARES-RX Sentinel diterima dari pabrik SkyWater.
