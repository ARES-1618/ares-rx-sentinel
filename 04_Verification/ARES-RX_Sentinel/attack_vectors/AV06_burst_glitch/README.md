# AV06: Receiver-Noise / AGC-Hash Disturbance Vector

## 1. Physical Description
Merepresentasikan kondisi fisik ketika tidak ada pemancar RF aktif (*no intended carrier*). Di dunia nyata, Automatic Gain Control (AGC) pada modul demodulator analog OOK/ASK (seperti RXB6/SYN470R) menaikkan gain ke tingkat jenuh maksimum, mengubah kebisingan termal frekuensi tinggi menjadi digital hash acak berdurasi $1 - 4$ clock cycles ($50 - 200\,\mu\text{s}$) secara masif (tercatat 7,000+ pulsa pada capture empiris `noise.csv`).

## 2. Stimulus Parameters
- Sifat sinyal: Rentetan pulsa pseudo-random bolak-balik dengan durasi acak $\tau \in \{1, 2, 3, 4\}$ sampling cycles ($50, 100, 150, 200\,\mu\text{s}$).
- Siklus: 50 pulsa acak berturut-turut.

## 3. Expected Behaviors
- **Baseline Design ($B$)**:
  - Mengalami reset loop thrashing terus menerus karena setiap rising edge noise memicu `transmission_begin`.
  - Mengonsumsi daya dinamis berlebih akibat switching frekuensi tinggi.
- **ARES-RX Sentinel ($S$)**:
  - Layer-1 langsung memblokir pulsa sempit ($N \le 7$) sehingga tidak pernah mencapai modul deserialisasi atau mereset register data.
  - Sistem tetap berada dalam status aman tanpa kebocoran data.

## 4. Acceptance Criteria
- [ ] Penolakan 100% pulsa $N \in [1, 4]$.
- [ ] Logika deserializer internal terlindungi dari spurious reset thrashing.
