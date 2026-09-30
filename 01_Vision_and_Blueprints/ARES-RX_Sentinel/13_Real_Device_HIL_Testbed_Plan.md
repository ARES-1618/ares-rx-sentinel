# ARES-RX Sentinel — Hardware-in-the-Loop (HIL) Real-Device Testbed Specification
## Document: `01_Vision_and_Blueprints/ARES-RX_Sentinel/13_Real_Device_HIL_Testbed_Plan.md`
**Classification:** Post-Tapeout Physical Integration & Edge Security Testbed (TRL-6 to TRL-7)  
**Target Systems:** ARES-RX Sentinel (ASIC TT08 / FPGA Prototype), ESP32-WROOM-32, Cellular Modem (SIM800L / SIM7600), VLAN Router, & VM Test Orchestrator  
**Status:** Approved Implementation Blueprint  
**Author:** ARES Semiconductor Engineering Team  

---

## 1. Tujuan & Ruang Lingkup Pengujian Nyata

Dokumen ini melengkapi `12_Post_Silicon_Bring_Up_Plan.md` dengan memfokuskan validasi pada integrasi tingkat sistem (*system-level integration*) dan ketahanan siber fisik menggunakan modul komersial (*off-the-shelf components*):

1. **Validasi Isolasi Pra-Demodulasi Real-Time**: Membuktikan bahwa proteksi perangkat keras ARES-RX mampu menyaring anomali sinyal masuk dari kanal nirkabel seluler sebelum menyentuh lapisan software mikrokontroler.
2. **Mitigasi Serangan *Denial-of-Sleep* (Anti-Drain Baterai)**: Memastikan host MCU (ESP32) tetap dalam mode *Deep-Sleep* saat jaringan seluler dibombardir oleh sinyal palsu, menjaga konsumsi daya sistem pada skala microwatt.
3. **Pengujian Isolasi Jaringan (*Hardware & VLAN Boundary*)**: Memastikan kebocoran data berbahaya bernilai nol (*zeroized output 8'h00*) sehingga penyerang dari jaringan luar tidak dapat melakukan lompatan (*pivoting*) antar-segmen VLAN router.

---

## 2. Arsitektur Topologi Testbed

```text
+---------------------------------------------------------------------------------------------------+
|                                  ARSITEKTUR HIL TESTBED TESTBENCH                                  |
|                                                                                                   |
|  +---------------------------------------------------------------------------------------------+  |
|  | [ CLOUD / LAB TEST ENGINE: VIRTUAL MACHINE (VM) ]                                           |  |
|  | - OS: Ubuntu Linux (Bridged / Direct Network Tap)                                           |  |
|  | - Roles:                                                                                    |  |
|  |   1. Telemetry Collector & Command Orchestrator                                             |  |
|  |   2. Attack Vector Injector (Scapy Frame Crafter, Timing Glitch Simulator, Preamble Fuzzer) |  |
|  +---------------------------------------------------------------------------------------------+  |
|                                       │                                                           |
|             ┌─────────────────────────┴────────────────────────┐                                  |
|             │ (Jalur Nirkabel Seluler)                         │ (Jalur Ethernet / TCP-IP)        |
|             ▼                                                  ▼                                  |
|  +----------------------+                           +------------------------------------------+  |
|  | [ CELLULAR MODEM ]   |                           | [ MANAGED ROUTER / SWITCH (VLAN ENGINE)] |  |
|  | - Modul: SIM800L /   |                           | - VLAN 10 (Untrusted / Ingress WAN)      |  |
|  |   SIM7600 LTE / NB-IoT|                           | - VLAN 20 (Quarantine / Raw Probe)       |  |
|  | - SIM Card Aktif     |                           | - VLAN 30 (Trusted Secure Core LAN)      |  |
|  +----------------------+                           +------------------------------------------+  |
|             │                                                  │                                  |
|             │ Raw Baseband / Serial Stream                     │ Managed Uplink                   |
|             ▼                                                  ▼                                  |
|  +---------------------------------------------------------------------------------------------+  |
|  | [ HARDWARE SECURITY GATE: ARES-RX SENTINEL (ASIC TT08 / FPGA TANG NANO 9K / iCE40) ]        |  |
|  | - Always-On Domain: 57.90 nW @ 20 kHz (SkyWater 130nm)                                      |  |
|  | - Input: ui_in[0] (rx_digital bitstream), ui_in[7:4] (Address bus)                         |  |
|  | - Sinyal Pengaman:                                                                          |  |
|  |   * uio_out[6] -> tamper_alert (Active-High Sticky Latch)                                   |  |
|  |   * uio_out[7] -> reception_active / wake_trigger                                           |  |
|  | - Proteksi Data: uo_out[7:0] (Safe Output: 8'h00 jika anomali dideteksi)                    |  |
|  +---------------------------------------------------------------------------------------------+  |
|             │                                                  │                                  |
|             │ Hardware Wake-Up Interrupt (GPIO34)              │ Safe Demodulated Bus (SPI/GPIO)  |
|             ▼                                                  ▼                                  |
|  +---------------------------------------------------------------------------------------------+  |
|  | [ HOST CONTROLLER: ESP32-WROOM-32 / ROUTER SoC ]                                            |  |
|  | - State: Deep-Sleep (Konsumsi ~10 uA) -> Wakes up only on Valid Secure Interrupt           |  |
|  | - Core Operations:                                                                          |  |
|  |   * Ingest payload dari uo_out[7:0] hanya saat tamper_alert = 0                             |  |
|  |   * Melaporkan status telemetri keamanan kembali ke VM via SIM/Ethernet                     |  |
|  |   * Mengisolasi port router jika tamper_alert terpicu                                       |  |
|  +---------------------------------------------------------------------------------------------+  |
|                                                                                                   |
|  [ INSTRUMENTASI PENGUKURAN PRESISI ]                                                             |
|  * Nordic Power Profiler Kit II (PPK2) / Keithley SMU: Monitoring konsumsi daya total (nW & uA)   |
|  * Saleae Logic Pro 16: Verifikasi latensi zero-cycle isolation & timing pulsa                    |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Pemetaan Pin Fisik & Interkoneksi Hardware

| Pin ARES-RX (TT08) | Tipe | Terhubung ke Pin ESP32 / Modul | Fungsi Operasional |
| :--- | :---: | :--- | :--- |
| `clk` | Input | ESP32 GPIO 18 (PWM Clock) / RP2040 | Master Clock generator ($20\,\text{kHz} - 50\,\text{MHz}$) |
| `rst_n` | Input | ESP32 GPIO 23 | Master Hardware Reset (Active-Low) untuk membersihkan sticky latch |
| `ui_in[0]` | Input | Sinyal Rx Modem SIM / Pulsa Masuk | Ingress baseband data stream (Manchester encoded) |
| `uio_out[6]` | Output | ESP32 GPIO 34 (RTC Wake-Up) | `tamper_alert` (Lapor ke ESP32 bahwa terjadi anomali/serangan) |
| `uio_out[7]` | Output | ESP32 GPIO 35 (RTC Wake-Up) | `reception_active` / Wake-Up trigger untuk sinyal valid |
| `uo_out[7:0]` | Output | ESP32 GPIO 12 s.d. 19 / 27 | Bus data paralel aman 8-bit (*zeroized* `8'h00` saat fault) |
| `V_DD` ($1.8\,\text{V}$) | Power | LDO Regulator Presisi | Tegangan suplai inti chip ARES-RX |

---

## 4. Matriks Skenario Uji Coba

### Skenario 1: Uji Ketahanan *Denial-of-Sleep* (Anti-Drain Baterai)
- **Kondisi Awal:** ESP32 berada pada mode `Deep-Sleep` (~$10\,\mu\text{A}$ arus siaga).
- **Vektor Uji:** VM menyuntikkan 100.000 frame interferensi acak dan glitch timing via modem seluler.
- **Kriteria Lulus:** Sinyal `reception_active` tetap LOW (`0`), pin `tamper_alert` mendeteksi anomali pada siklus pertama, dan ESP32 tidak terbangun sama sekali. Konsumsi daya rata-rata modul tetap $\le 20\,\mu\text{W}$.

### Skenario 2: Uji Penetrasi Jaringan & Segmentasi VLAN
- **Kondisi Awal:** Router mengalokasikan komunikasi ingress ke VLAN 10 dan sistem inti ke VLAN 30.
- **Vektor Uji:** VM menyuntikkan paket dengan anomali preamble dan panjang frame melebihi spesifikasi (*overrun*).
- **Kriteria Lulus:** Bus keluaran ARES-RX terkunci pada `8'h00` ($T_{\text{isolate}} = 0$). ESP32 membaca `0x00`, menolak memproses paket, dan memicu isolasi port pada router menuju VLAN 20 (Quarantine). Nol data bocor ke VLAN 30.

### Skenario 3: Profiling Konsumsi Daya & Latensi Respon
- **Instrumen:** Nordic PPK2 / Keithley SMU + Saleae Logic Analyzer.
- **Kriteria Lulus:**
  - Latensi isolasi bus data: $0$ siklus clock dari deteksi kesalahan.
  - False Alarm Rate ($FAR$): $0\%$ pada frame data valid.
