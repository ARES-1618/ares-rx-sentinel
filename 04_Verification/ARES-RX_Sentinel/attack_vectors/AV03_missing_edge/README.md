# AV03: Mid-Band Interval Anomaly Vector (11 <= N <= 15)

## 1. Description
Menguji penolakan anomali celah waktu mid-band ($11 \le N \le 15$ siklus sampling / $550 - 750\,\mu\text{s}$) yang berada di antara batas maksimum half-bit ($HB_{MAX}=10$) dan batas minimum full-bit ($BIT_{MIN}=16$). Celah mid-band ini secara fisik mustahil terjadi pada modulasi Manchester sah dan merepresentasikan pergeseran fase destruktif, distorsi demodulator, atau injeksi edge asimetris.

## 2. Stimulus
Menghasilkan pulsa aktif valid (Preamble), kemudian menyuntikkan interval $N = 13$ siklus ($650\,\mu\text{s}$).

## 3. Expected Outcome
- **Baseline ($B$)**: Desinkronisasi FSM internal tanpa pemberitahuan tamper atau indikasi kesalahan (silent desynchronization).
- **Sentinel ($S$)**: 
  - Mendeteksi anomali pada siklus kedatangan edge (zero cycle detection latency).
  - Mengaktifkan `temporal_fault = 1` dengan `fault_code = 3'b010` (FAULT_MIDBAND).
  - Mentransisikan Reception Context FSM dari `STATE_ACTIVE -> STATE_IDLE` dan menurunkan `reception_active = 0`.
