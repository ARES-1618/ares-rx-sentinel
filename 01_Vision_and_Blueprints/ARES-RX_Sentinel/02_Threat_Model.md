# ARES-RX Sentinel — Threat Model v1.0
**Document Version:** 1.1.0  
**Classification:** Core Security Specification  
**Status:** Approved by Technical Architect  

---

## 1. Domain Demarcation & Security Positioning

ARES-RX Sentinel beroperasi secara eksklusif pada **domain digital** pada antarmuka input ASIC Tiny Tapeout (`rx_in`). Sentinel memposisikan dirinya sebagai:

$$\boxed{\text{\bf Trusted Digital Reception Boundary}}$$

### Batasan Klaim Akademis & Rekayasa:
- **Klaim yang Valid & Defensible**:
  > "ARES-RX Sentinel mendeteksi anomali temporal (jarak antar-edge) dan struktural pada representasi digital penerimaan ($rx\_in$) yang diakibatkan oleh glitch injeksi, ketidaksesuaian modulasi, manipulasi pulsa, atau desinkronisasi protokol."
- **Klaim yang DITOLAK (Non-Defensible)**:
  > *"ARES mendeteksi segala bentuk jamming atau serangan analog RF 433 MHz."*
  > *Rasional*: ASIC digital tidak memiliki sensor analog RSSI/SNR atau ADC berkecepatan tinggi; gangguan RF hanya dapat dideteksi apabila memanifestasikan diri sebagai anomali pulsa digital pada keluaran modul demodulator.

---

## 2. Taksonomi Gangguan & Matriks Pertahanan

Sentinel mengklasifikasikan ancaman fisik dan protokol ke dalam 4 kategori utama:

| Kelas Gangguan | Domain Fisik | Terlihat pada $rx\_in$? | Dapat Dideteksi Layer-1 (Timing)? | Mekanisme Pertahanan Sentinel |
|---|---|---|---|---|
| **Short Pulse / Glitch** | Digital Timing | **Ya** (Pulsa $N_{edge} \le 7$ samples) | **Ya (100% Deterministic)** | Layer-1 Anomaly Trap $\rightarrow$ Sticky Fault Latch & Isolation |
| **Active Stretched Pulse** | Digital Timing | **Ya** ($11 \le N \le 15$ atau $N \ge 21$ in frame) | **Ya (100% Deterministic)** | Layer-1 Mid-Band Trap & Contextual Timeout Abort |
| **Receiver-Noise / AGC-Hash** | Analog/RF Demod | **Ya** (Muncul sebagai hash $1 - 4$ samples) | **Ya (100% Deterministic)** | Layer-1 Runt Rejection $\rightarrow$ Mengisolasi deserializer dari spurious reset |
| **Valid Waveform Spoofing** | Protocol / Content | **Tidak pada timing** ($N_{edge} \in \mathcal{V}$) | **Tidak Cukup** | Diperlukan **Layer-2 Frame Syntax Integrity** (Preamble, constant, type check) |

---

## 3. Analisis Mendalam Tiap Vektor Ancaman

### Ancaman 1: Short Pulse / Glitch Injection (AV01)
- **Mekanisme Serangan**: Injeksi pulsa sempit via EMFI (Electromagnetic Fault Injection) pada jalur PCB trace $rx\_in$ atau interferensi transien switching catu daya.
- **Dampak pada Baseline ($B$)**: Memicu `transmission_begin`, mereset deserializer, merusak frame yang sedang aktif di tengah transmisi.
- **Deteksi Sentinel ($S$)**: Setiap transisi dengan $N_{edge} \le 7$ sample ($< 400\,\mu\text{s}$) dideteksi seketika sebagai anomali. Sinyal `temporal_fault` aktif dan mengunci status fault.

### Ancaman 2: Missing Edge & Active Gap Resume (AV02-A, AV02-B)
- **Mekanisme Serangan**: Penundaan tepi sinyal (reactive jamming selektif pada bit transisi), pemutusan paket prematur, atau penyambungan frame palsu (*frame splicing*).
- **Dampak pada Baseline ($B$)**: Decoder baseline membaca bit invers atau mengalami desinkronisasi framing yang tak terdeteksi.
- **Deteksi Sentinel ($S$)**: 
  - Jika sinyal konstan $\ge 21$ siklus clock ($1050\,\mu\text{s}$) saat dalam status `ACTIVE`, Sentinel memasuki status observasi `LONG_GAP_PENDING`.
  - Jika transmisi dilanjutkan (edge baru tiba sebelum $N_{EOF}$), Sentinel seketika menegaskan `temporal_fault = 1` dengan `fault_code = 3'b011` (latensi terkonfirmasi tepat pada saat $t_{resume}$).
  - Jika keheningan berlanjut $\ge N_{EOF} = 64$ siklus ($3.2\text{ ms}$), Sentinel mengklasifikasikan situasi sebagai akhir burst normal dan kembali ke `STATE_IDLE` tanpa membangkitkan alarm palsu.

### Ancaman 3: Mid-Band Interval Anomaly (AV03)
- **Mekanisme Serangan**: Pergeseran fase destruktif atau clock drift ekstrim yang menghasilkan celah waktu tidak sah di antara batas half-bit dan full-bit ($11 \le N \le 15$ siklus / $550 - 750\,\mu\text{s}$).
- **Dampak pada Baseline ($B$)**: Desinkronisasi FSM internal tanpa indikasi kesalahan.
- **Deteksi Sentinel ($S$)**: Dideteksi seketika pada siklus kedatangan edge (**0 siklus clock latensi pasca-edge**) dengan `fault_code = 3'b010`.

### Ancaman 4: Receiver-Noise / AGC-Hash Disturbance (AV06)
- **Karakteristik Fisik**: Ketika tidak ada pemancar RF aktif (*no intended carrier*), AGC penerima analog memaksakan penguatan ke nilai maksimum, menghasilkan rentetan pulsa acak $1 - 4$ sample ($50 - 200\,\mu\text{s}$) secara masif.
- **Dampak pada Baseline ($B$)**: Deserializer baseline mengalami thrashing reset berulang kali pada setiap rising edge noise.
- **Deteksi Sentinel ($S$)**: Sentinel mengisolasi seluruh logika internal dari deserialisasi frame; pulsa sempit $N \le 7$ tidak pernah diizinkan memicu reset register.

### Ancaman 5: Structurally Valid Replay / Semantic Spoofing (AV08)
- **Mekanisme Serangan**: Attacker merekam transmisi asli dan memancarkannya kembali dengan timing Manchester yang sempurna.
- **Batas Kemampuan Timing Detector**: Karena timing $N_{edge} \in \mathcal{V}$, Layer-1 **tidak akan dan tidak boleh** memicu alarm false positive.
- **Pertahanan Multi-Layer**: Sentinel mengandalkan Layer-2 (validasi integritas frame) dan menyerahkan payload otentik ke lapisan kriptografi downstream (jika tersedia counter/HMAC pada sistem host).

---

## 4. Pembedaan Konseptual: Validitas vs Fault vs Otorisasi

Sentinel tidak menyamakan ketiadaan validitas dengan keberadaan serangan:
1. **Normal Inactive State (`IDLE`)**: $V_{protocol} = 0$, tetapi $\text{TamperAlert} = 0$.
2. **Active Attack State**: Terjadi pelanggaran timing atau protokol $\implies \text{FaultLatch} = 1 \implies \text{TamperAlert} = 1$.
3. **Data Release Authorization**: Data hanya dirilis jika $\text{FrameValid} = 1 \land \neg \text{FaultLatch}$.
