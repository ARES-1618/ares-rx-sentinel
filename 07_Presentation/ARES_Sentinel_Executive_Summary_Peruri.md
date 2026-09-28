# RINGKASAN EKSEKUTIF
## ARES-RX Sentinel: Security Boundary Perangkat Keras Mandiri pada Demarkasi Baseband Digital untuk Evaluasi Keamanan IoT Peruri

**Dokumen:** Ringkasan Eksekutif untuk Jajaran Direksi dan Manajemen Peruri  
**Instansi Pengusul:** ARES Semikonduktor Teknologi  
**Tanggal:** 28 September 2026  
**Klasifikasi:** Dokumen Strategis Non-Teknis  
**Status Pengajuan:** Materi Paparan Teknis dan Usulan Inovasi (Tahap Evaluasi)  

---

### Ikhtisar Strategis

ARES-RX Sentinel adalah security boundary berbasis perangkat keras yang ditempatkan pada batas penerimaan digital setelah sinyal radio nirkabel didemodulasi oleh penerima fisik. Sentinel memeriksa integritas waktu (timing) pulsa dan sintaks format data secara deterministik sebelum data diteruskan ke sistem komputasi hilir (downstream). Ketika anomali waktu atau pelanggaran protokol terdeteksi, status kesalahan dikunci dalam batas satu siklus logika dan bus keluaran diisolasi secara otomatis dalam konfigurasi fail-closed (jalur data dinolkan) guna mencegah keluaran dari kondisi fault diteruskan ke mikrokontroler utama.

Pada pengujian verifikasi terikat terhadap satu skenario transmisi nominal dan delapan skenario serangan manipulasi kanonik, seluruh delapan skenario serangan kanonik berhasil dideteksi dan keluaran diamankan dalam batas satu siklus logika, sementara skenario nominal AV00 diterima tanpa fault pada pengujian kanonik. Rangkaian pembuktian ini mencakup 10.737 siklus kerja logika dan 118.107 evaluasi sinyal mandiri dengan tingkat kecocokan jejak (trace concordance) 100% antara model referensi perilaku dan logika sirkuit mikro synthesizable M4. Seluruh jejak audit pengujian telah dicatat dan dirantai secara berurutan dalam buku rekaman digital bersegel (tamper-evident forensic ledger) yang dapat diaudit dan diverifikasi ulang secara transparan kapan saja.

Status kesiapan desain saat ini berada pada tahap pra-silikon (pre-silicon). Seluruh desain logika sirkuit mikro dan tata letak fisik telah diselesaikan dan dikunci secara internal, sedangkan penyerahan berkas melalui portal Tiny Tapeout, proses fabrikasi silikon fisik, dan pengukuran langsung pada keping chip fisik masih berstatus pending. Estimasi konsumsi daya utama sebesar 57,90 unit sepermiliar watt pada frekuensi kerja 20 kilohertz merupakan hasil estimasi simulasi pasca-tata letak berbasis beban kerja, dan bukan merupakan hasil pengukuran pada keping silikon fisik (pengukuran fisik silikon belum tersedia).

Arsitektur pengamanan perangkat keras ini disiapkan untuk dievaluasi dalam konteks infrastruktur IoT kritis yang relevan dengan kebutuhan integritas penerimaan data, termasuk skenario perangkat pembaca verifikasi dokumen sekuriti negara dan meteran pintar utilitas publik yang dapat didiskusikan bersama Peruri. Sebagai langkah tindak lanjut strategis, tim pengembang merencanakan penyerahan resmi ke portal Tiny Tapeout, perancangan instrumen dan protokol pengujian laboratorium bersama tim evaluasi Peruri, serta studi integrasi modul percontohan pasca-penerimaan keping fisik silikon.

---

### Tabel Matriks Evaluasi Eksekutif

| Dimensi Evaluasi | Status Kualifikasi | Penjelasan Ringkas untuk Pimpinan Peruri |
| :--- | :---: | :--- |
| **Kesiapan Desain Sirkuit** | **Selesai & Tersegel Internal** | Seluruh desain logika dan implementasi fisik telah diselesaikan serta melalui pemeriksaan verifikasi internal M4–M5. |
| **Uji Ketahanan Serangan** | **8/8 Serangan Ditangkap & AV00 Diterima Tanpa Fault** | 8/8 skenario serangan kanonik ditangkap dan keluaran diamankan dalam satu siklus; skenario nominal AV00 diterima tanpa fault pada pengujian kanonik. |
| **Jejak Audit Forensik** | **Tamper-Evident & Dapat Diaudit** | Seluruh data pengujian dirantai secara digital dan dapat diaudit ulang secara transparan. |
| **Karakterisasi Daya** | **57,90 nW @ 20 kHz (Estimasi)** | Estimasi pasca-layout berbasis simulasi beban kerja; pengukuran fisik silikon belum tersedia. |
| **Fabrikasi Chip Fisik** | **Pra-Silikon (PENDING)** | Berkas siap serah; penyerahan portal Tiny Tapeout dan proses fabrikasi fisik berstatus pending. |
| **Pengukuran Silikon Nyata** | **Belum Tersedia** | Karakterisasi instrumen pada keping fisik akan dilaksanakan pasca-penerimaan chip nyata. |
| **Status Hubungan dengan Peruri** | **Tahap Evaluasi Teknis** | Diserahkan sebagai usulan pembuktian inovasi; tidak mengklaim sertifikasi resmi yang belum terbit. |

---

### Lampiran: Referensi Teknis dan Tata Kelola untuk Tim Penilai

1. **Dokumen Paparan Teknis Lengkap:** `07_Presentation/ARES_Sentinel_Peruri_Technical_Deck.md` (Paparan komprehensif 12 slide bagi evaluator teknis).
2. **Identifikasi Eksekusi Pengujian Otentik:** `WO011R1-FINAL-20260927-225358`.
3. **Kode Jangkar Digital Buku Rekaman Bukti:** `6f0d379d749953af6e29737bb7e29aeb99eed0698bd2019269dba63a191733f0`.
4. **Komit Penguncian Tata Letak Fisik:** Repositori Proyek ARES pada komit Git `a748738cf665e63bc9c215748ee5bead18422665`.
5. **Platform Penyerahan Manufaktur:** Tiny Tapeout (jadwal peluncuran TT08).
6. **Frekuensi Kerja Acuan Sistem:** 20 kilohertz.
7. **Catatan Epistemik Konsumsi Daya:** Nilai konsumsi daya sebesar 57,90 nW (nanowatt) pada frekuensi kerja 20 kilohertz yang dilaporkan pada dokumen teknis merupakan hasil estimasi simulasi berbasis beban kerja pasca-tata letak (OpenSTA Scenario B, toggle rate 0,1418 berbasis simulasi beban kerja VCD), dan secara tegas **bukan** hasil pengukuran langsung pada keping silikon fisik (pengukuran fisik silikon belum tersedia).
