# ==============================================================================
# OpenSTA Post-Route Sign-off STA & Activity-Dependent Power Script
# PDK: SkyWater 130nm Standard Cells (sky130_fd_sc_hd)
# Corner: TT / 25C / 1.80V (sky130_fd_sc_hd__tt_025C_1v80.lib)
# Parasitics: OpenRCX Extracted SPEF (rules.openrcx.sky130A.nom.spef_extractor)
# ==============================================================================

set report_file "05_ASIC_Synthesis/pnr/results/post_route_sta_reports.txt"
set fp [open $report_file "w"]
puts $fp "================================================================================"
puts $fp "ARES-RX SENTINEL — POST-ROUTE SIGN-OFF STA & POWER BENCHMARKING REPORT"
puts $fp "PDK: SkyWater 130nm sky130_fd_sc_hd__tt_025C_1v80 (TT, 25C, 1.80V)"
puts $fp "Extraction: OpenRCX Nominal SPEF | Flow: OpenROAD TritonRoute 1x1 Tile"
puts $fp "Date: [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts $fp "================================================================================\n"
close $fp

proc characterize_post_route {design_name verilog_path spef_path top_module} {
    global report_file
    set lib_path "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib"

    set fp [open $report_file "a"]
    puts $fp "################################################################################"
    puts $fp "POST-ROUTE DESIGN: $design_name ($top_module)"
    puts $fp "Netlist: $verilog_path"
    puts $fp "SPEF:    $spef_path"
    puts $fp "################################################################################\n"
    close $fp

    # 1. Reg-to-reg and Timing Characterization at 50 MHz (20 ns)
    read_liberty $lib_path
    read_verilog $verilog_path
    link_design $top_module
    read_spef $spef_path

    create_clock -name clk -period 20.000 [get_ports clk]
    set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
    set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
    set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]

    set fp [open $report_file "a"]
    puts $fp "--- [1] TIMING CHECKS @ 50 MHz (Period = 20.000 ns, IO Delay = 5.000 ns) ---"
    close $fp

    # Reg to reg path
    set fp [open $report_file "a"]
    puts $fp "\n>>> CRITICAL PATH: REG-TO-REG <<<"
    close $fp
    report_checks -from [all_registers] -to [all_registers] -path_delay max -fields {slew cap input nets fanout} -format full_clock_expanded >> $report_file

    # Input to Reg path
    set fp [open $report_file "a"]
    puts $fp "\n>>> CRITICAL PATH: IN-TO-REG <<<"
    close $fp
    report_checks -from [all_inputs] -to [all_registers] -path_delay max -fields {slew cap input nets fanout} -format full_clock_expanded >> $report_file

    # Reg to Out path
    set fp [open $report_file "a"]
    puts $fp "\n>>> CRITICAL PATH: REG-TO-OUT <<<"
    close $fp
    report_checks -from [all_registers] -to [all_outputs] -path_delay max -fields {slew cap input nets fanout} -format full_clock_expanded >> $report_file

    # In to Out path
    set fp [open $report_file "a"]
    puts $fp "\n>>> CRITICAL PATH: IN-TO-OUT (FEEDTHROUGH) <<<"
    close $fp
    report_checks -from [all_inputs] -to [all_outputs] -path_delay max -fields {slew cap input nets fanout} -format full_clock_expanded >> $report_file

    # Hold check
    set fp [open $report_file "a"]
    puts $fp "\n>>> HOLD CHECK (MIN DELAY) <<<"
    close $fp
    report_checks -path_delay min -fields {slew cap input nets fanout} -format full_clock_expanded >> $report_file

    # Clock skew
    set fp [open $report_file "a"]
    puts $fp "\n>>> CLOCK TREE METRICS <<<"
    close $fp
    report_clock_skew >> $report_file

    # 2. Activity-dependent Power Sweeps at 20 kHz and 50 MHz
    set freqs { { "20 kHz (Operational Protocol)" 50000.000 } { "50 MHz (STA Stress Target)" 20.000 } }
    set activities { { "Default (Tool Default)" "" "" } { "Low (alpha = 0.05, duty = 0.5)" 0.05 0.5 } { "Nominal (alpha = 0.10, duty = 0.5)" 0.10 0.5 } { "Elevated (alpha = 0.20, duty = 0.5)" 0.20 0.5 } }

    set fp [open $report_file "a"]
    puts $fp "\n--- [2] ACTIVITY-DEPENDENT POWER SWEEP ---"
    close $fp

    foreach freq_info $freqs {
        set freq_label [lindex $freq_info 0]
        set period_ns [lindex $freq_info 1]

        set fp [open $report_file "a"]
        puts $fp "\n================================================================================"
        puts $fp ">>> FREQUENCY: $freq_label (T = $period_ns ns)"
        puts $fp "================================================================================"
        close $fp

        foreach act_info $activities {
            set act_label [lindex $act_info 0]
            set alpha [lindex $act_info 1]
            set duty [lindex $act_info 2]

            read_liberty $lib_path
            read_verilog $verilog_path
            link_design $top_module
            read_spef $spef_path

            create_clock -name clk -period $period_ns [get_ports clk]
            set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
            set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
            set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]

            if {$alpha ne ""} {
                set_power_activity -input -activity $alpha -duty $duty
            }

            set fp [open $report_file "a"]
            puts $fp "\n>>> Activity Scenario: $act_label"
            close $fp

            report_power >> $report_file
        }
    }
}

puts "=== Characterizing Baseline Routed Design ==="
characterize_post_route "Baseline (tt07-bep-decode in TT08)" "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.v" "05_ASIC_Synthesis/pnr/results/baseline/baseline_routed.spef" "tt_um_dusterthefirst_project"

puts "=== Characterizing Top Integrated Routed Design ==="
characterize_post_route "ARES Sentinel Integrated Top" "05_ASIC_Synthesis/pnr/results/top/top_routed.v" "05_ASIC_Synthesis/pnr/results/top/top_routed.spef" "tt_um_ares_sentinel_project"

puts "=== Post-Route STA & Power Characterization Complete ==="
exit 0
