# ARES-RX Sentinel — Paparan Teknis untuk Tim Evaluator Peruri
## Desain Sirkuit Terpadu (IC) Pengaman Demarkasi Sinyal Sub-GHz untuk Infrastruktur IoT Kritis Peruri

---

# SLIDE 1: COVER & IDENTITAS PROYEK

### ARES-RX Sentinel: Silicon-Level Trusted Digital Reception Boundary
**Desain Sirkuit Terpadu (IC) Pengaman Demarkasi Sinyal Sub-GHz untuk Infrastruktur IoT Kritis Peruri**

* **Produk:** ARES-RX Sentinel (Hardware Security Integrated Circuit)
* **Organisasi Pengembang:** ARES Semikonduktor Teknologi
* **Tanggal:** 28 September 2026
* **Target Manufaktur:** Tiny Tapeout TT08 Shuttle (Proses Fabrikasi SkyWater 130nm CMOS `sky130_fd_sc_hd`)
* **Status Desain & Verifikasi:**
  - RTL Source Core (M0–M4): **FROZEN & SEALED** (7 modul synthesizable Verilog, hash 3-arah identik)
  - Physical Tapeout Layout (M5): **SEALED / INTERNALLY QUALIFIED** (Git commit `a748738cf665e63bc9c215748ee5bead18422665`)
  - Cyber-Physical Evidence (M6): **SEALED** (Run ID `WO011R1-FINAL-20260927-225358`)
* **Status Fabrikasi Silikon:** **TT08 Fabrication PENDING** (Silikon fisik belum tersedia / pre-silicon)
* **Status Portal Tiny Tapeout:** **PENDING** (Menunggu pembukaan dan penyerahan portal resmi)
* **Audiens Sasaran:** Dewan Evaluator Teknis, Tim Audit Keamanan Perangkat Keras, dan Tim Rekayasa Sistem Siber-Fisik Perum Percetakan Uang Republik Indonesia (Peruri)

*Sumber: Dokumen Tata Kelola Proyek ARES Semikonduktor (WO-2026-M5F-AUDIT-002 & WO-2026-M6-QC-012)*

---

# SLIDE 2: LATAR BELAKANG ANCAMAN: KERENTANAN SUB-GHz RECEIVER

### Kerentanan Fundamental Sinyal Baseband pada Frekuensi Sub-GHz (433.92 MHz)

* **Konteks Operasional Peruri:**
  - Komunikasi nirkabel Sub-GHz (khususnya pita ISM 433.92 MHz) digunakan secara luas pada infrastruktur kritis: smart meter utilitas nasional, perangkat pelacak logistik dokumen sekuriti berharga, dan sensor telemetri fasilitas pencetakan uang.
  - Sifat propagasi gelombang Sub-GHz memiliki jangkauan jauh dan daya tembus struktural tinggi, menjadikannya sasaran empuk interferensi dan manipulasi fisik dari jarak jauh.

* **Tiga Kategori Ancaman Fisik & Protokol:**
  1. **Physical Glitch & Runt Pulses:** Pulsa liar berdurasi sangat sempit ($\le 7$ siklus clock nominal) yang diinduksikan ke jalur sinyal digital `rx_in` melalui interferensi elektromagnetik (EMI) atau injeksi pulsa aktif (glitching).
  2. **Clock Desynchronization & Mid-Band Jitter:** Pergeseran durasi pulsa Manchester (11 hingga 15 siklus clock nominal) akibat instabilitas osilator pengirim atau serangan desinkronisasi bertahap yang mengacaukan pemulihan data (clock recovery).
  3. **Adversarial Frame Injection:** Injeksi paket liar dengan manipulasi field pembuka (preamble), pengenal tipe protokol (protocol type ID), maupun pemalsuan panjang muatan (frame truncation atau frame overrun).

* **Celah Struktural Analog Front-End (AFE) Komersial:**
  - Chip penerima radio komersial (demodulator analog RF) dirancang hanya untuk demodulasi gelombang elektromagnetik menjadi aliran pulsa digital biner CMOS.
  - Demodulator **tidak memiliki logika validasi keamanan**. Pulsa derau, glitch liar, dan frame manipulatif diteruskan langsung ke pin GPIO mikrokontroler host tanpa penyaringan demarkasi di tingkat silikon.

*Sumber: Analisis Ancaman Siber-Fisik ARES & Model Ancaman Peruri (PERURI_CYBER_PHYSICAL_DEMO_DOSSIER.md Bab 1)*

---

# SLIDE 3: PERNYATAAN MASALAH: KEGAGALAN VALIDASI BERBASIS SOFTWARE

### Mengapa Parser Protokol Berbasis Perangkat Lunak pada Host MCU Tidak Memadai?

* **Keterbatasan Paradigma Software Validator:**
  Pada arsitektur konvensional, mikrokontroler host (Host MCU) mengandalkan rutin perangkat lunak (firmware ISR / parser) untuk membaca sinyal baseband. Pendekatan ini rentan terhadap empat kegagalan katastropik:

  1. **Interrupt Storm (Badai Interupsi) & CPU Exhaustion:**
     - Injeksi pulsa glitch berfrekuensi tinggi memicu interupsi perangkat keras eksternal (EXTI ISR) pada MCU secara beruntun dalam frekuensi kilohertz hingga megahertz.
     - Mengakibatkan CPU host terperangkap dalam penanganan interupsi (100% CPU utilization), memblokir eksekusi tugas utama, dan menguras cadangan daya baterai dalam hitungan jam (*Denial-of-Service / Power Exhaustion*).
  2. **Buffer Overflow & Memory Bleed:**
     - Aliran paket manipulatif yang terpotong (*truncated*) atau melebihi batas (*overrun* >192 bit) membanjiri alokasi buffer RAM mikrokontroler sebelum fungsi verifikasi checksum software sempat dieksekusi.
  3. **Latensi Komputasi & State Lockup:**
     - Validasi software beroperasi dalam skala waktu mikrodetik hingga milidetik setelah data masuk ke memori host. State machine software rentan terkunci (*deadlock* atau *unhandled exception*) ketika menghadapi anomali transisi biner tak terduga.
  4. **Korupsi Data Tersembunyi (Silent Data Corruption):**
     - Desinkronisasi bitstream dapat menghasilkan data cacat yang sempat terbaca oleh aplikasi sebelum kesalahan terdeteksi, berisiko memicu keputusan operasional yang salah pada sistem sekuriti Peruri.

* **Kesimpulan Kebutuhan Arsitektur:**
  Dibutuhkan gerbang pembatas perangkat keras (*hardware security boundary*) mandiri di tingkat silikon yang bertindak sebagai penjaga gerbang (*demarcation gatekeeper*) deterministik sebelum sinyal liar menyentuh bus data atau memicu interupsi prosesor host.

*Sumber: Analisis Batasan Keamanan Perangkat Lunak Host (ARES-RX Sentinel Threat Model & PERURI_CYBER_PHYSICAL_DEMO_DOSSIER.md Bab 1)*

---

# SLIDE 4: ARSITEKTUR SOLUSI: 3-LAYER DEFENCE-IN-DEPTH

### Prinsip Pertahanan Berlapis Mandiri pada Sirkuit Terpadu ($V_{\text{trusted}} = V_{\text{physical}} \land V_{\text{protocol}}$)

* **Layer 1: Temporal Sentinel (`ares_timing_sentinel.v`)**
  - Mengawasi integritas pulsa baseband secara kontinu pada clock $20\,\text{kHz}$ ($T_{\text{clk}} = 50.0\,\mu\text{s}$).
  - Memverifikasi jendela validitas Manchester: *half-bit* ($8 \le N \le 10$ siklus = $400..500\,\mu\text{s}$) dan *full-bit* ($16 \le N \le 20$ siklus = $800..1000\,\mu\text{s}$).
  - Menolak seketika pulsa *runt glitch* ($N \le 7$ siklus), *mid-band desync* ($11 \le N \le 15$ siklus), dan *missing-edge timeout* ($N \ge 21$ siklus).

* **Layer 2: Frame Syntax Monitor FSM (`ares_frame_fsm.v`)**
  - State machine deterministik pemantau tata bahasa protokol frame lengkap ($0..191$ bit).
  - Memvalidasi Preamble ($32\text{'hAAAAAAAA}$), Protocol Type Identifier ($16\text{'hD391}$), dan Constant Header Field ($32\text{'h0DFFFFFE}$).
  - Mengawal batas panjang frame secara ketat tepat 192 bit: mendeteksi dan menolak pemotongan (*truncation underflow* $<192$ bit) maupun kelebihan muatan (*overrun overflow* $>192$ bit).

* **Layer 3: Fail-Closed Isolation Subsystem (`ares_isolation_l3.v`)**
  - Terdiri atas Fault Priority Arbiter (prioritas L1 > L2), Sticky Fault Latch (`ares_fault_latch.v`), dan Zeroization Gate (`ares_isolation_gate.v`).
  - Mengunci status kegagalan dalam $T_{\text{latch}} = 1$ siklus clock ($50.0\,\mu\text{s}$), secara kombinatorial mengunci bus output `uo_out[7:0]` ke `0x00`, dan menyalakan flag interupsi non-maskable `tamper_alert = 1` hingga reset fisik (`rst_n`).

```text
                                  ARES-RX SENTINEL
                     Demodulated Digital Baseband Security Guard
                     
     +-----------------------------------------------------------------------+
     | ui_in[0] (rx_in)                                                      |
     | [Digital Baseband Input from Sub-GHz RF Demodulator - Digital CMOS]   |
     +------------------------------------+----------------------------------+
                                          |
                                          v
     +=======================================================================+
     | LAYER 1: TEMPORAL SENTINEL (ares_timing_sentinel.v)                   |
     |  - Pulse duration & interval counter (20 kHz sampling clock)          |
     |  - Runt Glitch Detection: Pulse width N <= 7 clock cycles             |
     |  - Mid-Band Desync Detection: 11 <= N <= 15 clock cycles              |
     |  - Missing-Edge Detection: Inter-edge interval N >= 21 clock cycles   |
     +------------------------------------+----------------------------------+
                                          | Valid Transitions
                                          v
     +=======================================================================+
     | LAYER 2: FRAME SYNTAX MONITOR FSM (ares_frame_fsm.v)                  |
     |  - Preamble Sync Lock: Strict 32-bit alternating pattern (0xAAAAAAAA) |
     |  - Protocol Type Identifier: Enforces mandatory Type ID (0xD391)      |
     |  - Constant Header Verification: Validates fixed field (0x0DFFFFFE)   |
     |  - Frame Length & Boundary Guard: Exactly 192 bits (bounds check)     |
     |  - Truncation (<192 bits) & Overrun (>192 bits) Trap States          |
     +------------------------------------+----------------------------------+
                                          |
                        +-----------------+-----------------+
                        | Temporal Fault                    | Syntactic Fault
                        v                                   v
     +=======================================================================+
     | LAYER 3: FAIL-CLOSED ISOLATION SUBSYSTEM                              |
     |  [Priority Fault Arbiter & Sticky Hardware Latch]                     |
     |  (ares_fault_arbiter.v, ares_fault_latch.v, ares_isolation_gate.v)    |
     |                                                                       |
     |  +-----------------------------------------------------------------+  |
     |  | Deterministic 1-Cycle Fault Latch (T_latch = 1 cycle / 50.0 us) |  |
     |  | Combinational Zeroization (T_isolate ~ 1.2 ns gate delay model) |  |
     |  +-----------------------------------------------------------------+  |
     +--------------------+-----------------------------+--------------------+
                          |                             |
                          | Clean Frame                 | Latched Fault
                          v                             v
           +------------------------------+   +------------------------------+
           | Parallel Safe Bus: uo_out[7:0]|   | Tamper Flag:  uio_out[6]     |
           | [Verified Payload to MCU]    |   | [Non-Maskable Hardware Alert]|
           | (On Fault: Bus = 8'h00)      |   | (Asserted = 1 until rst_n)   |
           +------------------------------+   +------------------------------+
```

*Sumber: Arsitektur RTL Tersegel M4 & 05_ASIC_Synthesis/tt08_submission_repo/README.md Bagian 3*

---

# SLIDE 5: SPESIFIKASI SILIKON & METRIK PASCA-LAYOUT

### Karakterisasi Fisik, Area, Timing, dan Daya pada SkyWater 130nm

| Parameter / Metrik Fisik | Nilai Desain Tersegel | Keterangan & Dasar Metodologi |
| :--- | :--- | :--- |
| **Teknologi Proses** | SkyWater 130nm High-Density CMOS | Standard cell library `sky130_fd_sc_hd`, tegangan inti $1.80\,\text{V}$ |
| **Format Die / Slot TT08** | $1 \times 1$ Standard Tile | Dimensi: $161.00\,\mu\text{m} \times 111.52\,\mu\text{m}$ (Luas total gross: $17,954.72\,\mu\text{m}^2$) |
| **Jumlah Gerbang Logika** | 758 standard cells | 741 sel logika movable + 17 clock tree buffers (Netgen: 764 devices termasuk tapcells) |
| **Luas Area Sel Standar** | $6,477.46\,\mu\text{m}^2$ | Utilisasi sel logika murni: $36.08\%$ dari total gross tile ($49.1\%$ core area) |
| **Sel Proteksi Fisik** | 225 tapcells, 78 endcaps, 1,547 fillers | Jarak substrate tapcell $\le 14\,\mu\text{m}$ (anti-latchup), 1,547 filler cells untuk densitas DRC |
| **Frekuensi Operasi** | $F_{\text{nom}} = 20\,\text{kHz}$ / $F_{\max} \approx 123.7\,\text{MHz}$ | Frekuensi kerja nominal $20\,\text{kHz}$; analisis OpenSTA sign-off mampu hingga $\approx 123.7\,\text{MHz}$ |
| **Setup Slack (@ 50 MHz Stress)**| **$+11.88\,\text{ns}$** (MET, $WNS = 0.00\,\text{ns}$) | Margin timing setup sangat lapang bahkan pada pengujian stres $2,500\times$ di atas nominal |
| **Hold Slack (@ 50 MHz Stress)** | **$+0.42\,\text{ns}$** (MET) | Bebas pelanggaran hold timing pada seluruh sudut proses (process corners) |
| **Routing Geometri** | Wirelength: $19,988\,\mu\text{m}$, Vias: 5,970 | Total panjang lintasan interkoneksi logam pasca-Detailed Routing |
| **Aturan Desain & Skematik** | **DRC: 0 active violations** \| **LVS: 100% Match** | 0 pelanggaran aktif di bawah kebijakan waiver rekayasa internal; 764/764 devices cocok sempurna |
| **Estimasi Daya Primer (Otoritatif)**| **57.90 nW @ 20 kHz ($1.80\,\text{V}$)** | **Authoritative post-route VCD-workload-derived power estimate (OpenSTA Scenario B, $\alpha=0.1418$)** |
| **Estimasi Daya Sekunder** | **50.90 nW @ 20 kHz ($1.80\,\text{V}$)** | **Secondary static activity sweep estimate (Scenario A, $\alpha=0.075$, dipertahankan di `docs/info.md`)** |

* **KEPATUHAN ATURAN EPISTEMIK DAYA (POWER EPISTEMIC RULE - MUTLAK):**
  - **Angka 57.90 nW adalah estimasi daya simulasi pasca-layout berbasis beban kerja VCD otentik (`ares_sentinel_integrated.vcd`), BUKAN pengukuran daya silikon terfabrikasi.**
  - **Pengukuran daya silikon = NOT AVAILABLE / BELUM TERSEDIA.**
  - **Fabrikasi silikon fisik = TT08 PENDING (Menunggu pencetakan wafer SkyWater 130nm).**
  - Overhead daya keamanan: Hanya $+12.70\,\text{nW}$ ($+28.1\%$) di atas demodulator baseline tanpa proteksi ($45.20\,\text{nW}$).

* **Pemetaan Antarmuka Pin I/O (Sesuai `info.yaml`):**
  - *Dedicated Inputs (`ui_in`):* `ui[0]` = `rx_in` (masukan digital CMOS baseband, bukan antena RF); `ui[2]` = `halt`; `ui[7:4]` = `address[3:0]`.
  - *Dedicated Outputs (`uo_out`):* `uo[7:0]` = `data_out[7:0]` (Parallel Safe Payload Bus, dikunci ke `0x00` saat tamper).
  - *Dedicated Bidirectional (`uio_out`, `uio_oe = 0xFF`):* `uio[0]` = `baseline_full`; `uio[1]` = `manchester_clock`; `uio[2]` = `manchester_data`; `uio[3]` = `transmission_begin`; `uio[4]` = `base_neg_edge`; `uio[5]` = `base_pos_edge`; `uio[6]` = `tamper_alert` (flag non-maskable); `uio[7]` = `reception_active`.

*Sumber: M5 Post-Route Sign-off Report, power_reconciliation.md (ARES-ASIC-M5F-PWR-001), dan info.yaml*

---

# SLIDE 6: METODOLOGI VERIFIKASI M6: CYBER-PHYSICAL DEMONSTRATOR

### Pembuktian Kausalitas Ujung-ke-Ujung ($P \rightarrow C \rightarrow B \rightarrow R$) dalam Lingkungan Terisolasi

* **Tujuan Pengujian M6:**
  Membuktikan bahwa proteksi ARES-RX Sentinel bekerja secara kausal tanpa putus: mulai dari penerimaan paket jaringan riil pada kernel Linux, diterjemahkan menjadi sinyal baseband fisik, dieksekusi siklus-demi-siklus pada RTL synthesizable, hingga penutupan gerbang isolasi perangkat keras dan pencatatan buku besar forensik.

* **Empat Tahapan Rantai Kausal ($P \rightarrow C \rightarrow B \rightarrow R$):**
  1. **Packet Ingress (P):** Paket UDP riil dikirim melintasi batas jaringan kernel Linux emulasi RF ($H_{\text{packet}}$).
  2. **Canonical Profile Decoding (C):** Muatan didekodekan menjadi profil urutan transisi siklus kanonik ($H_{\text{canonical}}$).
  3. **Baseband Signal Reconstruction (B):** Rekonstruksi biner sinyal pulsa per-siklus `(rx_in, serial_clock, serial_data)` ($H_{\text{baseband}}$).
  4. **In-Line RTL Co-Simulation (R):** Eksekusi langsung ke simulator RTL synthesizable Verilog (`iverilog`/`vvp`) untuk mengevaluasi 11 sinyal observable ($H_{\text{rtl}}$).

* **Topologi Jaringan Linux Terisolasi (Dual Network Namespaces):**
  - Namespace Penyerang (`ns_attacker`, IP `192.168.100.10`) dan Penerima (`ns_receiver`, IP `192.168.100.20`) dihubungkan melalui virtual bridge `br_ares`.
  - Emulasi latensi fisik RF menggunakan Linux Traffic Control (`tc netem delay 5.0ms ± 1.2ms`).
  - Latensi tempuh jaringan terukur: $2.186\,\text{ms} - 7.668\,\text{ms}$ (rata-rata $5.697\,\text{ms}$), selaras dengan distribusi stokastik Gaussian.

```text
[ns_attacker] ---> [br_ares: tc netem delay 5.0ms ± 1.2ms] ---> [ns_receiver: Packet Ingress]
                                                                        |
  +---------------------------------------------------------------------+
  v
[ Invariant C: Decode Ingress Packet -> Canonical Profile (H_canonical) ]
  |
  v
[ Invariant D: Reconstruct Baseband Signal Pulse Stream (H_baseband) ]
  |
  v
[ In-Line Synthesizable RTL Co-Simulation (vvp) -> Observable Vector O_RTL(n) (H_rtl) ]
  |
  v
[ Invariant E: Fault Latch (T_latch = 1 cycle) & Isolate (T_isolate = 0 cycles RTL) -> Bus Safe ]
  |
  v
[ Cryptographic Chained Ledger Entry (H_record) -> Final Anchor: 6f0d379d... ]
```

*Sumber: PERURI_CYBER_PHYSICAL_DEMO_DOSSIER.md Bab 4 & 5 (M6 Testbed Architecture)*

---

# SLIDE 7: HASIL VERIFIKASI: 9 VEKTOR KANONIK & 100% TRACE CONCORDANCE

### Evaluasi Empiris Komprehensif: 10,737 Siklus Clock & 118,107 Evaluasi Sinyal Tanpa Deviasi

* **Matriks 9 Kategori Vektor Serangan Kanonik (AV00–AV08):**

| ID Vektor | Kategori Stimulus | Parameter Anomali yang Diinjeksikan | Total Siklus | Siklus Pemicu | Siklus Latch | Status Tamper | Status Bus Data | Vonis Keamanan |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **AV00** | Transmisi Sah (Nominal) | Paket 433 MHz standar, preamble valid | 1,876 | N/A | N/A | `0` (Aman) | `0x55` (Valid) | `ACCEPTED_NOMINAL` |
| **AV01** | L1: Runt Glitch Attack | Lebar pulsa $N \le 7$ siklus ($N=4$) | 87 | 79 | 80 | `1` (Aktif)| `0x00` (Isolasi)| `MITIGATED_TRAPPED` |
| **AV02** | L1: Mid-Band Clock Desync | Lebar pulsa $11 \le N \le 15$ ($N=12$) | 96 | 88 | 89 | `1` (Aktif)| `0x00` (Isolasi)| `MITIGATED_TRAPPED` |
| **AV03** | L1: Missing-Edge Dropout | Jeda antar-tepi $N \ge 21$ siklus | 117 | 109 | 110 | `1` (Aktif)| `0x00` (Isolasi)| `MITIGATED_TRAPPED` |
| **AV04** | L2: Preamble Corruption | Pola preamble dirusak ($\ne \text{0xAAAAAAAA}$) | 1,876 | 178 | 179 | `1` (Aktif)| `0x00` (Isolasi)| `MITIGATED_TRAPPED` |
| **AV05** | L2: Malformed Type ID | Protocol Type ID dirusak ($\ne \text{0xD391}$) | 1,876 | 448 | 449 | `1` (Aktif)| `0x00` (Isolasi)| `MITIGATED_TRAPPED` |
| **AV06** | L2: Constant Header Corrupt | Header tetap dirusak ($\ne \text{0x0DFFFFFE}$) | 1,876 | 763 | 764 | `1` (Aktif)| `0x00` (Isolasi)| `MITIGATED_TRAPPED` |
| **AV07** | L2: Frame Truncation | Pemotongan muatan ($< 192$ bit) | 1,048 | 1040 | 1041 | `1` (Aktif)| `0x00` (Isolasi)| `MITIGATED_TRAPPED` |
| **AV08** | L2: Frame Overrun | Kelebihan muatan bit ($> 192$ bit) | 1,885 | 1816 | 1817 | `1` (Aktif)| `0x00` (Isolasi)| `MITIGATED_TRAPPED` |

* **Statistik Konkordansi & Latensi Mitigasi:**
  - **Total Siklus Diskrit yang Dievaluasi:** $10,737\,\text{siklus}$ clock ($536.85\,\text{ms}$ waktu eksekusi logika).
  - **Evaluasi Sinyal Observable (11 Sinyal per Siklus):** $118,107\,\text{evaluasi}$ sinyal mandiri.
  - **Tingkat Konkordansi Jejak (Trace Concordance):** **100.0%** ($118,107 / 118,107$ sinyal cocok sempurna antara model perilaku referensi dan RTL synthesizable).
  - **Latensi Penguncian Sinyal ($T_{\text{latch}}$):** Tepat 1 siklus clock ($50.0\,\mu\text{s}$) pada abstraksi register sinkron.
  - **Latensi Isolasi Kombinatorial ($T_{\text{isolate}}$):** 0 siklus tambahan pada RTL (model keterlambatan gerbang OpenSTA $\approx 1.2\,\text{ns}$).
  - **Behavioral Mutation Testing:** Mutan M1 (ambang timing diubah), M2 (konstanta dimodifikasi), M3 (gerbang isolasi dilewati) seluruhnya $100\%$ terdeteksi dan terjebak (*100% trap rate*).

* **Identitas Eksekusi & Anchor Kriptografis Akhir:**
  - **Authoritative Execution Run ID:** `WO011R1-FINAL-20260927-225358`
  - **Final Cryptographic Ledger Anchor:**
    `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0`

*Sumber: M6 Unified Evidence Ledger (m6_unified_evidence_ledger.jsonl) & PERURI_CYBER_PHYSICAL_DEMO_DOSSIER.md Bab 2 & 6*

---

# SLIDE 8: CHAIN-OF-CUSTODY KRIPTOGRAFIS & KONTRAK SERIALISASI

### Taksonomi Hash Pembuktian Forensik Anti-Pemalsuan (Tamper-Evident Hash Chaining)

* **Taksonomi 5 Hash Provenance Primer + 1 Hash Diagnostik Auxiliary:**
  1. $H_{\text{canonical}}$: SHA-256 spesifikasi profil stimulus pada manifes kanonik.
  2. $H_{\text{packet}}$: SHA-256 byte mentah paket UDP jaringan (menjamin integritas muatan ingress).
  3. $H_{\text{baseband}}$: SHA-256 byte terurut biner baseband:
     $$B_{\text{baseband}} = \text{UTF-8}\left(\prod_{n=0}^{N-1} (rx\_in_n \mathbin{\text{" "}} s\_clk_n \mathbin{\text{" "}} s\_data_n \mathbin{\text{"\textbackslash n"}})\right)$$
     Bertindak sebagai **Identitas Stimulus Primer** (terbukti unik tanpa collision pada ke-9 vektor kanonik).
  4. $H_{\text{rtl}}$: SHA-256 dari seluruh urutan vektor observable 11-sinyal $O_{\text{RTL}}(n)$ per siklus.
  5. $H_{\text{record}}$: SHA-256 perantaian rekaman buku besar forensik (*chained ledger record hash*).
  6. $H_{\text{rxin}}$ *(Auxiliary Diagnostic):* SHA-256 runtutan bit transisi pulsa pembawa carrier pada pin `rx_in`.

* **Kontrak Serialisasi Byte Eksplisit:**
  Setiap baris rekaman pada buku besar M6 dirantai secara kriptografis menggunakan aturan serialisasi deterministik:
  $$H_{\text{record}, i} = \operatorname{SHA-256}\Big(\operatorname{UTF-8}\big(H_{\text{record}, i-1} \mathbin{\Vert} \operatorname{JSON}_{\text{canonical}}(\text{Payload}_i)\big)\Big)$$
  dengan fungsi $\operatorname{JSON}_{\text{canonical}} = \text{json.dumps(sort_keys=True, separators=(',', ':'))}$.

* **Jaminan Integritas Rantai Bukti:**
  - Titik Awal Rantai (Genesis Hash): 64 karakter heksadesimal `'0'` ($0000000000000000\dots00000000$).
  - Titik Akhir Rantai (Final Anchor): `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0`.
  - Seluruh alur pembuktian kebal terhadap manipulasi urutan (*zero out-of-order execution*), penyisipan rekaman palsu, maupun penghapusan bukti pengujian.

*Sumber: Spesifikasi Kriptografi M6-QC-012 & PERURI_CYBER_PHYSICAL_DEMO_DOSSIER.md Bab 4 & 6*

---

# SLIDE 9: BATASAN EPISTEMIK (EPISTEMIC BOUNDARIES)

### Prinsip Transparansi Ilmiah dan Batasan Validasi Desain Semikonduktor

* **Aksioma Epistemik Inti:**
  ```text
  M6 Evidence Sealed ≠ Tiny Tapeout Portal Accepted ≠ Silicon Validated
  Bukti M6 Tersegel ≠ Diterima Portal Tiny Tapeout ≠ Tervalidasi Silikon
  ```

* **Apa yang SUDAH Dibuktikan Secara Ilmiah (*Bounded Empirical Evidence*):**
  - **Verifikasi Fungsional Terikat:** Konkordansi 100% pada 9 kategori serangan kanonik AV00–AV08 terhadap model RTL synthesizable M4.
  - **Kausalitas Siber-Fisik Ujung-ke-Ujung:** Rantai kausalitas $P \rightarrow C \rightarrow B \rightarrow R$ terbukti lengkap dan terkunci dalam ledger forensik berantai SHA-256.
  - **Karakterisasi Daya Pasca-Layout Deterministik:** Nilai $57.90\,\text{nW} @ 20\,\text{kHz}$ dihasilkan melalui simulasi OpenSTA pasca-route dengan parasitik SPEF di bawah switching activity VCD otentik.
  - **Kesesuaian Tata Letak Fisik Silikon:** LVS bersih 100% (758/758 instance cocok) dan DRC 0 pelanggaran aktif (di bawah waiver rekayasa proyek).

* **Apa yang BELUM Tersedia dan TIDAK Boleh Diklaim:**
  - **Pengukuran Daya Silikon Fisik:** **NOT AVAILABLE / BELUM TERSEDIA**. Tidak ada angka daya yang boleh diklaim sebagai hasil ukur laboratorium pada wafer/chip nyata.
  - **Fabrikasi Chip Fisik:** **TT08 PENDING**. Keping silikon fisik belum diproduksi di pabrik semikonduktor SkyWater.
  - **Penerimaan Portal Tiny Tapeout:** **PENDING**. Penyerahan resmi ke portal Tiny Tapeout masih menunggu jadwal upstream.
  - **Persetujuan / Sertifikasi Peruri:** **NOT CLAIMED / TIDAK DIKLAIM**. Paparan ini merupakan laporan pembuktian teknis dan proposal inovasi untuk dievaluasi oleh Dewan Evaluator Peruri, bukan sertifikasi kelulusan resmi Peruri.

*Sumber: Dokumen Batasan Epistemik Proyek ARES Semikonduktor (ORIGINAL_REQUEST.md & WO-2026-M6-QC-012)*

---

# SLIDE 10: GATE A LVS & GATE B INTERNAL CI PROVENANCE

### Kualifikasi Fisik Silikon dan Rekam Jejak Integrasi Berkelanjutan Jarak Jauh

* **Gate A — Hierarchical Layout vs. Schematic (LVS) Sign-off:**
  - **Alat Ekstraksi:** Netgen 1.5.133 terhadap netlist transistor SPICE SkyWater 130nm (`sky130_fd_sc_hd`).
  - **Hasil Evaluasi Struktural:**
    - 764/764 perangkat fisik (termasuk tapcells) cocok sempurna ($100.0\%$).
    - 776/776 net interkoneksi cocok sempurna ($100.0\%$).
    - 45/45 port pin I/O cocok tanpa ketidaksesuaian.
    - Status Log Resmi: `Circuits match uniquely.`
  - **Status Gate A:** **CLOSED / INTERNALLY QUALIFIED** (Desain tata letak fisik identik secara struktural dengan skematik gerbang logika).

* **Gate B — Internal Remote Continuous Integration (CI) Provenance:**
  - **Alur Kerja GitHub Actions Jarak Jauh:**
    1. Workflow Sintesis & Precheck GDS (`.github/workflows/gds.yaml`): **Remote CI Run ID: `36320019363`** (Status: PASS).
    2. Workflow Uji Fungsional & Injeksi Glitch (`.github/workflows/test.yaml`): **Remote CI Run ID: `36320019357`** (Status: PASS).
  - **Peran Pembuktian:** Membuktikan bahwa seluruh alur kerja sintesis OpenROAD, ekstraksi parasitik, pengecekan precheck Tiny Tapeout, dan eksekusi testbench Cocotb dapat direproduksi secara mandiri pada runner cloud bersih.
  - **Kualifikasi Epistemik Wajib:**
    - Kedua eksekusi CI ini mencatat **provenance remote CI internal proyek**.
    - Keduanya **BUKAN tanda terima penerimaan portal Tiny Tapeout**, dan **BUKAN sign-off foundry resmi dari SkyWater Technology**.

*Sumber: Laporan Gate A LVS (Netgen 1.5.133) & Gate B GitHub Actions CI Runs (36320019363, 36320019357)*

---

# SLIDE 11: STATUS TAPEOUT & KESIAPAN PABRIKASI

### Matriks Kesiapan Siklus Hidup Desain ARES-RX Sentinel

| Fase Siklus Hidup | Milestone Proyek | Status Kualifikasi | Catatan Audit & Hash Manifes |
| :--- | :--- | :---: | :--- |
| **RTL Source Core** | M0–M4 Synthesizable RTL | **FROZEN & SEALED** | 7/7 modul synthesizable Verilog identik 100% pada audit hash 3-arah (`verify_m4_hashes.py`) |
| **Physical Layout** | M5 Tapeout Hardening | **SEALED / QUALIFIED** | Git commit `a748738cf665e63bc9c215748ee5bead18422665` (GDS, DEF, SPEF, Verilog gate netlist) |
| **Cyber-Physical** | M6 Evidence Package | **SEALED** | Run ID `WO011R1-FINAL-20260927-225358` (Anchor: `6f0d379d...`) |
| **Internal CI** | Gate A LVS & Gate B CI | **PASSED** | Netgen 100% match, GitHub Actions Runs `36320019363` & `36320019357` |
| **Portal Submission**| Tiny Tapeout TT08 Portal | **PENDING** | Berkas siap diunggah; menunggu pembukaan portal resmi upstream |
| **Manufaktur Wafer** | Fabrikasi SkyWater 130nm | **PENDING** | Menunggu jadwal penutupan shuttle TT08 dan fabrikasi wafer fisik |
| **Uji Laboratorium** | Pengukuran Silikon Nyata | **NOT AVAILABLE** | Pengukuran daya dan karakterisasi fisik akan dilakukan pasca-penerimaan chip |

* **Tata Kelola & Immutability Guardrail:**
  - Seluruh artefak inti (RTL, GDS, DEF, SPEF, berkas manifes M5, dan ledger M6) dilindungi aturan tata kelola mutlak anti-modifikasi.
  - File metadata katalog `docs/info.md` (hash `0888d516...`) dan `info.yaml` (hash `a20b570e...`) tersegel aman di bawah pengawasan kriptografis.

*Sumber: Matriks Sign-Off Formal Proyek (PERURI_CYBER_PHYSICAL_DEMO_DOSSIER.md Bab 8)*

---

# SLIDE 12: KESIMPULAN & REKOMENDASI UNTUK EVALUATOR PERURI

### Nilai Strategis bagi Peruri dan Rencana Tindak Lanjut Evaluasi

* **Tiga Kesimpulan Teknis Utama:**
  1. **Proteksi Otonom Tingkat Silikon:** ARES-RX Sentinel membuktikan bahwa pertahanan deterministik pada lapisan fisik mampu menghentikan serangan glitch, desinkronisasi, dan injeksi frame dalam 1 siklus clock ($50.0\,\mu\text{s}$), melenyapkan ancaman *interrupt storm* dan *buffer overflow* pada host MCU secara tuntas.
  2. **Efisiensi Energi Ekstrem (Ultra-Low Power):** Estimasi daya pasca-layout sebesar $57.90\,\text{nW} @ 20\,\text{kHz}$ (dengan overhead keamanan hanya $+12.70\,\text{nW}$) membuktikan bahwa proteksi siber-fisik tingkat tinggi dapat diterapkan pada perangkat berbasis baterai koin atau pemanen energi tanpa mengorbankan masa pakai operasional perangkat Peruri.
  3. **Transparansi & Bukti Forensik Kriptografis:** Seluruh pengujian didukung oleh rantai bukti matematis berantai SHA-256 yang kebal manipulasi, memungkinkan audit independen dengan kepastian absolut.

* **Tiga Rekomendasi Tindak Lanjut untuk Tim Evaluator Peruri:**
  1. **Pelaksanaan Audit Forensik Mandiri:**
     - Menjalankan skrip verifikator independen (`independent_causal_verifier.py`) untuk memverifikasi keaslian dan kontinuitas rantai hash buku besar M6 secara langsung pada workstation audit Peruri.
  2. **Persiapan Fasilitas Uji Fisik Hardware-in-the-Loop (HIL) Bersama Pasca-Fabrikasi (M6-C):**
     - Mempersiapkan instrumen laboratorium dan papan uji (test bench PCB) untuk pengujian bench test fisik bersama segera setelah keping fisik silikon TT08 diterima dari pabrikasi SkyWater.
  3. **Penyusunan Rencana Integrasi Blok IP Peruri:**
     - Mempertimbangkan adopsi blok sirkuit ARES-RX Sentinel sebagai modul IP standar proteksi perangkat keras pada meteran pintar utilitas nasional, perangkat pembaca dokumen sekuriti, dan gateway IoT Peruri generasi berikutnya.

*Sumber: Rekomendasi Arsitektural ARES Semikonduktor untuk Peruri (WO-2026-M6-QC-012 Bab 8)*
