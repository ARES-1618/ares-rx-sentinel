# ==============================================================================
# Yosys RTL Elaboration & Hierarchy Check Script
# Target: tt_um_ares_sentinel_project
# Standard: Tiny Tapeout TT08
# ==============================================================================

# Read Baseline Modules (SystemVerilog)
# Note: data_multiplex.v includes serial_decode.v, which includes data_validate.v
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/edge_detect.v
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/state_machine.v
read_verilog -sv -I 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src 03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/data_multiplex.v

# Read Sealed M4 Core Modules (Verilog-2001)
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_timing_sentinel.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_latch.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_gate.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_l3.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_frame_fsm.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_arbiter.v
read_verilog 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_sentinel_top.v

# Read M5 Top Integration Shell
read_verilog 05_ASIC_Synthesis/src/tt_um_ares_sentinel_project.v

# Check Hierarchy & Elaborate
hierarchy -check -top tt_um_ares_sentinel_project

# Process RTL to generic cells
proc
opt
check -assert

# Print Generic Cell Statistics
stat
