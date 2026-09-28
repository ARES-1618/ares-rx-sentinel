# AV02: Long-Gap Ambiguity & Deferred Classification Vector

## 1. Physical Description
Menguji perilaku Sentinel terhadap anomali celah panjang ($N \ge 21$) dan mengevaluasi kebijakan **Deferred Fault Classification** untuk membedakan secara deterministik antara missing-edge di dalam paket aktif dan keheningan normal di akhir transmisi.

## 2. Sub-Vektor Uji

### AV02-A: Missing Edge with Signal Resume
- **Skenario**: Paket sedang aktif, terjadi celah $N = 35$ siklus ($1.75\text{ ms}$), kemudian transisi edge muncul kembali.
- **Expected Flow**:
  1. Pada $N = 21$: Transisi `ACTIVE -> LONG_GAP_PENDING`.
  2. Pada $N = 35$: Edge muncul kembali $\rightarrow$ Transisi `LONG_GAP_PENDING -> STATE_FAULT`.
  3. Sinyal `temporal_fault = 1` aktif dengan `fault_code = 3'b011`.
  4. `tamper_alert = 1` mengunci status fault, bus output di-zeroize.

### AV02-B: Normal Packet Termination Silence
- **Skenario**: Tepi terakhir dari paket valid selesai, diikuti keheningan normal $\ge N_{EOF}$ (misal $N \ge 64$ siklus / $3.2\text{ ms}$).
- **Expected Flow**:
  1. Pada $N = 21$: Transisi `ACTIVE -> LONG_GAP_PENDING`.
  2. Tidak ada tepi yang muncul hingga counter mencapai $N_{EOF} = 64$.
  3. Transisi `LONG_GAP_PENDING -> STATE_IDLE`.
  4. **TIDAK ADA** `temporal_fault` yang dibangkitkan (`tamper_alert = 0`, Zero False Positive).

## 3. Acceptance Criteria
- [ ] AV02-A mendeteksi missing edge secara deterministik saat transmisi berlanjut.
- [ ] AV02-B mengkonfirmasi akhir paket tanpa alarm palsu saat keheningan menetap.
