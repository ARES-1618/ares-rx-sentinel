# ==============================================================================
# OpenSTA Post-Route Scenario B Power Characterization (VCD-Derived Workload)
# Target Process: SkyWater 130nm CMOS (sky130_fd_sc_hd__tt_025C_1v80)
# SPEF: OpenRCX extracted parasitics
# Workload Basis: 04_Verification/ARES-RX_Sentinel/waveforms/ares_sentinel_integrated.vcd
# ==============================================================================

set report_file "05_ASIC_Synthesis/results/sta_power_scenario_b_vcd.txt"
set fp [open $report_file "w"]
puts $fp "================================================================================"
puts $fp "ARES-RX SENTINEL — POST-ROUTE SCENARIO B POWER CHARACTERIZATION (VCD WORKLOAD)"
puts $fp "Process: SkyWater 130nm (sky130_fd_sc_hd__tt_025C_1v80, TT, 25C, 1.80V)"
puts $fp "Source VCD: 04_Verification/ARES-RX_Sentinel/waveforms/ares_sentinel_integrated.vcd"
puts $fp "VCD Duration: 834.78 us | 16,695 Clock Cycles"
puts $fp "Empirical Activity Rates:"
puts $fp "  - clk:        toggle=33,391  (activity = 2.0000, 1 toggle / edge)"
puts $fp "  - ui_in[0]:   toggle=2,368   (activity = 0.1418 trans/cycle, Manchester N_BIT=16..20)"
puts $fp "  - rst_n:      toggle=2       (activity = 0.0001 trans/cycle, initial de-assertion)"
puts $fp "  - ena:        toggle=0       (activity = 0.0000, tied high, duty = 1.0)"
puts $fp "  - ui_in[1..7]:toggle=0       (activity = 0.0000, idle/static)"
puts $fp "  - uio_in[*]:  toggle=0       (activity = 0.0000, idle/static)"
puts $fp "Date: [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts $fp "================================================================================\n"
close $fp

proc characterize_vcd_power {design_label verilog_path spef_path top_module} {
    global report_file
    set lib_path "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib"

    set freqs { { "20 kHz (Operational Protocol)" 50000.000 } { "50 MHz (STA Stress Target)" 20.000 } }

    foreach freq_info $freqs {
        set freq_label [lindex $freq_info 0]
        set period_ns [lindex $freq_info 1]

        read_liberty $lib_path
        read_verilog $verilog_path
        link_design $top_module
        read_spef $spef_path

        create_clock -name clk -period $period_ns [get_ports clk]
        set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
        set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
        set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]

        # Apply VCD-derived workload activity
        # Reset and Enable
        set_power_activity -input_ports [get_ports rst_n] -activity 0.0001 -duty 0.999
        set_power_activity -input_ports [get_ports ena] -activity 0.0000 -duty 1.0

        # Protocol Manchester input rx_in = ui_in[0]
        set_power_activity -input_ports [get_ports {ui_in[0]}] -activity 0.1418 -duty 0.500

        # Inactive inputs
        set_power_activity -input_ports [get_ports {ui_in[1] ui_in[2] ui_in[3] ui_in[4] ui_in[5] ui_in[6] ui_in[7]}] -activity 0.0000 -duty 0.0
        set_power_activity -input_ports [get_ports {uio_in[*]}] -activity 0.0000 -duty 0.0

        set fp [open $report_file "a"]
        puts $fp "################################################################################"
        puts $fp "DESIGN: $design_label ($top_module)"
        puts $fp "FREQUENCY: $freq_label (T = $period_ns ns)"
        puts $fp "WORKLOAD: Realistic VCD Protocol Stream (rx_in alpha=0.1418, idle=0)"
        puts $fp "################################################################################"
        close $fp

        report_power >> $report_file
    }
}

puts "=== Running Scenario B Characterization for Baseline ==="
characterize_vcd_power "Baseline (tt07-bep-decode in TT08)" "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.v" "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.spef" "tt_um_dusterthefirst_project"

puts "=== Running Scenario B Characterization for Sentinel Integrated Top ==="
characterize_vcd_power "ARES Sentinel Integrated Top" "05_ASIC_Synthesis/pnr/results/top/top_routed.v" "05_ASIC_Synthesis/pnr/results/top/top_routed.spef" "tt_um_ares_sentinel_project"

puts "=== Scenario B Characterization Complete ==="
exit 0
