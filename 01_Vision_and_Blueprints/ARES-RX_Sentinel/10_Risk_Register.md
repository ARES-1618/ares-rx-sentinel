# ARES-RX Sentinel — Risk Register

| Risk ID | Deskripsi Risiko | Kategori | Dampak | Probabilitas | Rencana Mitigasi | Status |
|---|---|---|---|---|---|---|
| **RSK-01** | Clock jitter transmitter melebihi window $\Delta = \pm 1$ cycle pada suhu ekstrem | Fisik / Hardware | Sedang | Rendah | Parameter $\Delta$ didesain sebagai synthesizable parameter; toleransi $\pm 11.1\%$ telah divalidasi pada capture riil. | Dimonitor |
| **RSK-02** | Penggunaan area Tiny Tapeout melebihi 1 tile ($160 \times 100\,\mu\text{m}^2$) | PPA / Silikon | Tinggi | Rendah | Modul Sentinel didesain ultra-lean ($< 120$ cells); tidak ada memori SRAM besar, hanya register shift 96-bit dan counter 6-bit. | Terkendali |
| **RSK-03** | Metastabilitas pada input asinkron $rx\_in$ | Sirkuit Digital | Tinggi | Sedang | Wajib menggunakan 2-stage D-FF synchronizer sebelum sinyal masuk ke edge detector dan interval counter. | Diterapkan |
| **RSK-04** | Klaim berlebihan (over-promising) deteksi RF jamming ditolak reviewer | Akademis / Reputasi | Tinggi | Rendah | Klaim dikunci ketat: Hanya mendeteksi anomali pada representasi domain digital ($rx\_in$); tidak ada klaim deteksi analog langsung. | Tereliminasi |
| **RSK-05** | False alarm rate tinggi pada ambient noise di luar transmisi | Fungsionalitas | Sedang | Rendah | Layer 1 mengharuskan pola preamble valid terlebih dahulu sebelum mengaktifkan evaluasi frame aktif. | Terkendali |
