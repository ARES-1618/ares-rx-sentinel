# SLIDE PITCH DECK NASKAH PRESENTASI
## ARES-RX Sentinel: Silicon-Level Trusted Digital Reception Boundary
### Inovasi Keamanan Perangkat Keras untuk Kedaulatan IoT Kritis & Ekosistem Peruri

---

**Format:** Slide Deck Script & Presentation Guide (12 Slides)  
**Estimasi Durasi Pitch:** 8–10 Menit  
**Target Audiens:** Dewan Juri Kompetisi Desain IC, Pimpinan Peruri (Direksi Teknologi & Inovasi), dan Pakar Keamanan Siber  
**File Lokasi:** `06_Demonstration/ARES-RX_Sentinel/presentation/ARES_Sentinel_Pitch_Deck.md`  

---

```
================================================================================
SLIDE 1: JUDUL & IDENTITAS PROYEK
================================================================================
[Visual: Render Layout Silikon GDSII ARES-RX Sentinel pada Tiny Tapeout TT08,
 Logo Peruri & Logo ARES Semikonduktor, Badge: "SkyWater 130nm Tapeout-Ready"]

JUDUL:
ARES-RX Sentinel
Silicon-Level Trusted Digital Reception Boundary untuk Pengamanan Infrastruktur IoT Kritis

SUBJUDUL:
Mengamankan Antarmuka Digital Baseband dari Ancaman Siber-Fisik dengan Efisiensi Nanowatt

Presenter: Tim Rekayasa ARES Semikonduktor Technology
Target: Kompetisi Desain IC Nasional & Proposal Inovasi Strategis Peruri 2026

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 0:00 - 0:45):
"Selamat pagi Dewan Juri dan Pimpinan Peruri yang terhormat.
Hari ini, kami mempersembahkan ARES-RX Sentinel: terobosan arsitektur sirkuit
terpadu (ASIC) buatan anak bangsa yang dirancang untuk memecahkan titik lemah
paling rentan pada perangkat nirkabel nasional: antarmuka penerimaan digital.

Bukan sekadar konsep di atas kertas atau simulasi perangkat lunak, ARES-RX
Sentinel telah selesai dirancang, diverifikasi secara fisik, dan siap diproduksi
(tapeout-ready) pada teknologi silikon SkyWater 130nm dengan konsumsi daya hanya
50.9 nanowatt. Mari kita lihat mengapa inovasi ini sangat krusial bagi kedaulatan
teknologi Peruri dan Indonesia."
================================================================================
```

---

```
================================================================================
SLIDE 2: PERMASALAHAN: THE DEMODULATOR BLIND SPOT
================================================================================
[Visual: Diagram alur sinyal nirkabel konvensional.
 Antena -> RF Transceiver IC -> [Jalur rx_in tanpa pelindung] -> MCU Core.
 Tanda seru merah besar pada pin rx_in: "The Blind Spot: Unprotected Baseband"]

POIN UTAMA:
1. Komunikasi Nirkabel Kritis: Jutaan smart meter (listrik/air/gas) dan sensor logistik Peruri menggunakan komunikasi Sub-GHz.
2. Celah Mendasar: Demodulator radio komersial meneruskan semua pulsa mentah dari udara langsung ke pin mikrokontroler (MCU).
3. Kegagalan Mitigasi Software:
   - Glitch pulsa mikro memicu "Interrupt Storm" (baterai habis dalam hitungan hari).
   - Paket malformed memicu buffer overflow pada memori MCU.
   - Sinyal corrupt dieksekusi sebagai perintah yang salah (silent corruption).

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 0:45 - 1:30):
"Mari kita mulai dari permasalahan di lapangan.
Peruri mengamankan aset negara, mulai dari dokumen berharga hingga rantai pasok
logistik dan meteran pintar utilitas nasional. Seluruh perangkat ini menerima data
nirkabel dari udara.

Namun, di mana letak kelemahannya?
Demodulator radio komersial saat ini tidak memiliki kecerdasan keamanan. Radio hanya
mengubah gelombang menjadi pulsa digital '0' dan '1' mentah, lalu menyerahkannya
langsung ke mikrokontroler.

Jika penyerang menyuntikkan pulsa glitch liar atau memotong paket di tengah jalan,
apa yang terjadi? Mikrokontroler akan kebanjiran interupsi, baterai terkuras,
memorinya mengalami buffer overflow, atau bahkan mengeksekusi data yang korup
secara diam-diam (silent corruption). Perangkat lunak di mikrokontroler tidak mampu
menangkal serangan ini secara instan!"
================================================================================
```

---

```
================================================================================
SLIDE 3: LANDASAN ILMIAH & MATEMATIKA TRUST BOUNDARY
================================================================================
[Visual: Grafik transisi pulsa Manchester pada osiloskop/logic analyzer.
 Formula matematika besar dengan efek glow emas:
 V_trusted = V_physical ∧ V_protocol]

POIN UTAMA:
1. Ortogonalitas Pulsa Manchester 20 kHz:
   - Half-bit nominal: 9 siklus clock (jendela valid: 8..10 siklus).
   - Full-bit nominal: 18 siklus clock (jendela valid: 16..20 siklus).
   - Segala pulsa di luar jendela ini adalah anomali fisik atau serangan injeksi!
2. Formulasi Otentikasi Ganda:
   - V_physical : Integritas domain waktu (anti-glitch & anti-desinkronisasi).
   - V_protocol : Integritas sintaksis frame (panjang 192-bit & fixed fields).
3. Prinsip Fail-Closed: Jika salah satu kondisi tidak terpenuhi, V_trusted = 0.

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 1:30 - 2:30):
"Untuk menyelesaikan masalah ini, kami tidak menggunakan pendekatan coba-coba.
Kami membangun formulasi matematika berbasis sifat fisik sinyal modulasi Manchester.

Melalui tangkapan hardware analyzer riil, kami membuktikan bahwa pulsa radio
memiliki ortogonalitas waktu yang tegas. Pada clock 20 kHz, pulsa half-bit valid
pasti berada di antara 8 hingga 10 siklus, dan full-bit di antara 16 hingga 20 siklus.
Di luar jendela tersebut, sinyal tersebut secara matematis BUKAN data yang sah!

Oleh karena itu, kami menetapkan aturan mutlak:
V_trusted = V_physical DAN V_protocol.
Data hanya dianggap sah jika ia mematuhi hukum fisika gelombang DAN mematuhi
tata bahasa protokol 192-bit. Jika ada satu syarat saja yang dilanggar, silikon
kami akan menolak data tersebut secara mutlak!"
================================================================================
```

---

```
================================================================================
SLIDE 4: SOLUSI: ARES-RX SENTINEL SILICON CORE
================================================================================
[Visual: Diagram blok 3D chip ARES-RX Sentinel yang berdiri sebagai dinding gerbang
 (firewall) antara Radio Baseband dan Host Microcontroller]

POIN UTAMA:
1. Posisi Arsitektur: "The Silicon Bouncer" — Berada di level perangkat keras gerbang logika, independen dari CPU.
2. 3-Layer Defense-in-Depth:
   - Layer 1: Temporal Integrity Sentinel (Pengawal Fisik Pulsa)
   - Layer 2: Frame Syntax Monitor (Pengawal Tata Bahasa 192-Bit)
   - Layer 3: Hardware Fail-Closed Isolation (Gerbang Isolasi & Nol-kan Bus)
3. Zero CPU Overhead: 0% beban komputasi prosesor, 0 byte konsumsi RAM MCU.
4. Determinisme Mutlak: Deteksi kesalahan dan proteksi terjadi dalam 1 siklus clock.

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 2:30 - 3:30):
"Inilah solusi kami: ARES-RX Sentinel.
Sebuah IP Core silikon yang berfungsi sebagai 'satpam gerbang' di tingkat sirkuit
terpadu. Kami meletakkannya tepat di antara transceiver radio dan prosesor utama.

ARES-RX Sentinel bekerja dalam 3 lapisan pertahanan independen:
Layer 1 menjaga integritas waktu setiap pulsa radio.
Layer 2 mengawal struktur tata bahasa protokol 192-bit secara otonom.
Layer 3 mengisolasi jalur data dan menolkan bus seketika saat terjadi anomali.

Karena seluruh logika ini tertanam di gerbang logika fisik silikon, mikrokontroler
utama terbebas 100% dari beban parsing data kotor. Sistem menjadi kebal terhadap
segala bentuk memory corruption dan serangan berbasis buffer!"
================================================================================
```

---

```
================================================================================
SLIDE 5: DETAIL ARSITEKTUR 3-LAYER & SIGNAL FLOW
================================================================================
[Visual: Diagram arsitektur interkoneksi L1 -> L2 -> Arbiter -> L3.
 Sinyal rx_in masuk ke L1, status reception_active mengaktifkan L2,
 Fault Arbiter menyelesaikan konflik ke L3, output uo_out di-gating]

POIN UTAMA:
- Layer 1 (ares_timing_sentinel.v):
  * FSM 4-State: IDLE -> ARMED -> ACTIVE -> LONG_GAP_PENDING.
  * Menolak noise awal (squelch), menjebak runt-pulse (<8 siklus), dan memvalidasi keheningan akhir (EOP = 64 siklus).
- Layer 2 (ares_frame_fsm.v):
  * Pencacah otonom 0..191 siklus (tanpa ketergantungan flag eksternal).
  * Validasi seketika field tetap: Preamble (0xAAAAAAAA), Type (0xD391), Constant (0x0DFFFFFE).
  * Payload dinamis (ID sensor & suhu) lolos secara transparan.
  * Menjebak pemotongan frame (truncation) dan frame berlebih (overrun).
- Layer 3 (ares_isolation_l3.v):
  * Sticky Fault Latch mengunci status bahaya.
  * Zeroization Gate memaksa bus output data menjadi 0x00 dalam 1 siklus clock.

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 3:30 - 4:45):
"Bagaimana cara kerjanya secara mendalam?
Di Layer 1, FSM mendeteksi pulsa awal yang sah sebelum membuka jendela penerimaan
(reception_active). Jika penyerang menyuntikkan pulsa kerdil (runt pulse), Layer 1
langsung membunyikan fault.

Di Layer 2, pencacah otonom memeriksa setiap bit saat sampel tiba. Kami memvalidasi
preamble 32-bit, kode tipe, dan konstanta protokol secara instan. Jika data sah,
payload sensor suhu dan ID perangkat diteruskan secara mulus tanpa penundaan.
Namun jika bit field tetap dipalsukan atau ada bit berlebih (overrun), Layer 2
seketika membunyikan alarm.

Kedua sinyal kesalahan ini disatukan oleh Fault Arbiter deterministik menuju Layer 3.
Dalam waktu TEPAT 1 siklus clock, Layer 3 mengaktifkan 'bus zeroization':
seluruh jalur data ke mikrokontroler diputus dan dipaksa menjadi nol mutlak (0x00),
sementara pin tamper_alert menyalakan interupsi darurat ke sistem pusat."
================================================================================
```

---

```
================================================================================
SLIDE 6: BUKTI FISIK SILIKON: TAPE-OUT READY PADA SKYWATER 130nm
================================================================================
[Visual: Foto Tata Letak Post-Route Silicon GDSII, Floorplan Tile TT08,
 dan Grafik Ringkasan PPA Benchmark]

POIN UTAMA (Data Fisik Reconciled Sign-Off M5):
- Proses Fabrikasi: SkyWater 130nm High-Density (`sky130_fd_sc_hd`), TT08 Platform.
- Dimensi Die: 161.00 µm × 111.52 µm (Standard Tile 1x1, Luas: 17,954 µm²).
- Luas Logika Standard Cell: 6,477.46 µm² (36.08% luas tile kotor).
- Konsumsi Daya Sangat Rendah:
  * 50.90 nW pada clock operasi 20 kHz (Overhead bersih hanya +9.28 nW).
  * Mampu menyala >20 TAHUN hanya dengan satu baterai koin CR2032!
- Performa & Margin Waktu: Fmax = 123.7 MHz (Setup Slack +11.88 ns pada clock uji 50 MHz).
- Kualitas Pabrikasi: 0 Active Manufacturing DRC Violations, 100% LVS Match (758/758 gerbang).

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 4:45 - 6:00):
"Dewan Juri yang terhormat, keunggulan terbesar kami adalah kesiapan fisik silikon.
Kami telah merampungkan seluruh alur Place & Route hingga level GDSII fisik
menggunakan PDK SkyWater 130nm pada platform uji Tiny Tapeout TT08.

Lihatlah angka-angka terukur ini:
1. Konsumsi daya operasi kami pada 20 kHz hanya 50.9 nanowatt! Overhead keamanan
   yang kami tambahkan hanya 9.28 nanowatt. Ini berarti chip ini bisa beroperasi
   lebih dari 20 tahun hanya dengan sebuah baterai koin kecil!
2. Kecepatan maksimalnya mencapai 123 MHz, memberikan margin keamanan waktu yang
   luar biasa tinggi.
3. Kepatuhan manufaktur: 0 pelanggaran DRC aktif dan 100% cocok pada verifikasi LVS
   terhadap 758 gerbang logika.

Desain ini bukan lagi simulasi—desain ini sudah lolos pra-pemeriksaan resmi dan siap
masuk ke jalur pabrikasi semikonduktor!"
================================================================================
```

---

```
================================================================================
SLIDE 7: DEMONSTRASI HARDWARE KOMPARATIF: BASELINE VS SENTINEL
================================================================================
[Visual: Cuplikan output Terminal CLI Hardware Demo (ares_hardware_demo.py),
 Menampilkan tabel perbandingan side-by-side Baseline vs Sentinel pada 6 skenario]

TABEL HASIL UJI KOMPARATIF:
+----+-----------------------+---------------------+-------------------+
| No | Skenario Pengujian    | Baseline Demodulator| ARES-RX Sentinel  |
+----+-----------------------+---------------------+-------------------+
| 1  | Transmisi Valid       | Lolos (Data Masuk)  | Lolos (Transparan)|
| 2  | Runt Pulse Glitch     | Diam / Korup        | TRAPPED (L1 Runt) |
| 3  | Mid-Band Desync       | Desinkronisasi      | TRAPPED (L1 Desync|
| 4  | Preamble Corruption   | Menerima Data Salah | TRAPPED (L2 Field)|
| 5  | Overrun Attack (>192) | Buffer Overflow     | TRAPPED (L2 Over) |
| 6  | Real Hardware Trace   | Lolos (Nominal)     | Lolos (0 False Pos|
+----+-----------------------+---------------------+-------------------+

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 6:00 - 7:00):
"Kami telah menguji ketahanan ARES-RX Sentinel secara langsung melawan sistem
baseline tanpa proteksi melalui 6 skenario komparatif yang ketat:

Ketika diberi sinyal normal dan rekaman hardware capture riil (Skenario 1 & 6),
Sentinel bersikap 100% transparan dengan tingkat False Alarm Rate nol persen.

Namun saat diserang:
- Pada serangan Runt Glitch dan Desinkronisasi (Skenario 2 & 3), sistem baseline
  mengalami kekacauan timing, sedangkan Sentinel langsung menjebaknya di Layer 1.
- Pada serangan Preamble Palsu dan Overrun 193-bit (Skenario 4 & 5), baseline
  mengalami buffer overflow dan menerima data berbahaya. Sebaliknya, Sentinel
  seketika mengunci fault di Layer 2, menolkan bus data, dan melindungi sistem host.

Tidak ada satu bit data berbahaya pun yang pernah lolos ke host!"
================================================================================
```

---

```
================================================================================
SLIDE 8: NILAI STRATEGIS UNTUK PERURI & KEDAULATAN NASIONAL
================================================================================
[Visual: Diagram Ekosistem Peruri yang diperkuat oleh ARES-RX Sentinel:
 Pita Cukai Cerdas, Smart Metering PLN/PDAM, Track & Trace Kontainer, GovTech Secure IC]

POIN STRATEGIS PERURI:
1. Perlindungan Smart Metering Utilitas Publik:
   Mengamankan jutaan meteran listrik (PLN), gas (PGN), dan air (PDAM) dari sabotase radio dan pencurian konsumsi energi.
2. Keamanan Rantai Pasok Pita Cukai & Logistik Berharga:
   Mencegah sindikat pemalsu melakukan radio spoofing terhadap status kontainer berharga negara.
3. Kedaulatan Desain Silikon Nasional:
   Membuktikan bahwa Indonesia mampu merancang IP Core sirkuit terpadu keamanan tinggi secara mandiri, mengurangi ketergantungan impor chip asing.
4. Nilai Komersial Tinggi:
   IP Block ini dapat dilisensikan atau disertifikasi oleh Peruri untuk seluruh vendor IoT yang beroperasi di wilayah hukum Indonesia.

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 7:00 - 8:00):
"Mengapa inovasi ini sangat bernilai bagi Peruri?
Peruri adalah benteng penjamin keaslian dan kedaulatan negara. Melalui ARES-RX
Sentinel, Peruri dapat memperluas portofolio pengamanannya langsung ke level silikon:

Pertama, mengamankan infrastruktur utilitas nasional (Smart Metering PLN dan PDAM)
dari sabotase gelombang radio yang dapat melumpuhkan distribusi energi publik.

Kedua, memperkuat pengawasan rantai pasok pita cukai cerdas dan pelacak aset logistik
berharga agar kebal terhadap manipulasi nirkabel.

Ketiga, dan yang paling penting: Kedaulatan Semikonduktor.
Kita tidak lagi hanya menjadi konsumen chip impor yang rentan disusupi hardware
trojan. Kita mampu mendesain IP Core silikon berstandar keamanan tinggi sendiri
di bawah naungan Peruri!"
================================================================================
```

---

```
================================================================================
SLIDE 9: ROADMAP IMPLEMENTASI & TAHAPAN HILIRISASI
================================================================================
[Visual: Timeline Hilirisasi 3 Fase dari Tapeout 2026 hingga Adopsi Massal 2028]

ROADMAP HILIRISASI (2026 - 2028):
- FASE 1 (Q4 2026 - Q1 2027) — Tapeout & Silicon Validation:
  * Fabrikasi wafer silikon via Tiny Tapeout TT08 (SkyWater Foundry).
  * Pengujian fisik laboratorium dan karakterisasi kelistrikan chip.
- FASE 2 (Q2 2027 - Q4 2027) — Pilot Project Ekosistem Peruri:
  * Pembuatan Development Board untuk gateway pelacak aset cukai Peruri.
  * Uji lapangan bersama mitra utilitas (Smart Metering).
- FASE 3 (2028) — Komersialisasi & Standarisasi Nasional:
  * Integrasi Hard Macro ke dalam Secure Microcontroller buatan Peruri.
  * Pengusulan standar hardware security boundary nasional bersama BSSN.

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 8:00 - 8:45):
"Roadmap kami sangat jelas, terukur, dan dapat dicapai.
Saat ini kami berada di akhir Fase 1 dengan artefak fisik yang siap fabrikasi.
Pada tahun 2027, kami akan meluncurkan Evaluation Board untuk diuji langsung pada
gateway pelacak logistik sekuriti Peruri.
Dan pada tahun 2028, ARES-RX Sentinel siap diintegrasikan sebagai hard-macro
ke dalam chip Secure Microcontroller nasional, bekerja sama dengan BSSN dan
kementerian terkait."
================================================================================
```

---

```
================================================================================
SLIDE 10: KESIMPULAN & PENUTUP
================================================================================
[Visual: Foto seluruh tim pengembang, gambar die layout silikon ARES-RX Sentinel,
 Tulisan besar: "Securing the Nation's Silicon from the Physical Boundary Up"]

RINGKASAN KEUNGGULAN UTAMA:
- Pertama di Kelasnya: Trusted Digital Reception Boundary di level silikon.
- Ekstrem Efisien: Konsumsi daya 50.90 nW, tahan >20 tahun dengan baterai koin.
- Terbukti Fisik: SkyWater 130nm Tapeout-Ready, 0 DRC, 100% LVS Clean.
- Kedaulatan Nyata: Menjadikan Peruri pelopor keamanan semikonduktor Indonesia.

--------------------------------------------------------------------------------
NASKAH PRESENTER (Waktu: 8:45 - 9:30):
"Bapak dan Ibu Dewan Juri yang terhormat,
Keamanan siber masa depan tidak bisa lagi hanya bergantung pada perangkat lunak
yang rapuh. Keamanan sejati harus ditegakkan sejak gerbang pertama di tingkat silikon.

ARES-RX Sentinel membuktikan bahwa inovasi berkelas dunia dengan presisi nanodetik
dan efisiensi nanowatt dapat lahir dari tangan anak bangsa.
Kami siap melangkah bersama Peruri untuk mengawal kedaulatan teknologi dan keamanan
aset digital Republik Indonesia.

Terima kasih. Kami siap menyambut pertanyaan dan diskusi mendalam dari Dewan Juri."
================================================================================
```
