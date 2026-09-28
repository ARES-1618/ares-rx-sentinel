# AV01: Short Pulse / Glitch Injection Attack Vector

## 1. Physical Description
Injeksi pulsa digital abnormal sempit berdurasi $N \le 7$ siklus clock ($T < 400\,\mu\text{s}$) ke dalam jalur input `rx_in`. Di dunia fisik, fenomena ini muncul akibat:
- Induksi transien elektromagnetik cepat (EMFI).
- Crosstalk switching catu daya pada jalur PCB.
- Glitch noise demodulator RF akibat variasi AGC mendadak.

## 2. Stimulus Parameters
- Durasi Glitch: $1 - 7$ clock cycles ($50\,\mu\text{s} - 350\,\mu\text{s}$).
- Polarity: Positif (0 -> 1 -> 0) atau Negatif (1 -> 0 -> 1).
- Waktu Injeksi: Pada fase preamble, di tengah transmisi bit data, dan pada kondisi diam (idle).

## 3. Expected Behaviors
- **Baseline Design ($B$)**:
  - Glitch memicu `transmission_begin` secara palsu.
  - Deserializer mereset register geser, merusak paket yang sedang diterima.
- **ARES-RX Sentinel ($S$)**:
  - Layer-1 mendeteksi $N_{edge} \le 7 \notin \mathcal{V}$.
  - `temporal_fault` aktif seketika (`fault_code = 3'b001`).
  - Layer-3 Sticky Fault Latch mengunci status tamper (`tamper_alert = 1`).
  - Output data di-zeroize ($D_{out} = 0x00$).

## 4. Acceptance Criteria
- [ ] Deteksi deterministik pada 100% kasus injeksi $N \in [1, 7]$.
- [ ] Sinyal output terisolasi sepenuhnya.
- [ ] Waveform capture membuktikan assert `tamper_alert`.
