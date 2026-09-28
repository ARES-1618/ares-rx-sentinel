# ARES-RX Sentinel — Project Charter

## 1. Project Identity
- **Project Name:** ARES-RX Sentinel
- **Target Platform:** Tiny Tapeout (TT07 / TT08 / TT09) — SkyWater 130nm ASIC
- **Core Mission:** Membangun **Trusted Digital Reception Boundary** berbasis silikon untuk memproteksi receiver RF sub-GHz Manchester asinkron dari injeksi anomali temporal, glitch, pulsa abnormal, dan paket malformed secara hardware fail-closed.
- **Sponsor / Strategic Partner:** Peruri (Konteks Secure IoT & Hardware Security)
- **Role Alignment:**
  - **Technical Architect & Research Direction:** Human Architect (Ahmad) / Research Agent
  - **Implementation Engineer:** Copilot / Automated RTL Builder

---

## 2. Business & Security Case
Penerima RF sub-GHz sederhana (433.92 MHz ISM Band) banyak digunakan pada meteran air/gas pintar, remote keyless entry, sensor industri, dan smart home. Karakteristik analog penerima OOK/ASK murah (seperti RXB6 atau SYN470R) menyaturasi gain (AGC) saat tidak ada transmisi, menghasilkan hash acak, rentan terhadap glitch transien, dan rentan terhadap manipulasi pulsa. 

Jika mikrokontroler atau ASIC downstream menerima aliran digital mentah tanpa batas kepercayaan fisik (*trust boundary*), sistem dapat mengalami *denial-of-service*, *buffer desynchronization*, atau manipulasi data tersembunyi.

ARES-RX Sentinel menyelesaikan masalah ini tepat di lapisan paling awal silikon digital:
1. Memvalidasi integritas fisikal-temporal (Layer 1).
2. Memvalidasi kepatuhan sintaks protokol frame (Layer 2).
3. Mengisolasi bus data host secara fail-closed saat anomali terdeteksi (Layer 3).

---

## 3. Batasan & Lingkup Proyek (In-Scope vs Out-of-Scope)

### Dalam Lingkup (In-Scope):
- Deteksi anomali temporal durasi pulsa ($N_{edge} \notin \mathcal{V}$) pada $rx\_in$.
- Penolakan digital noise/hash transien AGC tanpa merusak status deserializer.
- Validasi kepatuhan format bingkai Manchester (Preamble 32-bit, Constant 32-bit, Tipe Data).
- Pemutusan jalur bus data (*zeroization*) dan latch tanda bahaya (*sticky tamper alert*).
- Pembuktian adversarial melalui suite AV01 s/d AV08.
- Sintesis ASIC SkyWater 130nm dengan luas area $< 1$ tile Tiny Tapeout ($160 \times 100\,\mu\text{m}^2$).

### Di Luar Lingkup (Out-of-Scope):
- Pemrosesan sinyal analog frekuensi tinggi (RF frontend / mixer / filter analog).
- Dekripsi kriptografi tingkat tinggi (AES/ECC) di dalam inti Sentinel (diserahkan ke downstream core).
- Klaim deteksi jamming elektromagnetik yang tidak menghasilkan anomali pada sinyal digital demodulasi.
