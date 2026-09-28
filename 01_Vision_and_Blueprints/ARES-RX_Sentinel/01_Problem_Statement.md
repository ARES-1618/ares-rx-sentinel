# ARES-RX Sentinel — Problem Statement

## 1. Problem Context: The Vulnerability of Demodulated RF Streams
Dalam sistem komunikasi nirkabel berbasis ASK/OOK 433.92 MHz ISM, penerima analog mengeluarkan sinyal digital bitstream mentah (`digital_in` / `rx_in`) ke mikrokontroler atau ASIC decoder.

Di level perangkat keras, aliran digital ini memiliki dua kelemahan mendasar:
1. **AGC Saturation Chatter**: Ketika transmitter tidak aktif, Automatic Gain Control (AGC) menaikkan penguatan secara ekstrim, mengubah kebisingan termal menjadi jutaan pulsa digital sempit liar ($1 - 4$ siklus sampling clock).
2. **Ketiadaan Validasi Fisik pada Deserializer**: Decoder konvensional (seperti pada modul referensi TT07 `tt07-bep-decode`) hanya mengandalkan logika deteksi edge sederhana tanpa memeriksa apakah lebar pulsa yang diterima secara matematis mematuhi ortogonalitas modulasi Manchester.

---

## 2. Root Cause Analysis pada Desain Baseline

Analisis terhadap baseline RTL `tt07-bep-decode` mengungkap kerentanan kritis:

```verilog
// state_machine.v baseline
case (state)
    state_armed: if (pos_edge) begin
        next_state = state_timing;
        transmission_begin_next = 1;  // <-- CRITICAL FLAW
    end
```

Dan pada `project.v`:
```verilog
data_multiplex data_multiplex (
    .reset_n(!transmission_begin && rst_n), // <-- RESET REGISTER SETIAP POS_EDGE
    ...
```

### Akibatnya:
1. **Spurious Reset Vulnerability**: Satu pulsa noise transien berdurasi $50\,\mu\text{s}$ (1 cycle) langsung mengaktifkan `transmission_begin`, mereset register geser paralel, dan mengacaukan penerimaan paket valid yang sedang berlangsung.
2. **Silent Corruption & Blind Ingestion**: Jika pulsa injeksi nakal memiliki interval sembarang yang lolos dari jendela kasar 4-9 siklus, bit cacat langsung digeser ke dalam register 96-bit dan disajikan ke pin output host tanpa ada indikasi kegagalan keamanan (*silent failure*).
3. **Ketiadaan Isolasi Fail-Closed**: Ketika frame terkorupsi, register output paralel tetap memegang data usang atau bit terdistorsi, membuka celah injeksi muatan palsu ke sistem kontrol downstream.

---

## 3. Solusi ARES: Trusted Digital Reception Boundary
ARES-RX Sentinel mengatasi masalah ini dengan memisahkan domain penerimaan fisik dari domain register data host menggunakan arsitektur gerbang multi-lapis:
- **Layer 1**: Memblokir pulsa sempit ($N < 8$) dan pulsa abnormal panjang ($N \ge 21$) dari memicu logika downstream.
- **Layer 2**: Menegakkan validasi protokol ganda (preamble sinkronisasi dan trailer konstan).
- **Layer 3**: Mengisolasi jalur bus data host dengan logika fail-closed (zeroization) dan mengunci status tampering secara sticky.
