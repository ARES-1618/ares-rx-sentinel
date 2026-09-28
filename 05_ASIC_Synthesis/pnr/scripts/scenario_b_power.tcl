# ==============================================================================
# OpenSTA Post-Route Scenario B Power Script (Workload-derived: alpha = 0.075)
# ==============================================================================
set lib_path "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib"

proc run_sta_power {design_name verilog_path spef_path top_module} {
    global lib_path
    puts "================================================================================"
    puts "DESIGN: $design_name ($top_module)"
    puts "================================================================================"
    
    # 20 kHz
    read_liberty $lib_path
    read_verilog $verilog_path
    link_design $top_module
    read_spef $spef_path
    create_clock -name clk -period 50000.0 [get_ports clk]
    set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
    set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
    set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
    set_power_activity -input -activity 0.075 -duty 0.5
    puts ">>> FREQ: 20 kHz (T = 50000 ns) | Scenario B: Workload-Derived (alpha = 0.075, duty = 0.5)"
    report_power

    # 50 MHz
    read_liberty $lib_path
    read_verilog $verilog_path
    link_design $top_module
    read_spef $spef_path
    create_clock -name clk -period 20.0 [get_ports clk]
    set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
    set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
    set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
    set_power_activity -input -activity 0.075 -duty 0.5
    puts ">>> FREQ: 50 MHz (T = 20 ns) | Scenario B: Workload-Derived (alpha = 0.075, duty = 0.5)"
    report_power
}

run_sta_power "Baseline (tt07-bep-decode in TT08)" "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.v" "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.spef" "tt_um_dusterthefirst_project"
run_sta_power "Sentinel Top Integrated" "05_ASIC_Synthesis/pnr/results/top/top_routed.v" "05_ASIC_Synthesis/pnr/results/top/top_routed.spef" "tt_um_ares_sentinel_project"

exit 0
