# ARES-RX Sentinel — Stage M5-B: Toolchain Reproducibility Manifest
**Authority:** Technical Architect / Research Direction  
**Work Order:** `WO-2026-M5-001-ARCH-REV-A`  
**Timestamp:** 2026-09-27T15:02:00+07:00  
**Status:** FROZEN & SEALED  

---

## 1. PURPOSE & PROVENANCE COMMITMENT

Sesuai direktif Technical Architect pada Work Order `WO-2026-M5-001-ARCH-REV-A`:
> *"M5-B: Pilih satu reproducible flow utama. Jangan mencampur random local Yosys + random OpenLane version + TinyTapeout GitHub Action tanpa provenance. Setiap report harus menyimpan: tool version, PDK version, standard-cell library commit/hash, command, constraint file, source manifest."*

Dokumen ini membekukan seluruh lingkungan eksekusi EDA, file pustaka sel standar, batasan timing, dan dependensi sumber untuk menjamin reproduktifitas 100% dari seluruh hasil sintesis dan Static Timing Analysis (STA).

---

## 2. EDA TOOLCHAIN ENVIRONMENT

| Perangkat Lunak | Biner / Perintah | Versi Resmi | Commit / Build Info | Lingkungan OS |
|---|---|---|---|---|
| **Logic Synthesis** | `/usr/bin/yosys` | **Yosys 0.52** | `git sha1 fee39a3284c90249e1d9684cf6944ffbbcbb8f90` | Linux x86_64 (WSL2 Ubuntu 26.04) |
| **Static Timing Engine** | `/usr/bin/sta` | **OpenSTA 2.0.17** | `0~20191111gitc018cb2+dfsg-1.1` | Linux x86_64 (WSL2 Ubuntu 26.04) |
| **RTL Compiler & Sim** | `iverilog.exe` | **Icarus Verilog 13.0** | Windows x64 Native Build | Windows 11 (Host) |
| **Python Model Engine** | `python.exe` | **Python 3.12.8** | CPython 64-bit | Windows 11 (Host) |

---

## 3. PDK & STANDARD CELL LIBRARY PROVENANCE

| Atribut PDK | Parameter Resmi | Catatan Teknis |
|---|---|---|
| **PDK Process** | **SkyWater 130nm CMOS** | Kompatibel penuh Tiny Tapeout TT07/TT08 |
| **Standard Cell Library**| **`sky130_fd_sc_hd`** | High-Density 7-track standard cells ($W_{\text{unit}} = 0.46\,\mu\text{m}, H = 2.72\,\mu\text{m}$) |
| **Characterization Corner**| **Typical-Typical (TT)** | Kondisi nominal: $V_{DD} = 1.80\,\text{V}$, $T = 25^\circ\text{C}$ |
| **Timing Liberty File** | [`05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib`](file:///c:/Users/ahmad/OneDrive/Vscode/03_Core_Projects/ARES%20SEMIKONDUKTOR%20TECHNOLOGY/05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib) | 12,841,637 bytes |
| **Liberty File SHA-256** | `8e78e14442062dba34d414fca6490b2f6b96038d4510d1438ca44fee31487135` | Ground truth hash |
| **Upstream Repository** | `efabless/skywater-pdk-libs-sky130_fd_sc_hd` | Branch: `master` |

---

## 4. DESIGN CONSTRAINTS & CLOCK CONVENTION

- **SDC File**: [`05_ASIC_Synthesis/constraints/ares_sentinel_sky130.sdc`](file:///c:/Users/ahmad/OneDrive/Vscode/03_Core_Projects/ARES%20SEMIKONDUKTOR%20TECHNOLOGY/05_ASIC_Synthesis/constraints/ares_sentinel_sky130.sdc)
- **Clock Semantics**:
  1. **Functional Protocol Clock**: $F_{clk} = 20\,\text{kHz}$ ($T_{clk} = 50,000.0\,\text{ns}$). Menjamin integritas jendela waktu Manchester $N_{HB}=8..10$, $N_{BIT}=16..20$, $N_{EOF}=64$.
  2. **STA Timing Target**: $50\,\text{MHz}$ ($T = 20.0\,\text{ns}$). Batasan stres OpenLane untuk mengekstraksi $T_{crit}$ dan menghitung $F_{\max} = 1 / T_{crit}$.

---

## 5. SOURCE CODE CRYPTOGRAPHIC MANIFEST

Seluruh modul M4 yang disertakan dalam sintesis telah dikunci secara kriptografis:

```text
1a81438d4a21d2bd9a993e9e29ca67f9d89441abacf04b5183d1a42b4fd50121 *ares_timing_sentinel.v
97a4c0a11f4b21711a6dc569caa1f993d72251db1105d8f5c263f3a98df3904a *ares_fault_latch.v
dc590938d3be8af2a181f6f11b2ddb815263e8d824d4f33e117a500722e14fe7 *ares_isolation_gate.v
a03c9502de512a89225fb13a048136bf2acb13f6d6cdb4166e9eeaf23c561767 *ares_isolation_l3.v
cf38b67bc8910f3d9837cec47bc61d38fc3e577ca99cd71e97685c7638dc4fb4 *ares_frame_fsm.v
e7016fa50ffa35f179fb32adf9773dbf19417c5e7ca9b3886e4c170cbc4b0f72 *ares_fault_arbiter.v
abad4a47a1917931dbe136004b4480a1ad78213451194f9e9ad2526bab9e6c8a *ares_sentinel_top.v
```

Manifest resmi: [`00_Governance/M4_Cryptographic_Manifest.sha256`](file:///c:/Users/ahmad/OneDrive/Vscode/03_Core_Projects/ARES%20SEMIKONDUKTOR%20TECHNOLOGY/00_Governance/M4_Cryptographic_Manifest.sha256).

---

## 6. REPRODUCIBLE SYNTHESIS RECIPE

Setiap target ($B$, $S_{\text{core}}$, $S_{\text{top}}$) disintesis menggunakan *synthesis pipeline* Yosys yang identik:
1. `read_verilog -sv` / `read_verilog`
2. `hierarchy -check -top <TOP_MODULE>`
3. `proc; opt; fsm; opt; memory; opt`
4. `techmap; opt`
5. `dfflibmap -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib`
6. `abc -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib`
7. `clean`
8. `stat -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib`
9. `write_verilog -noattr 05_ASIC_Synthesis/results/<target>_netlist.v`

---

## 7. PHYSICAL PLACE & ROUTE (P&R) BOUNDARY & EXECUTION GATE (STAGE M5-F)

Berdasarkan mandat resmi Technical Architect pada `WO-2026-M5-F-001`:
1. **Status**: Stage M5-A..E dinyatakan **CLOSED / QUALIFIED PRE-LAYOUT**, dan Stage M5-F dinyatakan **OPEN**.
2. **Kepatuhan Epistematik**: Dilarang mengklaim "tile fit", "final Fmax", "final power", atau "silicon-ready" sebelum bukti artefak fisik pasca-routing tersedia secara lengkap.
3. **Persyaratan Artefak Fisik M5-F**:
   - Manifest toolchain fisik (OpenLane/OpenROAD version, Magic version, Netgen version).
   - Provenans fisik PDK (SkyWater 130nm Tech LEF, Cell LEF, GDS views, layer rules).
   - Laporan Floorplan ($1 \times 1$ Tile Tiny Tapeout TT08 $\approx 167\,\mu\text{m} \times 108\,\mu\text{m}$).
   - Laporan Global & Detailed Placement (kemacetan / density).
   - Laporan Clock Tree Synthesis (CTS - skew, insertion delay).
   - Laporan Global & Detailed Routing (wirelength, via count, antenna violations).
   - Laporan Post-Route Static Timing Analysis (ekstraksi parasitik RC nyata, WNS/TNS, post-route Fmax).
   - Laporan Verifikasi Fisik: Clean DRC (Magic) & Clean LVS (Netgen).
   - GDSII Layout Final.
   - Matriks PPA Pasca-Routing ($B \leftrightarrow S_{\text{top}}$).


