# ==============================================================================
# Yosys Comparative Elaboration Script (M5-A Pre-Synthesis Baseline vs Sentinel)
# Authority: Technical Architect / Research Direction (WO-2026-M5-001-ARCH-REV-A)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Elaborate Baseline Unprotected (B)
# ------------------------------------------------------------------------------
design -reset
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/project.v
hierarchy -check -top tt_um_dusterthefirst_project
proc
opt
check -assert
tee -o 05_ASIC_Synthesis/results/elab_baseline_stat.txt stat

# ------------------------------------------------------------------------------
# 2. Elaborate Sentinel Core Subsystem (S_core)
# ------------------------------------------------------------------------------
design -reset
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_timing_sentinel.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_latch.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_gate.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_l3.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_frame_fsm.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_arbiter.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_sentinel_top.v
hierarchy -check -top ares_sentinel_top
proc
opt
check -assert
tee -o 05_ASIC_Synthesis/results/elab_sentinel_stat.txt stat

# ------------------------------------------------------------------------------
# 3. Elaborate Integrated Top Subsystem (S_top)
# ------------------------------------------------------------------------------
design -reset
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/edge_detect.v
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/state_machine.v
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/data_multiplex.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_timing_sentinel.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_latch.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_gate.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_l3.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_frame_fsm.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_arbiter.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_sentinel_top.v
read_verilog 05_ASIC_Synthesis/src/tt_um_ares_sentinel_project.v
hierarchy -check -top tt_um_ares_sentinel_project
proc
opt
check -assert
tee -o 05_ASIC_Synthesis/results/elab_top_stat.txt stat
