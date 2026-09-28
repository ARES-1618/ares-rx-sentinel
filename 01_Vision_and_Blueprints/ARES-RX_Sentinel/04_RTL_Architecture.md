# ARES-RX Sentinel — RTL Architecture Specification
**Document Version:** 1.2.0  
**Classification:** Core Hardware Design Specification  
**Status:** Approved by Technical Architect  

---

## 1. Top-Level Architectural Decomposition

Sistem ARES-RX Sentinel memisahkan antarmuka fisik penerimaan digital dari register bus downstream host melalui subsistem modular yang beroperasi tanpa dependensi sirkular terhadap FSM baseline:

```
+-----------------------------------------------------------------------------------+
|                            ARES-RX SENTINEL TOP MODULE                            |
|                                                                                   |
|                   +--------------------------------------------+                  |
|  rx_in -----------> 2-Stage CDC Synchronizer & Edge Detector   |                  |
|                   +--------------------------------------------+                  |
|                                 | pos_edge, neg_edge, rx_sync                     |
|         +-----------------------+------------------------+                        |
|         |                                                |                        |
|         v                                                v                        |
|  +-----------------------------+               +-------------------------------+  |
|  | Layer 1:                    |               | Manchester Decoder Core       |  |
|  | ares_timing_sentinel        |               | (Data Recovery & Clock Gen)   |  |
|  |                             |               +-------------------------------+  |
|  | [Reception Context FSM]     |                                 |                |
|  | IDLE -> ARMED -> ACTIVE     |                                 | recovered_clk  |
|  |      -> LONG_GAP_PENDING    |                                 | recovered_data |
|  +-----------------------------+                                 |                |
|         |                                                        |                |
|         | edge_interval [7:0]                                    |                |
|         | reception_active                                       |                |
|         | temporal_valid (V_phys)                                |                |
|         | temporal_fault                                         |                |
|         v                                                        |                |
|  +-----------------------------+                                 |                |
|  | Layer 2:                    |<--------------------------------+                |
|  | ares_frame_fsm (Future M3)  |                                                  |
|  +-----------------------------+                                                  |
|         |                                                                         |
|         | frame_valid (V_prot)                                                    |
|         | protocol_fault                                                          |
|         v                                                                         |
|  +-------------------------------------------------------------+                  |
|  | Layer 3: Security Policy Enforcement (Zeroization & Latch)  |                  |
|  |                                                             |                  |
|  | FaultLatch = temporal_fault | protocol_fault                |                  |
|  | DataPass   = frame_valid & !FaultLatch                      |                  |
|  | Output MUX : DataPass ? DecodedData : 8'h00                 |                  |
|  +-------------------------------------------------------------+                  |
|         |                                             |                           |
|         v                                             v                           |
|    parallel_out [7:0]                           tamper_alert                      |
+-----------------------------------------------------------------------------------+
```

---

## 2. Layer 1: Timing Sentinel & Reception Context FSM

Layer 1 mengimplementasikan **Reception Context Controller** 4-keadaan yang mengisolasi keputusan timing murni tanpa membutuhkan informasi protokol Layer-2:

```
                 ┌──────────────┐
                 │     IDLE     │ <──────────────────────────────┐
                 └──────┬───────┘                                │
                        │                                        │
                   first edge                                    │
                        │                                        │
                        ▼                                        │
                 ┌──────────────┐                                │
                 │    ARMED     │ ── invalid interval ──┐        │
                 └──────┬───────┘                       │        │
                        │                               │        │
                  valid interval                        │        │
                        │                               │        │
                        ▼                               │        │
                 ┌──────────────┐                       │        │
                 │    ACTIVE    │ ── invalid interval ──┤        │
                 └──────┬───────┘                       │        │
                        │                               │        │
                  N >= 21                               │        │
                        │                               │        │
                        ▼                               │        │
              ┌────────────────────┐                    │        │
              │ LONG_GAP_PENDING   │                    │        │
              └───────┬───────┬────┘                    │        │
                      │       │                         │        │
               edge resumes   │ N >= N_EOF              │        │
                      │       │ (Confirm End of Burst)  │        │
                      │       └─────────────────────────┼────────┘
                      ▼                                 ▼
              [TEMPORAL FAULT]                  [TEMPORAL FAULT]
          (Missing Edge in Active)             (Glitch / Mid-band)
```

### Logika Keadaan Reception Context:
1. **`STATE_IDLE`**: Keadaan hening antar-paket. Pada keadaan ini, interval counter dibiarkan melampaui $N \ge 21$ tanpa membangkitkan fault. Transisi tepi pertama memindahkan status ke `STATE_ARMED`.
2. **`STATE_ARMED`**: Tepi awal terdeteksi, tetapi interval belum dapat dihitung karena belum ada tepi pembanding sebelumnya. Tepi kedua dievaluasi:
   - Jika $N_{edge} \in \mathcal{V} = [8, 10] \cup [16, 20]$: Pindah ke `STATE_ACTIVE`, aktifkan `reception_active = 1`.
   - Jika $N_{edge} \le 7$ atau $11 \le N_{edge} \le 15$: Pindah ke `STATE_FAULT`.
3. **`STATE_ACTIVE`**: Burst penerimaan sedang aktif.
   - Setiap tepi yang masuk dievaluasi terhadap $\mathcal{V}$.
   - Jika terjadi keheningan $N \ge 21$ siklus ($1050\,\mu\text{s}$), sistem bertransisi ke `STATE_LONG_GAP_PENDING`.
4. **`STATE_LONG_GAP_PENDING` (Deferred Fault Classification)**:
   - Sistem menahan keputusan kesalahan sambil menunggu bukti temporal lanjutan.
   - **Kasus A (Missing Edge / Anomali)**: Jika tepi sinyal muncul kembali saat status masih `LONG_GAP_PENDING`, ini membuktikan terjadinya celah ilegal di tengah paket $\rightarrow$ Pindah ke `STATE_FAULT` (`fault_code = 3'b011`).
   - **Kasus B (Normal End-of-Burst)**: Jika keheningan berlanjut hingga $N \ge N_{EOF}$ (misal $N_{EOF} = 64$ siklus / $3.2\text{ ms}$), sistem menyimpulkan bahwa paket transmisi telah berakhir normal $\rightarrow$ Kembali ke `STATE_IDLE` tanpa membangkitkan `temporal_fault` (Zero False Positive).

---

## 3. Layer 3: Pembedaan Konseptual Tri-Part

Arsitektur Sentinel memisahkan secara tegas tiga konsep:

### A. VALIDITY (Otentikasi Kepatuhan Protokol):
$$V_{trusted} = V_{physical} \land V_{protocol}$$
- $V_{trusted} = 0$ **TIDAK** berarti ada serangan (contoh: pada kondisi `IDLE`, `RESET`, atau saat paket belum selesai, $V_{protocol} = 0$ adalah kondisi normal).

### B. FAULT (Status Anomali Keamanan):
$$\text{FaultCondition} = \text{TemporalFault} \lor \text{ProtocolFault}$$
$$\text{StickyTamperLatch} \Leftarrow \text{FaultCondition} \lor \text{StickyTamperLatch}$$
- `tamper_alert` hanya dipicu oleh peristiwa anomali aktif, bukan karena sistem sedang idle.

### C. AUTHORIZATION (Izin Penerusan Data / DataPass):
$$\text{DataPass} = \text{FrameValid} \land \neg \text{StickyTamperLatch}$$
$$\text{parallel\_out} = \text{DataPass} \ ? \ \text{shift\_register\_data} : 8\text{'h00}$$
