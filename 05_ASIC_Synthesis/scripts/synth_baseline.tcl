# ==============================================================================
# ARES-RX Sentinel — Yosys ASIC Synthesis Script for Baseline Unprotected (B)
# Target Process: SkyWater 130nm Standard Cells (sky130_fd_sc_hd)
# Corner: TT / 25C / 1.80V
# Authority: Technical Architect / Research Direction (WO-2026-M5-001-ARCH-REV-A)
# ==============================================================================

# 1. Read Baseline Verilog Sources
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/project.v

# 2. Check Hierarchy
hierarchy -check -top tt_um_dusterthefirst_project

# 3. High-Level Synthesis & Flattening
synth -top tt_um_dusterthefirst_project -flatten

# 4. Sequential Cell Mapping to Sky130 DFFs
dfflibmap -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 5. Combinational Cell Mapping via ABC to Sky130 Standard Cells
abc -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 6. Tie-High and Tie-Low Mapping
hilomap -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO

# 7. Cleanup & Optimization
opt_clean -purge

# 7. Print Cell & Area Statistics
tee -o 05_ASIC_Synthesis/results/baseline_synth_stat.txt stat -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 8. Write Gate-Level Netlist
write_verilog -noattr 05_ASIC_Synthesis/results/baseline_synth_netlist.v
