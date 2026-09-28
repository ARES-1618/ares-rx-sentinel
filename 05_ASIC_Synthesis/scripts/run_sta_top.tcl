# ==============================================================================
# OpenSTA Static Timing Analysis Script for Integrated Top (S_top)
# Target Process: SkyWater 130nm Standard Cells (sky130_fd_sc_hd)
# Authority: Technical Architect / Research Direction (WO-2026-M5-001-ARCH-REV-A)
# ==============================================================================

# 1. Read Standard Cell Liberty File & Gate-Level Netlist
read_liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog 05_ASIC_Synthesis/results/top_synth_netlist.v
link_design tt_um_ares_sentinel_project

# ------------------------------------------------------------------------------
# 2. Operational Protocol Analysis (20 kHz, T = 50,000.0 ns)
# ------------------------------------------------------------------------------
create_clock -name clk -period 50000.000 [get_ports clk]
set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]

puts "================================================================================"
puts "ARES-RX Sentinel (S_top) — Operational Timing at 20 kHz (T = 50,000 ns)"
puts "================================================================================"
report_worst_slack -max
report_worst_slack -min
report_tns

# ------------------------------------------------------------------------------
# 3. STA Stress Target & Critical Path Extraction (50 MHz, T = 20.0 ns)
# ------------------------------------------------------------------------------
create_clock -name clk -period 20.000 [get_ports clk]

puts "================================================================================"
puts "ARES-RX Sentinel (S_top) — STA Stress Target at 50 MHz (T = 20.0 ns)"
puts "================================================================================"
report_worst_slack -max
report_worst_slack -min
report_tns

puts "================================================================================"
puts "Critical Path Report & Data Arrival Time:"
puts "================================================================================"
report_checks -path_delay max -fields {slew cap input nets fanout} -digits 4
