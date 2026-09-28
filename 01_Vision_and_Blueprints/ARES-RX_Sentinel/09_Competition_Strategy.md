# ARES-RX Sentinel — Competition Strategy & Strategic Positioning
**Document Version:** 1.0.0  
**Target:** Kompetisi Desain IC / Proposal Inovasi Peruri  
**Status:** Approved by Technical Architect  

---

## 1. Value Proposition & Academic Differentiation

Mayoritas peserta kompetisi ASIC/Tiny Tapeout membuat proyek seperti:
- UART/SPI serializer standar
- Game sederhana / LED matrix
- Akselerator perkalian matriks / neural net mainan
- Modul kriptografi tanpa proteksi fisik antarmuka

**ARES-RX Sentinel membedakan diri secara radikal:**
1. **First-in-Class Hardware Boundary**: Kami tidak sekadar mendemonstrasikan decoder komunikasi, kami memecahkan masalah keamanan fisik nyata di level silikon—**menjaga antarmuka penerimaan digital dari serangan injeksi dan desinkronisasi**.
2. **Defensible Physical Grounding**: Tidak ada klaim berlebihan yang tidak dapat dibuktikan (*no unsubstantiated analog jamming claims*). Semua metrik didasarkan pada data logic analyzer perangkat keras nyata.
3. **Dual-Condition Trust Formulation**: Inovasi matematis otentikasi ganda:
   $$V_{trusted} = V_{physical} \land V_{protocol}$$
4. **Hardware Fail-Closed Guarantee**: Perlindungan aktif tingkat silikon yang mencegah kebocoran muatan berbahaya ke sistem host.

---

## 2. Relevansi Strategis untuk Peruri (Secure IoT & Critical Infrastructure)

Peruri sebagai BUMN penjamin keamanan dan keaslian membutuhkan teknologi hardware security untuk infrastruktur digital:
- **Perlindungan Smart Metering & Industrial Telemetry**: Melindungi sensor utilitas publik (air, gas, listrik) yang menggunakan frekuensi 433 MHz dari serangan manipulasi data konsumsi dan sabotase pulsa.
- **Kemandirian Silikon Nasional**: Membuktikan kemampuan rekayasa sirkuit terintegrasi (IC design) dari spesifikasi matematika hingga silikon SkyWater 130nm yang dapat diuji secara fisik.
- **Standar Trust Boundary Perangkat Keras**: Sentinel dapat menjadi IP block silikon standar pada chip IoT masa depan yang diproduksi atau disertifikasi oleh Peruri.

---

## 3. Struktur Presentasi Pembuktian (Winning Pitch Narrative)

```
[The Problem]
RF Receiver murah rentan injeksi glitch -> Decoder konvensional gagal diam-diam (silent corruption)

[The Scientific Grounding]
Analisis empiris 20 kHz / Discovery 3 membuktikan ortogonalitas pulsa Manchester memiliki jendela valid V = [8,10] U [16,20]

[The Innovation: ARES-RX Sentinel]
Arsitektur 3-Layer: Temporal Integrity + Protocol Syntax + Fail-Closed Isolation

[The Proof: Comparative Adversarial Testing]
Demonstrasi komparatif B vs S:
- Baseline (B): Terkorupsi dan reset terus menerus saat diserang glitch
- Sentinel (S): Mendeteksi 100% glitch, mengisolasi bus data, dan membunyikan tamper_alert
```
