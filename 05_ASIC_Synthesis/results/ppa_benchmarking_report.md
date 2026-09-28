# ARES-RX Sentinel — Official PPA Benchmarking Report (Stage M5-E Closed / Stage M5-F Open)
**Authority:** Technical Architect / Research Direction  
**Work Order:** `WO-2026-M5-F-001` (Physical Implementation / P&R Opening)  
**Standard Process:** SkyWater 130nm High-Density CMOS (`sky130_fd_sc_hd`)  
**Operating Conditions:** Typical-Typical (TT), $25^\circ\text{C}$, $1.80\,\text{V}$ (`tt_025C_1v80`)  
**PDK Liberty File:** `sky130_fd_sc_hd__tt_025C_1v80.lib` (SHA-256: `8e78e14442062dba34d414fca6490b2f6b96038d4510d1438ca44fee31487135`)  
**EDA Toolchain:** Yosys 0.52 (`fee39a3284c9...`) & OpenSTA 2.0.17  
**Timestamp:** 2026-09-27T15:47:00+07:00  
**Status:** M5-E CLOSED / QUALIFIED PRE-LAYOUT — M5-F OPEN  

---

## 1. EXECUTIVE SUMMARY & ARTIFACT GROUNDING

Laporan ini menyajikan hasil karakterisasi komparatif fisik (*apples-to-apples comparison*) antara **Baseline Receiver Tanpa Perlindungan ($B$)**, **Subsistem Demarkasi Sentinel Saja ($S_{\text{core}}$)**, dan **Top Terintegrasi Terlindungi ($S_{\text{top}}$)**.

Karakterisasi dilakukan berdasarkan mandat arsitektur **WO-2026-M5-F-001**, dengan normalisasi metodologi dan klasifikasi epistemik yang ketat:
1. **Reklasifikasi Estimasi Daya**: Seluruh angka konsumsi daya diklasifikasikan secara formal sebagai **estimasi pra-tata-letak berbasis aktivitas (*activity-dependent pre-layout estimates*)**, bukan konsumsi daya aktual hardware. Analisis mencakup tiga skenario aktivitas asumtif ($\alpha = 0.05, 0.10, 0.20$ dengan siklus kerja 50%).
2. **Estimasi Arus Bocor Berbasis Liberty**: Disipasi daya statis diklasifikasikan sebagai **$P_{leak}^{\text{prelayout, lib}} = 2.74\,\text{nW}$** (*Liberty-based pre-layout leakage estimate*), bukan pengukuran kebocoran silikon fisik (*physical silicon leakage*).
3. **Pemisahan Semantik Jam**:
   - $F_{\text{functional}} = 20\,\text{kHz}$ ($T_{clk} = 50\,\mu\text{s}$) adalah **jam operasional protokol fungsional** ($N_{HB}=8..10$, $N_{BIT}=16..20$, $N_{EOF}=64$).
   - $50\,\text{MHz}$ ($T = 20\,\text{ns}$) adalah **target stres STA tiruan** untuk mengekstrak margin setup/hold dan delay jalur kritis.
4. **Hirarki Frekuensi Silikon & Disambiguasi Kecepatan**:
   - **Pre-layout reg-to-reg Fmax metric**: $F_{\max, \text{reg}} \approx \mathbf{185.3\,\text{MHz}}$ ($T_{crit, \text{reg}} = 5.3947\,\text{ns}$, delay murni antar-register tanpa penalti I/O).
   - **Pre-layout I/O-constrained STA metric**: $F_{\max, \text{IO}} \approx \mathbf{85.95\,\text{MHz}}$ ($T_{crit, \text{IO}} = 11.6344\,\text{ns}$, jalur pad-to-pad di bawah asumsi budget I/O).
   - **Tiny Tapeout I/O input rating**: $\approx \mathbf{66\,\text{MHz}}$ (rating frekuensi input clock pad eksternal dengan *insertion delay* pad $\le 10\,\text{ns}$).
5. **Asumsi Batasan I/O SDC**:
   - Parameter batasan `set_input_delay 5.0 ns`, `set_output_delay 5.0 ns`, dan `set_load 30 fF` diklasifikasikan secara eksplisit sebagai **asumsi batasan STA (*STA constraint assumptions*)**, bukan pengukuran fisik pad Tiny Tapeout riil.
6. **Akuntansi Logika Bruto vs. Bersih**:
   - Gross Sentinel Core ($S_{\text{core}}$): 214 sel ($2,009.43\,\mu\text{m}^2$).
   - Baseline ($B$): 575 sel ($4,979.78\,\mu\text{m}^2$).
   - Top Terintegrasi ($S_{\text{top}}$): 733 sel ($6,447.43\,\mu\text{m}^2$).
   - Overhead bersih top-level ($\Delta = S_{\text{top}} - B$): $+158$ sel (+27.48%), $+1,467.65\,\mu\text{m}^2$ (+29.47%).
   - Selisih optimasi hirarki: $(575 + 214) - 733 = 56$ sel tereduksi berkat optimasi sintesis lintas batas (*boundary logic optimization*).
7. **Metrik Luas Area Tile**:
   - Fraksi luas sel standar pra-tata-letak = **$35.75\%$** terhadap luas kotor tile Tiny Tapeout TT08 $1 \times 1$ ($18,036\,\mu\text{m}^2$).
   - Kelonggaran luas sel standar pra-tata-letak (*pre-layout cell-area headroom*) = **$64.25\%$** ($11,588\,\mu\text{m}^2$).
   - Kepastian *tile fit* dan densitas fisik akhir ditangguhkan hingga pelaksanaan Place & Route (Stage M5-F).

---

## 2. COMPARATIVE PPA BENCHMARKING MATRIX

| Metrik Karakterisasi ASIC | Baseline Unprotected ($B$) | Sentinel Subsystem ($S_{\text{core}}$) | Integrated Protected Top ($S_{\text{top}}$) | Overhead Bersih Top ($\Delta = S_{\text{top}} - B$) | Overhead Relatif ($\%$) | Batas Epistemik & Status |
|---|---|---|---|---|---|---|
| **Total Standard Cells** | **575** | **214** | **733** | **$+158$ sel** | **$+27.48\%$** | Kompak (56 sel teroptimasi lintas-batas) |
| **Sequential Flops (DFF)** | 110 | 40 | 142 | $+32$ flops | $+29.09\%$ | Nol inferred latches |
| *DFF Breakdown* | 97 dfrtp, 1 dfstp, 12 dfxtp | 38 dfrtp, 2 dfstp | 127 dfrtp, 3 dfstp, 12 dfxtp | $+30$ dfrtp, $+2$ dfstp | — | Reset asinkron/sinkron |
| **Combinational Gates** | 465 | 174 | 591 | $+126$ gerbang | $+27.10\%$ | MUX, pembanding, isolasi fail-closed |
| **Total Standard Cell Area**| **$4,979.78\,\mu\text{m}^2$** | **$2,009.43\,\mu\text{m}^2$** | **$6,447.43\,\mu\text{m}^2$** | **$+1,467.65\,\mu\text{m}^2$**| **$+29.47\%$** | Ukuran sel standar pra-tata-letak |
| *Sequential Area* | $2,693.83\,\mu\text{m}^2$ (54.1%) | $1,003.46\,\mu\text{m}^2$ (49.9%) | $3,497.10\,\mu\text{m}^2$ (54.2%) | $+803.27\,\mu\text{m}^2$ | $+29.82\%$ | Proporsi sequential terjaga konsisten |
| *Combinational Area* | $2,285.94\,\mu\text{m}^2$ (45.9%) | $1,005.96\,\mu\text{m}^2$ (50.1%) | $2,950.33\,\mu\text{m}^2$ (45.8%) | $+664.39\,\mu\text{m}^2$ | $+29.06\%$ | Logika combinational teroptimasi |
| **Tile Area Fraction ($1 \times 1$)** | **$27.61\%$** | **$11.14\%$** | **$35.75\%$** | **$+8.14\%$** | — | **Fraksi luas sel standar pra-tata-letak** |
| **Tile Cell Headroom** | **$72.39\%$** | **$88.86\%$** | **$64.25\%$** | **$-8.14\%$** | — | **Kelonggaran luas pra-tata-letak: $11,588\,\mu\text{m}^2$** |
| **Operational Slack @ 20 kHz** | $+49,988.61\,\text{ns}$ | $+49,989.93\,\text{ns}$ | $+49,988.37\,\text{ns}$ | $-0.24\,\text{ns}$ | — | Margin timing $> 49.9\,\mu\text{s}$ (MET) |
| **Total Negative Slack (TNS)** | **$0.00\,\text{ns}$** | **$0.00\,\text{ns}$** | **$0.00\,\text{ns}$** | **$0.00\,\text{ns}$** | — | **Nol Pelanggaran Setup / Hold** |
| **STA Stress Slack @ 50 MHz** | $+8.5974\,\text{ns}$ | $+9.9048\,\text{ns}$ | $+8.3656\,\text{ns}$ | $-0.2318\,\text{ns}$ | — | Target stres STA tiruan (MET) |
| **Reg-to-Reg Path ($T_{crit}^{\text{reg}}$)** | $5.31\,\text{ns}$ | $4.85\,\text{ns}$ | $5.3947\,\text{ns}$ | $+0.08\,\text{ns}$ | $+1.51\%$ | **Pre-layout reg-to-reg Fmax metric: 185.3 MHz** |
| **I/O Constrained Period ($T_{crit}^{\text{IO}}$)**| **$11.4026\,\text{ns}$** | **$10.0952\,\text{ns}$** | **$11.6344\,\text{ns}$** | **$+0.2318\,\text{ns}$** | **$+2.03\%$** | **STA assumptions: 5 ns in / 5 ns out / 30 fF load** |
| **Pre-Layout Core Fmax ($F_{\max, \text{IO}}$)**| **$87.70\,\text{MHz}$** | **$99.06\,\text{MHz}$** | **$85.95\,\text{MHz}$** | **$-1.75\,\text{MHz}$** | **$-2.00\%$** | **Pre-layout I/O-constrained STA metric** |
| **Tiny Tapeout Package Limit** | $\approx 66\,\text{MHz}$ | $\approx 66\,\text{MHz}$ | $\approx 66\,\text{MHz}$ | $0.0\,\text{MHz}$ | — | **Tiny Tapeout I/O input rating (~66 MHz)** |
| **Liberty-Estimated Leakage** | **$2.12\,\text{nW}$** | **$0.81\,\text{nW}$** | **$2.74\,\text{nW}$** | **$+0.62\,\text{nW}$** | **$+29.25\%$** | **$P_{leak}^{\text{prelayout, lib}}$ (Liberty-based estimate)** |

---

## 3. ACTIVITY-DEPENDENT POWER ESTIMATION BREAKDOWN

Seluruh estimasi daya di bawah dianalisis pada tegangan suplai $V_{DD} = 1.80\,\text{V}$, suhu $T = 25^\circ\text{C}$, sudut proses *Typical-Typical* (TT) menggunakan OpenSTA 2.0.17 dengan *capacitive load* asumtif $C_L = 30\,\text{fF}$ pada port output.

> [!IMPORTANT]
> **Klasifikasi Metodologi Daya**:
> - **Skenario A (Dievaluasi di sini)**: *Assumption-based power* dengan sapuan aktivitas input global ($\alpha = 0.05, 0.10, 0.20$). Angka ini mencerminkan sensitivitas sirkuit terhadap aktivitas, bukan konsumsi daya aktual hardware.
> - **Skenario B (Direncanakan pada M5-F)**: *VCD-derived workload power* yang diturunkan langsung dari trace simulasi pergantian sinyal riil.

### 3.1 Jam Fungsional Protokol ($F_{clk} = 20\,\text{kHz}$, $T = 50.0\,\mu\text{s}$)

| Skenario Aktivitas Input (Asumsi) | Baseline ($B$) | Sentinel Core ($S_{\text{core}}$) | Integrated Top ($S_{\text{top}}$) | Overhead Bersih Top ($\Delta$) | Overhead Relatif ($\%$) |
|---|---|---|---|---|---|
| **Default Tool Activity (OpenSTA)** | $18.0\,\text{nW}$ ($15.9\,\text{nW}$ dyn) | $13.9\,\text{nW}$ ($13.1\,\text{nW}$ dyn) | $35.2\,\text{nW}$ ($32.4\,\text{nW}$ dyn) | $+17.2\,\text{nW}$ | $+95.6\%$ |
| **Assumed Low Activity ($\alpha = 0.05$, duty = 0.5)** | **$10.5\,\text{nW}$** ($8.41\,\text{nW}$ dyn) | **$5.34\,\text{nW}$** ($4.53\,\text{nW}$ dyn) | **$14.0\,\text{nW}$** ($11.3\,\text{nW}$ dyn) | **$+3.5\,\text{nW}$** | **$+33.3\%$** |
| **Assumed Nominal Activity ($\alpha = 0.10$, duty = 0.5)**| **$17.2\,\text{nW}$** ($15.0\,\text{nW}$ dyn) | **$14.4\,\text{nW}$** ($13.6\,\text{nW}$ dyn) | **$24.9\,\text{nW}$** ($22.2\,\text{nW}$ dyn) | **$+7.7\,\text{nW}$** | **$+44.8\%$** |
| **Assumed High Activity ($\alpha = 0.20$, duty = 0.5)** | **$33.4\,\text{nW}$** ($31.2\,\text{nW}$ dyn) | **$29.2\,\text{nW}$** ($28.4\,\text{nW}$ dyn) | **$46.1\,\text{nW}$** ($43.3\,\text{nW}$ dyn) | **$+12.7\,\text{nW}$** | **$+38.0\%$** |

### 3.2 Target Stres STA Tiruan ($F_{clk} = 50\,\text{MHz}$, $T = 20.0\,\text{ns}$)

> [!NOTE]
> Pengujian pada frekuensi $50\,\text{MHz}$ ini murni merupakan evaluasi stres dinamis sintetik untuk membuktikan linearitas disipasi daya terhadap frekuensi, bukan mode operasional fungsional sistem.

| Skenario Aktivitas Input (Asumsi) | Baseline ($B$) | Sentinel Core ($S_{\text{core}}$) | Integrated Top ($S_{\text{top}}$) | Overhead Bersih Top ($\Delta$) | Overhead Relatif ($\%$) |
|---|---|---|---|---|---|
| **Default Tool Activity (OpenSTA)** | $62.3\,\mu\text{W}$ | $36.7\,\mu\text{W}$ | $82.2\,\mu\text{W}$ | $+19.9\,\mu\text{W}$ | $+31.9\%$ |
| **Assumed Low Activity ($\alpha = 0.05$, duty = 0.5)** | $28.3\,\mu\text{W}$ | $18.9\,\mu\text{W}$ | $30.8\,\mu\text{W}$ | $+2.5\,\mu\text{W}$ | $+8.83\%$ |
| **Assumed Nominal Activity ($\alpha = 0.10$, duty = 0.5)**| $40.1\,\mu\text{W}$ | $57.1\,\mu\text{W}$ | $66.5\,\mu\text{W}$ | $+26.4\,\mu\text{W}$ | $+65.8\%$ |
| **Assumed High Activity ($\alpha = 0.20$, duty = 0.5)** | $61.0\,\mu\text{W}$ | $39.2\,\mu\text{W}$ | $109.0\,\mu\text{W}$ | $+48.0\,\mu\text{W}$ | $+78.7\%$ |

---

## 4. DETAILED TIMING ANALYSIS & SPEED CEILING DISAMBIGUATION

### 4.1 Jalur Kritis Register-to-Register Internal
Ekstraksi STA pada jalur murni antar-register (*flip-flop to flip-flop*) menunjukkan performa intrinsik logika internal:
- **Startpoint**: Register bit counter / FSM (`_1264_/CLK`, `sky130_fd_sc_hd__dfrtp_1`)
- **Endpoint**: Register state validasi (`_1193_/D`, `sky130_fd_sc_hd__dfrtp_1`)
- **Data Arrival Time**: $5.0857\,\text{ns}$
- **Library Setup Time**: $0.3090\,\text{ns}$
- **Total Internal Delay**: $T_{crit, \text{reg}} = 5.0857 + 0.3090 = \mathbf{5.3947\,\text{ns}}$
- **Slack pada 50 MHz**: $+14.6054\,\text{ns}$ (MET)
- **Pre-Layout Reg-to-Reg Fmax Metric**:
  $$F_{\max, \text{reg}} = \frac{1}{5.3947\,\text{ns}} \approx \mathbf{185.3\,\text{MHz}}$$

### 4.2 Jalur Kritis Terikat I/O Tiny Tapeout
Ketika batasan I/O Tiny Tapeout diterapkan sebagai **asumsi batasan STA** ($5.0\,\text{ns}$ external input delay + $5.0\,\text{ns}$ external output delay = $10.0\,\text{ns}$ budget eksternal):
- **Startpoint**: Input port `ui_in[6]`
- **Endpoint**: Output port `uo_out[7]` (jalur combinational bypass telemetri baseline yang melewati gerbang kontrol isolasi Sentinel)
- **Data Arrival Time**: $6.6344\,\text{ns}$ ($5.0\,\text{ns}$ input delay + $1.6344\,\text{ns}$ delay gerbang combinational)
- **Data Required Time**: $15.0000\,\text{ns}$ ($20.0\,\text{ns}$ period - $5.0\,\text{ns}$ output delay)
- **Slack pada 50 MHz**: $+8.3656\,\text{ns}$ (MET)
- **Total Critical Period**: $T_{crit, \text{IO}} = 11.6344\,\text{ns}$
- **Pre-Layout I/O-Constrained STA Metric**:
  $$F_{\max, \text{IO}} = \frac{1}{11.6344\,\text{ns}} = \mathbf{85.95\,\text{MHz}}$$
- **Tiny Tapeout Package Limit**: Clock pad input rating Tiny Tapeout adalah $\approx \mathbf{66\,\text{MHz}}$ dengan insertion delay $\le 10\,\text{ns}$.

> [!IMPORTANT]
> Angka $1.6344\,\text{ns}$ adalah delay propagasi combinational murni yang melintasi 5 tingkatan logika (`nand2b` $\to$ `nor3` $\to$ `a222oi` $\to$ `and3` $\to$ `a31oi`) pada jalur *pad-to-pad*. Angka ini **bukan** delay internal keseluruhan sirkuit.

---

## 5. HARDWARE LOGIC ACCOUNTING & OPTIMIZATION ANALYSIS

Karakterisasi sel standar menunjukkan adanya efek optimasi sintesis lintas batas (*inter-module boundary optimization*) saat Baseline dan Sentinel digabungkan dalam modul top `tt_um_ares_sentinel_project`:
- **Komponen Bruto Terpisah**:
  - Baseline Unprotected: $575$ sel ($4,979.78\,\mu\text{m}^2$)
  - Gross Sentinel Core: $214$ sel ($2,009.43\,\mu\text{m}^2$)
  - Penjumlahan Bruto Matematis ($B + S_{\text{core}}$): $789$ sel ($6,989.21\,\mu\text{m}^2$)
- **Komponen Terintegrasi ($S_{\text{top}}$)**:
  - Total Sel Riil: **$733$ sel** ($6,447.43\,\mu\text{m}^2$)
- **Reduksi Melalui Optimasi**:
  $$\text{Reduksi Sel} = 789 - 733 = \mathbf{56\text{ sel}} \quad (541.78\,\mu\text{m}^2)$$
  Yosys berhasil mengeliminasi redundansi logika pada antarmuka penangkapan edge `serial_clock`/`serial_data` dan multiplexer isolasi `uo_out`, menghasilkan integrasi yang lebih ramping daripada penjumlahan independen.
- **Overhead Bersih Sejati terhadap Baseline**:
  $$\Delta_{\text{Net}} = 733 - 575 = \mathbf{+158\text{ sel}} \quad (+27.48\%)$$
  $$\Delta\text{Area}_{\text{Net}} = 6,447.43 - 4,979.78 = \mathbf{+1,467.65\,\mu\text{m}^2} \quad (+29.47\%)$$

---

## 6. RAW LOG ARTIFACT PROVENANCE & REPRODUCIBILITY

Laporan ini didukung penuh oleh bukti log artefak raw yang dapat direproduksi secara mandiri:
1. `05_ASIC_Synthesis/results/baseline_synth_stat.txt` (Log Yosys Sintesis Baseline)
2. `05_ASIC_Synthesis/results/sentinel_synth_stat.txt` (Log Yosys Sintesis Sentinel Core)
3. `05_ASIC_Synthesis/results/top_synth_stat.txt` (Log Yosys Sintesis Integrated Top)
4. `05_ASIC_Synthesis/results/sta_baseline.txt` (Log OpenSTA Baseline)
5. `05_ASIC_Synthesis/results/sta_sentinel.txt` (Log OpenSTA Sentinel Core)
6. `05_ASIC_Synthesis/results/sta_top.txt` (Log OpenSTA Integrated Top)
7. `05_ASIC_Synthesis/scripts/run_sta_power_activity.tcl` (Skrip Sapuan Daya Aktivitas OpenSTA)
8. `05_ASIC_Synthesis/results/sta_power_activity_sweep.txt` (Log Raw Sapuan Daya Multi-Aktivitas)
9. Netlist Struktural Verilog: `baseline_synth_netlist.v`, `sentinel_synth_netlist.v`, `top_synth_netlist.v`
10. PDK Liberty: `05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib` (SHA-256 diverifikasi)
