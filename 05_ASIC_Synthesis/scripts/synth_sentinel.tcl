# ==============================================================================
# ARES-RX Sentinel — Yosys ASIC Synthesis Script for Sentinel Subsystem (S_core)
# Target Process: SkyWater 130nm Standard Cells (sky130_fd_sc_hd)
# Corner: TT / 25C / 1.80V
# Authority: Technical Architect / Research Direction (WO-2026-M5-001-ARCH-REV-A)
# ==============================================================================

# 1. Read Sealed M4 Verilog Sources
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_timing_sentinel.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_latch.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_gate.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_l3.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_frame_fsm.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_arbiter.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_sentinel_top.v

# 2. Check Hierarchy
hierarchy -check -top ares_sentinel_top

# 3. High-Level Synthesis & Flattening
synth -top ares_sentinel_top -flatten

# 4. Sequential Cell Mapping to Sky130 DFFs
dfflibmap -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 5. Combinational Cell Mapping via ABC to Sky130 Standard Cells
abc -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 6. Cleanup & Optimization
opt_clean -purge

# 7. Print Cell & Area Statistics
tee -o 05_ASIC_Synthesis/results/sentinel_synth_stat.txt stat -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 8. Write Gate-Level Netlist
write_verilog -noattr 05_ASIC_Synthesis/results/sentinel_synth_netlist.v
