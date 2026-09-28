# ARES-RX Sentinel — Security Model
**Document Version:** 1.0.0  
**Classification:** Core Security Specification  
**Status:** Approved by Technical Architect  

---

## 1. Security Philosophy: Zero Trust at Physical Boundary

Sentinel mengimplementasikan prinsip **Zero-Trust Physical Ingestion**. Setiap transisi tepi sinyal yang masuk melalui pin `rx_in` dianggap berbahaya dan tidak terpercaya sampai dibuktikan sebaliknya melalui verifikasi dua tingkat:
1. **Bukti Fisik ($\mathcal{P}$)**: Apakah timing transisi mematuhi hukum fisika modulasi Manchester ($V_{physical} = 1$)?
2. **Bukti Protokol ($\mathcal{S}$)**: Apakah sekuens simbol mematuhi konvensi struktural frame ($V_{protocol} = 1$)?

---

## 2. Invariants Keamanan (Formal Security Properties)

### Properti 1: Containment Invariant (Isolasi Mutlak)
$$\forall t, \quad (\text{FaultLatch}(t) = 1 \lor V_{trusted}(t) = 0) \implies D_{out}(t) = 0x00$$
Tidak ada bit data yang dapat diteruskan ke bus downstream kecuali seluruh tahapan validasi lulus secara simultan.

### Properti 2: Sticky Alert Invariant (Ketahanan Status Alarm)
$$\text{TamperAlert}(t_1) = 1 \implies \forall t_2 \ge t_1, \quad \text{TamperAlert}(t_2) = 1 \quad (\text{selama } rst\_n = 1)$$
Status peringatan manipulasi bersifat "sticky"; penyerang tidak dapat meniadakan peringatan dengan mengirimkan paket valid setelah melakukan injeksi glitch.

### Properti 3: Glitch Rejection Invariant (Kekebalan Noise Transien)
$$\forall \text{pulse } p \text{ dengan durasi } \tau(p) < 400\,\mu\text{s}, \quad \text{ResetDeserializer}(p) = 0$$
Pulsa noise sempit tidak pernah diizinkan memicu reset parasitik pada deserializer data.

---

## 3. Asumsi Lingkungan & Batas Tanggung Jawab

| Entitas | Tanggung Jawab Sentinel | Tanggung Jawab Sistem Host / SoC Eksternal |
|---|---|---|
| **RF Demodulator Output** | Memfilter glitch, mendeteksi anomali interval | Menyediakan sinyal demodulasi digital biner |
| **Koneksi Bus Data** | Zeroize output saat fault | Membaca pin `tamper_alert` sebelum memproses data |
| **Reset Sistem** | Mempertahankan latch hingga hard reset | Mengirimkan sinyal hard reset (`rst_n`) setelah audit fault |
| **Otentikasi Kriptografi**| Menyediakan aliran data bersih bebas cacat fisik | Melakukan verifikasi HMAC / Signature / Replay counter |
