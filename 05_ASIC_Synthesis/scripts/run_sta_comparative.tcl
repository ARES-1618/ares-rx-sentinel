# ==============================================================================
# OpenSTA Comparative Static Timing & Power Analysis Script
# Target Process: SkyWater 130nm Standard Cells (sky130_fd_sc_hd)
# Corner: TT / 25C / 1.80V
# Authority: Technical Architect / Research Direction (WO-2026-M5-001-ARCH-REV-A)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Baseline Unprotected (B)
# ------------------------------------------------------------------------------
read_liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog 05_ASIC_Synthesis/results/baseline_synth_netlist.v
link_design tt_um_dusterthefirst_project

# 20 kHz operational timing
create_clock -name clk -period 50000.000 [get_ports clk]
set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]

set fp [open "05_ASIC_Synthesis/results/sta_baseline.txt" "w"]
puts $fp "================================================================================"
puts $fp "BASELINE UNPROTECTED (B) — OPENSTA TIMING & POWER REPORT"
puts $fp "================================================================================"
puts $fp "--- 1. OPERATIONAL TIMING (20 kHz, T = 50,000 ns) ---"
close $fp

report_checks -path_delay max -digits 4 >> 05_ASIC_Synthesis/results/sta_baseline.txt
report_tns >> 05_ASIC_Synthesis/results/sta_baseline.txt
report_power >> 05_ASIC_Synthesis/results/sta_baseline.txt

# 50 MHz stress timing
create_clock -name clk -period 20.000 [get_ports clk]

set fp [open "05_ASIC_Synthesis/results/sta_baseline.txt" "a"]
puts $fp "\n--- 2. STA STRESS TIMING (50 MHz, T = 20.0 ns) ---"
close $fp

report_checks -path_delay max -digits 4 >> 05_ASIC_Synthesis/results/sta_baseline.txt
report_tns >> 05_ASIC_Synthesis/results/sta_baseline.txt
report_power >> 05_ASIC_Synthesis/results/sta_baseline.txt

# ------------------------------------------------------------------------------
# 2. Sentinel Core Subsystem (S_core)
# ------------------------------------------------------------------------------
read_liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog 05_ASIC_Synthesis/results/sentinel_synth_netlist.v
link_design ares_sentinel_top

# 20 kHz operational timing
create_clock -name clk -period 50000.000 [get_ports clk]
set_input_delay -clock clk 5.000 [all_inputs]
set_output_delay -clock clk 5.000 [all_outputs]

set fp [open "05_ASIC_Synthesis/results/sta_sentinel.txt" "w"]
puts $fp "================================================================================"
puts $fp "SENTINEL SUBSYSTEM (S_core) — OPENSTA TIMING & POWER REPORT"
puts $fp "================================================================================"
puts $fp "--- 1. OPERATIONAL TIMING (20 kHz, T = 50,000 ns) ---"
close $fp

report_checks -path_delay max -digits 4 >> 05_ASIC_Synthesis/results/sta_sentinel.txt
report_tns >> 05_ASIC_Synthesis/results/sta_sentinel.txt
report_power >> 05_ASIC_Synthesis/results/sta_sentinel.txt

# 50 MHz stress timing
create_clock -name clk -period 20.000 [get_ports clk]

set fp [open "05_ASIC_Synthesis/results/sta_sentinel.txt" "a"]
puts $fp "\n--- 2. STA STRESS TIMING (50 MHz, T = 20.0 ns) ---"
close $fp

report_checks -path_delay max -digits 4 >> 05_ASIC_Synthesis/results/sta_sentinel.txt
report_tns >> 05_ASIC_Synthesis/results/sta_sentinel.txt
report_power >> 05_ASIC_Synthesis/results/sta_sentinel.txt

# ------------------------------------------------------------------------------
# 3. Integrated Top Subsystem (S_top)
# ------------------------------------------------------------------------------
read_liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog 05_ASIC_Synthesis/results/top_synth_netlist.v
link_design tt_um_ares_sentinel_project

# 20 kHz operational timing
create_clock -name clk -period 50000.000 [get_ports clk]
set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]

set fp [open "05_ASIC_Synthesis/results/sta_top.txt" "w"]
puts $fp "================================================================================"
puts $fp "INTEGRATED TOP SUBSYSTEM (S_top) — OPENSTA TIMING & POWER REPORT"
puts $fp "================================================================================"
puts $fp "--- 1. OPERATIONAL TIMING (20 kHz, T = 50,000 ns) ---"
close $fp

report_checks -path_delay max -digits 4 >> 05_ASIC_Synthesis/results/sta_top.txt
report_tns >> 05_ASIC_Synthesis/results/sta_top.txt
report_power >> 05_ASIC_Synthesis/results/sta_top.txt

# 50 MHz stress timing
create_clock -name clk -period 20.000 [get_ports clk]

set fp [open "05_ASIC_Synthesis/results/sta_top.txt" "a"]
puts $fp "\n--- 2. STA STRESS TIMING (50 MHz, T = 20.0 ns) ---"
close $fp

report_checks -path_delay max -digits 4 >> 05_ASIC_Synthesis/results/sta_top.txt
report_tns >> 05_ASIC_Synthesis/results/sta_top.txt
report_power >> 05_ASIC_Synthesis/results/sta_top.txt

exit
