# ARES-RX Sentinel — Timing Model v2.0
**Document Version:** 2.0.0  
**Classification:** Core Physical & Timing Specification  
**Authority:** Technical Architect / Research Direction  
**Executing Engineer:** Implementation Engineer (Copilot)  
**Status:** Grounded on Empirical Logic Analyzer Dataset (25 Hardware Captures)  

---

## 1. Landasan Fisik & Domain Observasi

Sinyal masukan $rx\_in$ pada pin ASIC Tiny Tapeout (`ui_in[0]`) merupakan keluaran digital demodulator dari modul penerima RF sub-GHz (433.92 MHz ISM band ASK/OOK receiver, seperti seri RXB6 / SYN470R / superheterodyne demodulator).

```
                      +------------------------------------------+
                      |         ASIC INPUT DOMAIN (DIGITAL)      |
                      |                                          |
                      |   Sampling Reference: Fs = 20.0 kHz      |
                      |                       Ts = 50.0 us       |
  433.92 MHz RF       |                                          |
  ASK/OOK Antena      |   rx_in (Pin ui_in[0])                   |
      |               |     |                                    |
      v               |     v                                    |
  [RF Demodulator] ---> [Synchronizer / Edge Detect]             |
  (Demodulasi Analog) |     |                                    |
                      |     +---> [Layer-1 Timing Sentinel]      |
                      |     |                                    |
                      |     +---> [Manchester Decoder]           |
                      +------------------------------------------+
```

### Nomenklatur & Resolusi Waktu:
- **Sampling Frequency of Physical Capture ($F_s$)**: $20.0\text{ kHz}$.
- **Capture Time Quantum ($T_s$)**: $50.0\,\mu\text{s}$.
- **Hubungan dengan Clock RTL ASIC ($F_{clk}$)**:
  - $F_s = 20\text{ kHz}$ dan $T_s = 50\,\mu\text{s}$ adalah **resolusi observasi / akuisisi sinyal**, bukan otomatis clock master internal ASIC.
  - **Case A (Direct Physical Capture Clock)**: Clock RTL ASIC disinkronkan langsung pada $F_{clk} = F_s = 20.0\text{ kHz}$ ($T_{clk} = T_s = 50.0\,\mu\text{s}$).
  - **Case B (High-Frequency Master Clock with Prescaler)**: Clock internal ASIC bekerja pada frekuensi tinggi (misal $F_{clk} = 10\text{ MHz} - 50\text{ MHz}$ pada Tiny Tapeout), di mana setiap interval capture $T_s$ dipetakan melalui prescaler atau *baud tick generator*:
    $$K_{sample} = \frac{F_{clk}}{F_s}$$
  Dalam dokumen ini, kuantisasi waktu dinyatakan dalam **sample-count equivalent ($N$)** berbasis interval observasi $T_s = 50\,\mu\text{s}$.

---

## 2. Karakterisasi Dataset Empiris (25 Hardware Captures)

Karakterisasi empiris dilakukan secara menyeluruh terhadap **25 rekaman logic analyzer fisik** (*Digilent Discovery 3 Logic Analyzer*, $F_s = 20\text{ kHz}, T_s = 50\,\mu\text{s}$) yang mencakup $401.408$ sample fisik dan $>30.000$ transisi.

### 2.1 Profil Transmisi Tunggal (`transmission_digital_hs.csv`)
1. **Leading Silence**: 2.296 sample ($114.8\text{ ms}$) keheningan sebelum paket dimulai.
2. **Settling Chirp Awal**: 2 transisi settling demodulator awal ($N=12$ dan $N=15$ sample).
3. **Active Manchester Burst**: Tepat **289 transisi aktif sah** ($3.452\text{ sample} = 172.6\text{ ms}$).
   - Half-bit range: $N \in [8, 10]$ sample ($400 - 500\,\mu\text{s}$).
   - Full-bit range: $N \in [16, 20]$ sample ($800 - 1000\,\mu\text{s}$).
   - Seluruh 289 transisi berada di dalam himpunan valid $\mathcal{V} = [8, 10] \cup [16, 20]$.
4. **Trailing Silence**: 2.444 sample ($122.2\text{ ms}$) keheningan pasca-burst.

### 2.2 Distribusi Inter-Frame Gap Normal ($G_{IFG}$)
Pada capture transmisi berulang (`hs_repeating/01.csv` s/d `10.csv`), transmisi sensor memancar secara periodik. Analisis gap antar-burst menghasilkan:
- **Total Inter-Burst Gaps Dievaluasi**: 10 burst pairs.
- **Minimum Normal IFG ($G_{IFG, min}$)**: **$6547\text{ samples}$ ($327.35\text{ ms}$)**.
- **Median Normal IFG ($G_{IFG, median}$)**: **$6547\text{ samples}$ ($327.35\text{ ms}$)**.
- **Maximum Normal IFG ($G_{IFG, max}$)**: **$6548\text{ samples}$ ($327.40\text{ ms}$)**.
- **Transmitter Burst Repeat Rate**: $\approx 3.05\text{ Hz}$ ($T_{repeat} \approx 327.4\text{ ms}$).

---

## 3. Kuantisasi Waktu Simbol & Acceptance Window

- **Observed Half-Bit Period ($T_{HB}$)**:
  $$T_{HB} \approx N_{HB} \cdot T_s = 9 \times 50.0\,\mu\text{s} = 450.0\,\mu\text{s}$$
- **Observed Full-Bit Period ($T_{bit}$)**:
  $$T_{bit} \approx N_{bit} \cdot T_s = 18 \times 50.0\,\mu\text{s} = 900.0\,\mu\text{s}$$
- **Nominal Baud Rate ($R_{baud}$)**:
  $$R_{baud} = \frac{1}{T_{bit}} = \frac{1}{900 \times 10^{-6}\text{ s}} \approx 1111.11\text{ baud} \quad (\approx 1.11\text{ kbps})$$

### Empirical Timing Acceptance Window ($\pm 11.11\%$):
$$\mathcal{V}_{HB} = [8, 10]\text{ samples} \quad (400\,\mu\text{s} - 500\,\mu\text{s})$$
$$\mathcal{V}_{bit} = [16, 20]\text{ samples} \quad (800\,\mu\text{s} - 1000\,\mu\text{s})$$

Rentang toleransi ini merupakan **Empirical Timing Acceptance Window** multi-faktor yang mengintegrasikan:
1. Asinkroni antara sampling clock logic analyzer dan transmitter.
2. Kuantisasi $\pm 1$ sample pada setiap deteksi edge ($T_s = 50\,\mu\text{s}$).
3. Slew-rate dan filter low-pass pada tahap demodulator analog.
4. Respon Automatic Gain Control (AGC) pada modul RF receiver.

---

## 4. Pembuktian Batas $N_{EOF}$ & Deferred Fault Classification

Kebijakan **Deferred Fault Classification** memisahkan anomali missing-edge di tengah burst dari keheningan normal di akhir burst tanpa bergantung pada baseline decoder.

```
                    ACTIVE BURST
                         |
                         v (N >= 21)
                LONG_GAP_PENDING
                  /            \
    Edge Resumes /              \ Silence reaches N_EOF (64)
                v                v
          STATE_FAULT        STATE_IDLE
      (Missing Edge Trapped) (End-of-Burst Silence Confirmed)
```

### 4.1 Hubungan Ketidaksamaan Ambang Batas:
Ambang batas akhir paket ($N_{EOF}$) wajib memenuhi relasi:
$$\boxed{N_{TIMEOUT} < N_{EOF} < G_{IFG, min}}$$

Substitusi nilai empiris:
$$21\text{ samples } (1.05\text{ ms}) < 64\text{ samples } (3.20\text{ ms}) < 6547\text{ samples } (327.35\text{ ms})$$

### 4.2 Evaluasi Margin Keamanan Temporal:
1. **Margin terhadap Burst Baru**:
   $$\text{Temporal margin} = \frac{G_{IFG, min}}{N_{EOF}} = \frac{6547}{64} \approx \mathbf{102.3\times}$$
   (Ekuivalen dengan rasio temporal $10\log_{10}(102.3) \approx 20.1\text{ dB}$). FSM Sentinel telah berada kembali di `STATE_IDLE` dalam waktu $3.2\text{ ms}$, yang berjarak aman $>324\text{ ms}$ sebelum burst berikutnya tiba secara fisik.
2. **Margin terhadap Timeout Celah Aktif**:
   $$\text{Margin}_{TIMEOUT} = \frac{N_{EOF}}{N_{TIMEOUT}} = \frac{64}{21} \approx 3.05\times$$
   Memberikan jendela observasi yang memadai ($43\text{ cycles} = 2.15\text{ ms}$) untuk mendeteksi missing edge yang disambung kembali.

---

## 5. Latensi Deteksi Anomali Temporal

Sifat temporal dari berbagai vektor serangan membedakan latensi deteksi:

| Kategori Anomali | Vektor Uji | Kondisi Deteksi | Latensi Deteksi | Respon Sentinel |
|---|---|---|---|---|
| **Runt Glitch** | AV01 | $N \le 7$ ($< 400\,\mu\text{s}$) | **0 siklus clock** dari edge arrival | Strobe `temporal_fault=1`, `fault_code=3'b001`, transisi ke `STATE_IDLE` |
| **Mid-Band Anomaly** | AV03 | $11 \le N \le 15$ ($550 - 750\,\mu\text{s}$) | **0 siklus clock** dari edge arrival | Strobe `temporal_fault=1`, `fault_code=3'b010`, transisi ke `STATE_IDLE` |
| **Extra Edge / Bouncing**| AV04 | $N \le 7$ saat interval bit | **0 siklus clock** dari edge arrival | Strobe `temporal_fault=1`, `fault_code=3'b001`, transisi ke `STATE_IDLE` |
| **Missing Edge / Gap Resume** | AV02-A | $N \ge 21$ diikuti edge baru | **$21 T_s$ untuk pending**, confirmed pada saat edge tiba ($t_{resume}$) | Strobe `temporal_fault=1`, `fault_code=3'b011`, transisi ke `STATE_IDLE` |
| **End-of-Burst Silence** | AV02-B | $N \ge N_{EOF} = 64$ tanpa edge | **$64 T_s$ ($3.2\text{ ms}$)** | Transisi ke `STATE_IDLE`, `temporal_fault=0` (Zero False Alarm) |
| **EOP Squelch Noise** | AV06 | Noise chatter $N = 1..4$ pasca-EOF | N/A (Filtered in `ARMED`) | Ditampung di `STATE_ARMED`, timeout ke `STATE_IDLE`, no false alarm |
