# External References & Academic Provenance Catalog

This catalog documents the external reference materials, baseline academic prior art, and third-party artifacts associated with the ARES-RX Sentinel research project.

To maintain repository hygiene, optimal clone bandwidth, and strict version control best practices, large third-party binary artifacts (PDFs and presentation slide decks) are not checked into the primary Git tree. They are documented below with complete metadata, citations, and upstream access URLs.

---

## 1. Upstream Baseline Implementation

- **Project Title:** Manchester Decoder on the Tiny Tapeout 07 Shuttle
- **Author / Designer:** Zachary Kohnen
- **Affiliation:** Eindhoven University of Technology (TU/e), Department of Electrical Engineering
- **Upstream Repository:** [https://github.com/DusterTheFirst/tt07-bep-decode](https://github.com/DusterTheFirst/tt07-bep-decode)
- **Target Process / Shuttle:** SkyWater 130nm CMOS (`sky130_fd_sc_hd`), Tiny Tapeout 07 (TT07)
- **Design Overview:** A Manchester-encoded wireless packet receiver for a home thermostat (433 MHz RF ASK/OOK link). Implements dual FSMs for Manchester edge timing decode and 96-bit packet frame extraction.
- **Local Baseline Location:** `03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/` (Verilog RTL preserved for comparative benchmark).

---

## 2. Associated Academic Publications & Presentations

### 2.1 Bachelor's Thesis
- **Title:** *Manchester Decoder of a Home Thermostat's Wireless Protocol in the Tiny Tapeout 07 Shuttle*
- **Author:** Zachary Kohnen
- **Degree:** Bachelor of Science (BSc) in Electrical Engineering
- **Institution:** Eindhoven University of Technology (TU/e), Casimir Institute
- **Year:** 2025
- **Original Document:** `BSc Thesis - Zachary Kohnen.pdf` (2.08 MB)
- **Quarantine Reference:** `99_Quarantine/references_3rdparty_binaries/BSc Thesis - Zachary Kohnen.pdf`
- **Upstream Access:** Available via the upstream project repository at [tt07-bep-decode/docs](https://github.com/DusterTheFirst/tt07-bep-decode).

### 2.2 Conference Presentation (Free Silicon Conference - FSiC 2025)
- **Title:** *Manchester Decoder of a Home Thermostat’s Wireless Protocol in the Tiny Tapeout 07 Shuttle*
- **Authors:** Zachary Kohnen and Alex Alvarado
- **Conference:** 2025 Free Silicon Conference (FSiC 2025)
- **Location:** Frankfurt an der Oder, Germany
- **Date:** July 2025
- **Conference Recording:** [PeerTube Video](https://peertube.f-si.org/w/nxpSoEMwNQ6MwAt6Z65Aeo)
- **Original Slides:** 
  - `FSIC2025 - Zachary Kohnen - Manchester decoder TT07.pdf` (38.19 MB)
  - `FSIC2025 - Zachary Kohnen - Manchester decoder TT07.pptx` (14.50 MB)
- **Quarantine Reference:** `99_Quarantine/references_3rdparty_binaries/`
- **Upstream Access:** [https://github.com/DusterTheFirst/tt07-bep-decode](https://github.com/DusterTheFirst/tt07-bep-decode).

### 2.3 Scientific Poster Session
- **Title:** *Tiny Tapeout 07 Manchester Decoder Demonstration*
- **Presenter:** Zachary Kohnen
- **Event:** Casimir Institute Launch Event, TU/e
- **Date:** September 2025
- **Original Poster:** `Poster Chips Event - Zachary Kohnen.pdf` (721 KB)
- **Quarantine Reference:** `99_Quarantine/references_3rdparty_binaries/Poster Chips Event - Zachary Kohnen.pdf`
- **Upstream Access:** [https://github.com/DusterTheFirst/tt07-bep-decode](https://github.com/DusterTheFirst/tt07-bep-decode).

---

## 3. Local Reference Diagrams

The following lightweight vector architecture diagrams remain directly available in the reference directory:
- `02_References/ARES-RX_Sentinel/TinyTapeout/elaborated.svg`: Manchester edge decoding state machine diagram.
- `02_References/ARES-RX_Sentinel/TinyTapeout/data_layout1.svg`: Shift register validation and buffer loading layout.
- `02_References/ARES-RX_Sentinel/TinyTapeout/data_layout2.svg`: Over-the-air packet bit format and frame boundaries.
- `02_References/ARES-RX_Sentinel/TinyTapeout/info.md`: Technical summary and pin-mapping specification.
