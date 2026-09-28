# ==============================================================================
# ARES-RX Sentinel — Yosys ASIC Synthesis Script for Integrated Top (S_top)
# Target Process: SkyWater 130nm Standard Cells (sky130_fd_sc_hd)
# Corner: TT / 25C / 1.80V
# Authority: Technical Architect / Research Direction (WO-2026-M5-001-ARCH-REV-A)
# ==============================================================================

# 1. Read Baseline Verilog Sources
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/edge_detect.v
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/state_machine.v
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/data_multiplex.v

# 2. Read Sealed M4 Core Verilog Sources
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_timing_sentinel.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_latch.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_gate.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_l3.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_frame_fsm.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_arbiter.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_sentinel_top.v

# 3. Read M5 Top Integration Shell
read_verilog 05_ASIC_Synthesis/src/tt_um_ares_sentinel_project.v

# 4. Check Hierarchy
hierarchy -check -top tt_um_ares_sentinel_project

# 5. High-Level Synthesis & Flattening
synth -top tt_um_ares_sentinel_project -flatten

# 6. Sequential Cell Mapping to Sky130 DFFs
dfflibmap -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 7. Combinational Cell Mapping via ABC to Sky130 Standard Cells
abc -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 8. Tie-High and Tie-Low Mapping
hilomap -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO

# 9. Cleanup & Optimization
opt_clean -purge

# 9. Print Cell & Area Statistics
tee -o 05_ASIC_Synthesis/results/top_synth_stat.txt stat -liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib

# 10. Write Gate-Level Netlist
write_verilog -noattr 05_ASIC_Synthesis/results/top_synth_netlist.v
