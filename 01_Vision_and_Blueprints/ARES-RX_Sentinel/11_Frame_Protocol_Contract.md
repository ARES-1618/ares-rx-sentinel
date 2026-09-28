# ARES-RX Sentinel — Layer-2 Protocol Contract & Frame Specification
**Document Version:** 2.0.0 (Post Contract-Freeze Pass)  
**Classification:** Core Protocol & Frame Syntax Specification (Milestone M3)  
**Authority:** Technical Architect / Research Direction  
**Executing Engineer:** Implementation Engineer (Copilot)  
**Reference Baseline:** `tt07-bep-decode` (`serial_decode.v`, `data_validate.v`, `state_machine.v`, `project.v`)  
**Status:** Frozen Protocol Contract  

---

## 1. Executive Summary: Hasil Contract-Freeze Pass

Berdasarkan audit forensik terhadap kode sumber *frozen baseline* (`tt07-bep-decode/src/`) dan dataset rekaman fisik (`transmission_digital_hs.csv`), seluruh 6 butir investigasi arsitektur telah dibuktikan secara definitif:

1. **Struktur Frame Definitif (192 Bit)**:
   - Satu frame lengkap terdiri dari tepat **192 bit serial**, terbagi atas 96 bit Header dan 96 bit Payload/Trailer.
   - Preamble: `32'hAAAAAAAA` (Bits 0..31)
   - Type 1: `16'hD391` (Bits 32..47)
   - Type 2: `16'hD391` (Bits 48..63)
   - Constant: `32'h0DFFFFFE` (Bits 64..95)
   - Payload Dinamis: Thermostat ID (32b), Room Temp (16b), Set Temp (16b), State (8b) (Bits 96..167)
   - Protocol Trailer: `Tail[23:0]` (Bits 168..191)
2. **Karakteristik Sinyal `serial_clock`**:
   - Berpolaritas **ACTIVE-HIGH**, berupa strobe pulsa tunggal selebar 1 siklus clock ASIC (`clock_mask = 1` pada `state_machine.v`) yang dibangkitkan pada deteksi transisi di tengah sel Manchester.
   - Data `serial_data` stabil dan valid saat `serial_clock == 1'b1`.
3. **Sifat Sinyal `full`**:
   - `full` **bukan pulsa (strobe)**, melainkan **level steady** yang aktif tinggi (`1'b1`) tepat pada saat bit ke-192 (bit 191 payload) di-clock masuk ke `shift_register[96]`.
   - Begitu `full == 1`, register baseline membeku (`!full` menjadi false) dan mengabaikan seluruh bit berikutnya hingga terjadi reset via `transmission_begin` atau `rst_n`.
4. **Status Tail 24-bit**:
   - **Bukan CRC terverifikasi**. Baseline `data_validate.v` sama sekali tidak memeriksa Tail, dan komentar desainer baseline secara literal menulis `tail_1; // CRC?`.
   - Kontrak M3 menetapkan: `Tail[23:0] = protocol trailer / reserved tail fields`. Verifikasi CRC adalah `OUT OF SCOPE`.
5. **Demarkasi Integritas Framing vs Validitas Semantik**:
   - M3 **TIDAK** memvalidasi isi payload dinamis (ID, suhu, status). Perubahan nilai data normal tidak dianggap sebagai anomali.
   - M3 hanya memeriksa integritas sintaks: bit count, field boundaries, fixed constants/types, dan terminasi frame.
6. **Kontrak Terminasi: Deteksi Truncation & Overrun**:
   - Menggunakan sinyal konteks fisik dari Layer-1 (`reception_active` / EOP transition):
     - **Truncation**: Jika keheningan fisik EOP ($N \ge 64$) atau missing gap terjadi saat frame belum lengkap ($0 < \text{bit\_count} < 192 \land full == 0$) $\implies$ `FAULT_TRAILER_CORRUPT` (`3'b111`).
     - **Overrun**: Jika strobe `serial_clock == 1` tambahan tiba setelah bit ke-191 ($bit\_count > 192$) sebelum jeda fisik antar-frame $\implies$ `FAULT_TRAILER_CORRUPT` (`3'b111`).

---

## 2. Protocol Contract Matrix Definitif

Tabel berikut menjadi kontrak tunggal yang mengikat implementasi RTL `ares_frame_fsm.v`:

| Baseline Field | Bit Index (Offset) | Sampling Event | Nominal Value / Constraint | M3 Integrity Check | Assigned Fault Code |
|---|---|---|---|---|---|
| **Preamble** | Bits $0 \dots 31$ ($32\text{b}$) | `posedge clk` saat `serial_clock == 1` | `32'hAAAAAAAA` | Verifikasi 32 bit pola sinkronisasi awal. Deviasi bit langsung memicu fault. | `3'b100` (`FAULT_PREAMBLE_CORRUPT`) |
| **Type 1** | Bits $32 \dots 47$ ($16\text{b}$) | `posedge clk` saat `serial_clock == 1` | `16'hD391` | Verifikasi identifier tipe pesan bagian 1. Deviasi nilai memicu fault. | `3'b101` (`FAULT_TYPE_CORRUPT`) |
| **Type 2** | Bits $48 \dots 63$ ($16\text{b}$) | `posedge clk` saat `serial_clock == 1` | `16'hD391` | Verifikasi redundansi tipe pesan bagian 2. Deviasi memicu fault. | `3'b101` (`FAULT_TYPE_CORRUPT`) |
| **Constant** | Bits $64 \dots 95$ ($32\text{b}$) | `posedge clk` saat `serial_clock == 1` | `32'h0DFFFFFE` | Verifikasi konstanta pembatas header. Deviasi 1 bit memicu fault. | `3'b110` (`FAULT_CONSTANT_CORRUPT`) |
| **Header Transition** | Bit $95 \rightarrow 96$ | `posedge clk` saat `serial_clock == 1` | Transisi ke payload | Validasi transisi internal FSM; kegagalan field sebelumnya telah tertangkap di kodenya masing-masing. | Sesuai field yang gagal |
| **Dynamic Payload** | Bits $96 \dots 167$ ($72\text{b}$) | `posedge clk` saat `serial_clock == 1` | Dynamic data (ID, Room, Set, State) | **Framing integrity only**. Bit dihitung sesuai panjang tetap 72 bit; validitas semantik payload adalah `OUT OF SCOPE`. | N/A (Normal Passthrough) |
| **Protocol Trailer** | Bits $168 \dots 191$ ($24\text{b}$) | `posedge clk` saat `serial_clock == 1` | Reserved trailer fields | Verifikasi penerimaan tepat 24 bit trailer penutup frame. | `3'b111` (`FAULT_TRAILER_CORRUPT`) |
| **Frame Complete** | Bit $191$ | `posedge clk` saat `serial_clock == 1` | Assert `full == 1` | Verifikasi penegasan `full` tepat pada bit ke-192. | `3'b111` (`FAULT_TRAILER_CORRUPT`) |
| **Termination Check: Truncation** | Bit $< 191$ | `posedge clk` saat physical EOP | `reception_active` jatuh ke 0 | Sinyal fisik berhenti sebelum 192 bit lengkap diterima. | `3'b111` (`FAULT_TRAILER_CORRUPT`) |
| **Termination Check: Overrun** | Bit $> 191$ | `posedge clk` saat `serial_clock == 1` | Tidak boleh ada bit tambahan | Bit clock tambahan terdeteksi setelah frame 192 bit selesai. | `3'b111` (`FAULT_TRAILER_CORRUPT`) |

---

## 3. Ruang Alokasi Fault Code 3-Bit (`[2:0]`)

Ruang kode diagnostik tertutup dan ortogonal:

$$\begin{aligned}
\text{3'b000} &= \text{FAULT\_NONE (Kondisi normal / tidak ada fault)} \\
\text{3'b001} &= \text{FAULT\_RUNT (Layer-1: Glitch / Short Pulse } N \le 7\text{)} \\
\text{3'b010} &= \text{FAULT\_MIDBAND (Layer-1: Forbidden Interval } 11 \le N \le 15\text{)} \\
\text{3'b011} &= \text{FAULT\_GAP\_RES (Layer-1: Active-Frame Missing Edge Resume } N \ge 21\text{)} \\
\text{3'b100} &= \text{FAULT\_PREAMBLE\_CORRUPT (Layer-2: Deviasi pada 32-bit Preamble)} \\
\text{3'b101} &= \text{FAULT\_TYPE\_CORRUPT (Layer-2: Deviasi pada 16-bit Type 1 / Type 2)} \\
\text{3'b110} &= \text{FAULT\_CONSTANT\_CORRUPT (Layer-2: Deviasi pada 32-bit Constant)} \\
\text{3'b111} &= \text{FAULT\_TRAILER\_CORRUPT (Layer-2: Truncation, Overrun, atau Boundary Violation)}
\end{aligned}$$

---

## 4. Arsitektur Upstream Priority Arbiter (`ares_fault_arbiter.v`)

Modul `ares_fault_arbiter.v` adalah modul terpisah kombinasional murni:
- **Same-Cycle Priority**: $L1 > L2$.
- **Stateless & Zero Cycles Delay**: Tidak memiliki register, clock, atau status sticky.
- **Across-Cycles Persistence**: Ditangani sepenuhnya oleh `ares_fault_latch.v` (M2).

```verilog
module ares_fault_arbiter (
    input  wire       temporal_fault,
    input  wire [2:0] temporal_code,
    input  wire       frame_fault,
    input  wire [2:0] frame_code,
    output reg        set_fault,
    output reg  [2:0] fault_code
);

    always @(*) begin
        if (temporal_fault) begin
            set_fault  = 1'b1;
            fault_code = temporal_code;
        end else if (frame_fault) begin
            set_fault  = 1'b1;
            fault_code = frame_code;
        end else begin
            set_fault  = 1'b0;
            fault_code = 3'b000;
        end
    end

endmodule
```
