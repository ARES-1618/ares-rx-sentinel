# ARES-RX Sentinel — System Architecture v1.0
**Document Version:** 1.0.0  
**Classification:** Core System Architecture  
**Status:** Approved by Technical Architect  

---

## 1. Konsep Inti: Trusted Digital Reception Boundary

ARES-RX Sentinel bukan sekadar Manchester Decoder dengan detektor glitch sederhana. Sentinel adalah **Trusted Digital Reception Boundary** yang berdiri sebagai benteng pengaman perangkat keras antara antarmuka penerima RF yang tidak terpercaya (*untrusted physical reception domain*) dan register data internal sistem downstream.

```
                 UNTRUSTED DOMAIN (RF / Demodulator Out)
                                    │
                                    ▼
                                rx_in(t)
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
                      ▼                           ▼
            Manchester Decoder            Timing Sentinel (Layer 1)
              (Data Recovery)             (Pulse-Width & Interval Monitor)
                      │                           │
                      │                           ▼
                      │                   temporal_anomaly
                      │                           │
                      ▼                           ▼
             decoded_bitstream            Frame Integrity FSM (Layer 2)
                      │                   (Preamble, SFD, Type, Trailer)
                      │                           │
                      │                           ▼
                      │                   protocol_anomaly
                      │                           │
                      └─────────────┬─────────────┘
                                    ▼
                     Hardware Fail-Closed Isolation (Layer 3)
                     (Zeroization MUX & Sticky Fault Latch)
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
                      ▼                           ▼
                  VALID PATH                  FAULT PATH
                      │                           │
                      ▼                           ▼
                 DATA OUT (Host)              DATA OUT = 0
                                                  │
                                                  ▼
                                            tamper_alert = 1
```

---

## 2. Dekomposisi Tiga Lapisan (The Three Sentinel Layers)

### Layer 1: Temporal Integrity Sentinel (`ares_timing_sentinel`)
- **Tujuan**: Memverifikasi kesesuaian fisik setiap durasi pulsa dan interval transisi terhadap model transmisi Manchester yang sah.
- **Masukan**: Sinyal digital tersinkronisasi `digital_in`, clock $20\text{ kHz}$, reset aktif-rendah.
- **Keluaran**: `temporal_valid` ($V_{physical}$), `temporal_fault`, `pulse_width_cycles[5:0]`.
- **Kondisi Validitas**:
  $$N_{edge} \in \mathcal{V} \iff (8 \le N_{edge} \le 10) \lor (16 \le N_{edge} \le 20)$$
- **Kondisi Pelanggaran**:
  $$N_{edge} \in [1, 7] \cup [11, 15] \cup [21, \infty)$$

---

### Layer 2: Frame Protocol Integrity Sentinel (`ares_frame_fsm`)
- **Tujuan**: Memastikan bahwa bitstream yang valid secara temporal juga mematuhi sintaks dan struktur protokol transmisi biphase.
- **Status FSM**:
  1. `STATE_IDLE / ARMED`: Menunggu deteksi transisi pertama yang valid.
  2. `STATE_PREAMBLE_SYNC`: Memvalidasi pola alternating sequence (32-bit `0xAAAAAAAA`).
  3. `STATE_HEADER_VERIFY`: Memeriksa identifier tipe payload (dua field 16-bit `0xD391`).
  4. `STATE_PAYLOAD_SHIFT`: Menerima 96-bit data sensor (Thermostat ID, Suhu Ruangan, Target Suhu, State).
  5. `STATE_TRAILER_CHECK`: Memvalidasi konstanta penutup (32-bit `0x0DFFFFFE`).
  6. `STATE_FRAME_VALID`: Menegaskan sinyal $V_{protocol} = 1$.
  7. `STATE_FAULT`: Mengunci FSM ke kondisi aman bila sintaks dilanggar di tengah jalan.
- **Kondisi Otentikasi Ganda**:
  $$V_{trusted} = V_{physical} \land V_{protocol}$$

---

### Layer 3: Hardware Fail-Closed Isolation (`ares_isolation_gate`)
- **Tujuan**: Mencegah kebocoran data terkorupsi atau manipulasi register host saat anomali terjadi.
- **Mekanisme**:
  $$D_{out} = \begin{cases} D_{decoded}, & \text{bila } V_{trusted} = 1 \text{ dan } \text{FaultLatch} = 0 \\ 0x00, & \text{bila } V_{trusted} = 0 \text{ atau } \text{FaultLatch} = 1 \end{cases}$$
- **Sticky Fault Latch**:
  Sekali `temporal_fault` atau `protocol_fault` terpicu:
  $$\text{TamperAlert} \leftarrow 1$$
  dan tidak dapat di-reset oleh sinyal data masukan berikutnya. Reset hanya dapat dilakukan melalui pin `rst_n` fisik eksternal.

---

## 3. Matriks Pin Antarmuka ASIC (Tiny Tapeout TT07/TT08)

| Pin Tiny Tapeout | Arah | Nama Sinyal | Deskripsi |
|---|---|---|---|
| `ui_in[0]` | Input | `digital_in` / `rx_in` | Masukan digital demodulasi RF 433.92 MHz |
| `ui_in[1]` | Input | `manual_reset_latch` | Opsi reset fault latch manual (atau di-tie low) |
| `ui_in[2]` | Input | `halt` | Kontrol transfer paralel host (active-high) |
| `ui_in[7:4]` | Input | `address[3:0]` | Selektor register data paralel 8-bit |
| `uo_out[7:0]` | Output | `parallel_out[7:0]` | Data register paralel (ter-isolasi fail-closed) |
| `uio_out[0]` | Output | `frame_valid` | Indikator frame selesai & valid ($V_{trusted}$) |
| `uio_out[1]` | Output | `tamper_alert` | Pin indikator serangan/anomali fisik (Sticky) |
| `uio_out[2]` | Output | `temporal_fault_strobe`| Strobe anomali timing Layer-1 |
| `uio_out[3]` | Output | `protocol_fault_strobe`| Strobe anomali protokol Layer-2 |
| `uio_out[4]` | Output | `manchester_clock` | Pulsa clock pemulihan data |
| `uio_out[5]` | Output | `manchester_data` | Aliran data serial decoded |
| `uio_out[7:6]` | Output | `reserved` | Ditarik ke logika 0 |
| `clk` | Input | `clk` | Master clock $20.0\text{ kHz}$ |
| `rst_n` | Input | `rst_n` | Master reset asynchronous active-low |
